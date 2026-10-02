package app.fieldwatch.domain

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

data class DebriefSection(
    val number: String,
    val title: String,
    val body: String,
    val alert: Boolean = false,
)

data class DebriefPlaces(
    val attempted: Boolean,
    val available: Boolean,
    val note: String,
    val lines: List<String> = emptyList(),
    val namesByCell: Map<String, String> = emptyMap(),
) {
    /** Exact GPS cell, then nearest named cell within [maxM]. */
    fun nameNear(lat: Double, lon: Double, maxM: Double = 90.0): String? {
        namesByCell[Geo.cellKey(lat, lon)]?.let { return it }
        var best: String? = null
        var bestD = maxM
        for ((key, name) in namesByCell) {
            val parts = key.split(',')
            if (parts.size != 2) continue
            val klat = parts[0].toDoubleOrNull() ?: continue
            val klon = parts[1].toDoubleOrNull() ?: continue
            val d = Geo.meters(lat, lon, klat, klon)
            if (d < bestD) {
                bestD = d
                best = name
            }
        }
        return best
    }

    fun areaLine(): String {
        if (!attempted) return "关闭"
        val named = namesByCell.values.map { it.trim() }.filter { it.isNotEmpty() }.distinct()
        if (named.isEmpty()) return note
        return named.joinToString(" · ")
    }

    companion object {
        val Off = DebriefPlaces(false, false, "关闭")
    }
}

data class ExtraAttentionHit(
    val signature: String,
    val radioLabel: String,
    val note: String,
)

data class DebriefDoc(
    val generatedUtc: String,
    val windowLine: String,
    val meta: List<Pair<String, String>>,
    val disclaimer: String,
    val trackingAlert: Boolean,
    val takeaway: String,
    val sections: List<DebriefSection>,
    val extraAttention: List<ExtraAttentionHit> = emptyList(),
    val heading: String = "FIELDWATCH 观测总结",
    val pdfKicker: String = "观测总结",
    val pdfTitle: String = "观测总结",
    val pathFigure: SitPathPlot.Figure? = null,
    val extraFigures: List<SitPathPlot.Figure> = emptyList(),
) {
    fun toPlainText(): String = buildString {
        appendLine(heading)
        appendLine()
        appendLine("免责声明")
        appendLine(disclaimer)
        appendLine()
        meta.forEach { (k, v) -> appendLine("${k.padEnd(14)}$v") }
        appendLine()
        sections.forEach { sec ->
            appendLine("${sec.number}. ${sec.title.uppercase()}")
            appendLine(sec.body.trimEnd())
            appendLine()
        }
        appendLine("—")
        appendLine("要点：$takeaway")
    }

    fun withDemoMacs(macs: Collection<String>, demo: Boolean): DebriefDoc {
        if (!demo) return this
        fun t(s: String) = Geo.redactCoordsIn(MacUtil.redactMacsIn(s, macs, true), true)
        val note = "MAC 尾部（**:**:**）及 GPS 坐标已遮蔽。手机中的日志保持不变。"
        return copy(
            meta = listOf("隐私" to note) + meta.map { it.first to t(it.second) },
            disclaimer = t(disclaimer),
            takeaway = t(takeaway),
            sections = sections.map { it.copy(title = t(it.title), body = t(it.body)) },
            extraAttention = extraAttention.map {
                it.copy(signature = t(it.signature), radioLabel = t(it.radioLabel), note = t(it.note))
            },
        )
    }
}

/**
 * Standalone field debrief (not an AI prompt). Heuristic sit report from
 * the last 15 minutes plus GPS co-travel of tracker-like radios.
 */
object DebriefReport {
    private const val WINDOW_MS = 15 * 60_000L
    private const val SHORT_MS = 5 * 60_000L
    private const val MOVE_M = 45.0
    /** Possible-tail extra gates. Own-kit uses a louder, longer “still here” window. */
    private const val COVER_FRAC = 0.5
    private const val FADE_DB = 12
    private const val TRAIL_LOUD_DBM = CoTravel.TRAIL_LOUD_DBM
    /** Own-kit “still here” — AirTags advertise slowly and rotate. */
    private const val OWN_HERE_MS = 180_000L
    private const val TAIL_HERE_MS = 20_000L
    private const val ON_BODY_MAX = -55
    private const val ON_BODY_MIN = -70

    fun build(
        devices: List<Sighting>,
        fleets: List<Fleet>,
        settings: AppSettings,
        operatorPath: List<GpsSample>,
        now: Long = System.currentTimeMillis(),
        places: DebriefPlaces = DebriefPlaces.Off,
        window: DebriefWindow? = null,
        customNames: Map<String, String> = emptyMap(),
        observerNotes: Map<String, String> = emptyMap(),
        bookmarkedKeys: Set<String> = emptySet(),
        watchedFleetIds: Set<String> = emptySet(),
    ): String = document(
        devices, fleets, settings, operatorPath, now, places, window,
        customNames, observerNotes, bookmarkedKeys, watchedFleetIds,
    ).toPlainText()

