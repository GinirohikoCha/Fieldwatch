package app.fieldwatch.domain

/**
 * Plain-language decode of advertised identity. Guesses are what the radio
 * is broadcasting, not a visual identification.
 */
object DeviceExplain {
    data class Guess(
        val headline: String,
        val because: String,
        val confidence: Confidence,
    )

    enum class Confidence { HIGH, MEDIUM, LOW }

    fun guess(device: Sighting, signatureNames: List<String>): Guess {
        val hints = ArrayList<Hint>(8)
        val appearance = device.facts.appearance?.let { RadioDb.appearance(it) }
        appearanceHint(appearance)?.let { hints += it }
        CodDecoder.decodeOrNull(device.facts.deviceClass)?.let { codHint(it)?.let { h -> hints += h } }
        hints += uuidHints(device.serviceUuids + device.facts.serviceData.map { it.uuid })
        hints += AdvPayloadDecoder.roleHints(device).map {
            Hint(it.bucket, it.label, it.reason, it.weight)
        }
        hints += signatureHints(signatureNames)
        if (device.kind == RadioKind.WIFI) hints += wifiHints(device, signatureNames)

        if (hints.isEmpty()) {
            return Guess(
                headline = if (device.kind == RadioKind.WIFI) {
                    "Wi-Fi 接入点"
                } else {
                    "低功耗蓝牙广播设备"
                },
                because = "检测到了广播，但设备没有广播产品类别" +
                    "（没有提供 Appearance、设备类别或可识别类型的常见服务）。",
                confidence = Confidence.LOW,
            )
        }
        val grouped = LinkedHashMap<String, Hint>()
        for (hint in hints.sortedByDescending { it.weight }) {
            val key = hint.bucket
            val prev = grouped[key]
            if (prev == null || hint.weight > prev.weight) grouped[key] = hint
        }
        val best = grouped.values.maxBy { it.weight }
        val support = grouped.values
            .filter { it.bucket == best.bucket || it.weight >= 3 }
            .map { it.reason }
            .distinct()
        val confidence = when {
            best.weight >= 6 -> Confidence.HIGH
            best.weight >= 3 -> Confidence.MEDIUM
            else -> Confidence.LOW
        }
        val hedge = when (confidence) {
            Confidence.HIGH -> "最可能是"
            Confidence.MEDIUM -> "可能是"
            Confidence.LOW -> "或许是"
        }
        return Guess(
            headline = "$hedge ${RadioLabels.label(best.label)}",
            because = support.joinToString(" ") +
                " 这反映设备广播的内容，不是目视确认的身份。",
            confidence = confidence,
        )
    }

    /**
     * Compact Live-row title from the same guess as detail. Null if we only
     * know it is an unnamed advertiser — caller may fall back to vendor.
     */
    fun listLabel(device: Sighting, signatureNames: List<String> = emptyList()): String? {
        val guess = guess(device, signatureNames)
        val generic = guess.headline.contains("低功耗蓝牙广播设备", ignoreCase = true) ||
            guess.headline.contains("Wi-Fi 接入点", ignoreCase = true)
        val core = if (generic) null else tidyHeadline(guess.headline)
        val vendor = device.vendor?.trim()?.takeIf { it.isNotBlank() && it.length <= 24 }
        if (core != null) {
            return if (vendor != null && !core.contains(vendor, ignoreCase = true)) {
                "$vendor · $core"
            } else {
                core
            }
        }
        if (vendor != null) return "$vendor 设备"
        return null
    }

    private fun tidyHeadline(headline: String): String {
        var s = headline
            .removePrefix("最可能是 ").removePrefix("Most likely ")
            .removePrefix("可能是 ").removePrefix("Probably ")
            .removePrefix("或许是 ").removePrefix("Could be ")
            .trim()
        s = s.replace(Regex("""\s*[（(][^）)]*[）)]"""), "").trim()
        s = s.removePrefix("an ").removePrefix("a ").trim()
        if (s.isEmpty()) return headline
        return s.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
    }

    fun flagsExplain(flags: Int): String = buildList {
        if (flags and 0x01 != 0) {
            add("限时可发现：短暂寻找附近连接。")
        }
        if (flags and 0x02 != 0) {
            add("可发现：其他 BLE 设备可以发现它。")
        }
        if (flags and 0x04 != 0) {
            add("仅 BLE：不支持经典蓝牙（耳机音频 / 文件传输使用的无线功能）。")
        } else {
            add("除 BLE 外，也可能支持经典蓝牙（BR/EDR）。")
        }
        if (flags and 0x08 != 0 || flags and 0x10 != 0) {
            add("双模芯片：BLE 和经典蓝牙可以同时运行。")
        }
    }.joinToString(" ")

    fun phyExplain(label: String): String = when {
        label.contains("Coded") -> "$label — 远距离 BLE（速度较慢，覆盖较远）"
        label.contains("2M") -> "$label — 高速 BLE（蓝牙 5）"
        label.contains("1M") -> "$label — 标准 BLE 无线模式"
        else -> label
    }

    fun addressExplain(device: Sighting): String {
        val type = device.facts.addressType
        return when {
            device.kind == RadioKind.WIFI && device.randomized ->
                "本地管理的 BSSID。车载、Mesh 和访客 AP 经常使用固定的此类地址，不代表手机轮换的 MAC。"
            type.equals("Public", true) && !device.randomized ->
                "公开出厂地址（稳定，由 IEEE 分配）。"
            type.equals("Random", true) || device.randomized ->
                "随机 / 隐私地址。MAC 可能变化，因此不能作为长期身份标识。"
            type.equals("Anonymous", true) ->
                "匿名：系统协议栈隐藏了地址。"
            else ->
                listOfNotNull(type?.let(RadioLabels::label), "全球 IEEE 地址（稳定 OUI）。").joinToString(" · ")
        }
    }

