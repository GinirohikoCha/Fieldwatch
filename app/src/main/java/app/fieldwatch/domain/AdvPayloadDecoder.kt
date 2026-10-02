package app.fieldwatch.domain

/**
 * Decode well-known BLE advertisement payloads: Apple Continuity / iBeacon,
 * Google Fast Pair, Eddystone, Microsoft CDP. After company ID / UUID the rest
 * is proprietary; only published or well-reverse-engineered layouts are named.
 */
object AdvPayloadDecoder {
    data class Field(val label: String, val value: String)

    data class RoleHint(
        val bucket: String,
        val label: String,
        val reason: String,
        val weight: Int,
    )

    fun decodeManufacturer(record: MfgRecord): List<Field> {
        val bytes = hexToBytes(record.dataHex) ?: return emptyList()
        return when (record.companyId) {
            0x004C -> decodeApple(bytes)
            0x0006 -> decodeMicrosoft(bytes)
            0x0157 -> decodeAltBeacon(bytes)
            0x00E0 -> listOf(Field("Google 厂商数据", "${bytes.size} 字节"))
            else -> emptyList()
        }
    }

    fun decodeService(record: ServiceDataRecord): List<Field> {
        val bytes = hexToBytes(record.dataHex) ?: return emptyList()
        val short = uuid16(record.uuid) ?: return emptyList()
        return when (short) {
            0xFE2C -> decodeFastPair(bytes)
            0xFEAA -> decodeEddystone(bytes)
            else -> emptyList()
        }
    }

    fun roleHints(device: Sighting): List<RoleHint> {
        val out = ArrayList<RoleHint>(4)
        val mfg = device.facts.mfgRecords.ifEmpty {
            device.manufacturerId?.let { listOf(MfgRecord(it, device.manufacturerDataHex)) } ?: emptyList()
        }
        for (rec in mfg) {
            if (rec.companyId != 0x004C) continue
            val bytes = hexToBytes(rec.dataHex) ?: continue
            for (tlv in appleTlvs(bytes)) {
                when (tlv.type) {
                    0x02 -> if (tlv.data.size >= 20) {
                        val hex = tlv.data.toHexUpper()
                        val teslaPrefix = DefaultCatalog.TESLA_IBEACON_MFG_PREFIX
                        val targetPrefix = DefaultCatalog.TARGET_ATRIUS_IBEACON_MFG_PREFIX
                        if (hex.startsWith(teslaPrefix) || hex.startsWith(teslaPrefix.drop(4))) {
                            out += RoleHint(
                                "vehicle",
                                "Tesla 车辆或手机钥匙",
                                "Tesla 手机钥匙 iBeacon UUID（用于 iOS 后台查找）。",
                                8,
                            )
                        } else if (hex.startsWith(targetPrefix) || hex.startsWith(targetPrefix.drop(4))) {
                            out += RoleHint(
                                "beacon",
                                "Target Atrius 购物篮标签",
                                "Target / Atrius iBeacon UUID（购物篮资产标签）。",
                                8,
                            )
                        } else {
                            out += RoleHint("beacon", "iBeacon 信标", "Apple iBeacon 载荷。", 7)
                        }
                    }
                    0x05 -> out += RoleHint("phone", "已开启隔空投送的 iPhone 或 iPad", "Apple 隔空投送广播。", 5)
                    0x07 -> {
                        val model = airPodsModel(tlv.data)
                        out += RoleHint(
                            "audio-personal",
                            model ?: "AirPods 或 Beats 耳机",
                            if (model != null) "Apple 近距离配对：$model。"
                            else "Apple 近距离配对（AirPods / Beats）。",
                            8,
                        )
                    }
                    0x08 -> out += RoleHint("siri", "刚听到“嘿 Siri”的 Apple 设备", "“嘿 Siri”广播。", 6)
                    0x09 -> out += RoleHint("audio-speaker", "AirPlay 音箱或 Apple TV", "AirPlay 广播。", 5)
                    0x0B -> out += RoleHint("phone", "正在使用接力的 Apple 设备", "接力广播。", 4)
                    0x0C -> out += RoleHint("phone", "正在寻找即时热点的 Apple 设备", "网络共享目标端广播。", 5)
                    0x0D, 0x0E -> out += RoleHint("hotspot", "提供即时热点的 iPhone / iPad", "网络共享源端广播。", 6)
                    0x0F -> out += RoleHint("phone", "Apple 设备（附近操作）", nearbyActionReason(tlv.data), 4)
                    0x10 -> out += RoleHint("phone", "iPhone / iPad / Mac（附近信息）", nearbyInfoReason(tlv.data), 5)
                    0x12 -> out += RoleHint(
                        "tag",
                        "“查找”网络设备",
                        "Apple 离线查找：可能是 AirTag、“查找”配件或正在定位自身的 Apple 设备。",
                        4,
                    )
                }
            }
        }
        for (sd in device.facts.serviceData) {
            when (uuid16(sd.uuid)) {
                0xFE2C -> {
                    val bytes = hexToBytes(sd.dataHex) ?: continue
                    if (bytes.size == 3) {
                        val id = modelId24(bytes)
                        val name = FastPairModels.name(id)
                        out += RoleHint(
                            "audio-personal",
                            name ?: "Fast Pair 配件（通常为耳机或音箱）",
                            if (name != null) "Google Fast Pair 型号 $name（0x%06X），处于配对模式。".format(id)
                            else "Google Fast Pair 型号 0x%06X，处于配对模式。".format(id),
                            if (name != null) 8 else 6,
                        )
                    } else {
                        out += RoleHint(
                            "audio-personal",
                            "已与某个账户配对的 Fast Pair 配件",
                            "Google Fast Pair 账户密钥广播（未处于配对模式）。",
                            4,
                        )
                    }
                }
                0xFEAA -> {
                    val frame = hexToBytes(sd.dataHex)?.firstOrNull()?.toInt()?.and(0xFF)
                    when (frame) {
                        0x40, 0x41 -> out += RoleHint(
                            "tag",
                            "Google Find Hub 寻物标签",
                            if (frame == 0x41) "Find Hub 分离（防非自愿追踪）帧。"
                            else "Find Hub 附近帧。",
                            8,
                        )
                        else -> out += RoleHint("beacon", "Eddystone 信标", "Eddystone 服务数据。", 6)
                    }
                }
            }
        }
        return out
    }