    fun document(
        devices: List<Sighting>,
        fleets: List<Fleet>,
        settings: AppSettings,
        operatorPath: List<GpsSample>,
        now: Long = System.currentTimeMillis(),
        places: DebriefPlaces = DebriefPlaces.Off,
        window: DebriefWindow? = null,
        customNames: Map<String, String> = emptyMap(),
        observerNotes: Map<String, String> = emptyMap(),
        bookmarkedKeys: Set<String> = emptySet(),
        watchedFleetIds: Set<String> = emptySet(),
    ): DebriefDoc {
        val names = fleets.associate { it.id to it.name }
        val win = window ?: DebriefWindow(now - WINDOW_MS, now)
        val windowStart = win.startAt
        val windowEnd = win.endAt
        val inWin = devices.filter { it.lastSeen >= windowStart || it.firstSeen >= windowStart }
            .sortedByDescending { it.rssi }
        val wifi = inWin.filter { it.kind == RadioKind.WIFI }
        val ble = inWin.filter { it.kind == RadioKind.BLE }
        val named = inWin.filter { it.fleetIds.isNotEmpty() }
        val hidden = wifi.filter { it.hiddenSsid }
        val randomized = ble.count { it.randomized }
        val arrived = inWin.filter { it.firstSeen >= windowStart }
        val persistent = inWin.filter { dwellMs(it, windowStart, windowEnd) >= win.durationMs * 2 / 3 }
        val path = operatorPath.filter { it.at in windowStart..windowEnd }
        val pathSpan = Geo.spanM(path)
        val pathLen = Geo.pathLengthM(path)
        val trackers = inWin.filter { TrackerMatch.kind(it, names) == TrackerMatch.Kind.FINDER }
        val follow = followAssessments(trackers, names, path, windowStart, windowEnd, TrackerMatch.Kind.FINDER)
        val following = follow.filter { it.verdict == Verdict.FOLLOWING }
        val withYou = follow.filter { it.verdict == Verdict.MOVED_WITH_YOU }
        val ownLikely = follow.filter { it.verdict == Verdict.OWN_LIKELY }
        val wholeSit = ownLikely + withYou
        val beaconFollow = followAssessments(
            inWin.filter { TrackerMatch.kind(it, names) == TrackerMatch.Kind.BEACON },
            names, path, windowStart, windowEnd, TrackerMatch.Kind.BEACON,
        )
        val wearableFollow = followAssessments(
            inWin.filter { TrackerMatch.kind(it, names) == TrackerMatch.Kind.WEARABLE },
            names, path, windowStart, windowEnd, TrackerMatch.Kind.WEARABLE,
        )
        val beaconsWithYou = stayedWithYou(beaconFollow)
        val wearablesWithYou = stayedWithYou(wearableFollow)

        val byCh = wifi.groupBy { it.channel }.toSortedMap()
        val networks = buildString {
            appendLine("接收到 ${wifi.size} 个 AP；${hidden.size} 个隐藏 SSID；${persistent.count { it.kind == RadioKind.WIFI }} 个在该时段的大部分时间持续出现。")
            if (byCh.isNotEmpty()) {
                appendLine("信道占用：")
                byCh.forEach { (ch, list) ->
                    val label = if (ch == 0) "未知" else "信道 $ch"
                    appendLine("  $label — ${list.size} 个 AP，最强 ${list.maxOf { it.rssi }} dBm")
                }
            }
            appendLine("信号最强的 AP：")
            wifi.take(12).forEach { d ->
                appendLine("  · ${wifiLine(d, names, windowStart, now, customNames)}")
                d.attentionNotes(fleets).forEach { (sig, note) ->
                    appendLine("    重点关注（$sig）：$note")
                }
            }
            if (hidden.isNotEmpty()) {
                appendLine("隐藏 SSID：")
                hidden.forEach { appendLine("  · ${it.mac}  ${it.vendor ?: ""}  ${it.rssi} dBm  信道 ${it.channel}") }
            }
        }
        val notable = ble.filter {
            inventoryKeep(it, settings, bookmarkedKeys) &&
                (it.fleetIds.isNotEmpty() || it.name.isNotBlank() || it.rssi >= -65 || it.manufacturerId != null)
        }.sortedByDescending { it.rssi }.take(20)
        val omittedRand = ble.count { !inventoryKeep(it, settings, bookmarkedKeys) }
        val bleBody = buildString {
            appendLine("接收到 ${ble.size} 个广播设备；$randomized 个使用随机地址；${named.count { it.kind == RadioKind.BLE }} 个匹配了特征。")
            if (omittedRand > 0) {
                appendLine("列表中省略了未匹配特征的轮换地址 BLE 设备（$omittedRand 个），统计数量仍包含它们。观测导出包含所有无线设备。")
            }
            if (notable.isNotEmpty()) {
                appendLine("值得留意的 BLE：")
                notable.forEach { d ->
                    val guess = DeviceExplain.guess(d, d.fleetIds.map { names[it] ?: it })
                    appendLine("  · ${bleLine(d, names, windowStart, now, customNames)}  |  ${guess.headline}")
                    d.attentionNotes(fleets).forEach { (sig, note) ->
                        appendLine("    重点关注（$sig）：$note")
                    }
                    val decoded = SignatureFieldDecoder.decodeSighting(d, fleets)
                    if (decoded.isNotEmpty()) {
                        decoded.forEach { row ->
                            appendLine("    ${row.label}: ${row.display}")
                            if (row.note.isNotBlank()) appendLine("    ${row.note}")
                        }
                    } else {
                        d.liveDecode.forEach { chip ->
                            append("    ${chip.reportLabel()}")
                            if (chip.note.isNotBlank()) append("  ").append(chip.note)
                            appendLine()
                        }
                    }
                }
            }
        }
        val sigBody = buildString {
            if (named.isEmpty()) appendLine("本时段内没有。")
            else {
                named.groupBy { it.fleetIds.joinToString("+") { id -> names[id] ?: id } }
                    .toList().sortedByDescending { it.second.size }
                    .forEach { (sig, list) ->
                        appendLine("${list.size}× $sig")
                        list.sortedByDescending { it.rssi }.take(8).forEach { d ->
                            append("  · ${d.reportName(customNames)}  ${d.mac}  ${d.rssi} dBm")
                            val labels = d.liveDecode.reportLabels()
                            if (labels.isNotEmpty()) append("  ").append(labels.joinToString(", "))
                            appendLine()
                        }
                        list.flatMap { it.attentionNotes(fleets) }.distinct().forEach { (name, note) ->
                            appendLine("  重点关注（$name）：$note")
                        }
                    }
            }
        }
        val persistBody = buildString {
            appendLine("本时段大部分时间持续出现：${persistent.size}")
            persistent.filter { inventoryKeep(it, settings, bookmarkedKeys) }.take(15).forEach {
                appendLine("  · ${it.reportName(customNames)}  ${it.mac}  停留 ${fmtDur(dwellMs(it, windowStart, now))}")
            }
            if (persistent.isEmpty()) appendLine("  · 无。")
            appendLine("本时段首次发现：${arrived.size}（下方列出信号最强的 8 个）")
            arrived.filter { inventoryKeep(it, settings, bookmarkedKeys) }.sortedByDescending { it.rssi }.take(8).forEach {
                appendLine("  · ${it.reportName(customNames)}  ${it.mac}  ${it.rssi} dBm")
            }
        }
        val flags = anomalyLines(inWin, customNames, settings, bookmarkedKeys)
        val anomalyBody = if (flags.isEmpty()) {
            "没有其他标记。特征命中、重点关注和追踪提示已涵盖已命名的模式匹配。"
        } else flags.joinToString("\n") { "  · $it" }
        val attentionHits = inWin.flatMap { d ->
            d.attentionNotes(fleets).map { (sig, note) -> Triple(d, sig, note) }
        }
        val actionBody = actions(following, withYou, ownLikely, beaconsWithYou, wearablesWithYou, settings, pathSpan)
            .joinToString("\n") { "  · $it" }

        val distanceLine = when {
            !settings.tagLocation -> "GPS 位置标记已关闭，无轨迹"
            path.size < 2 -> "GPS 位置标记已开启，本时段内不足 2 个定位点"
            else -> "沿轨迹移动 ${fmtDist(pathLen)} · 跨度 ${fmtDist(pathSpan)} · ${path.size} 个定位点"
        }
        val lookupLine = when {
            !places.attempted -> "关闭"
            places.namesByCell.isNotEmpty() -> places.areaLine()
            else -> places.note
        }
        val pictures = AircraftTrail.pictures(
            inWin.mapNotNull { d ->
                AircraftTrail.source(d, d.reportName(customNames))
            },
            path,
        )
        val aircraftBody = AircraftTrail.body(pictures)
        var n = 1
        fun next() = (n++).toString()
        val sections = buildList {
            add(DebriefSection(next(), "概要", execSummary(wifi, ble, named, hidden, randomized, pathSpan, pathLen, following, withYou, ownLikely, beaconsWithYou, wearablesWithYou, settings, places, win) + craftSentence(pictures)))
            add(DebriefSection(next(), "所在地点", whereYouWere(settings, path, pathLen, pathSpan, inWin, names, places, windowEnd, customNames, bookmarkedKeys)))
            if (aircraftBody.isNotEmpty()) {
                add(DebriefSection(next(), "航空器", aircraftBody))
            }
            observerNotesSection(inWin, customNames, observerNotes)?.let { body ->
                add(DebriefSection(next(), "观测备注", body))
            }
            add(
                DebriefSection(
                    next(),
                    "追踪评估",
                    trackingSection(settings, path, pathSpan, pathLen, following, wholeSit, beaconsWithYou, wearablesWithYou),
                ),
            )
            if (wholeSit.isNotEmpty()) {
                add(
                    DebriefSection(
                        next(),
                        "可能随行的追踪器",
                        trackerCallout(
                            "寻物标签（AirTag / Find My、SmartTag、Tile、Chipolo、Pebblebee）及信号较强、可能在口袋中的 Apple BLE 设备。" +
                                "这些无线设备在本次观测期间持续随您的 GPS 轨迹出现。" +
                                "Fieldwatch 无法区分您的标签或手机，和出发前被放入车内、包中或身上的追踪器。" +
                                "请逐一核实每个 MAC。这不代表已确认的事实或身份。",
                            wholeSit,
                            customNames,
                        ),
                        alert = true,
                    ),
                )
            }
            if (following.isNotEmpty()) {
                add(
                    DebriefSection(
                        next(),
                        "可能尾随",
                        trackerCallout(
                            "这些寻物标签在本次观测开始时未被接收到，随后持续沿您的轨迹出现。" +
                                "这可能表示有人开始随行（其手机或标签），也可能是途中新增了设备。" +
                                "这不代表已确认的事实或身份。",
                            following,
                            customNames,
                        ),
                        alert = true,
                    ),
                )
            }
            if (beaconsWithYou.isNotEmpty()) {
                add(
                    DebriefSection(
                        next(),
                        "随行的零售信标",
                        trackerCallout(
                            "iBeacon / Minew / Estimote / Kontakt.io / Target Atrius 购物篮无线设备持续沿您的 GPS 轨迹出现。" +
                                "定位信标通常固定在商店或场馆内，一般不会随您移动。" +
                                "若出现随行，请核实原因（例如您推着 Target 购物篮、自有测试标签、胸牌，或较短轨迹仍处于固定设备覆盖范围内）。" +
                                "这不同于 Find My 尾随，也不代表已确认的事实或身份。",
                            beaconsWithYou,
                            customNames,
                        ),
                        alert = true,
                    ),
                )
            }
            if (wearablesWithYou.isNotEmpty()) {
                add(
                    DebriefSection(
                        next(),
                        "随行的可穿戴设备",
                        trackerCallout(
                            "Garmin / Fitbit / Oura 无线设备持续沿您的 GPS 轨迹出现。" +
                                "手表和戒指通常随佩戴者移动，往往是您自己的装备，或同行者的设备。" +
                                "它们通常不是被放置的追踪器。请逐一核实每个 MAC。这不代表已确认的事实或身份。",
                            wearablesWithYou,
                            customNames,
                        ),
                        alert = true,
                    ),
                )
            }
            add(DebriefSection(next(), "环境", environment(wifi, ble, randomized, persistent, pathSpan, pathLen)))
            add(DebriefSection(next(), "网络（Wi-Fi 接入点）", networks.trimEnd()))
            add(DebriefSection(next(), "低功耗蓝牙", bleBody.trimEnd()))
            add(DebriefSection(next(), "特征命中", sigBody.trimEnd()))
            add(DebriefSection(next(), "持续出现情况", persistBody.trimEnd()))
            if (attentionHits.isNotEmpty()) {
                add(
                    DebriefSection(
                        next(),
                        "重点关注",
                        buildString {
                            appendLine("仅为模式匹配，不代表身份，不是盗刷器检测结果，也不是安全结论。")
                            attentionHits.forEach { (d, sig, note) ->
                                appendLine("  · ${d.reportName(customNames)}  ${d.mac}  ${d.rssi} dBm  [$sig]")
                                appendLine("    $note")
                            }
                        }.trimEnd(),
                        alert = true,
                    ),
                )
            }
            add(DebriefSection(next(), "异常", anomalyBody))
            add(DebriefSection(next(), "隐私", privacy(wifi, ble, randomized, hidden, settings, places, pictures.isNotEmpty())))
            add(DebriefSection(next(), "建议操作", actionBody))
        }

        val windowLine = if (win.sitName != null) {
            "观测 ${win.sitName}（${utc(windowStart)} → ${utc(windowEnd)} UTC）"
        } else {
            "最近 15 分钟（${utc(windowStart)} → ${utc(windowEnd)} UTC）"
        }
        val heading = if (win.sitName != null) {
            "FIELDWATCH 观测 — ${win.sitName}"
        } else {
            "FIELDWATCH 观测总结"
        }
        val meta = buildList {
            add("生成时间" to "${utc(now)} UTC")
            if (win.sitName != null) add("观测" to win.sitName)
            add("时段" to windowLine)
            add("无线设备数" to "${inWin.size}")
            add("工具" to "Fieldwatch（app.fieldwatch）· 原生 Android · 仅接收 Wi-Fi AP + BLE 广播")
            add("扫描" to "${DebriefPrompt.scanIntensityLabel(settings.intensity)} · ${settings.staleSec} 秒后过期 · 短暂保留 ${settings.decaySec} 秒")
            add("GPS 标记" to if (settings.tagLocation) "开启" else "关闭")
            add("距离" to distanceLine)
            add("地点" to lookupLine)
            add(
                "信息分类" to if (pictures.isNotEmpty()) {
                    "敏感观测信息 — 附近 SSID、MAC、操作者 GPS、广播的航空器轨迹"
                } else {
                    "敏感观测信息 — 附近 SSID、MAC、操作者 GPS"
                },
            )
        }
        return DebriefDoc(
            generatedUtc = utc(now),
            windowLine = windowLine,
            meta = meta,
            disclaimer = FieldwatchDisclaimer.report(win),
            trackingAlert = following.isNotEmpty() || ownLikely.isNotEmpty() || withYou.isNotEmpty(),
            takeaway = takeaway(following, withYou, ownLikely, beaconsWithYou, wearablesWithYou, pathSpan, settings, named),
            sections = sections,
            extraAttention = attentionHits.map { (d, sig, note) ->
                ExtraAttentionHit(
                    signature = sig,
                    radioLabel = "${d.reportName(customNames)}  ${d.mac}  ${d.rssi} dBm",
                    note = note,
                )
            },
            heading = heading,
            pdfKicker = if (win.sitName != null) "观测" else "观测总结",
            pdfTitle = if (win.sitName != null) "观测 — ${win.sitName}" else "观测总结",
            pathFigure = AircraftTrail.applyWalk(
                pathFigure(
                    win.sitName ?: "最近 15 分钟", path, inWin, fleets,
                    customNames, observerNotes, bookmarkedKeys, watchedFleetIds,
                ),
                pictures,
                secondary = false,
            ),
            extraFigures = AircraftTrail.ownFigures(pictures),
        )
    }