    fun rssiBand(rssi: Int): String = when {
        !Rssi.measured(rssi) -> "不可用"
        rssi >= -45 -> "极强"
        rssi >= -60 -> "强"
        rssi >= -75 -> "中等"
        rssi >= -88 -> "弱"
        else -> "极弱"
    }

    fun rssiExplain(rssi: Int): String =
        if (!Rssi.measured(rssi)) "不可用"
        else "%d dBm · %s".format(rssi, rssiBand(rssi))

    fun wifiSecurityExplain(raw: String): String {
        val bits = ArrayList<String>(4)
        val u = raw.uppercase()
        when {
            "SAE" in u || "WPA3" in u -> bits += "WPA3 密码（SAE 握手）"
            "OWE" in u -> bits += "增强开放网络（加密，无密码）"
            "PSK" in u && "WPA2" in u -> bits += "WPA2 密码（PSK）"
            "PSK" in u || "WPA" in u -> bits += "Wi-Fi 密码（WPA/PSK）"
            "802.1X" in u || "EAP" in u -> bits += "企业认证（802.1X）"
            "WEP" in u -> bits += "WEP（老旧，安全性弱）"
            "ESS" in u && bits.isEmpty() -> bits += "开放网络或未解析出加密方式"
        }
        when {
            "CCMP" in u || "GCMP" in u -> bits += "AES 加密"
            "TKIP" in u -> bits += "TKIP（较旧且较弱的加密方式）"
        }
        if ("WPS" in u) bits += "已启用 WPS 配置"
        if ("MESH" in u) bits += "Mesh 节点"
        if ("IBSS" in u) bits += "自组网络"
        if ("ESS" in u) bits += "基础设施接入点"
        return if (bits.isEmpty()) raw else bits.distinct().joinToString("。") + "。"
    }

    fun uuidGloss(uuid: String): String? {
        val name = RadioDb.serviceUuid(uuid)?.let(RadioLabels::label)
        val short = uuid16(uuid) ?: return name
        val extra = when (short) {
            0x1800 -> "基本连接信息"
            0x1801 -> "属性协议"
            0x180A -> "型号 / 序列号 / 固件"
            0x180F -> "电池电量"
            0x1812 -> "键盘、鼠标或游戏手柄"
            0x180D -> "心率传感器"
            0x1810 -> "血压传感器"
            0x181A -> "温湿度等环境传感器"
            0x1844, 0x1845, 0x1846 -> "低功耗骑行功率 / 速度"
            0x1850, 0x184E, 0x184F -> "低功耗音频（LE Audio）"
            0xFE2C -> "Google Fast Pair（常见于耳塞 / 音箱）"
            0xFD5A -> "Samsung SmartTag"
            0xFD44 -> "Apple Find My 相关"
            0xFEED, 0xFEDD -> "Tile 追踪标签"
            0xFD50 -> "Tuya 物联网"
            0xFEBE, 0xFE21 -> "Bose"
            0xFE78 -> "HP 打印机"
            0xFE07 -> "Sonos 音箱"
            0xFEAF, 0xFEB0 -> "Nest Weave"
            0xFCBF -> "ASSA ABLOY Opening Solutions"
            0xFE24 -> "August Home 智能锁"
            0xFCF4 -> "Allegion / Schlage"
            0xFCB2 -> "Apple（并非 ASSA ABLOY）"
            else -> null
        }
        return when {
            name != null && extra != null -> "$name — $extra"
            name != null -> name
            extra != null -> extra
            else -> null
        }
    }

    private data class Hint(
        val bucket: String,
        val label: String,
        val reason: String,
        val weight: Int,
    )

    private fun appearanceHint(name: String?): Hint? {
        if (name.isNullOrBlank() || name.equals("Unknown", true)) return null
        val n = name.lowercase()
        val (bucket, label, w) = when {
            "ear" in n || "headphone" in n || "headset" in n || "hearable" in n || "hearing" in n ->
                Triple("audio-personal", "耳塞或头戴耳机", 7)
            "speaker" in n || "loudspeaker" in n || "hifi" in n ->
                Triple("audio-speaker", "音箱", 7)
            "mouse" in n -> Triple("mouse", "鼠标", 8)
            "keyboard" in n -> Triple("keyboard", "键盘", 8)
            "gamepad" in n || "joystick" in n -> Triple("gamepad", "游戏控制器", 7)
            "watch" in n -> Triple("watch", "手表或腕戴设备", 7)
            "phone" in n -> Triple("phone", "手机", 6)
            "laptop" in n || "computer" in n || "desktop" in n || "tablet" in n ->
                Triple("computer", "电脑或平板", 6)
            "tag" in n || "keyring" in n -> Triple("tag", "寻物标签 / 追踪器", 6)
            "remote" in n -> Triple("remote", "遥控器", 6)
            "hid" in n -> Triple("hid", "输入设备（键盘、鼠标等）", 4)
            "heart" in n -> Triple("health", "心率监测器", 7)
            "glucose" in n || "oximeter" in n || "blood pressure" in n || "thermometer" in n ->
                Triple("health", "健康传感器", 6)
            "display" in n || "monitor" in n -> Triple("display", "显示设备或电视棒", 4)
            "clock" in n -> Triple("clock", "时钟", 5)
            "glasses" in n -> Triple("glasses", "智能眼镜", 6)
            else -> Triple("other", name, 3)
        }
        return Hint(bucket, label, "其广播中的 Appearance 类型为 ${RadioLabels.label(name)}。", w)
    }