    private data class Tlv(val type: Int, val data: ByteArray)

    private fun decodeApple(bytes: ByteArray): List<Field> {
        val tlvs = appleTlvs(bytes)
        if (tlvs.isEmpty()) return listOf(Field("Apple 载荷", "${bytes.size} 字节（未解析）"))
        val out = ArrayList<Field>(8)
        for (tlv in tlvs) {
            out += Field("Apple 连续互通类型", "0x%02X · %s".format(tlv.type, appleTypeName(tlv.type)))
            out += when (tlv.type) {
                0x02 -> decodeIBeacon(tlv.data)
                0x05 -> decodeAirDrop(tlv.data)
                0x06 -> listOf(Field("HomeKit", "${tlv.data.size} 字节的 HomeKit 设置数据"))
                0x07 -> decodeAirPods(tlv.data)
                0x08 -> decodeHeySiri(tlv.data)
                0x09 -> listOf(Field("AirPlay", "此设备正作为 AirPlay 源端或目标端广播。"))
                0x0A -> listOf(Field("Magic Switch", "与 Apple Watch 佩戴或解锁有关。"))
                0x0B -> decodeHandoff(tlv.data)
                0x0C -> decodeHandoffOrTetherTarget(tlv.data)
                0x0D, 0x0E -> decodeTetherSource(tlv.data)
                0x0F -> decodeNearbyAction(tlv.data)
                0x10 -> decodeNearbyInfo(tlv.data)
                0x12 -> decodeFindMy(tlv.data)
                else -> listOf(Field("载荷", "${tlv.data.size} 字节"))
            }
        }
        return out
    }

    private fun appleTlvs(bytes: ByteArray): List<Tlv> {
        val out = ArrayList<Tlv>(3)
        var i = 0
        while (i + 2 <= bytes.size) {
            val type = bytes[i].toInt() and 0xFF
            val len = bytes[i + 1].toInt() and 0xFF
            if (len <= 0 || i + 2 + len > bytes.size) break
            out += Tlv(type, bytes.copyOfRange(i + 2, i + 2 + len))
            i += 2 + len
        }
        return out
    }