    private fun pathFigure(
        title: String,
        path: List<GpsSample>,
        devices: List<Sighting>,
        fleets: List<Fleet>,
        customNames: Map<String, String>,
        observerNotes: Map<String, String> = emptyMap(),
        bookmarkedKeys: Set<String> = emptySet(),
        watchedFleetIds: Set<String> = emptySet(),
    ): SitPathPlot.Figure? {
        val path = Geo.despikePath(path)
        if (path.size < 2) return null
        val plot = SitPathPlot.dotsFrom(
            devices, fleets, namedKeys = customNames.keys,
            customNames = customNames, observerNotes = observerNotes,
            bookmarkedKeys = bookmarkedKeys,
            watchedFleetIds = watchedFleetIds,
            alertsOnly = true,
        )
        return SitPathPlot.Figure(
            kicker = "操作者轨迹",
            tracks = listOf(SitPathPlot.FigureTrack(title, path)),
            dots = plot.points,
            lengthM = Geo.pathLengthM(path),
            spanM = Geo.spanM(path),
            caption = "上北下南。线条表示本手机的轨迹（${path.lengthM()}）。每个 MAC 提醒或特征提醒只绘制一次。解码得到的经纬度表示最近一次广播位置，其余表示接收信号最强的位置。数字对应该地点（见轨迹图例）。",
        )
    }