    private fun codHint(cod: CodDecoder.Decoded): Hint? {
        val minor = cod.minor.lowercase()
        val major = cod.major.lowercase()
        val (bucket, label, w) = when {
            "headphone" in minor || "headset" in minor || "hands-free" in minor ->
                Triple("audio-personal", "耳塞或耳机", 6)
            "loudspeaker" in minor || "portable audio" in minor || "hifi" in minor || "car audio" in minor ->
                Triple("audio-speaker", "音箱", 6)
            "pointing" in minor || minor == "mouse" -> Triple("mouse", "鼠标", 7)
            "keyboard" in minor -> Triple("keyboard", "键盘", 7)
            "gamepad" in minor || "joystick" in minor -> Triple("gamepad", "游戏控制器", 6)
            "smartphone" in minor || (major == "phone" && "uncategorized" !in minor) ->
                Triple("phone", "手机", 5)
            "laptop" in minor || "tablet" in minor || "desktop" in minor ->
                Triple("computer", "电脑", 5)
            "wristwatch" in minor -> Triple("watch", "手表", 6)
            "heart" in minor || "pulse" in minor || "glucose" in minor || "oximeter" in minor ->
                Triple("health", "健康传感器", 6)
            "audio" in major -> Triple("audio-personal", "音频设备", 3)
            "peripheral" in major -> Triple("hid", "输入配件", 3)
            "uncategorized" in major || "miscellaneous" in major -> return null
            else -> return null
        }
        val shown = if (cod.minor.isNotBlank() && cod.minor != "Uncategorized") {
            "${RadioLabels.label(cod.major)} / ${RadioLabels.label(cod.minor)}"
        } else {
            RadioLabels.label(cod.major)
        }
        return Hint(bucket, label, "设备类别声明为 $shown。", w)
    }

    private fun uuidHints(uuids: List<String>): List<Hint> {
        val out = ArrayList<Hint>(4)
        for (uuid in uuids) {
            val id = uuid16(uuid) ?: continue
            when (id) {
                0x1812 -> out += Hint("hid", "键盘、鼠标或游戏手柄", "它提供 HID（人机接口）服务。", 5)
                0x1108, 0x1112, 0x111E, 0x110B, 0x110A, 0x1131, 0x1203 ->
                    out += Hint("audio-personal", "头戴耳机、耳麦或音箱", "它提供经典蓝牙音频 / 耳机服务。", 5)
                0x184E, 0x184F, 0x1850, 0x1851 ->
                    out += Hint("audio-personal", "LE Audio 耳塞或音箱", "它提供蓝牙 LE Audio 服务。", 6)
                0x180D -> out += Hint("health", "心率监测器", "它提供心率服务。", 6)
                0x1810 -> out += Hint("health", "血压计", "它提供血压服务。", 6)
                0x181A -> out += Hint("sensor", "环境传感器", "它提供环境感知服务。", 4)
                0xFE2C -> out += Hint("audio-personal", "耳塞或音箱", "存在 Google Fast Pair（常见于耳塞和音箱）。", 4)
                0xFD5A -> out += Hint("tag", "Samsung SmartTag", "具有 SmartTag 服务 UUID。", 7)
                0xFD44 -> out += Hint("tag", "Apple Find My 配件", "具有 Find My 相关 UUID。", 6)
                0xFEED, 0xFEDD -> out += Hint("tag", "Tile 追踪标签", "具有 Tile 服务 UUID。", 7)
            }
        }
        return out
    }