    private fun appleTypeName(type: Int): String = when (type) {
        0x02 -> "iBeacon"
        0x03 -> "AirPrint"
        0x05 -> "AirDrop"
        0x06 -> "HomeKit"
        0x07 -> "近距离配对（AirPods / Beats）"
        0x08 -> "Hey Siri"
        0x09 -> "AirPlay"
        0x0A -> "Magic Switch（手表）"
        0x0B -> "接力"
        0x0C -> "接力或即时热点（目标端）"
        0x0D -> "即时热点（源端）"
        0x0E -> "即时热点（源端）"
        0x0F -> "附近操作"
        0x10 -> "附近信息"
        0x12 -> "查找 / 离线查找"
        0x13 -> "附近操作（扩展）"
        0x16 -> "附近信息"
        else -> "未收录"
    }

    private fun decodeIBeacon(data: ByteArray): List<Field> {
        // TLV payload is length-byte already consumed; data is 0x15 + 21 bytes OR 21 bytes.
        val body = when {
            data.size >= 22 && data[0] == 0x15.toByte() -> data.copyOfRange(1, 22)
            data.size >= 21 -> data.copyOfRange(0, 21)
            else -> return listOf(Field("iBeacon", "数据不完整（${data.size} 字节）"))
        }
        val uuid = uuidFromBe(body, 0)
        val major = u16be(body, 16)
        val minor = u16be(body, 18)
        val tx = body[20].toInt()
        val teslaKey = uuid.filter { it.isLetterOrDigit() }.equals(
            DefaultCatalog.TESLA_IBEACON_MFG_PREFIX.drop(4),
            ignoreCase = true,
        )
        return listOf(
            Field(
                "iBeacon UUID",
                if (teslaKey) "$uuid — Tesla 手机钥匙（用于 iOS 后台查找），并非商场信标。" else uuid,
            ),
            Field("iBeacon 主编号 / 次编号", "$major / $minor"),
            Field("iBeacon 校准发射功率", "1 米处 $tx dBm（用于估算距离）"),
        )
    }

    private fun decodeAirDrop(data: ByteArray): List<Field> {
        // 8 zeros, version, appleID hash(2), phone(2), email(2), email2(2), 0
        if (data.size < 18) return listOf(Field("AirDrop", "附近有人开启了隔空投送（${data.size} 字节）。"))
        return listOf(
            Field("AirDrop", "附近有人开启了隔空投送接收。哈希是截断的 ID，并非姓名。"),
            Field("Apple ID 哈希（2 字节）", data.copyOfRange(9, 11).toHexUpper()),
        )
    }

    private fun decodeAirPods(data: ByteArray): List<Field> {
        // prefix 0x01, model u16be, status, batt nibble, charge+case, lid, color, 0x00, enc 16
        if (data.size < 5) return listOf(Field("AirPods", "近距离配对，数据不完整。"))
        val start = if (data[0] == 0x01.toByte()) 1 else 0
        if (data.size < start + 4) return listOf(Field("AirPods", "近距离配对。"))
        val model = ((data[start].toInt() and 0xFF) shl 8) or (data[start + 1].toInt() and 0xFF)
        val status = data[start + 2].toInt() and 0xFF
        val batt = data[start + 3].toInt() and 0xFF
        val left = batt and 0x0F
        val right = (batt shr 4) and 0x0F
        val out = ArrayList<Field>(6)
        out += Field("产品", airPodsModelName(model) ?: "Apple 音频设备 0x%04X".format(model))
        out += Field("耳机位置", airPodsStatus(status))
        out += Field("电量（左 / 右）", "${nibblePct(left)} / ${nibblePct(right)}")
        if (data.size > start + 4) {
            val ch = data[start + 4].toInt() and 0xFF
            val caseBatt = ch and 0x0F
            val charging = buildList {
                if (ch and 0x10 != 0) add("充电盒")
                if (ch and 0x20 != 0) add("右耳")
                if (ch and 0x40 != 0) add("左耳")
            }
            out += Field("充电盒电量", nibblePct(caseBatt))
            if (charging.isNotEmpty()) out += Field("正在充电", charging.joinToString(", "))
        }
        if (data.size > start + 6) {
            out += Field("颜色", airPodsColor(data[start + 6].toInt() and 0xFF))
        }
        return out
    }