    private fun List<GpsSample>.lengthM(): String {
        val m = Geo.pathLengthM(this)
        return if (m >= 1000) "${"%.1f".format(java.util.Locale.US, m / 1000)} 千米" else "${m.toInt()} 米"
    }

    /**
     * GPS / places / co-travel block for the AI Export prompt. Same heuristics
     * as the field debrief; markdown so a chat model can cite it.
     */
    fun gpsAnalystMarkdown(
        devices: List<Sighting>,
        fleets: List<Fleet>,
        settings: AppSettings,
        operatorPath: List<GpsSample>,
        now: Long = System.currentTimeMillis(),
        places: DebriefPlaces = DebriefPlaces.Off,
        window: DebriefWindow? = null,
        customNames: Map<String, String> = emptyMap(),
        bookmarkedKeys: Set<String> = emptySet(),
    ): String = buildString {
        val names = fleets.associate { it.id to it.name }
        val win = window ?: DebriefWindow(now - WINDOW_MS, now)
        val windowStart = win.startAt
        val windowEnd = win.endAt
        val path = operatorPath.filter { it.at in windowStart..windowEnd }
        val pathSpan = Geo.spanM(path)
        val pathLen = Geo.pathLengthM(path)
        val inWin = devices.filter { it.lastSeen >= windowStart || it.firstSeen >= windowStart }
        val trackers = inWin.filter { TrackerMatch.kind(it, names) == TrackerMatch.Kind.FINDER }
        val follow = followAssessments(trackers, names, path, windowStart, windowEnd, TrackerMatch.Kind.FINDER)
        val beaconsMd = stayedWithYou(
            followAssessments(
                inWin.filter { TrackerMatch.kind(it, names) == TrackerMatch.Kind.BEACON },
                names, path, windowStart, windowEnd, TrackerMatch.Kind.BEACON,
            ),
        )
        val wearablesMd = stayedWithYou(
            followAssessments(
                inWin.filter { TrackerMatch.kind(it, names) == TrackerMatch.Kind.WEARABLE },
                names, path, windowStart, windowEnd, TrackerMatch.Kind.WEARABLE,
            ),
        )

        appendLine("## 所在地点（操作者 GPS）")
        appendLine("- 为检测记录添加 GPS 标记：${if (settings.tagLocation) "开启" else "关闭"}。")
        appendLine(
            "- 在线地名查询：" +
                if (places.attempted) places.note
                else "关闭（设置 → 观测总结中的在线地名）。本次导出未进行反向地理编码。",
        )
        append(whereYouWere(settings, path, pathLen, pathSpan, inWin, names, places, windowEnd, customNames, bookmarkedKeys).trimEnd())
        appendLine()
        appendLine()
        if (path.size < 2 || pathSpan < MOVE_M) {
            appendLine("- 跟随检测：移动不足（需要约 45 米跨度）。不要推断尾随。")
            appendLine()
        }
        appendLine("## GPS 同行分析")
        appendLine(
            "仅列出持续沿操作者轨迹出现的无线设备。" +
                "经过的住宅标签及其他无线设备已省略，它们没有表现出随行。" +
                "不能确认身份。Find My 的 MAC 轮换后，不会自动关联变更地址的尾随记录。" +
                "步行场景中“可能尾随”的额外条件：接收轨迹覆盖操作者轨迹至少一半，" +
                "至少 2/3 的 GPS 标记对应信号达到 −75 dBm 或更强，最后一个标记的信号相比最强值衰减不超过 12 dB。" +
                "任一条件不满足则按经过处理并省略，不判为尾随。" +
                "寻物标签（AirTag / SmartTag / Tile / Chipolo / Pebblebee / Find My / 口袋中强信号 Apple 设备）" +
                "是追踪检测对象。同行的零售信标和可穿戴设备会单独列出，" +
                "信标通常不会随您移动，可穿戴设备则通常是自有装备。",
        )
        val followingMd = follow.filter { it.verdict == Verdict.FOLLOWING }
        val wholeSitMd = follow.filter {
            it.verdict == Verdict.OWN_LIKELY || it.verdict == Verdict.MOVED_WITH_YOU
        }
        if (followingMd.isEmpty() && wholeSitMd.isEmpty() && beaconsMd.isEmpty() && wearablesMd.isEmpty()) {
            appendLine("- 没有设备持续沿轨迹出现。")
        } else {
            fun dump(title: String, rows: List<FollowHit>) {
                if (rows.isEmpty()) return
                appendLine()
                appendLine("### $title")
                rows.forEach { h ->
                    val d = h.device
                    appendLine(
                        "- ${h.label}  ${d.reportName(customNames)}  ${d.mac}  RSSI ${d.rssi} dBm " +
                            "（最低 ${d.rssiMin} / 最高 ${d.rssiMax}）  轨迹 ${h.samples} 个定位点，跨度 ${h.spanM.toInt()} 米",
                    )
                    appendLine("  ${h.detail}")
                }
            }
            dump(
                "可能随行的追踪器（全程出现的寻物标签，可能自有或出发前被放置）",
                wholeSitMd,
            )
            dump(
                "可能尾随（观测开始后首次接收到、随后持续出现的寻物标签）",
                followingMd,
            )
            dump(
                "随行的零售信标（iBeacon / Minew / Estimote / Kontakt.io / Target Atrius 购物篮，通常为固定设施；推行的购物车会随行）",
                beaconsMd,
            )
            dump(
                "随行的可穿戴设备（Garmin / Fitbit / Oura，通常为自有或同行者装备）",
                wearablesMd,
            )
        }
    }

    private enum class Verdict { FOLLOWING, MOVED_WITH_YOU, OWN_LIKELY, STATIONARY, INSUFFICIENT }

    private data class FollowHit(
        val device: Sighting,
        val label: String,
        val verdict: Verdict,
        val detail: String,
        val spanM: Double,
        val samples: Int,
    )

    private fun stayedWithYou(hits: List<FollowHit>): List<FollowHit> =
        hits.filter {
            it.verdict == Verdict.FOLLOWING ||
                it.verdict == Verdict.MOVED_WITH_YOU ||
                it.verdict == Verdict.OWN_LIKELY
        }