    private fun signatureHints(names: List<String>): List<Hint> {
        return names.mapNotNull { raw ->
            if (isGenericSignatureName(raw)) return@mapNotNull null
            val n = raw.lowercase()
            when {
                "airtag" in n || n == "find my" || "find hub" in n || "dult" in n ->
                    Hint(
                        "tag",
                        when {
                            "dult" in n -> "DULT 寻物标签"
                            "find hub" in n -> "Google Find Hub 标签"
                            else -> "Apple AirTag / Find My 标签"
                        },
                        "匹配特征 $raw。",
                        8,
                    )
                "apple device" in n ->
                    Hint("phone", "iPhone、iPad 或 Mac", "匹配特征 $raw。", 7)
                "apple audio" in n ->
                    Hint("audio-personal", "AirPods、Beats 或 AirPlay", "匹配特征 $raw。", 7)
                "microsoft" in n ->
                    Hint("computer", "Windows / Surface / Xbox 无线设备", "匹配特征 $raw。", 6)
                n == "tesla tstpms" ->
                    Hint("vehicle", "Tesla BLE 轮胎传感器", "匹配特征 $raw。", 7)
                "tpms" in n || n == "tirecheck" || n == "sytpms" ->
                    Hint("vehicle", "BLE 胎压传感器", "匹配特征 $raw。", 7)
                n == "vuzix" ->
                    Hint("glasses", "Vuzix 智能眼镜", "匹配特征 $raw。", 7)
                n == "tesla" ->
                    Hint("vehicle", "Tesla 车辆（包括 Cybertruck）或手机钥匙", "匹配特征 $raw。", 7)
                n == "google" ->
                    Hint("phone", "Pixel 或其他 Google 无线设备", "匹配特征 $raw。", 6)
                n == "sony" ->
                    Hint("audio-personal", "Sony 耳机、电视或相机", "匹配特征 $raw。", 6)
                n == "bose" ->
                    Hint("audio-personal", "Bose 耳机或音箱", "匹配特征 $raw。", 7)
                n == "garmin" ->
                    Hint("watch", "Garmin 手表或 inReach", "匹配特征 $raw。", 7)
                n == "amazon" ->
                    Hint("speaker", "Echo、Fire 或其他 Amazon 无线设备", "匹配特征 $raw。", 6)
                n == "fitbit" ->
                    Hint("watch", "Fitbit", "匹配特征 $raw。", 7)
                n == "oura" ->
                    Hint("wearable", "Oura 智能戒指", "匹配特征 $raw。", 7)
                n == "logitech" ->
                    Hint("hid", "Logitech 鼠标、键盘或网络摄像头", "匹配特征 $raw。", 6)
                "jbl" in n || n == "harman" ->
                    Hint("audio-personal", "JBL 或 Harman 音频设备", "匹配特征 $raw。", 6)
                n == "sonos" ->
                    Hint("audio-speaker", "Sonos 音箱", "匹配特征 $raw。", 7)
                n == "gopro" ->
                    Hint("camera", "GoPro", "匹配特征 $raw。", 7)
                n == "osmo" ->
                    Hint("camera", "DJI Osmo 运动相机", "匹配特征 $raw。", 7)
                n == "insta360" ->
                    Hint("camera", "Insta360 相机", "匹配特征 $raw。", 7)
                n == "dji" ->
                    Hint("drone", "DJI 无人机或遥控器", "匹配特征 $raw。", 7)
                n == "remote id" ->
                    Hint("drone", "广播 ASTM Remote ID 的无人机", "匹配特征 $raw。", 8)
                n == "skydio" ->
                    Hint("drone", "Skydio 无人机", "匹配特征 $raw。", 7)
                n == "autel" ->
                    Hint("drone", "Autel 无人机", "匹配特征 $raw。", 7)
                n == "parrot" ->
                    Hint("drone", "Parrot ANAFI 或 Bebop 无人机", "匹配特征 $raw。", 7)
                n == "hoverair" ->
                    Hint("drone", "HOVERAir 飞行相机", "匹配特征 $raw。", 7)
                n == "netgear" || n == "orbi" ->
                    Hint("ap", "NETGEAR 或 Orbi 接入点", "匹配特征 $raw。", 6)
                n == "tp-link" ->
                    Hint("ap", "TP-Link 接入点", "匹配特征 $raw。", 6)
                n == "asus" ->
                    Hint("ap", "ASUS 接入点", "匹配特征 $raw。", 6)
                n == "linksys" ->
                    Hint("ap", "Linksys 或 Velop 接入点", "匹配特征 $raw。", 6)
                n == "eero" ->
                    Hint("ap", "Eero Mesh 节点", "匹配特征 $raw。", 6)
                n == "google wifi" ->
                    Hint("ap", "Google Wifi 或 Nest Wifi 接入点", "匹配特征 $raw。", 6)
                n == "d-link" ->
                    Hint("ap", "D-Link 接入点", "匹配特征 $raw。", 6)
                n == "belkin" ->
                    Hint("ap", "Belkin 接入点", "匹配特征 $raw。", 6)
                n == "xfinity" ->
                    Hint("ap", "Xfinity 网关或热点", "匹配特征 $raw。", 6)
                n == "spectrum" ->
                    Hint("ap", "Spectrum 网关或 Spectrum Mobile 热点", "匹配特征 $raw。", 6)
                n == "at&t" ->
                    Hint("ap", "AT&T 网关或 attwifi 热点", "匹配特征 $raw。", 6)
                n == "verizon" ->
                    Hint("ap", "Verizon 或 Fios 网关", "匹配特征 $raw。", 6)
                n == "starlink" ->
                    Hint("ap", "Starlink 路由器", "匹配特征 $raw。", 7)
                n == "meraki" ->
                    Hint("ap", "Cisco Meraki 接入点", "匹配特征 $raw。", 7)
                n == "cisco" ->
                    Hint("ap", "Cisco Aironet、Catalyst、Business、RV 或 SPVTG 接入点", "匹配特征 $raw。", 7)
                n == "mist" ->
                    Hint("ap", "Juniper Mist 接入点", "匹配特征 $raw。", 7)
                n == "t-mobile" ->
                    Hint("ap", "T-Mobile Home Internet 网关或热点", "匹配特征 $raw。", 6)
                n == "humax" ->
                    Hint("ap", "HUMAX 网关（常用于 T-Mobile Home Internet）", "匹配特征 $raw。", 6)
                n == "sagemcom" ->
                    Hint("ap", "Sagemcom 运营商网关", "匹配特征 $raw。", 6)
                n == "arcadyan" ->
                    Hint("ap", "Arcadyan 运营商网关", "匹配特征 $raw。", 6)
                n == "askey" ->
                    Hint("ap", "Askey 运营商 / 5G 网关", "匹配特征 $raw。", 6)
                n == "calix" ->
                    Hint("ap", "Calix 光纤网关", "匹配特征 $raw。", 6)
                n == "nokia" ->
                    Hint("ap", "Nokia Solutions and Networks 网关", "匹配特征 $raw。", 6)
                n == "airties" ->
                    Hint("ap", "AirTies 运营商 Mesh 节点", "匹配特征 $raw。", 6)
                n == "tenda" ->
                    Hint("ap", "Tenda 接入点", "匹配特征 $raw。", 6)
                n == "ruijie" ->
                    Hint("ap", "Ruijie 或 Reyee 接入点", "匹配特征 $raw。", 6)
                n == "dwnet" ->
                    Hint("ap", "DWnet 接入点", "匹配特征 $raw。", 6)
                n == "wavlink" ->
                    Hint("ap", "WAVLINK 接入点", "匹配特征 $raw。", 6)
                n == "sercomm" ->
                    Hint("ap", "Sercomm 运营商网关", "匹配特征 $raw。", 6)
                n == "luxul" ->
                    Hint("ap", "Luxul 接入点", "匹配特征 $raw。", 6)
                n == "sophos" ->
                    Hint("ap", "Sophos 防火墙或接入点", "匹配特征 $raw。", 7)
                n == "aumovio" ->
                    Hint("hotspot", "AUMOVIO / Continental 车载 Wi-Fi 无线设备", "匹配特征 $raw。", 6)
                n == "centurylink" ->
                    Hint("ap", "CenturyLink 网关", "匹配特征 $raw。", 6)
                n == "gm hotspot" ->
                    Hint("hotspot", "GM 车载热点（Cadillac / GMC / Buick / Chevrolet）", "匹配特征 $raw。", 6)
                n == "audi mmi" ->
                    Hint("hotspot", "Audi MMI 车载热点", "匹配特征 $raw。", 6)
                n == "extreme" ->
                    Hint("ap", "Extreme Networks 接入点", "匹配特征 $raw。", 7)
                n == "adtran" ->
                    Hint("ap", "Adtran 光纤网关（常为 CenturyLink / Quantum Fiber 代工产品）", "匹配特征 $raw。", 6)
                n == "cambium" ->
                    Hint("ap", "Cambium 或 IgniteNet 接入点", "匹配特征 $raw。", 6)
                n == "trendnet" ->
                    Hint("ap", "TRENDnet 接入点", "匹配特征 $raw。", 6)
                n == "cudy" ->
                    Hint("ap", "Cudy 旅行或家用路由器", "匹配特征 $raw。", 6)
                n == "snapav" ->
                    Hint("ap", "SnapAV / Control4 / Wattbox 接入点", "匹配特征 $raw。", 6)
                n == "arlo" ->
                    Hint("camera", "Arlo 摄像头或 VMB 基站", "匹配特征 $raw。", 6)
                n == "vantiva" ->
                    Hint("ap", "Vantiva 或 Technicolor 运营商网关", "匹配特征 $raw。", 6)
                n == "hitron" ->
                    Hint("ap", "Hitron 有线网关（常为 Xfinity 代工产品）", "匹配特征 $raw。", 6)
                n == "actiontec" ->
                    Hint("ap", "Actiontec FiOS 或 Frontier 网关", "匹配特征 $raw。", 6)
                n == "buffalo" ->
                    Hint("ap", "Buffalo AirStation 或路由器", "匹配特征 $raw。", 6)
                n == "grandstream" ->
                    Hint("ap", "Grandstream GWN 接入点", "匹配特征 $raw。", 6)
                n == "edgecore" ->
                    Hint("ap", "Edgecore 接入点", "匹配特征 $raw。", 7)
                n == "watchguard ap" ->
                    Hint("ap", "WatchGuard 防火墙或接入点", "匹配特征 $raw。", 7)
                n == "mojo" ->
                    Hint("ap", "Mojo Networks / Arista Cognitive Wi-Fi 接入点", "匹配特征 $raw。", 7)
                n == "winegard" ->
                    Hint("hotspot", "Winegard 房车或船用 Wi-Fi 无线设备", "匹配特征 $raw。", 6)
                n == "inseego" ->
                    Hint("ap", "Inseego 5G 或 MiFi 热点", "匹配特征 $raw。", 6)
                n == "franklin" ->
                    Hint("ap", "Franklin Technology 5G 家庭网络网关（RG3100 类）", "匹配特征 $raw。", 6)
                n == "synology" ->
                    Hint("ap", "Synology NAS 或路由接入点", "匹配特征 $raw。", 6)
                n == "aruba" ->
                    Hint("ap", "HPE Aruba Instant 或 Instant On 接入点", "匹配特征 $raw。", 7)
                n == "ruckus" ->
                    Hint("ap", "RUCKUS 接入点", "匹配特征 $raw。", 7)
                n == "fortinet" ->
                    Hint("ap", "Fortinet FortiAP 或 FortiWiFi", "匹配特征 $raw。", 7)
                n == "mikrotik" ->
                    Hint("ap", "MikroTik 路由器或接入点", "匹配特征 $raw。", 6)
                n == "engenius" ->
                    Hint("ap", "EnGenius 接入点", "匹配特征 $raw。", 6)
                n == "zyxel" ->
                    Hint("ap", "Zyxel 网关或接入点", "匹配特征 $raw。", 6)
                n == "peplink" ->
                    Hint("ap", "Peplink 或 Pepwave 路由器", "匹配特征 $raw。", 6)
                n == "openwrt" ->
                    Hint("ap", "OpenWrt 路由器", "匹配特征 $raw。", 6)
                n == "arris" ->
                    Hint("ap", "Arris 或 SURFboard 有线网关", "匹配特征 $raw。", 6)
                n == "unifi ap" ->
                    Hint("ap", "Ubiquiti UniFi 接入点", "匹配特征 $raw。", 7)
                n == "unifi protect" ->
                    Hint("camera", "UniFi Protect Instant 摄像头", "匹配特征 $raw。", 7)
                n == "unifi" ->
                    Hint("ap", "使用 UniFi / Ubiquiti 名称的设备", "匹配特征 $raw。", 5)
                n == "ecobee" ->
                    Hint("thermostat", "ecobee 温控器", "匹配特征 $raw。", 7)
                n == "sensi" ->
                    Hint("thermostat", "Sensi 温控器", "匹配特征 $raw。", 6)
                n == "honeywell home" ->
                    Hint("thermostat", "Honeywell Home 或 Lyric 温控器", "匹配特征 $raw。", 6)
                "honeywell xenon" in n ->
                    Hint("health", "Honeywell Xenon 医疗条码扫描器", "匹配特征 $raw。", 7)
                n == "omron" ->
                    Hint("health", "Omron 血压计或体重秤", "匹配特征 $raw。", 7)
                n == "withings" ->
                    Hint("health", "Withings 体重秤或血压计", "匹配特征 $raw。", 7)
                n == "dexcom" ->
                    Hint("health", "Dexcom 血糖传感器", "匹配特征 $raw。", 7)
                n == "nest thermostat" ->
                    Hint("thermostat", "Nest 温控器或 Nest Labs BLE 传感器", "匹配特征 $raw。", 6)
                n == "nest weave" ->
                    Hint("sensor", "Nest Protect、摄像头或其他 Weave BLE 设备", "匹配特征 $raw。", 7)
                n == "haiku fan" || n == "haiku" ->
                    Hint("fan", "Haiku 或 Mammoth 吊扇", "匹配特征 $raw。", 7)
                n == "tuya" ->
                    Hint("iot", "Tuya BLE 设备（插座、灯、摄像头、传感器）", "匹配特征 $raw。", 6)
                n == "seos" || n == "assa abloy" ->
                    Hint("access", "ASSA ABLOY 锁、Yale 锁、HID 读卡器或 Seos 凭证", "匹配特征 $raw。", 7)
                n == "august" ->
                    Hint("lock", "August 智能锁", "匹配特征 $raw。", 7)
                n == "schlage" ->
                    Hint("lock", "Schlage 或 Allegion 锁", "匹配特征 $raw。", 7)
                n == "nuki" ->
                    Hint("lock", "Nuki 锁或开门器", "匹配特征 $raw。", 7)
                n == "salto" ->
                    Hint("access", "SALTO 门禁读卡器或锁", "匹配特征 $raw。", 7)
                n == "dormakaba" ->
                    Hint("access", "dormakaba、Saflok 或 Oracode 锁", "匹配特征 $raw。", 7)
                n == "lockly" ->
                    Hint("lock", "Lockly 智能锁", "匹配特征 $raw。", 6)
                n == "kevo" ->
                    Hint("lock", "Kwikset Kevo 或 Unikey 锁", "匹配特征 $raw。", 7)
                n == "master lock" ->
                    Hint("lock", "Master Lock 挂锁", "匹配特征 $raw。", 7)
                n == "igloohome" ->
                    Hint("lock", "igloohome 锁或钥匙盒", "匹配特征 $raw。", 7)
                n == "tedee" ->
                    Hint("lock", "Tedee 智能锁", "匹配特征 $raw。", 7)
                n == "paxton" ->
                    Hint("access", "Paxton 读卡器或 Net2 接入点", "匹配特征 $raw。", 7)
                n == "kwikset" ->
                    Hint("lock", "Kwikset 锁", "匹配特征 $raw。", 6)
                n == "myq" ->
                    Hint("garage", "Chamberlain myQ 车库中枢", "匹配特征 $raw。", 7)
                n == "chevrolet hotspot" ->
                    Hint("hotspot", "Chevrolet 车载 Wi-Fi 热点", "匹配特征 $raw。", 7)
                n == "rivian" ->
                    Hint("vehicle", "Rivian 车辆、手机钥匙或传感器", "匹配特征 $raw。", 7)
                n == "ford" ->
                    Hint("vehicle", "Ford 或 Lincoln 车辆或手机钥匙", "匹配特征 $raw。", 7)
                n == "honda" ->
                    Hint("vehicle", "Honda 或 Acura 车辆或手机钥匙", "匹配特征 $raw。", 7)
                n == "hyundai" ->
                    Hint("vehicle", "Hyundai 或 Genesis 车辆或手机钥匙", "匹配特征 $raw。", 7)
                n == "toyota" ->
                    Hint("vehicle", "Toyota 或 Lexus 车辆或手机钥匙", "匹配特征 $raw。", 7)
                n == "nissan" ->
                    Hint("vehicle", "Nissan 或 Infiniti 车辆或手机钥匙", "匹配特征 $raw。", 7)
                n == "subaru" ->
                    Hint("vehicle", "Subaru 车辆或手机钥匙", "匹配特征 $raw。", 7)
                n == "bmw" ->
                    Hint("vehicle", "BMW 车辆、手机钥匙或原厂热点", "匹配特征 $raw。", 7)
                n == "volkswagen" ->
                    Hint("vehicle", "Volkswagen 车辆或手机钥匙", "匹配特征 $raw。", 7)
                n == "porsche" ->
                    Hint("vehicle", "Porsche 车辆或手机钥匙", "匹配特征 $raw。", 7)
                n == "jaguar land rover" ->
                    Hint("vehicle", "Jaguar、Land Rover 或 Range Rover", "匹配特征 $raw。", 7)
                n == "byd" ->
                    Hint("vehicle", "BYD 车辆或手机钥匙", "匹配特征 $raw。", 7)
                n == "govee" ->
                    Hint("light", "Govee 灯或传感器", "匹配特征 $raw。", 6)
                n == "hp" ->
                    Hint("printer", "HP 打印机", "匹配特征 $raw。", 6)
                n == "epson" ->
                    Hint("printer", "Epson EcoTank 或 WorkForce 打印机", "匹配特征 $raw。", 6)
                n == "lg webos tv" ->
                    Hint("tv", "LG webOS 电视", "匹配特征 $raw。", 7)
                n == "roku" ->
                    Hint("tv", "Roku 流媒体棒或 Roku TV（常见为隐藏的 Wi-Fi Direct 遥控 AP）", "匹配特征 $raw。", 7)
                n == "samsung appliance" ->
                    Hint("iot", "Samsung 冰箱、炉灶、烤箱或灶台（配置 AP）", "匹配特征 $raw。", 6)
                n == "ecowater" ->
                    Hint("iot", "EcoWater 软水机（配置 AP）", "匹配特征 $raw。", 6)
                n == "nespresso" ->
                    Hint("iot", "Nespresso 咖啡机", "匹配特征 $raw。", 7)
                n == "radiacode" ->
                    Hint("sensor", "RadiaCode 辐射检测仪", "匹配特征 $raw。", 7)
                n == "shokz" ->
                    Hint("audio-personal", "Shokz OpenRun 或 OpenFit 耳机", "匹配特征 $raw。", 7)
                n == "mercedes mbux" ->
                    Hint("hotspot", "Mercedes MBUX 车载热点", "匹配特征 $raw。", 7)
                n == "motive" ->
                    Hint("hotspot", "Motive / KeepTruckin 车队 ELD 热点", "匹配特征 $raw。", 6)
                n == "peoplenet" ->
                    Hint("hotspot", "PeopleNet 车队 ELD 热点", "匹配特征 $raw。", 6)
                n == "uconnect" ->
                    Hint("hotspot", "Uconnect 车载热点", "匹配特征 $raw。", 6)
                n == "carplay" ->
                    Hint("hotspot", "CarPlay 车载热点", "匹配特征 $raw。", 6)
                n == "cradlepoint" ->
                    Hint("hotspot", "Cradlepoint 车载路由器（常用于公共安全 / 车队）", "匹配特征 $raw。", 7)
                n == "airlink" ->
                    Hint("hotspot", "Sierra Wireless AirLink 车载网关", "匹配特征 $raw。", 7)
                n == "compex" ->
                    Hint("hotspot", "Compex 接入点（有时用于公共安全 / 车队）", "匹配特征 $raw。", 6)
                n == "novatel wireless" ->
                    Hint("hotspot", "Novatel Wireless / Inseego 车载无线设备", "匹配特征 $raw。", 6)
                n == "utility inc" ->
                    Hint("hotspot", "Utility, Inc 车载或公共安全无线设备", "匹配特征 $raw。", 6)
                "gl.inet" in n || n == "glinet" ->
                    Hint("ap", "GL.iNet 旅行路由器", "匹配特征 $raw。", 6)
                "smarttag" in n ->
                    Hint("tag", "Samsung SmartTag", "匹配特征 $raw。", 8)
                "tile" in n ->
                    Hint("tag", "Tile 追踪标签", "匹配特征 $raw。", 8)
                n == "ibeacon" ->
                    Hint("beacon", "iBeacon 信标", "匹配特征 $raw。", 7)
                "target atrius" in n ->
                    Hint("beacon", "Target Atrius 购物篮标签", "匹配特征 $raw。", 8)
                n == "minew" ->
                    Hint("beacon", "Minew BLE 信标或传感器", "匹配特征 $raw。", 7)
                n == "estimote" ->
                    Hint("beacon", "Estimote 信标", "匹配特征 $raw。", 7)
                n == "kontakt.io" || n == "kontakt" ->
                    Hint("beacon", "Kontakt.io 信标", "匹配特征 $raw。", 7)
                "bluetoad" in n ->
                    Hint(
                        "roadside",
                        "Iteris BlueTOAD / Vantage Velocity 路侧蓝牙行程时间读取器",
                        "匹配特征 $raw。",
                        7,
                    )
                "bliptrack" in n ->
                    Hint(
                        "roadside",
                        "BLIP Systems BlipTrack 路侧行程时间传感器",
                        "匹配特征 $raw。",
                        7,
                    )
                "raven" in n || "shotspotter" in n || "soundthinking" in n ->
                    Hint(
                        "acoustic",
                        "Flock Raven 或 ShotSpotter 声学枪声传感器",
                        "匹配特征 $raw。",
                        8,
                    )
                "digital ally" in n ->
                    Hint("camera", "Digital Ally 随身或车载摄像头", "匹配特征 $raw。", 8)
                "reveal media" in n || "bodyworn" in n ->
                    Hint("camera", "Reveal Media 随身摄像头", "匹配特征 $raw。", 8)
                n == "wolfcom" ->
                    Hint("camera", "Wolfcom 随身或车载摄像头", "匹配特征 $raw。", 8)
                "i-pro" in n || "arbitrator" in n ->
                    Hint("camera", "Panasonic i-PRO 摄像头或 Arbitrator 车载系统", "匹配特征 $raw。", 8)
                "limitless" in n ->
                    Hint("wearable", "Limitless Pendant 对话记录吊坠", "匹配特征 $raw。", 8)
                n == "bee pendant" || "bee pioneer" in n ->
                    Hint("wearable", "Bee Pioneer 可穿戴录音设备", "匹配特征 $raw。", 8)
                n == "omi" || "openglass" in n ->
                    Hint("wearable", "Omi 吊坠或 OpenGlass 摄像眼镜", "匹配特征 $raw。", 8)
                "friend pendant" in n ->
                    Hint("wearable", "Friend Pendant 项链", "匹配特征 $raw。", 8)
                "brilliant frame" in n ->
                    Hint("glasses", "Brilliant Labs Frame AR 眼镜", "匹配特征 $raw。", 8)
                n == "even g1" ->
                    Hint("glasses", "Even Realities G1 眼镜", "匹配特征 $raw。", 8)
                "hayden" in n ->
                    Hint("camera", "Hayden AI 公交或车载摄像头", "匹配特征 $raw。", 8)
                "miovision" in n ->
                    Hint("camera", "Miovision 路口交通摄像头", "匹配特征 $raw。", 8)
                n == "tattile" ->
                    Hint("camera", "Tattile 车牌识别设备", "匹配特征 $raw。", 8)
                "lvt" in n || "liveview" in n ->
                    Hint("camera", "LVT / LiveView 太阳能监控拖车", "匹配特征 $raw。", 8)
                "hanwha" in n || "wisenet" in n ->
                    Hint("camera", "Hanwha Vision / Wisenet 摄像头", "匹配特征 $raw。", 7)
                n == "uniview" ->
                    Hint("camera", "Uniview / UNV 摄像头", "匹配特征 $raw。", 7)
                n == "rhombus" ->
                    Hint("camera", "Rhombus 云摄像头", "匹配特征 $raw。", 7)
                n == "meshcore" ->
                    Hint("mesh", "MeshCore LoRa 配套无线设备", "匹配特征 $raw。", 7)
                "gotenna" in n ->
                    Hint("mesh", "goTenna Mesh 或 Pro 无线设备", "匹配特征 $raw。", 7)
                n == "sensecap" ->
                    Hint("mesh", "SenseCAP LoRaWAN / Helium 网关", "匹配特征 $raw。", 7)
                "wisgate" in n || n == "rak wisgate" ->
                    Hint("mesh", "RAK WisGate LoRaWAN 网关", "匹配特征 $raw。", 7)
                n == "ghostesp" ->
                    Hint("pentest", "GhostESP ESP32 审计开发板", "匹配特征 $raw。", 7)
                n == "bruce" ->
                    Hint("pentest", "Bruce ESP32 渗透测试开发板", "匹配特征 $raw。", 7)
                n == "liteon camera radio" ->
                    Hint(
                        "module",
                        "摄像头模块无线设备（LiteOn 或类似产品）",
                        "匹配特征 $raw。",
                        3,
                    )
                "chipolo" in n || "pebblebee" in n || "moto tag" in n ->
                    Hint("tag", "寻物标签", "匹配特征 $raw。", 7)
                "airpods" in n ->
                    Hint("audio-personal", "AirPods", "匹配特征 $raw。", 8)
                else -> Hint("named", raw, "匹配特征 $raw。", 7)
            }
        }
    }

