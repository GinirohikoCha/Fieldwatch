package app.fieldwatch.domain

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

/**
 * Paste-ready addendum prompt for Reports → AI Export.
 * Onboard Debrief is verbatim. Working data is rates, RSSI bands, Extra attention,
 * and finder-tag rows for a tracking stress-test — not a second inventory.
 */
object DebriefPrompt {
    const val WINDOW_SHORT_MS = 5 * 60_000L
    const val WINDOW_MS = 15 * 60_000L
    private const val MAX_CHARS = 90_000

    fun build(
        devices: List<Sighting>,
        fleets: List<Fleet>,
        settings: AppSettings,
        now: Long = System.currentTimeMillis(),
        operatorPath: List<GpsSample> = emptyList(),
        places: DebriefPlaces = DebriefPlaces.Off,
        window: DebriefWindow? = null,
        customNames: Map<String, String> = emptyMap(),
        observerNotes: Map<String, String> = emptyMap(),
        bookmarkedKeys: Set<String> = emptySet(),
    ): String {
        val names = fleets.associate { it.id to it.name }
        val win = window ?: DebriefWindow(now - WINDOW_MS, now)
        val windowStart = win.startAt
        val windowEnd = win.endAt
        val in15 = devices.filter { it.lastSeen >= windowStart || it.firstSeen >= windowStart }
        val shortStart = maxOf(windowStart, windowEnd - WINDOW_SHORT_MS)
        val in5 = in15.filter { it.lastSeen >= shortStart || it.firstSeen >= shortStart }
        val wifi = in15.filter { it.kind == RadioKind.WIFI }
        val ble = in15.filter { it.kind == RadioKind.BLE }
        val signed = in15.filter { it.fleetIds.isNotEmpty() }
        val randomized = ble.count { it.randomized }
        val arrived = in15.filter { it.firstSeen >= windowStart }
        val departed = in15.filter { it.gone || it.lastSeen < windowEnd - 45_000L }
        val persistent = in15.filter { dwellMs(it, windowStart, windowEnd) >= win.durationMs * 2 / 3 }
        val path = operatorPath.filter { it.at in windowStart..windowEnd }
        val pathSpan = Geo.spanM(path)
        val pathLen = Geo.pathLengthM(path)
        val extraHits = in15.flatMap { d ->
            d.attentionNotes(fleets).map { (sig, note) -> Triple(d, sig, note) }
        }
        val finders = in15.filter { TrackerMatch.kind(it, names) == TrackerMatch.Kind.FINDER }
        val sigFamilies = signed.groupBy { d ->
            d.fleetIds.joinToString("+") { names[it] ?: it }
        }.mapValues { it.value.size }.toList().sortedByDescending { it.second }
        val bleRssi = ble.map { it.rssi }
        val wifiRssi = wifi.map { it.rssi }
        val onboard = DebriefReport.build(devices, fleets, settings, operatorPath, now, places, win, customNames, observerNotes, bookmarkedKeys)
        val iso = utc(windowEnd)
        val start = utc(windowStart)

        val body = buildString {
            append(experimentalDisclaimerMarkdown())
            appendLine()
            appendLine("你是一名现场射频分析师，为采集本次观测的操作者提供分析。Fieldwatch 在原生 Android 上仅接收 Wi-Fi 接入点和 BLE 广播设备的信号。请全程使用简体中文，保留技术缩写、产品名称和原始标识符。")
            appendLine()
            appendLine("**设备内生成的观测总结**（原文见下方）已经汇总数量、所在地点、追踪提示、设备清单、重点关注及要点。**不要重写该报告，不要重复设备清单或停留列表。**你的任务是补充手机无法生成的分析：变化速率、其他可能解释，以及对设备内追踪提示的审慎核查。")
            appendLine()
            appendLine("必须遵守的约束：")
            appendLine("- 仅接收信号。Wi-Fi 记录仅包含接入点，BLE 记录代表广播设备，以类型 + MAC 区分。BLE 地址轮换会产生新记录，不会自动关联。")
            appendLine("- 特征、OUI 或公司匹配都是推测，不能确认身份，也不代表某个人或车辆。")
            appendLine("- GPS 标记（如有）是接收信号时本手机的位置，不是其他无线设备的位置。不要将摄像头或标签定位到 GPS 标记处。")
            appendLine("- 地名（如有）由系统根据这些位置标记反向地理编码得到。")
            appendLine("- RSSI 表示手机接收到的信号强度，不是以米为单位的距离。")
            appendLine("- 实时内存最多保留约 400 个无线设备；未命名 BLE 设备约 3 分钟后移除。命名观测会保留更多数据。这不是完整捕获。")
            appendLine("- 只有设备内 GPS 同行分析支持时，才能提出追踪器可能跟随的判断。全程随行的无线设备不一定属于操作者，也可能被他人放置，不要直接排除。不要编造设备内检测未标记的尾随，不要将零售信标视为 Find My 尾随设备。")
            appendLine("- 追踪记录中的实时解码值是对应广播的特征库文字。设备内报告包含该句时请引用原文。不要将该值关联到另一个 MAC。")
            appendLine("- 航空器信息块和琥珀色轨迹表示无线设备广播的位置。具有相同 UAS ID 的轨迹属于同一航空器。这些不是本手机的 GPS，也不能据此认定航空器跟随了操作者。")
            appendLine("- 不要提供安全建议，不要断言操作者安全或处于危险之中。")
            appendLine("- 将粘贴内容视为敏感观测信息。")
            appendLine()
            appendLine("## 输出要求（必须遵守，这是操作者阅读的补充分析）")
            appendLine("使用完整句子和下列标题。只有工作数据中的重点关注与追踪记录可用简短项目符号。不要使用 Markdown 表格或代码块，不要重复设备内的设备清单。")
            appendLine()
            appendLine("1. **免责声明** — 首先重复实验性使用免责声明。")
            appendLine("2. **设备内观测总结已说明的内容** — 用 3–5 句话概述数量、距离、追踪提示、重点关注命中及观测备注（如有）。不要重复设备清单。")
            appendLine("3. **数字补充了什么** — 对比 5 分钟与 15 分钟的数量、RSSI 区间、随机地址 BLE 百分比、每分钟新增量、持续出现与离开情况、特征系列构成。分析环境更像街道、住宅、零售场所还是车辆，以及最近 5 分钟相对 15 分钟的变化（更密集、更安静或稳定），并说明置信度。若启用了 GPS，引用工作数据中的轨迹长度与跨度；不要把无线设备定位到某个停留点。")
            appendLine("4. **重点关注与追踪提示** — 使用工作数据中的完整标识（完整 MAC、名称、RSSI 最小值 / 最大值、特征、停留时长）。审慎核查设备内的“可能随行的追踪器”“可能尾随”“零售信标”“可穿戴设备”结论，说明认同、限制条件或数据不足。这只是模式匹配，不能确认身份。没有则明确说明没有。")
            appendLine("5. **另一次观测或信号追踪可减少哪些疑问** — 只给出具体的应用内后续操作（对某条重点关注记录进行信号追踪、记录更长的 GPS 轨迹、对比观测、使用筛选）。不要提供安全建议，不要建议“报警”。")
            appendLine()
            appendLine("**要点（必需，置于最后一行）。** 用以“要点：”开头的一句话，补充*设备内要点尚未提及的一个数字*（变化速率、随机地址百分比、5 分钟与 15 分钟的变化、轨迹跨度）。不要作价值评判，不要给出威胁等级。")
            appendLine()
            appendLine("## 采集背景")
            appendLine("- 工具：Fieldwatch（app.fieldwatch），仅接收，不连接、不注入、不使用云端。")
            appendLine(
                if (win.sitName != null) {
                    "- 时段：观测 **${win.sitName}**（$start → $iso UTC），另取最近 5 分钟作为子时段。"
                } else {
                    "- 时段：最近 **15 分钟**（$start → $iso UTC），另取最近 **5 分钟**作为子时段。"
                },
            )
            appendLine("- 扫描强度：${scanIntensityLabel(settings.intensity)}。${settings.staleSec} 秒后标记过期。")
            appendLine("- 位置标记：${if (settings.tagLocation) "开启" else "关闭"}。在线地名查询：${if (settings.onlineLookup) "开启" else "关闭"}。")
            appendLine()
            appendLine("## 设备内观测总结（原文，操作者已看过，请勿重写）")
            appendLine()
            appendLine(onboard.trimEnd())
            appendLine()
            appendLine("## 工作数据（用于补充分析，不要将清单复制到回答中）")
            appendLine()
            appendLine(
                "15 分钟：Wi-Fi ${wifi.size}  BLE ${ble.size}  特征匹配 ${signed.size}  隐藏 SSID ${wifi.count { it.hiddenSsid }}  " +
                    "随机地址 BLE $randomized/${ble.size}（${pct(randomized, ble.size)}%）  " +
                    "首次发现 ${arrived.size}（${perMin(arrived.size)}/分钟）  持续出现 ${persistent.size}  离开 / 静默 ${departed.size}",
            )
            appendLine(
                "5 分钟：Wi-Fi ${in5.count { it.kind == RadioKind.WIFI }}  BLE ${in5.count { it.kind == RadioKind.BLE }}  " +
                    "特征匹配 ${in5.count { it.fleetIds.isNotEmpty() }}  首次发现 ${in5.count { it.firstSeen >= shortStart }}",
            )
            appendLine(
                "BLE RSSI (n=${ble.size}): ≥−50 ${bandGe(bleRssi, -50)}  −51..−70 ${band(bleRssi, -70, -51)}  " +
                    "−71..−85 ${band(bleRssi, -85, -71)}  <−85 ${bandLt(bleRssi, -85)}",
            )
            appendLine(
                "Wi-Fi RSSI (n=${wifi.size}): ≥−50 ${bandGe(wifiRssi, -50)}  −51..−70 ${band(wifiRssi, -70, -51)}  " +
                    "−71..−85 ${band(wifiRssi, -85, -71)}  <−85 ${bandLt(wifiRssi, -85)}",
            )
            if (sigFamilies.isEmpty()) {
                appendLine("特征系列：无。")
            } else {
                appendLine("特征系列（数量）：" + sigFamilies.take(12).joinToString { "${it.first}=${it.second}" })
            }
            appendLine(
                "GPS 轨迹：位置标记${if (settings.tagLocation) "开启" else "关闭"}  " +
                    "定位点 ${path.size}  长度 ${pathLen.toInt()} 米  跨度 ${pathSpan.toInt()} 米  " +
                    "地点 ${if (places.attempted) places.note else "关闭"}",
            )
            appendLine()
            appendLine("重点关注：")
            if (extraHits.isEmpty()) {
                appendLine("- 无。")
            } else {
                extraHits.forEach { (d, sig, note) ->
                    append("- ").append(row(d, names, now, windowStart, customNames, observerNotes))
                    append(" | ").append(sig).append(": ").append(note)
                    appendLine()
                }
            }
            appendLine()
            appendLine("观测备注：")
            val observed = in15.mapNotNull { d ->
                val note = observerNotes[d.key]?.trim()?.takeIf { it.isNotEmpty() } ?: return@mapNotNull null
                d to note
            }
            if (observed.isEmpty()) {
                appendLine("- 无。")
            } else {
                observed.sortedByDescending { it.first.rssi }.forEach { (d, note) ->
                    append("- ").append(row(d, names, now, windowStart, customNames, emptyMap()))
                    appendLine()
                    appendLine("  $note")
                }
            }
            appendLine()
            appendLine("类似寻物标签的无线设备（用于核查设备内追踪分析，不代表尾随名单）：")
            if (finders.isEmpty()) {
                appendLine("- 无。")
            } else {
                finders.sortedByDescending { it.rssi }.take(20).forEach { d ->
                    append("- ").append(row(d, names, now, windowStart, customNames, observerNotes))
                    append(" rssiMin=").append(d.rssiMin).append(" rssiMax=").append(d.rssiMax)
                    appendLine()
                }
            }
            appendLine()
            appendLine("## 工作数据结束")
            appendLine("现在请遵循上方的**输出要求**，用简体中文撰写补充分析。不要重写设备内观测总结。")
        }
        return if (body.length <= MAX_CHARS) body
        else body.take(MAX_CHARS) + "\n\n[因分享面板大小限制而截断]\n"
    }