    private fun followAssessments(
        trackers: List<Sighting>,
        names: Map<String, String>,
        operatorPath: List<GpsSample>,
        windowStart: Long,
        now: Long,
        kind: TrackerMatch.Kind,
    ): List<FollowHit> {
        val opSpan = Geo.spanM(operatorPath)
        val opLen = Geo.pathLengthM(operatorPath)
        return trackers.map { d ->
            val label = TrackerMatch.label(d, names)
            val trail = d.gpsTrail.filter { it.at >= windowStart }
            val span = Geo.spanM(trail)
            val trailLen = Geo.pathLengthM(trail)
            val presentAtStart = d.firstSeen <= windowStart + 15_000L
            val stillHere = now - d.lastSeen <= TAIL_HERE_MS
            val ownHere = now - d.lastSeen <= OWN_HERE_MS
            val onBody = d.rssiMax >= ON_BODY_MAX && d.rssiMin >= ON_BODY_MIN && trail.size >= 2
            val cover = opLen > 0.0 && trailLen >= COVER_FRAC * opLen
            val (verdict, detail) = when {
                operatorPath.size < 2 || opSpan < MOVE_M ->
                    Verdict.INSUFFICIENT to "操作者 GPS 轨迹过短（${opSpan.toInt()} 米），无法检测跟随。"
                trail.size < 2 ->
                    Verdict.INSUFFICIENT to "接收到了信号，但没有两个 GPS 定位点，无法检测同行。"
                onBody && ownHere ->
                    Verdict.OWN_LIKELY to onBodyLine(kind, d, trail.size)
                cover && ownHere && d.rssiMax >= ON_BODY_MAX ->
                    Verdict.OWN_LIKELY to
                        "在您 ${opLen.toInt()} 米轨迹中的 ${trailLen.toInt()} 米范围内接收到信号，且仍然较强（${d.rssiMax} dBm）。" +
                        withYouNote(kind, d)
                span < MOVE_M * 0.6 ->
                    Verdict.STATIONARY to "您移动了 ${opSpan.toInt()} 米，信号仅在某地点附近接收到（跨度 ${span.toInt()} 米）。设备看起来固定不动，您正在远离它。"
                presentAtStart && stillHere && d.rssiMax >= ON_BODY_MAX ->
                    Verdict.OWN_LIKELY to
                        "随您移动了 ${span.toInt()} 米，在该 15 分钟时段开始时已广播，信号较强（${d.rssi} dBm）。" +
                        withYouNote(kind, d)
                presentAtStart && stillHere ->
                    Verdict.MOVED_WITH_YOU to
                        "GPS 采样沿您的轨迹跨越 ${span.toInt()} 米（${trail.size} 个定位点）。时段开始时已广播，目前仍在。" +
                        withYouNote(kind, d)
                !presentAtStart && span >= MOVE_M && trail.size >= 3 ->
                    possibleTail(trail, span, opLen, kind, d)
                else ->
                    Verdict.STATIONARY to
                        "在 ${span.toInt()} 米范围内接收到信号（${trail.size} 个 GPS 标记），但没有持续保持较强信号。更像经过附近区域，不是尾随。"
            }
            FollowHit(d, label, verdict, detail, span, trail.size)
        }.sortedBy { it.verdict.ordinal }
    }

    private fun onBodyLine(kind: TrackerMatch.Kind, d: Sighting, stamps: Int): String {
        val loud = "本次观测全程随行且保持较强信号（${d.rssiMax} 至 ${d.rssiMin} dBm，$stamps 个 GPS 标记）。"
        return loud + withYouNote(kind, d)
    }

    /**
     * Catalog sentence for a live decode, when the signature wrote one.
     * A label with no sentence is named only. No fleet id is special.
     */
    private fun liveDecodeSentence(device: Sighting): String? {
        val chips = device.liveDecode
        if (chips.isEmpty()) return null
        val notes = chips.map { it.note.trim() }.filter { it.isNotEmpty() }.distinct()
        if (notes.isNotEmpty()) return notes.joinToString(" ")
        val labels = chips.reportLabels()
        if (labels.isEmpty()) return null
        return "解码：${labels.joinToString("、")}。"
    }

    private fun withYouNote(kind: TrackerMatch.Kind, device: Sighting): String {
        val decoded = liveDecodeSentence(device)
        val base = when (kind) {
            TrackerMatch.Kind.FINDER ->
                "本次观测全程随行，可能是自有设备，也可能出发前已被放置。请核实来源。"
            TrackerMatch.Kind.BEACON ->
                "定位信标通常不会随您移动。请核实原因（自有测试标签、胸牌，或短距离内仍处于固定设备覆盖范围）。"
            TrackerMatch.Kind.WEARABLE ->
                "这符合您或同行者佩戴手表或戒指的情况，通常不是被放置的追踪器。"
        }
        return when {
            decoded != null -> "$base $decoded"
            kind == TrackerMatch.Kind.FINDER ->
                "$base Find My / iPhone 地址会轮换，此 MAC 只对应本次会话。"
            else -> base
        }
    }

    /**
     * Extra gates on possible tail only. A neighborhood radio heard on a sidewalk
     * arc, or that faded as you walked, is stationary — not a follower.
     * Bag/car tags still cover most of the path and stay loud.
     */
    private fun possibleTail(
        trail: List<GpsSample>,
        span: Double,
        opLen: Double,
        kind: TrackerMatch.Kind,
        device: Sighting,
    ): Pair<Verdict, String> {
        val trailLen = Geo.pathLengthM(trail)
        val peak = trail.maxOf { it.rssi }
        val last = trail.last().rssi
        val fade = peak - last
        val loudN = trail.count { it.rssi >= TRAIL_LOUD_DBM }
        val loudNeed = (trail.size * 2 + 2) / 3
        val coverNeed = opLen * COVER_FRAC
        val coverPct = if (opLen <= 0.0) 0 else ((trailLen / opLen) * 100.0).toInt()
        return when {
            fade >= FADE_DB ->
                Verdict.STATIONARY to
                    "观测开始后出现，但最后一个 GPS 标记的信号为 $last dBm，最强曾为 $peak dBm（衰减 ${fade} dB）。看起来是您远离了固定设备，不是尾随。"
            loudN < loudNeed ->
                Verdict.STATIONARY to
                    "观测开始后出现，GPS 跨度为 ${span.toInt()} 米，但只有 $loudN/${trail.size} 个标记的信号较强（≥ −75 dBm）。看起来只是经过，不是尾随。"
            trailLen < coverNeed ->
                Verdict.STATIONARY to
                    "观测开始后出现，但只在您 ${opLen.toInt()} 米轨迹中的 ${trailLen.toInt()} 米范围内接收到信号（$coverPct%）。更像经过附近区域，不是尾随。"
            else -> {
                val stats =
                    "观测开始后出现，随后在 ${span.toInt()} 米跨度内持续随行并保持较强信号" +
                        "（覆盖您 ${opLen.toInt()} 米轨迹中的 ${trailLen.toInt()} 米，即 $coverPct%；" +
                        "$loudN/${trail.size} 个 GPS 标记达到 ≥ −75 dBm）。"
                val note = when (kind) {
                    TrackerMatch.Kind.FINDER ->
                        "在目视核实其来源前，按可能尾随处理。"
                    TrackerMatch.Kind.BEACON ->
                        "对零售 / 定位信标而言不常见，它们通常不会随您移动。请核实来源；这不同于 Find My 尾随。"
                    TrackerMatch.Kind.WEARABLE ->
                        "这符合观测途中加入的手表（您戴上了手表，或有人同行）的情况，通常不是被放置的追踪器。"
                }
                Verdict.FOLLOWING to stats + note
            }
        }.let { (verdict, text) ->
            val extra = liveDecodeSentence(device)
            verdict to if (extra == null) text else "$text $extra"
        }
    }