    private fun airPodsModel(data: ByteArray): String? {
        if (data.size < 4) return null
        val start = if (data[0] == 0x01.toByte()) 1 else 0
        if (data.size < start + 2) return null
        val model = ((data[start].toInt() and 0xFF) shl 8) or (data[start + 1].toInt() and 0xFF)
        return airPodsModelName(model)
    }

    private fun airPodsModelName(id: Int): String? = when (id) {
        0x0220 -> "AirPods（第 1 代）"
        0x0F20 -> "AirPods（第 2 代）"
        0x1320 -> "AirPods（第 3 代）"
        0x1920 -> "AirPods（第 4 代）"
        0x1C20 -> "AirPods 4"
        0x0E20 -> "AirPods Pro"
        0x1420 -> "AirPods Pro（第 2 代）"
        0x2420 -> "AirPods Pro 2 (USB-C)"
        0x1F20 -> "AirPods Max"
        0x0A20 -> "Beats Solo3"
        0x0B20 -> "Powerbeats 3"
        0x0C20 -> "Beats Studio Buds"
        0x0D20 -> "Beats Fit Pro"
        0x1020 -> "Powerbeats Pro"
        0x1120 -> "Beats Studio Buds +"
        0x1220 -> "Beats Solo Pro"
        0x1720 -> "Beats Flex"
        0x1A20 -> "Beats Studio Pro"
        0x1B20 -> "Beats Fit Pro"
        0x0520 -> "BeatsX"
        0x0920 -> "Beats Studio³ Wireless"
        0x1620 -> "Beats Studio Buds +"
        0x2520 -> "Beats Solo 4"
        0x2620 -> "Beats Solo Buds"
        0x2D20 -> "AirPods Max 2"
        0x3820 -> "Beats 360"
        0x038F -> "Beats Studio Buds"
        else -> null
    }

    private fun airPodsStatus(status: Int): String = when (status) {
        0x01 -> "一只或两只耳机已取出"
        0x02 -> "充电盒已打开"
        0x03 -> "取出 / 入耳切换中"
        0x05 -> "一只耳机已入耳"
        0x09 -> "两只均已取出但未入耳"
        0x0B -> "入耳活动"
        0x11, 0x13 -> "两只耳机均已入耳"
        0x21 -> "一只耳机已入耳（可能正在共享）"
        0x51 -> "两只均在盒内，盒盖打开"
        0x55 -> "两只均在盒内，盒盖关闭"
        0x75 -> "在充电盒内"
        else -> "状态 0x%02X".format(status)
    }

    private fun airPodsColor(v: Int): String = when (v) {
        0x00 -> "白色"
        0x01 -> "黑色"
        0x02 -> "红色"
        0x03 -> "蓝色"
        0x04 -> "粉色"
        0x05 -> "灰色"
        0x06 -> "银色"
        0x07 -> "金色"
        0x08 -> "玫瑰金"
        0x09 -> "深空灰"
        0x0A -> "深蓝色"
        0x0B -> "浅蓝色"
        0x0C -> "黄色"
        else -> "0x%02X".format(v)
    }

    private fun nibblePct(n: Int): String = when (n) {
        in 0..9 -> "${n * 10}%"
        10, 11, 12, 13, 14 -> "100%"
        15 -> "未知 / 不在位"
        else -> "$n"
    }

    private fun decodeHeySiri(data: ByteArray): List<Field> {
        if (data.size < 6) return listOf(Field("Hey Siri", "附近的 Apple 设备刚触发 Siri。"))
        val klass = u16be(data, 4)
        val device = when (klass) {
            0x0002 -> "iPhone"
            0x0003 -> "iPad"
            0x0007 -> "HomePod"
            0x0009 -> "Mac"
            0x000A -> "手表"
            else -> "类别 0x%04X".format(klass)
        }
        return listOf(
            Field("Hey Siri", "一台 $device 刚听到 Siri 唤醒词。数据包仅携带简短的语音哈希，不包含说话内容。"),
        )
    }