    private fun isGenericSignatureName(name: String): Boolean {
        val n = name.trim()
        return n.equals("Unknown Signature", ignoreCase = true) ||
            n.equals("Unknown Fleet", ignoreCase = true)
    }

    private fun wifiHints(device: Sighting, signatureNames: List<String>): List<Hint> {
        val name = device.name
        val caps = (device.facts.capabilities ?: "").uppercase()
        val specific = signatureNames.any { !isGenericSignatureName(it) }
        val out = ArrayList<Hint>(2)
        when {
            name.startsWith("DIRECT-", true) ->
                out += if (specific) {
                    Hint("wifi-direct", "Wi-Fi Direct 接入点", "SSID 以 DIRECT- 开头。", 4)
                } else {
                    Hint("wifi-direct", "使用 Wi-Fi Direct 的手机或电视", "SSID 以 DIRECT- 开头。", 6)
                }
            name.startsWith("ANDROID-", true) || name.contains("hotspot", true) ->
                if (!specific) {
                    out += Hint("hotspot", "手机热点", "SSID 看起来像手机热点。", 6)
                }
            "MESH" in caps ->
                out += Hint("mesh", "Mesh Wi-Fi 节点", "能力列表包含 Mesh。", 5)
            device.hiddenSsid ->
                out += Hint("ap", "隐藏的 Wi-Fi 接入点", "SSID 已隐藏，无线设备仍在发送信标。", 4)
            else ->
                if (!specific) {
                    out += Hint("ap", "Wi-Fi 接入点", "原生 Android 只会报告广播信标的 AP。", 3)
                }
        }
        return out
    }

    private fun uuid16(uuid: String): Int? {
        val hex = uuid.filter { it.isLetterOrDigit() }.uppercase()
        return when {
            hex.length == 4 -> hex.toIntOrNull(16)
            hex.length == 32 && hex.startsWith("0000") && hex.endsWith("00001000800000805F9B34FB") ->
                hex.substring(4, 8).toIntOrNull(16)
            hex.length == 8 -> hex.takeLast(4).toIntOrNull(16)
            else -> null
        }
    }
}