    private fun execSummary(
        wifi: List<Sighting>,
        ble: List<Sighting>,
        named: List<Sighting>,
        hidden: List<Sighting>,
        randomized: Int,
        pathSpan: Double,
        pathLen: Double,
        following: List<FollowHit>,
        withYou: List<FollowHit>,
        ownLikely: List<FollowHit>,
        beaconsWithYou: List<FollowHit>,
        wearablesWithYou: List<FollowHit>,
        settings: AppSettings,
        places: DebriefPlaces,
        window: DebriefWindow,
    ): String = buildString {
        val whenPhrase = if (window.sitName != null) {
            "在观测 ${window.sitName} 中，"
        } else {
            "在最近 15 分钟内，"
        }
        append("${whenPhrase}Fieldwatch 接收到 ${wifi.size} 个 Wi-Fi 接入点和 ${ble.size} 个 BLE 广播设备")
        append("（${named.size} 个匹配特征、${hidden.size} 个隐藏 SSID、$randomized 个随机地址 BLE）。")
        if (settings.tagLocation && pathLen > 0) {
            append("总移动距离：沿 GPS 轨迹 ${fmtDist(pathLen)}（直线跨度 ${fmtDist(pathSpan)}）。")
        }
        if (places.namesByCell.isNotEmpty()) {
            append("停留点 / 区域：${places.areaLine()}。")
        } else if (places.attempted && settings.tagLocation) {
            append("${places.note} ")
        }
        val wholeSit = ownLikely + withYou
        when {
            following.isNotEmpty() || wholeSit.isNotEmpty() -> {
                append("追踪提示。")
                if (wholeSit.isNotEmpty()) {
                    append("${wholeSit.size} 个寻物标签全程随行（可能自有或出发前已被放置）：")
                    append(wholeSit.joinToString { trackId(it) })
                    append(". ")
                }
                if (following.isNotEmpty()) {
                    append("${following.size} 个可能尾随设备在本次观测开始后首次接收到：")
                    append(following.joinToString { trackId(it) })
                    append(". ")
                }
                append("请逐一核实每个 MAC；Fieldwatch 无法区分自有设备和他人放置的设备。")
            }
            !settings.tagLocation -> {
                append("GPS 位置标记已关闭，因此未进行跟随检测。请开启“为检测记录添加 GPS 标记”并移动后再检测。")
            }
            pathSpan < MOVE_M -> {
                append("GPS 位移仅 ${pathSpan.toInt()} 米，过短，无法检测追踪器是否跟随。请保持位置标记开启并移动更远。")
            }
            else -> append("本时段内没有寻物标签明显持续沿 GPS 轨迹出现。")
        }
        if (beaconsWithYou.isNotEmpty()) {
            append("另有零售信标持续沿轨迹出现（不常见，固定设施通常不会随您移动）：")
            append(beaconsWithYou.joinToString { "${it.label} ${it.device.mac}" })
            append(". ")
        }
        if (wearablesWithYou.isNotEmpty()) {
            append("可穿戴设备持续沿轨迹出现（通常为您或同行者的手表 / 戒指）：")
            append(wearablesWithYou.joinToString { "${it.label} ${it.device.mac}" })
            append(".")
        }
    }

    private fun trackingSection(
        settings: AppSettings,
        path: List<GpsSample>,
        pathSpan: Double,
        pathLen: Double,
        following: List<FollowHit>,
        wholeSit: List<FollowHit>,
        beaconsWithYou: List<FollowHit>,
        wearablesWithYou: List<FollowHit>,
    ): String = buildString {
        if (!settings.tagLocation) {
            appendLine("GPS 位置标记已关闭。Fieldwatch 无法检测无线设备是否随您移动。")
            appendLine("请开启“设置 → 为检测记录添加 GPS 标记”，步行或驾车移动至少 50 米，然后重新生成观测总结。")
            return@buildString
        }
        appendLine("总移动距离：沿 GPS 轨迹 ${fmtDist(pathLen)}（${path.size} 个采样点）。直线跨度 ${fmtDist(pathSpan)}。")
        appendLine("同行设备按类别分组：寻物标签（AirTag / Find My、SmartTag、Tile、Chipolo、Pebblebee、口袋中强信号 Apple 设备）、零售信标（iBeacon、Minew、Estimote、Kontakt.io、Target Atrius 购物篮）和可穿戴设备（Garmin、Fitbit、Oura）。")
        if (path.size < 2 || pathSpan < MOVE_M) {
            appendLine("移动距离不足，无法区分随行设备与经过的设备。请步行或驾车移动更远后重新运行。")
            return@buildString
        }
        if (following.isEmpty() && wholeSit.isEmpty() && beaconsWithYou.isEmpty() && wearablesWithYou.isEmpty()) {
            appendLine("没有寻物标签、零售信标或可穿戴设备持续随行。仅经过的住宅标签及其他无线设备未列出。")
        } else {
            appendLine("下方提示仅包含持续沿轨迹出现的无线设备。您经过的设备（商店固定设施、住宅标签）已省略。")
        }
    }

    private fun observerNotesSection(
        devices: List<Sighting>,
        customNames: Map<String, String>,
        observerNotes: Map<String, String>,
    ): String? {
        val hits = devices.mapNotNull { d ->
            val note = observerNotes[d.key]?.trim()?.takeIf { it.isNotEmpty() } ?: return@mapNotNull null
            d to note
        }
        if (hits.isEmpty()) return null
        return buildString {
            appendLine("您为本时段接收到的无线设备所写的备注。按类型 + MAC 对应命名设备，不属于特征库说明。")
            hits.sortedWith(
                compareByDescending<Pair<Sighting, String>> { it.first.rssi }.thenBy { it.first.mac },
            ).forEach { (d, note) ->
                val kind = if (d.kind == RadioKind.WIFI) "WIFI" else "BLE"
                appendLine("  · $kind  ${d.reportName(customNames)}  ${d.mac}  ${d.rssi} dBm")
                appendLine("    $note")
            }
        }.trimEnd()
    }

    private fun trackerCallout(
        intro: String,
        rows: List<FollowHit>,
        customNames: Map<String, String> = emptyMap(),
    ): String = buildString {
        appendLine(intro)
        appendLine()
        rows.forEach { h ->
            val d = h.device
            appendLine("  • ${h.label}")
            appendLine("    ${d.reportName(customNames)}  ${d.mac}  RSSI ${d.rssi} dBm（最低 ${d.rssiMin} / 最高 ${d.rssiMax}）")
            appendLine("    ${h.detail}")
        }
    }.trimEnd()