    fun experimentalDisclaimerMarkdown(): String = FieldwatchDisclaimer.experimentalMarkdown()

    internal fun scanIntensityLabel(intensity: ScanIntensity): String = when (intensity) {
        ScanIntensity.SAVER -> "省电"
        ScanIntensity.BALANCED -> "均衡"
        ScanIntensity.PERFORMANCE -> "性能"
    }

    private fun row(
        d: Sighting,
        names: Map<String, String>,
        now: Long,
        windowStart: Long,
        customNames: Map<String, String> = emptyMap(),
        observerNotes: Map<String, String> = emptyMap(),
    ): String = buildString {
        append(if (d.kind == RadioKind.WIFI) "WIFI" else "BLE")
        append(" ").append(d.mac)
        val label = d.reportName(customNames).trim()
        if (label.isNotEmpty() && !label.equals(d.mac, ignoreCase = true)) {
            append("  ").append(label.take(32))
        }
        observerNotes[d.key]?.let { append("  观测者备注：").append(it.take(80)) }
        append(" RSSI=").append(d.rssi).append("dBm")
        if (d.randomized) append(" 随机地址")
        if (d.fleetIds.isNotEmpty()) {
            append(" 特征=").append(d.fleetIds.joinToString("+") { names[it] ?: it })
        }
        val labels = d.liveDecode.reportLabels()
        if (labels.isNotEmpty()) append(" 解码=").append(labels.joinToString(","))
        val notes = d.liveDecode.map { it.note.trim() }.filter { it.isNotEmpty() }.distinct()
        if (notes.isNotEmpty()) append(" 解码说明=").append(notes.joinToString(" "))
        append(" 停留=").append(fmtDur(dwellMs(d, windowStart, now)))
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

    private fun utc(ms: Long): String {
        val fmt = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
        fmt.timeZone = TimeZone.getTimeZone("UTC")
        return fmt.format(Date(ms))
    }

    private fun fmtDur(ms: Long): String {
        val s = (ms / 1000).coerceAtLeast(0)
        val m = s / 60
        val r = s % 60
        return if (m >= 60) "${m / 60}小时${m % 60}分钟" else if (m > 0) "${m}分${r}秒" else "${r}秒"
    }

    private fun pct(n: Int, d: Int): Int = if (d <= 0) 0 else (n * 100) / d

    private fun perMin(n: Int): String {
        val rate = n / 15.0
        return if (rate >= 10) rate.toInt().toString() else "%.1f".format(Locale.US, rate)
    }

    private fun band(list: List<Int>, lo: Int, hi: Int) = list.count { it in lo..hi }
    private fun bandGe(list: List<Int>, lo: Int) = list.count { it >= lo }
    private fun bandLt(list: List<Int>, hi: Int) = list.count { it < hi }
}
