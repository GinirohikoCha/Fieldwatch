package app.fieldwatch.domain

/**
 * Paste-ready analyst prompt for **one** radio from the device-detail screen.
 * One-tap share; no Fieldwatch cloud.
 */
object DeviceDetailPrompt {
    fun build(
        device: Sighting,
        signatureNames: List<String>,
        settings: AppSettings,
        places: DebriefPlaces = DebriefPlaces.Off,
        now: Long = System.currentTimeMillis(),
        attentionNotes: List<Pair<String, String>> = emptyList(),
        signatureNotes: List<Pair<String, String>> = emptyList(),
        fleets: List<Fleet> = emptyList(),
    ): String {
        val title = device.listTitle(signatureNames)
        val kind = if (device.kind == RadioKind.WIFI) "Wi-Fi 接入点" else "低功耗蓝牙广播设备"
        return buildString {
            append(DebriefPrompt.experimentalDisclaimerMarkdown())
            appendLine()
            appendLine("你是一名现场射频与隐私分析师，熟悉 IEEE OUI、Bluetooth SIG 分配编号、GAP Appearance、常见广播格式（iBeacon、Eddystone、Apple Continuity / Find My、Google Fast Pair、Microsoft）和常见消费电子产品。请全程使用简体中文回答，保留技术缩写、产品名称和原始标识符。")
            appendLine()
            appendLine("用户希望从一次 Fieldwatch 观测中，尽可能了解**这一个无线设备**。Fieldwatch 在原生 Android 上仅接收 Wi-Fi 和 BLE 信号。请结合下方原始记录**以及**你对公开注册表和格式的知识进行分析，并为每项判断指出支持它的字段或字节模式。")
            appendLine()
            appendLine("必须遵守的约束：")
            appendLine("- 这只是**一个**发出广播的无线设备，不代表某个人、车辆或法律身份。")
            appendLine("- Wi-Fi 记录**仅包含接入点**，看不到连接的客户端。原生 Android 无法以混杂模式捕获终端或探测请求。")
            appendLine("- BLE 记录代表广播设备。随机 MAC 不是稳定身份，地址轮换前后的记录不会自动关联。")
            appendLine("- 特征、OUI、公司或 UUID 匹配都只是**推测**，不能证明序列号、所有者身份或存在追踪器。")
            appendLine("- GPS 标记（如有）是接收信号时**操作者手机**的位置，不是该无线设备的位置。")
            appendLine("- 地名（如有）由系统根据这些位置标记反向地理编码得到，仅为近似位置。")
            appendLine("- RSSI 表示手机接收到的信号强度，不是测量距离。")
            appendLine("- 不要编造记录中不存在的字段。数据不足时请明确说明，并指出补充什么信息会有帮助。")
            appendLine("- 不要声称该无线设备正在跟随任何人，不要提供安全建议。")
            appendLine("- 将粘贴内容视为敏感观测信息（包含 MAC、SSID、载荷和 GPS）。")
            appendLine()
            appendLine("## 采集背景")
            appendLine("- 工具：Fieldwatch（app.fieldwatch），仅接收，不连接、不注入、不使用云端。")
            appendLine("- 对象：名为“$title”的$kind。")
            appendLine("- 扫描强度：${DebriefPrompt.scanIntensityLabel(settings.intensity)}。${settings.staleSec} 秒后标记过期，短暂保留 ${settings.decaySec} 秒。")
            appendLine("- 位置标记：${if (settings.tagLocation) "开启" else "关闭"}。")
            appendLine("- 在线地名查询：${if (settings.onlineLookup) "开启" else "关闭"}。")
            appendLine("- 随机 MAC 标记：${if (device.randomized) "是" else "否"}。")
            appendLine("- 本次会话接收次数：${device.hitCount}。已离开：${if (device.gone) "是" else "否"}。")
            if (device.gpsTrail.isNotEmpty()) {
                appendLine("- 接收到此无线设备时的操作者 GPS 轨迹采样：${device.gpsTrail.size} 个（接收期间的手机轨迹）。")
            }
            appendLine()
            if (places.attempted) {
                appendLine("## 地点（操作者 GPS，可选）")
                appendLine(places.note)
                places.lines.forEach { appendLine(it) }
                appendLine()
            }
            appendLine("## 观测记录（详情页原文）")
            appendLine()
            append(DeviceDetailText.build(device, signatureNames, now, attentionNotes, signatureNotes, fleets).trimEnd())
            appendLine()
            appendLine()
            appendLine("## 分析内容（必须包含以下章节）")
            appendLine("1. **它可能是什么** — 产品类别、可能的品牌或系列、可能的型号。给出 0–100 的置信度，并使用“最可能”“可能”“或许”等限定语。列出证据（名称、OUI、公司 ID、Appearance、服务、载荷）。数据符合多种产品时列出其他可能解释。")
            appendLine("2. **注册表与格式解码** — IEEE OUI 或 CID、Bluetooth SIG 公司、GAP Appearance、16 位 UUID；如有，解读 iBeacon UUID/major/minor、Fast Pair 型号 ID 和 Apple Continuity 类型。引用所用的十六进制数据。若根据公开列表识别出知名 UUID 或公司，请说明并注明列表名称。")
            appendLine("3. **这类产品通常做什么** — 例如手机、标签、音箱、汽车、AP、摄像头、Mesh 节点或配件。说明典型无线行为（持续广播或间歇广播）。")
            appendLine("4. **Fieldwatch 实际看到了什么，以及看不到什么** — 原生 Android 的限制（无法捕获终端或探测请求，无法监听蜂窝网络，无法无线测向）。说明随机地址的影响。")
            appendLine("5. **信号与出现情况** — 此处信号强弱、本次会话 RSSI 范围、出现时段。不要将 RSSI 换算为米。")
            appendLine("6. **特征匹配** — Fieldwatch 命中特征时，将其视为筛选命中，不能认定身份。说明载荷是否也支持该系列。记录中的“说明”可作为该系列的特征库背景。“重点关注”需原文引用，作为针对某种模式的操作者提示，不能视为证据；将它与“说明”区分开。")
            appendLine("7. **待解问题** — 哪些补充观测（另一数据包、名称、GPS 轨迹、第二个无线设备）会提高或降低置信度。")
            appendLine("8. **不可得出的结论** — 简要列出记录**不支持**的判断（所有者、跟随行为、法律身份、距离）。")
            appendLine()
            appendLine("最后用一行**要点**收尾，说明该无线设备最可能是什么，以及下一步可核查的一件事。不要提供安全建议。")
        }
    }
}