    private fun whereYouWere(
        settings: AppSettings,
        path: List<GpsSample>,
        pathLen: Double,
        pathSpan: Double,
        devices: List<Sighting>,
        names: Map<String, String>,
        places: DebriefPlaces,
        now: Long,
        customNames: Map<String, String> = emptyMap(),
        bookmarkedKeys: Set<String> = emptySet(),
    ): String = buildString {
        appendLine("这是接收信号时手机的 GPS 位置，不是其他无线设备或摄像头杆的位置。停留点由约 40 米范围内的定位聚合而成，停留点之间的移动为途经路段。各 Wi-Fi / BLE 记录不重复列出坐标。")
        if (!settings.tagLocation) {
            appendLine("GPS 位置标记已关闭。请开启“设置 → 为检测记录添加 GPS 标记”，以记录接收无线信号时您所在的位置。")
            return@buildString
        }
        if (path.isEmpty()) {
            appendLine("GPS 位置标记已开启，但本时段尚无定位点。")
            return@buildString
        }
        appendLine("总体：轨迹长度 ${fmtDist(pathLen)}，跨度 ${fmtDist(pathSpan)}，${path.size} 个定位点。")
        if (places.attempted) {
            appendLine(places.note)
            appendLine("街道名称仅为近似位置。不要将街道视为匹配到的摄像头或标签所在地。")
        }
        val legs = Geo.legs(path, now = now)
        if (legs.isEmpty()) {
            appendLine("没有轨迹分段。")
            return@buildString
        }
        val stopNames = legs.filter { it.stay }.mapNotNull { places.nameNear(it.lat, it.lon) }
        if (stopNames.isNotEmpty()) {
            appendLine("停留点：" + stopNames.joinToString(" → "))
        }
        var stayN = 0
        legs.forEachIndexed { i, leg ->
            if (leg.stay) {
                stayN++
                appendLine()
                appendLine("${i + 1}. 停留  ${clock(leg.startAt)}–${clock(leg.endAt)} UTC（${fmtDur(leg.durationMs)}）")
                appendLine("   ${placeAndGps(leg.lat, leg.lon, places)}")
                val here = devices.filter { heardAt(it, leg) }
                val aps = here.count { it.kind == RadioKind.WIFI }
                val ble = here.count { it.kind == RadioKind.BLE }
                val sigs = here.flatMap { d -> d.fleetIds.map { names[it] ?: it } }.distinct()
                append("   此处接收到：$aps 个 AP，$ble 个 BLE")
                if (sigs.isNotEmpty()) append("  ·  ${sigs.take(6).joinToString(", ")}")
                appendLine()
                here.filter { inventoryKeep(it, settings, bookmarkedKeys) }.sortedByDescending { it.rssi }.take(4).forEach { d ->
                    appendLine("   · ${d.reportName(customNames)}  ${d.mac}  ${d.rssi} dBm")
                }
                if (here.isEmpty()) appendLine("   · 此停留点没有关联带 GPS 标记的无线设备（可能在首次接收后才开启位置标记）。")
            } else {
                appendLine()
                appendLine(
                    "${i + 1}. 途经  ${clock(leg.startAt)}–${clock(leg.endAt)} UTC  " +
                        "轨迹长度 ${fmtDist(leg.pathM)}",
                )
                appendLine("   ${placeAndGps(leg.lat, leg.lon, places)}")
                appendLine("   → ${placeAndGps(leg.endLat, leg.endLon, places)}")
            }
        }
        val stays = legs.count { it.stay }
        if (stays == 1 && pathSpan < MOVE_M) {
            appendLine()
            appendLine("仅有一个停留点，本时段移动距离不足以区分不同地点。")
        }
    }

    private fun heardAt(device: Sighting, leg: Geo.PathLeg): Boolean {
        val nearM = 60.0
        val trail = device.gpsTrail.filter { it.at >= leg.startAt && it.at <= leg.endAt }
        if (trail.isNotEmpty()) {
            return trail.any { Geo.meters(it.lat, it.lon, leg.lat, leg.lon) <= nearM }
        }
        val lat = device.latitude ?: return false
        val lon = device.longitude ?: return false
        if (device.lastSeen < leg.startAt || device.firstSeen > leg.endAt) return false
        return Geo.meters(lat, lon, leg.lat, leg.lon) <= nearM
    }

    private fun environment(
        wifi: List<Sighting>,
        ble: List<Sighting>,
        randomized: Int,
        persistent: List<Sighting>,
        pathSpan: Double,
        pathLen: Double,
    ): String {
        val ap = wifi.size
        val persistAp = persistent.count { it.kind == RadioKind.WIFI }
        val guess = when {
            pathSpan > 200 && ap in 1..25 -> "正在移动（步行 / 车载），经过混合无线环境。"
            ap <= 4 && ble.size < 30 && persistAp >= 1 -> "可能为住宅或小型办公室：固定 AP 较少，BLE 数量有限。"
            ap >= 15 && randomized >= 40 -> "密集的公共 / 零售 / 街道环境：有较多 AP 和类似手机的随机地址 BLE。"
            ap >= 8 && persistAp >= 4 -> "可能是部署了固定 AP 且有访客的建筑物。"
            else -> "混合环境或采样不足。"
        }
        return "$guess（${ap} 个 AP、${ble.size} 个 BLE、${persistAp} 个持续出现的 AP，移动 ${fmtDist(pathLen)}，跨度 ${fmtDist(pathSpan)}。）"
    }

    private fun wifiLine(
        d: Sighting,
        names: Map<String, String>,
        from: Long,
        now: Long,
        customNames: Map<String, String> = emptyMap(),
    ): String = buildString {
        append(d.reportName(customNames)).append("  ").append(d.mac)
        d.vendor?.let { append("  ").append(it) }
        append("  ").append(d.rssi).append(" dBm")
        if (d.channel != 0) append("  信道 ").append(d.channel)
        if (d.hiddenSsid) append("  隐藏")
        if (d.fleetIds.isNotEmpty()) append("  ").append(d.fleetIds.joinToString("+") { names[it] ?: it })
        append("  停留 ").append(fmtDur(dwellMs(d, from, now)))
    }

    private fun bleLine(
        d: Sighting,
        names: Map<String, String>,
        from: Long,
        now: Long,
        customNames: Map<String, String> = emptyMap(),
    ): String = buildString {
        append(d.reportName(customNames)).append("  ").append(d.mac)
        if (d.randomized) append("  随机地址")
        append("  ").append(d.rssi).append(" dBm")
        if (d.fleetIds.isNotEmpty()) append("  ").append(d.fleetIds.joinToString("+") { names[it] ?: it })
        append("  停留 ").append(fmtDur(dwellMs(d, from, now)))
    }

    /** Unmatched rotating BLE stays in counts/export; inventories omit it unless Extra attention, named, bookmark, or payload. */
    private fun inventoryKeep(
        d: Sighting,
        settings: AppSettings,
        bookmarkedKeys: Set<String>,
    ): Boolean {
        if (settings.debriefShowUnmatchedRandomBle) return true
        if (d.kind != RadioKind.BLE) return true
        if (!d.randomized) return true
        if (d.fleetIds.isNotEmpty()) return true
        if (d.payloadLat != null && d.payloadLon != null) return true
        if (d.key in bookmarkedKeys) return true
        return false
    }

    private fun anomalyLines(
        devices: List<Sighting>,
        customNames: Map<String, String> = emptyMap(),
        settings: AppSettings,
        bookmarkedKeys: Set<String>,
    ): List<String> {
        val out = ArrayList<String>()
        val pairing = devices.filter { d ->
            d.facts.serviceData.any { it.uuid.contains("FE2C", true) && it.dataHex.length == 6 }
        }
        if (pairing.isNotEmpty()) {
            out += "处于配对模式的 Google Fast Pair：" +
                pairing.joinToString { "${it.reportName(customNames)} ${it.mac}" }
        }
        val loudUnknown = devices.filter {
            it.rssi >= -50 && it.fleetIds.isEmpty() && it.name.isBlank() &&
                inventoryKeep(it, settings, bookmarkedKeys)
        }
        if (loudUnknown.isNotEmpty()) {
            out += "信号极强的未命名无线设备（≥ −50 dBm）：" +
                loudUnknown.take(8).joinToString { "${it.mac} ${it.rssi} dBm" }
        }
        val rand = devices.count { it.kind == RadioKind.BLE && it.randomized }
        if (rand >= 20) {
            out += "随机地址 BLE 较多（$rand 个），这常见于手机，不能据此认定追踪。"
        }
        return out
    }

    private fun privacy(
        wifi: List<Sighting>,
        ble: List<Sighting>,
        randomized: Int,
        hidden: List<Sighting>,
        settings: AppSettings,
        places: DebriefPlaces,
        includeAircraft: Boolean,
    ): String = buildString {
        append("使用相同无线接口的被动观察者会看到 ${wifi.size} 个有名称或隐藏的 AP，")
        append("以及 ${ble.size} 个 BLE 广播设备（$randomized 个随机地址）。")
        if (hidden.isNotEmpty()) append("隐藏 SSID 仍会发送信标，并通过 BSSID 标识 AP。")
        if (settings.tagLocation) append("本观测总结包含用于计算距离及检测跟随的操作者 GPS 采样。")
        if (includeAircraft) {
            append("本观测总结包含无线设备通过经纬度广播的航空器位置。")
        }
        if (places.attempted && places.available) {
            append("街道名称来自手机在线时的系统地理编码服务。")
        }
        append("请先脱敏，再将此文件分享至设备之外。")
    }

