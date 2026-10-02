package app.fieldwatch.domain

/** Operator-facing disclaimer. First-run, Debrief, and AI Export share the same core. */
object FieldwatchDisclaimer {
    const val HOBBY =
        "这是一个业余项目，按 MIT 许可证以现状提供。使用风险由您自行承担。"

    const val HYPOTHESES =
        "检测、模式匹配、“随行” / “可能尾随”、观测总结文字" +
            "和 AI 导出都只是推测，不代表身份或法律结论，也不是" +
            "完整的射频捕获。处于关闭、休眠、地址随机化、仅使用蜂窝网络" +
            "或被操作系统隐藏的无线设备不会出现。"

    const val LIABILITY =
        "您须独自承担使用本应用及遵守当地法律的责任。" +
            "在法律允许的最大范围内，Off Grid Pete LLC 不对因使用本应用产生的" +
            "间接、附带、特殊、后果性或惩罚性损害承担责任。"

    const val LOCATION =
        "GPS 标记是接收信号时本手机的位置，不是其他无线设备的位置；但解码映射" +
            "广播其自身经纬度（Remote ID 位置）时除外。分享观测总结、" +
            "观测对比、AI 导出（观测或单个无线设备）、设备详情的文字分享或日志，可能使这些" +
            "轨迹离开本设备。开启 TAK/CoT 数据发送后，会将标记发送到" +
            "局域网，相关责任由操作者承担。"

    const val ACCEPT =
        "勾选并继续即表示您接受这些条款及 MIT 许可证。"

    const val LICENSE_TITLE = "MIT 许可证（中文译文）"

    /** Body of LICENSE in the repository, without the title line. */
    const val LICENSE_BODY =
        "版权所有 (c) 2026 Off Grid Pete LLC\n" +
            "\n" +
            "特此免费授予任何获得本软件及相关文档文件（以下称“软件”）副本的人，" +
            "不受限制地处理本软件的权利，" +
            "包括但不限于使用、复制、修改、合并、发布、" +
            "分发、再许可和 / 或销售" +
            "软件副本的权利，并允许获得软件的人" +
            "同样享有上述权利，条件如下：\n" +
            "\n" +
            "上述版权声明和本许可声明应包含在本软件的所有副本" +
            "或主要部分中。\n" +
            "\n" +
            "本软件按“现状”提供，不附带任何明示或默示的担保，" +
            "包括但不限于适销性、" +
            "特定用途适用性及不侵权的担保。在任何情况下，" +
            "作者或版权持有人均不对因本软件、使用本软件或其他软件交易" +
            "引起、产生或与之相关的任何索赔、损害或其他责任承担责任，" +
            "无论其基于合同、侵权" +
            "还是其他法律依据。"

    val LICENSE_TEXT = "$LICENSE_TITLE\n\n$LICENSE_BODY"

    val firstRunDisclaimer: String = "$HOBBY\n\n$HYPOTHESES\n\n$LIABILITY"

    val firstRun: String =
        "$firstRunDisclaimer\n\n$LICENSE_TEXT\n\n$ACCEPT"

    /** Debrief text / PDF. Same core as first-run, without the click-through line. */
    fun report(window: DebriefWindow? = null): String {
        val source = if (window?.sitName != null) {
            "命名观测“${window.sitName}”（该时段内接收到的无线设备；观测期间仍受实时列表数量上限限制）。"
        } else {
            "内存中的实时设备集（最近 15 分钟，上限约 400 个）。"
        }
        return "$HOBBY\n\n$HYPOTHESES\n\n$LIABILITY\n\n$LOCATION\n\n" +
            "本次观测报告来源于$source" +
            "请勿将其用于任何涉及安全判断的场景。"
    }

    fun compare(): String =
        "$HOBBY\n\n$HYPOTHESES\n\n$LIABILITY\n\n$LOCATION\n\n" +
            "本次对比涵盖手机在两个时段内接收到的无线设备（类型 + MAC）。" +
            "BLE 地址轮换会产生新记录。请勿将其用于任何涉及安全判断的场景。"

    fun experimentalMarkdown(): String = buildString {
        appendLine("## 免责声明（请在回答中重复）")
        appendLine(HOBBY)
        appendLine(HYPOTHESES)
        appendLine(LIABILITY)
        appendLine(LOCATION)
        appendLine("请勿将 Fieldwatch、本次粘贴内容或分析结果用于任何涉及安全判断的场景。")
        appendLine("请以此免责声明开始回答，全程使用简体中文，不要提供安全建议。")
    }
}