    private fun decodeHandoff(data: ByteArray): List<Field> =
        listOf(Field("接力", "连续互通接力：可在另一台 Apple 设备上继续任务。载荷已加密。"))

    private fun decodeHandoffOrTetherTarget(data: ByteArray): List<Field> =
        if (data.size >= 14) decodeHandoff(data)
        else listOf(Field("即时热点（寻找中）", "此 Apple 设备正在搜索已配对手机的热点。"))

    private fun decodeTetherSource(data: ByteArray): List<Field> {
        if (data.size < 6) return listOf(Field("即时热点", "一台 iPhone / iPad 正在提供个人热点。"))
        val batt = data[2].toInt() and 0xFF
        val cell = if (data.size >= 5) u16be(data, 3) else -1
        val bars = if (data.size >= 6) data[5].toInt() and 0xFF else -1
        val cellName = when (cell) {
            0, 6 -> "4G"
            1 -> "1xRTT"
            2 -> "GPRS"
            3 -> "EDGE"
            4, 5 -> "3G"
            7 -> "LTE"
            8 -> "5G"
            else -> if (cell >= 0) "类型 $cell" else null
        }
        return listOf(
            Field(
                "即时热点（提供中）",
                buildString {
                    append("已配对的 iPhone / iPad 热点")
                    if (batt in 0..100) append(" · 手机电量 $batt%")
                    cellName?.let { append(" · $it") }
                    if (bars in 0..5) append(" · 信号 $bars/5 格")
                },
            ),
        )
    }

    private fun decodeNearbyAction(data: ByteArray): List<Field> {
        if (data.isEmpty()) return listOf(Field("附近操作", "Apple 附近操作"))
        val action = if (data.size >= 2) data[1].toInt() and 0xFF else data[0].toInt() and 0xFF
        val name = nearbyActionName(action)
        return listOf(Field("附近操作", name))
    }

    private fun nearbyActionReason(data: ByteArray): String {
        val action = if (data.size >= 2) data[1].toInt() and 0xFF else return "附近操作广播。"
        return "附近操作：${nearbyActionName(action)}。"
    }

    private fun nearbyActionName(action: Int): String = when (action) {
        0x01 -> "Apple TV 设置"
        0x04 -> "移动设备备份"
        0x05 -> "手表设置"
        0x06 -> "Apple TV 配对"
        0x08 -> "Wi-Fi 密码共享（向附近 iPhone 提示）"
        0x09 -> "iOS 设置"
        0x0A -> "修复"
        0x0B -> "音箱设置"
        0x0C -> "Apple Pay"
        0x0D -> "全屋音响设置"
        0x0F -> "已接听电话"
        0x10 -> "已结束通话"
        0x13 -> "远程自动填充"
        0x14 -> "Companion Link 近距离连接"
        0x17 -> "远程显示"
        else -> "操作 0x%02X".format(action)
    }

    private fun decodeNearbyInfo(data: ByteArray): List<Field> {
        if (data.isEmpty()) return listOf(Field("附近信息", "Apple 设备使用状态。"))
        val status = data[0].toInt() and 0xFF
        val action = status and 0x0F
        val flagsHi = (status shr 4) and 0x0F
        val dataFlags = if (data.size > 1) data[1].toInt() and 0xFF else 0
        val activity = when (action) {
            0x00 -> "活动未知"
            0x01 -> "活动报告已关闭"
            0x03 -> "空闲（屏幕已锁定）"
            0x05 -> "正在播放音频，屏幕已锁定"
            0x07 -> "正在使用（屏幕亮起）"
            0x09 -> "屏幕亮起，正在播放视频"
            0x0A -> "手表已佩戴且解锁"
            0x0B -> "最近有交互"
            0x0D -> "用户正在驾驶"
            0x0E -> "电话或 FaceTime 通话"
            else -> "活动 0x%X".format(action)
        }
        val extras = buildList {
            if (flagsHi and 0x1 != 0) add("主要 iCloud 设备")
            if (flagsHi and 0x4 != 0) add("隔空投送接收已开启")
            if (dataFlags and 0x04 != 0) add("Wi-Fi 已开启")
            if (dataFlags and 0x01 != 0) add("AirPods 已连接")
            if (dataFlags and 0x20 != 0) add("手表已锁定")
        }
        return listOf(
            Field(
                "Apple 设备当前活动",
                buildString {
                    append(activity.replaceFirstChar { it.uppercase() })
                    if (extras.isNotEmpty()) {
                        append(". ")
                        append(extras.joinToString("; "))
                    }
                    append(".")
                },
            ),
        )
    }