    private fun actions(
        following: List<FollowHit>,
        withYou: List<FollowHit>,
        ownLikely: List<FollowHit>,
        beaconsWithYou: List<FollowHit>,
        wearablesWithYou: List<FollowHit>,
        settings: AppSettings,
        pathSpan: Double,
    ): List<String> = buildList {
        if (following.isNotEmpty()) {
            add("可能尾随（本次观测开始后出现）：${following.joinToString { trackId(it) }}。暂停实时列表，打开详情，在走折线路线时观察 RSSI。不要停用他人的标签。")
        }
        if (ownLikely.isNotEmpty() || withYou.isNotEmpty()) {
            add(
                "可能随行的追踪器：${(ownLikely + withYou).joinToString { trackId(it) }}。" +
                    "可能是自有设备，也可能出发前已被放在车内、包中或身上。请逐一核实每个 MAC，不要直接认定为自己的设备而排除。",
            )
        }
        if (beaconsWithYou.isNotEmpty()) {
            add(
                "随行的零售信标（不常见，固定设施通常不会随您移动）：" +
                    beaconsWithYou.joinToString { it.label + " " + it.device.mac } +
                    "。将其视为跟随设备前，请先核实是否为测试标签或胸牌。",
            )
        }
        if (wearablesWithYou.isNotEmpty()) {
            add(
                "随行的可穿戴设备（通常为自有或同行者装备）：" +
                    wearablesWithYou.joinToString { it.label + " " + it.device.mac } +
                    ".",
            )
        }
        if (!settings.tagLocation) add("开启“为检测记录添加 GPS 标记”并移动至少 50 米，再次生成观测总结以检测跟随。")
        else if (pathSpan < MOVE_M) add("保持 GPS 位置标记开启，移动更远（至少 50 米），然后重新生成观测总结。")
        add("使用“实时 → 暂停”检查繁忙列表。如果本次观测设备较多，可关注追踪器特征。")
        add("Wi-Fi 终端侧数据（探测请求 / 客户端）仍需专用嗅探器，Fieldwatch 无法看到。")
    }

    private fun takeaway(
        following: List<FollowHit>,
        withYou: List<FollowHit>,
        ownLikely: List<FollowHit>,
        beaconsWithYou: List<FollowHit>,
        wearablesWithYou: List<FollowHit>,
        pathSpan: Double,
        settings: AppSettings,
        named: List<Sighting>,
    ): String {
        val extra = buildString {
            if (beaconsWithYou.isNotEmpty()) {
                append(" 另有零售信标随行（不常见）：")
                append(beaconsWithYou.joinToString { it.label + " (" + it.device.mac + ")" })
                append(".")
            }
            if (wearablesWithYou.isNotEmpty()) {
                append(" 可穿戴设备随行（通常为自有装备）：")
                append(wearablesWithYou.joinToString { it.label + " (" + it.device.mac + ")" })
                append(".")
            }
        }
        val core = when {
            following.isNotEmpty() && (ownLikely.isNotEmpty() || withYou.isNotEmpty()) ->
                "可能尾随（观测开始后出现）：${following.joinToString { trackId(it) }}。" +
                    "另有随行寻物标签（自有或此前被放置）：${(ownLikely + withYou).joinToString { trackId(it) }}。请逐一核实每个 MAC。"
            following.isNotEmpty() ->
                "可能尾随（本次观测开始后出现）：${following.joinToString { trackId(it) }}。请核实身上或车内对应的设备。"
            !settings.tagLocation ->
                "请开启 GPS 位置标记并移动，之后才能检测追踪器是否随行。"
            pathSpan < MOVE_M ->
                "GPS 移动不足（${pathSpan.toInt()} 米），无法检测跟随；请移动后重新生成观测总结。"
            ownLikely.isNotEmpty() || withYou.isNotEmpty() ->
                "随行寻物标签（自有或出发前被放置）：${(ownLikely + withYou).joinToString { trackId(it) }}。本时段没有新加入的设备。请逐一核实每个 MAC，不要直接认定为自己的设备而排除。"
            beaconsWithYou.isNotEmpty() || wearablesWithYou.isNotEmpty() ->
                "没有寻物标签持续沿轨迹出现。"
            named.isEmpty() ->
                "该 15 分钟时段没有特征命中，也没有追踪器沿 GPS 轨迹同行。"
            else ->
                "本时段没有寻物标签、零售信标或可穿戴设备明显持续沿您的 GPS 轨迹出现。"
        }
        return (core + extra).trim()
    }

    /** Label and MAC, plus the live-decode name when the signature asked for one. */
    private fun trackId(hit: FollowHit): String {
        val labels = hit.device.liveDecode.reportLabels()
        val id = "${hit.label} ${hit.device.mac}"
        return if (labels.isEmpty()) id else "$id (${labels.joinToString(", ")})"
    }

    private fun craftSentence(pictures: List<AircraftTrail.Picture>): String {
        if (pictures.isEmpty()) return ""
        val bits = pictures.take(3).joinToString { pic ->
            if (pic.status.isBlank()) pic.title else "${pic.title} (${pic.status})"
        }
        val more = if (pictures.size > 3) "，另有 ${pictures.size - 3} 个" else ""
        return " 广播位置：$bits$more。"
    }

    private fun dwellMs(d: Sighting, from: Long, to: Long): Long {
        var sum = 0L
        val spans = d.presence.ifEmpty { listOf(PresenceSpan(d.firstSeen, if (d.gone) d.lastSeen else null)) }
        for (span in spans) {
            val a = maxOf(span.start, from)
            val b = minOf(span.end ?: to, to)
            if (b > a) sum += b - a
        }
        return sum
    }

    private fun absDelta(a: Long, b: Long) = kotlin.math.abs(a - b)

    private fun utc(ms: Long): String {
        val fmt = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
        fmt.timeZone = TimeZone.getTimeZone("UTC")
        return fmt.format(Date(ms))
    }

    private fun clock(ms: Long): String {
        val fmt = SimpleDateFormat("HH:mm", Locale.US)
        fmt.timeZone = TimeZone.getTimeZone("UTC")
        return fmt.format(Date(ms))
    }

    private fun fmtDist(m: Double): String =
        if (m >= 1000.0) String.format(Locale.US, "%.2f 千米", m / 1000.0) else "${m.toInt()} 米"

    private fun fmtCoord(s: GpsSample): String =
        String.format(Locale.US, "%.5f, %.5f", s.lat, s.lon)

    private fun placeAndGps(lat: Double, lon: Double, places: DebriefPlaces): String {
        val gps = fmtCoord(GpsSample(0L, lat, lon))
        val name = places.nameNear(lat, lon)
        return if (!name.isNullOrBlank()) {
            "$name（$gps，操作者手机）"
        } else if (places.attempted) {
            "$gps（操作者手机，本次导出无街道名称）"
        } else {
            "$gps（操作者手机）"
        }
    }

    private fun fmtDur(ms: Long): String {
        val s = (ms / 1000).coerceAtLeast(0)
        val m = s / 60
        val r = s % 60
        return if (m >= 60) "${m / 60}小时${m % 60}分钟" else if (m > 0) "${m}分${r}秒" else "${r}秒"
    }
}
