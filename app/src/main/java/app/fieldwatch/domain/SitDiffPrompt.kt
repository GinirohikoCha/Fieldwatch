package app.fieldwatch.domain

/**
 * Paste-ready addendum prompt for Reports → Compare sits → AI Export.
 * Onboard compare is verbatim. Working data is overlap + exclusive Extra attention /
 * Named radios — not a second inventory.
 */
object SitDiffPrompt {
    private const val MAX_CHARS = 90_000

    fun build(
        thisSit: SitDiff.Side,
        second: SitDiff.Side,
        demoMode: Boolean,
    ): String {
        val macs = (thisSit.radios + second.radios).map { it.mac }
        val onboard = SitDiff.document(thisSit, second).withDemoMacs(macs, demoMode)
        val thisKeys = thisSit.keys
        val secondKeys = second.keys
        val byKey = (thisSit.radios + second.radios).associateBy { it.key }
        val onlyThis = thisKeys.minus(secondKeys)
        val onlySecond = secondKeys.minus(thisKeys)
        val both = thisKeys.intersect(secondKeys)
        val union = thisKeys.union(secondKeys)
        val overlapPct = if (union.isEmpty()) 0 else (both.size * 100) / union.size
        fun bucket(keys: Set<String>): Triple<Int, Int, Int> {
            val rows = keys.mapNotNull { byKey[it] }
            val wifi = rows.count { it.kind == RadioKind.WIFI }
            val ble = rows.count { it.kind == RadioKind.BLE }
            val randBle = rows.count { it.kind == RadioKind.BLE && it.randomized }
            return Triple(wifi, ble, randBle)
        }
        val onlyThisB = bucket(onlyThis)
        val onlySecondB = bucket(onlySecond)
        val bothB = bucket(both)
        fun line(row: SitDiff.Radio): String = buildString {
            append(if (row.kind == RadioKind.WIFI) "WIFI" else "BLE")
            append("  ").append(row.mac)
            val label = row.name.trim()
            if (label.isNotEmpty() && !label.equals(row.mac, ignoreCase = true)) {
                append("  ").append(label)
            }
            row.fleetNames.filter { it.isNotBlank() }.forEach { append("  ").append(it) }
            if (row.extraAttention) append("  重点关注")
            val labels = row.liveDecode.reportLabels()
            if (labels.isNotEmpty()) append("  ").append(labels.joinToString(", "))
            if (row.kind == RadioKind.BLE && row.randomized) append("  随机地址")
        }
        fun exclusive(keys: Set<String>, where: String, pred: (SitDiff.Radio) -> Boolean) =
            keys.mapNotNull { byKey[it] }.filter(pred).map { "$where  ${line(it)}" }

        val extraRows =
            exclusive(onlyThis, "仅本次观测出现", { it.extraAttention }) +
                exclusive(onlySecond, "仅第二次观测出现", { it.extraAttention })
        val namedRows =
            exclusive(onlyThis, "仅本次观测出现", { it.named }) +
                exclusive(onlySecond, "仅第二次观测出现", { it.named })

        val body = buildString {
            append(FieldwatchDisclaimer.experimentalMarkdown())
            appendLine()
            appendLine("你是一名现场射频分析师，为对比两次 Fieldwatch 观测的操作者提供分析。Fieldwatch 在原生 Android 上仅接收 Wi-Fi 接入点和 BLE 广播设备的信号。请全程使用简体中文，保留技术缩写、产品名称和原始标识符。")
            appendLine()
            appendLine("**设备内生成的对比**（原文见下方）已将出现情况分为：仅本次出现、仅第二次出现、两次均出现。**不要重写该报告，不要重复这些列表。**你的任务是补充手机无法生成的分析：变化属于什么类型，以及其中多少反映真实变化。")
            appendLine()
            appendLine("必须遵守的约束：")
            appendLine("- 仅接收信号，以类型 + MAC 区分。BLE 地址轮换会产生新记录，不会自动关联。")
            appendLine("- Wi-Fi 记录仅包含接入点，看不到已连接的客户端。")
            appendLine("- 重点关注和特征匹配都只是推测，不能确认身份，也不代表某个人或车辆。")
            appendLine("- GPS 标记（如有）是接收信号时本手机的位置，不是其他无线设备的位置。")
            appendLine("- 最近 15 分钟与命名观测的范围不同（内存约 400 个，命名观测最多 ${Sit.RADIO_CAP} 个）。内存一侧缺少 BLE 可能是被移出列表，不一定已离开。")
            appendLine("- 出现不代表同行。不要编造尾随、跟随者或摄像头位置。")
            appendLine("- 记录中的实时解码值是对应类型 + MAC 的特征库文字。如果设备内对比指出该值变化，请说明变化。不要将该值关联到另一个 MAC。")
            appendLine("- 航空器信息块表示无线设备广播的位置，按 UAS ID 合并。如果设备内对比指出状态变化，请说明变化。该轨迹不是本手机的 GPS。")
            appendLine("- 不要提供安全建议，不要断言操作者安全或处于危险之中。")
            appendLine("- 将粘贴内容视为敏感观测信息。")
            appendLine()
            appendLine("## 输出要求（必须遵守，这是操作者阅读的补充分析）")
            appendLine("使用完整句子和下列标题。只有单次出现的重点关注和命名设备可用简短项目符号。不要使用 Markdown 表格或代码块，不要重复设备内的列表。")
            appendLine()
            appendLine("1. **免责声明** — 首先重复实验性使用免责声明。")
            appendLine("2. **设备内对比已说明的内容** — 用 3–5 句话概述时段名称、数量、单次出现的重点关注以及观测备注（如有）。不要重复设备清单。")
            appendLine("3. **数字补充了什么** — 重合率（两次均出现数 / 合集数量的百分比）、每组 Wi-Fi 与 BLE 数量、单次出现的 BLE 中随机地址的比例。分析差异更像固定设施、不同摊位或时段，还是数量上限造成的现象，并说明置信度。使用工作数据，不要编造变化速率。")
            appendLine("4. **单次出现的重点关注与命名设备** — 使用工作数据中的完整标识（完整 MAC、名称、特征、所属时段）。这只是模式匹配，不能确认身份。没有则明确说明没有。")
            appendLine("5. **另一次观测或信号追踪可减少哪些疑问** — 只给出具体的应用内后续操作（在同一摊位进行第三次观测、对某条单次出现的重点关注记录进行信号追踪、使用筛选）。不要提供安全建议，不要建议“报警”。")
            appendLine()
            appendLine("**要点（必需，置于最后一行）。** 用以“要点：”开头的一句话，补充*设备内要点尚未提及的一个数字*（重合率、单次出现的重点关注数量，或单次出现 BLE 中随机地址的比例）。不要作价值评判，不要给出威胁等级。")
            appendLine()
            appendLine("## 设备内对比（原文，操作者已看过，请勿重写）")
            appendLine()
            appendLine(onboard.toPlainText().trimEnd())
            appendLine()
            appendLine("## 工作数据（用于补充分析，不要将清单复制到回答中）")
            appendLine()
            appendLine("本次观测：${thisSit.name}（${thisSit.radios.size} 个无线设备${if (thisSit.ram) "，内存约 400" else "，命名观测上限 ${Sit.RADIO_CAP}"}）")
            appendLine("第二次观测：${second.name}（${second.radios.size} 个无线设备${if (second.ram) "，内存约 400" else "，命名观测上限 ${Sit.RADIO_CAP}"}）")
            appendLine("仅本次出现：${onlyThis.size}  仅第二次出现：${onlySecond.size}  两次均出现：${both.size}  合计：${union.size}  重合率：$overlapPct%")
            appendLine("仅本次出现的设备：Wi-Fi ${onlyThisB.first}  BLE ${onlyThisB.second}  随机地址 BLE ${onlyThisB.third}")
            appendLine("仅第二次出现的设备：Wi-Fi ${onlySecondB.first}  BLE ${onlySecondB.second}  随机地址 BLE ${onlySecondB.third}")
            appendLine("两次均出现的设备：Wi-Fi ${bothB.first}  BLE ${bothB.second}  随机地址 BLE ${bothB.third}")
            if (thisSit.ram || second.ram) {
                appendLine("数量上限说明：最近 15 分钟来自实时内存（约 400 个）。命名观测最多保留 ${Sit.RADIO_CAP} 个。两者的统计范围不同。")
            }
            appendLine()
            appendLine("单次出现的重点关注：")
            if (extraRows.isEmpty()) appendLine("- 无。")
            else extraRows.forEach { appendLine("- $it") }
            appendLine()
            appendLine("单次出现的命名设备：")
            if (namedRows.isEmpty()) appendLine("- 无。")
            else namedRows.forEach { appendLine("- $it") }
            appendLine()
            appendLine("观测备注：")
            val observed = (thisSit.radios + second.radios)
                .distinctBy { it.key }
                .mapNotNull { r ->
                    val note = r.observerNotes.trim().takeIf { it.isNotEmpty() } ?: return@mapNotNull null
                    r to note
                }
            if (observed.isEmpty()) appendLine("- 无。")
            else observed.forEach { (r, note) ->
                val where = when {
                    r.key in onlyThis -> "仅本次观测出现"
                    r.key in onlySecond -> "仅第二次观测出现"
                    else -> "两次均出现"
                }
                appendLine("- $where  ${line(r)}")
                appendLine("  $note")
            }
            appendLine()
            appendLine("## 工作数据结束")
            appendLine("现在请遵循上方的**输出要求**，用简体中文撰写补充分析。不要重写设备内对比。")
        }
        val masked = MacUtil.redactMacsIn(body, macs, demoMode)
        val withPrivacy = if (demoMode) {
            "隐私模式：MAC 尾部显示为 **:**:**，GPS 坐标已遮蔽。手机中的日志保持不变。\n\n$masked"
        } else {
            masked
        }
        return if (withPrivacy.length <= MAX_CHARS) withPrivacy
        else withPrivacy.take(MAX_CHARS) + "\n\n[因分享面板大小限制而截断]\n"
    }
}