    private fun nearbyInfoReason(data: ByteArray): String {
        if (data.isEmpty()) return "附近信息广播。"
        val action = data[0].toInt() and 0x0F
        return when (action) {
            0x03 -> "手机处于空闲或锁定状态。"
            0x05 -> "屏幕锁定时正在播放音频。"
            0x07 -> "屏幕亮起，有人正在使用。"
            0x0D -> "设备报告用户正在驾驶。"
            0x0E -> "正在进行电话或 FaceTime 通话。"
            else -> "附近信息广播。"
        }
    }

    private fun decodeFindMy(data: ByteArray): List<Field> {
        if (data.isEmpty()) return listOf(Field("Find My", "离线查找广播。"))
        val status = data[0].toInt() and 0xFF
        val maintained = status and 0x04 != 0
        val batt = (status shr 6) and 0x3
        val battName = when (batt) {
            0 -> "充足"
            1 -> "中等"
            2 -> "偏低"
            else -> "极低"
        }
        val keyLen = (data.size - 1).coerceAtLeast(0)
        return listOf(
            Field(
                "查找 / 离线查找",
                buildString {
                    append("正在广播公钥，以便“查找”网络报告位置。")
                    append("用于 AirTag、“查找”配件以及定位自身的 Apple 设备。")
                    if (maintained) append("最近检测到主人。")
                    else append("当前密钥时间窗口内未检测到主人。")
                    if (maintained || batt in 0..3) append("电量：$battName。")
                    append("（$keyLen 字节的密钥片段，并非序列号。）")
                },
            ),
        )
    }

    private fun decodeFastPair(bytes: ByteArray): List<Field> {
        if (bytes.size == 3) {
            val id = modelId24(bytes)
            val name = FastPairModels.name(id)
            return listOf(
                Field("Google Fast Pair", "处于配对模式，Android 会弹出点按配对卡片。"),
                Field(
                    "型号 ID",
                    if (name != null) "$name  (0x%06X)".format(id) else "0x%06X（本地名称表未收录）".format(id),
                ),
            )
        }
        if (bytes.isEmpty()) return emptyList()
        val verFlags = bytes[0].toInt() and 0xFF
        val version = (verFlags shr 4) and 0x0F
        val ui = if (bytes.size > 1) {
            val lt = bytes[1].toInt() and 0xFF
            val type = lt and 0x0F
            when (type) {
                0x0 -> "请求显示配对卡片"
                0x2 -> "隐藏配对卡片（例如耳机放回盒中）"
                else -> "筛选类型 $type"
            }
        } else "账户密钥布隆过滤器"
        return listOf(
            Field(
                "Google Fast Pair",
                "已与账户配对（未处于配对模式）。$ui。版本 $version。",
            ),
        )
    }

    private fun decodeEddystone(bytes: ByteArray): List<Field> {
        if (bytes.isEmpty()) return emptyList()
        return when (bytes[0].toInt() and 0xFF) {
            0x00 -> {
                if (bytes.size < 18) listOf(Field("Eddystone-UID", "数据不完整"))
                else listOf(
                    Field("Eddystone-UID 命名空间", bytes.copyOfRange(2, 12).toHexUpper()),
                    Field("Eddystone-UID 实例", bytes.copyOfRange(12, 18).toHexUpper()),
                )
            }
            0x10 -> listOf(Field("Eddystone-URL", eddystoneUrl(bytes) ?: "${bytes.size} 字节"))
            0x20 -> listOf(Field("Eddystone-TLM", "遥测（电量 / 温度 / 广播次数）"))
            0x30 -> listOf(Field("Eddystone-EID", "临时 ID（轮换）"))
            0x40, 0x41 -> {
                val mode = if (bytes[0].toInt() and 0xFF == 0x41) "分离（防非自愿追踪模式）" else "附近 / 靠近主人"
                val eidLen = when {
                    bytes.size >= 33 -> 32
                    bytes.size >= 21 -> 20
                    else -> (bytes.size - 1).coerceAtLeast(0)
                }
                val eid = if (eidLen > 0) bytes.copyOfRange(1, 1 + eidLen).toHexUpper() else ""
                listOf(
                    Field("Find Hub", mode),
                    Field("Find Hub EID", eid.ifBlank { "${bytes.size} 字节" }),
                )
            }
            else -> listOf(Field("Eddystone", "帧 0x%02X".format(bytes[0])))
        }
    }

    private fun eddystoneUrl(bytes: ByteArray): String? {
        if (bytes.size < 3) return null
        val scheme = when (bytes[2].toInt() and 0xFF) {
            0 -> "http://www."
            1 -> "https://www."
            2 -> "http://"
            3 -> "https://"
            else -> return null
        }
        val expansions = arrayOf(
            ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",
            ".com", ".org", ".edu", ".net", ".info", ".biz", ".gov",
        )
        val sb = StringBuilder(scheme)
        for (i in 3 until bytes.size) {
            val b = bytes[i].toInt() and 0xFF
            if (b < expansions.size) sb.append(expansions[b]) else if (b in 0x20..0x7E) sb.append(b.toChar())
        }
        return sb.toString()
    }

    private fun decodeMicrosoft(bytes: ByteArray): List<Field> {
        if (bytes.isEmpty()) return emptyList()
        if (bytes[0] == 0x01.toByte() && bytes.size >= 2) {
            val type = bytes[1].toInt() and 0x1F
            val kind = when (type) {
                1 -> "Xbox"
                6 -> "iPhone"
                7 -> "iPad"
                8 -> "Android"
                9 -> "Windows 台式电脑"
                11 -> "Windows 手机"
                12 -> "Linux"
                13 -> "Windows IoT"
                14 -> "Surface Hub"
                15 -> "Windows 笔记本电脑"
                16 -> "Windows 平板电脑"
                else -> "类型 $type"
            }
            return listOf(Field("Microsoft 附近共享 / 快速配对", "一台 $kind 正在广播，以便快速配对或共享。"))
        }
        return listOf(Field("Microsoft 厂商数据", "${bytes.size} 字节"))
    }

    private fun decodeAltBeacon(bytes: ByteArray): List<Field> {
        if (bytes.size >= 22 && bytes[0] == 0xBE.toByte() && bytes[1] == 0xAC.toByte()) {
            return listOf(
                Field("AltBeacon UUID", uuidFromBe(bytes, 2)),
                Field("AltBeacon 主编号 / 次编号", "${u16be(bytes, 18)} / ${u16be(bytes, 20)}"),
            )
        }
        return emptyList()
    }

    private fun modelId24(bytes: ByteArray): Int =
        ((bytes[0].toInt() and 0xFF) shl 16) or
            ((bytes[1].toInt() and 0xFF) shl 8) or
            (bytes[2].toInt() and 0xFF)

    private fun u16be(data: ByteArray, offset: Int): Int =
        ((data[offset].toInt() and 0xFF) shl 8) or (data[offset + 1].toInt() and 0xFF)

    private fun uuidFromBe(data: ByteArray, offset: Int): String {
        fun h(i: Int) = "%02x".format(data[offset + i].toInt() and 0xFF)
        return "${h(0)}${h(1)}${h(2)}${h(3)}-${h(4)}${h(5)}-${h(6)}${h(7)}-${h(8)}${h(9)}-${h(10)}${h(11)}${h(12)}${h(13)}${h(14)}${h(15)}"
    }

    private fun uuid16(uuid: String): Int? {
        val hex = uuid.filter { it.isLetterOrDigit() }.uppercase()
        return when {
            hex.length == 4 -> hex.toIntOrNull(16)
            hex.length == 32 && hex.startsWith("0000") && hex.endsWith("00001000800000805F9B34FB") ->
                hex.substring(4, 8).toIntOrNull(16)
            else -> null
        }
    }

    private fun hexToBytes(hex: String): ByteArray? {
        val h = hex.filter { it.isLetterOrDigit() }
        if (h.isEmpty() || h.length % 2 != 0) return null
        return ByteArray(h.length / 2) { i ->
            h.substring(i * 2, i * 2 + 2).toInt(16).toByte()
        }
    }
}
