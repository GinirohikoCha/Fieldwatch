package app.fieldwatch.domain

import java.util.UUID

object DefaultCatalog {
    /**
     * Tesla phone-as-key uses Apple iBeacon layout (0x004C type 0x02 length 0x15)
     * so iOS can find the car in the background. That is the Tesla row, not iBeacon.
     */
    const val TESLA_IBEACON_MFG_PREFIX = "021574278BDAB64445208F0C720EAF059935"

    /**
     * Target Atrius basket tags advertise Apple iBeacon layout (0x004C type 0x02
     * length 0x15) with this UUID, plus service 0xB1BB. Not Acuity company 0x0346
     * on the hundreds of basket radios (two Florida stores, 2026-09-02).
     */
    const val TARGET_ATRIUS_IBEACON_MFG_PREFIX = "02155993A94C7D974DF79ABFE493BFD5D000"

    /**
     * DJI company 0x08AA manufacturer-data model id (u16 LE). Osmo cameras sit
     * in 0x0006–0x0022. Aircraft (Mavic 3 0x0070, Neo 2 0x007e, …) do not.
     * Do not put bare mfg(0x08AA) on the Osmo row — that is every DJI radio.
     */
    val OSMO_CAMERA_MFG_PREFIXES = listOf(
        "0600", // Osmo Action 1
        "1000", // Osmo Action 2
        "1200", // Osmo Action 3
        "1400", // Osmo Action 4
        "1500", // Osmo Action 5 Pro / Xtra Edge Pro
        "1700", // Osmo 360
        "1800", // Osmo Action 6
        "1900", // Osmo Nano
        "2000", // Osmo Pocket 3
        "2100", // Osmo Pocket 4
        "2200", // Osmo Pocket 4 Pro
    )

    /**
     * Stock palette slots by device class. Same index as [Palette.fleet].
     * Operators can still change any row in the editor.
     */
    private object Hue {
        const val MESH = 0          // phosphor green — LoRa / community mesh
        const val SURVEILLANCE = 1  // amber — ALPR / Flock-family / municipal cameras
        const val DRONE = 1         // same amber; class (not color) splits poles vs aircraft
        const val HACKING = 2       // red — pentest kit and cheap UART overlays
        const val TRACKER = 3       // cyan — SmartTag / Tile / Pebblebee
        const val FIND_MY = 4       // purple — Apple/Google phones and Find My tags
        const val GLASSES = 5       // orange — smart glasses
        const val AUDIO = 5         // same orange; class splits glasses vs headphones / speakers
        const val CAMERA = 6        // silver — consumer / action cameras (not poles)
        const val HOME_CAM = 6      // silver — PCs / home IoT / retail signage
        const val LAW = 7           // teal — public safety / vehicle (class splits them)
        const val VEHICLE = 7       // same teal; class (not color) splits LE vs civilian vehicle
        const val HEALTH = 8        // clinical blue — scanners, BP, scales, CGM
    }

    /**
     * Bookmark these on first launch / Restore so they beep (and speak, with Voice on).
     * Extra attention rows: body-cam / public-safety APs, camera glasses,
     * recording wearables, pentest kit, and roadside / public camera + ALPR.
     * Plus every built-in Drone-class row. Not Tesla, not headphones, not
     * UniFi Protect, not BlueTOAD Spectra, not BlipTrack, not access-control locks.
     */
    fun defaultWatchlist(): List<WatchTarget> =
        fleets()
            .filter { it.builtIn && (it.attentionNote.isNotBlank() || it.kind == SignatureClass.DRONE) }
            .sortedBy { it.name.lowercase() }
            .map { fleet ->
                WatchTarget(id = "watch-${fleet.id}", fleetId = fleet.id, label = fleet.name)
            }

    fun fleets(): List<Fleet> = listOf(
        flockCameras(),
        liteOnCameraRadio(),
        ravenAcoustic(),
        airTags(),
        smartTags(),
        tileTrackers(),
        ibeacon(),
        targetAtriusBasket(),
        minew(),
        estimote(),
        kontakt(),
        penguin(),
        dultTracker(),
        pigvision(),
        fsExtBattery(),
        appleDevice(),
        appleAudio(),
        microsoftDevice(),
        tesla(),
        teslaTstpms(),
        ford(),
        hondaMotor(),
        hyundaiMotor(),
        toyota(),
        nissanMotor(),
        subaru(),
        bmw(),
        volkswagen(),
        porsche(),
        jaguarLandRover(),
        bydAuto(),
        googleDevice(),
        fastPair(),
        sony(),
        bose(),
        garmin(),
        amazon(),
        fitbit(),
        oura(),
        logitech(),
        jblHarman(),
        sonos(),
        gopro(),
        osmo(),
        insta360(),
        dji(),
        remoteId(),
        skydio(),
        autel(),
        parrot(),
        hoverAir(),
        netgear(),
        tpLink(),
        asus(),
        linksys(),
        eero(),
        googleWifi(),
        huawei(),
        plume(),
        phoneHotspot(),
        dlink(),
        dwnet(),
        belkin(),
        xfinity(),
        spectrum(),
        attWifi(),
        verizon(),
        starlink(),
        meraki(),
        cisco(),
        aruba(),
        ruckus(),
        ruijie(),
        fortinet(),
        mikrotik(),
        engenius(),
        zyxel(),
        peplink(),
        openwrt(),
        arris(),
        mist(),
        tMobile(),
        humax(),
        sagemcom(),
        arcadyan(),
        askey(),
        calix(),
        nokiaNsn(),
        airties(),
        tenda(),
        wavlink(),
        sercomm(),
        luxul(),
        sophos(),
        aumovio(),
        centuryLink(),
        gmHotspot(),
        audiMmi(),
        extremeNetworks(),
        adtran(),
        cambium(),
        trendnet(),
        cudy(),
        snapAv(),
        vantiva(),
        hitron(),
        actiontec(),
        buffalo(),
        grandstream(),
        edgecore(),
        watchGuard(),
        mojo(),
        winegard(),
        inseego(),
        franklin(),
        synology(),
        glInet(),
        chipolo(),
        pebblebee(),
        findHub(),
        verkada(),
        vigilant(),
        eufy(),
        wyze(),
        ring(),
        arlo(),
        nest(),
        nestThermostat(),
        nestWeave(),
        ecobee(),
        sensi(),
        honeywellHome(),
        haiku(),
        tuya(),
        seos(),
        augustLock(),
        schlage(),
        nuki(),
        salto(),
        dormakaba(),
        lockly(),
        kevo(),
        masterLock(),
        igloohome(),
        tedee(),
        paxton(),
        kwikset(),
        myq(),
        chevroletHotspot(),
        uconnect(),
        carPlay(),
        carlink(),
        rivian(),
        goodyearTpms(),
        schraderTpms(),
        pacificTpms(),
        hufTpms(),
        foboTpms(),
        aftermarketTpms(),
        sytpms(),
        tireCheck(),
        tpmsService(),
        ruuvi(),
        blueMaestro(),
        sensorPush(),
        samsara(),
        govee(),
        hpPrinter(),
        epson(),
        lgWebosTv(),
        roku(),
        nespresso(),
        radiacode(),
        shokz(),
        mercedesMbux(),
        motive(),
        peopleNet(),
        cradlepoint(),
        airlink(),
        compex(),
        novatelWireless(),
        utilityInc(),
        tapo(),
        reolink(),
        hikvision(),
        dahua(),
        meshtastic(),
        helium(),
        meshCore(),
        goTenna(),
        senseCap(),
        rakWisGate(),
        genetec(),
        blueToadSpectra(),
        blipTrack(),
        hanwhaWisenet(),
        uniview(),
        rhombus(),
        rekor(),
        axon(),
        watchGuardVideo(),
        digitalAlly(),
        revealMedia(),
        wolfcom(),
        panasonicIpro(),
        avigilon(),
        axis(),
        haydenAi(),
        miovision(),
        tattile(),
        liveViewLvt(),
        unifi(),
        unifiAp(),
        unifiProtect(),
        hobbyBleSerial(),
        metaGlasses(),
        snapSpectacles(),
        vuzix(),
        brilliantFrame(),
        evenG1(),
        hak5Pineapple(),
        flipperZero(),
        pwnagotchi(),
        marauderDeauther(),
        ghostEsp(),
        bruceFirmware(),
        porkchop(),
        pokemonGoPlus(),
        hatch(),
        bhyve(),
        samsungAppliance(),
        ecoWater(),
        fieldy(),
        plaud(),
        limitlessPendant(),
        beePendant(),
        omiPendant(),
        friendPendant(),
        retailLedSign(),
        electronicShelfLabel(),
        honeywellXenonHc(),
        omronHealthcare(),
        withings(),
        dexcom(),
    ).sortedBy { it.name.lowercase() }

    private fun flockCameras() = Fleet(
        id = "fleet-flock-cameras",
        name = "Flock Safety Cameras",
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Flock 系列路边车牌自动识别（ALPR）设备或摄像杆。依据 IEEE B4:1E:52 或 Flock-* / FLCK / Condor / Falcon / Sparrow 名称匹配。当前型号通常不发出 Wi-Fi 或 BLE 广播。LiteOn 模块前缀单独列出，不属于重点关注。",
        attentionNote = "Flock 系列路边车牌自动识别（ALPR）设备或摄像杆，可读取车牌并用于定位车辆。IEEE B4:1E:52 或 Flock-* SSID 是较强的匹配依据。当前型号通常不发出 Wi-Fi 或 BLE 广播。这里只是模式匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            oui("B4:1E:52"),
            name("Flock"),
            name("FLCK"),
            glob("Flock-*"),
            glob("Flock-??????"),
            name("CONDOR"),
            name("FALCON"),
            name("SPARROW"),
        ),
    )

    /** Component-vendor prefixes seen on camera boards, including some Flock poles. Not Flock's IEEE block. */
    private fun liteOnCameraRadio() = Fleet(
        id = "fleet-liteon-camera-radio",
        name = "LiteOn camera radio",
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "摄像头主板常见的 Wi-Fi 模块前缀（LiteOn 等），并非 Flock 的 IEEE 地址段。门铃及其他厂商设备也使用这些芯片。Flock 名称或 B4:1E:52 归入 Flock Safety Cameras。",
        builtIn = true,
        rules = buildList {
            listOf(
                "70:C9:4E", "3C:91:80", "D8:F3:BC", "80:30:49", "B8:35:32",
                "14:5A:FC", "74:4C:A1", "08:3A:88", "9C:2F:9D", "C0:35:32",
                "94:08:53", "E4:AA:EA", "F4:6A:DD", "F8:A2:D6", "24:B2:B9",
                "00:F4:8D", "D0:39:57", "E8:D0:FC", "B8:1E:A4",
                "70:08:94", "58:00:E3", "5C:93:A2", "64:6E:69",
                "48:27:EA", "82:6B:F2",
            ).forEach { add(oui(it)) }
            add(vendorIe("00:80:19"))
            add(vendorIe("00:0A:EB"))
        },
    )

    private fun ravenAcoustic() = Fleet(
        id = "fleet-raven",
        name = "Raven / ShotSpotter",
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Flock Raven 或 ShotSpotter 系列枪声声学传感器，通常与摄像头安装在同一根杆上。BLE UUID 3100–3500 对应 Raven 无线模块。XUNTONG 电池厂商 ID 归入 Penguin，不属于此项。当前 Flock 系列杆装设备通常不发出 Wi-Fi 或 BLE 广播。",
        builtIn = true,
        rules = listOf(
            name("RAVEN"),
            name("ShotSpotter"),
            name("SoundThinking"),
            name("Shot Spotter"),
            uuid("3100"),
            uuid("3200"),
            uuid("3300"),
            uuid("3400"),
            uuid("3500"),
            oui("D4:11:D6"),
        ),
    )

    private fun airTags() = Fleet(
        id = "fleet-airtag",
        name = "Apple AirTags",
        colorIndex = Hue.FIND_MY,
        kind = SignatureClass.FINDER,
        matchAny = true,
        notes = "Apple AirTag 或“查找”配件。iPhone 也会发送“查找”广播以定位自身；除非名称为 AirTag，否则归入 Apple Device。地址会轮换。",
        builtIn = true,
        rules = listOf(
            name("AirTag"),
            name("Find My"),
            mfgData(0x004C, "12"),
            uuid("FD44"),
        ),
    )

    private fun smartTags() = Fleet(
        id = "fleet-smarttag",
        name = "Samsung SmartTags",
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.FINDER,
        matchAny = true,
        notes = "Samsung SmartTag / SmartTag+ 寻物标签。地址通常会轮换。",
        builtIn = true,
        rules = listOf(
            name("SmartTag"),
            name("Smart Tag"),
            name("Galaxy SmartTag"),
            uuid("FD5A"),
            mfg(0x0075),
        ),
    )

    private fun ibeacon() = Fleet(
        id = "fleet-ibeacon",
        name = "iBeacon",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.BEACON,
        matchAny = true,
        notes = "通用近距离信标。商店、购物篮、电视和汽车都可能发送这种 Apple 格式的广播。在密集商场中可关闭其提醒。",
        builtIn = true,
        rules = listOf(
            mfgData(0x004C, "0215"),
            bleName("iBeacon"),
            bleGlob("*iBeacon*"),
        ),
    )

    private fun targetAtriusBasket() = Fleet(
        id = "fleet-target-atrius",
        name = "Target Atrius basket",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.BEACON,
        matchAny = true,
        notes = "Target 购物篮标签。可能同时匹配通用 iBeacon；此项专指商店购物篮。",
        builtIn = true,
        rules = listOf(
            mfgData(0x004C, TARGET_ATRIUS_IBEACON_MFG_PREFIX),
            uuid("B1BB"),
        ),
    )

    private fun minew() = Fleet(
        id = "fleet-minew",
        name = "Minew",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.BEACON,
        matchAny = true,
        notes = "Minew 定位或资产信标。同一无线设备往往还发送 iBeacon 或 Eddystone 广播。",
        builtIn = true,
        rules = listOf(
            oui("AC:23:3F"),
            bleName("Minew"),
            bleGlob("Minew*"),
        ),
    )

    private fun estimote() = Fleet(
        id = "fleet-estimote",
        name = "Estimote",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.BEACON,
        matchAny = true,
        notes = "商店或场馆使用的定位信标或贴片。解码字段可区分 Nearable 和遥测帧。",
        builtIn = true,
        decode = CatalogDecodes.estimote,
        rules = listOf(
            mfg(0x015D),
            bleName("Estimote"),
            bleGlob("Estimote*"),
        ),
    )

    private fun kontakt() = Fleet(
        id = "fleet-kontakt",
        name = "Kontakt.io",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.BEACON,
        matchAny = true,
        notes = "商店或场馆使用的定位信标。解码字段可显示电量、发射功率和移动状态。",
        builtIn = true,
        decode = CatalogDecodes.kontakt,
        rules = listOf(
            mfg(0x01FD),
            bleName("Kontakt"),
            bleGlob("Kontakt*"),
        ),
    )

    private fun tileTrackers() = Fleet(
        id = "fleet-tile",
        name = "Tile Trackers",
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.FINDER,
        matchAny = true,
        notes = "Tile 寻物标签。解码字段可能显示轮换的私有 ID，该 ID 不是序列号。",
        builtIn = true,
        decode = CatalogDecodes.tile,
        rules = listOf(
            name("Tile"),
            uuid("FEED"),
            uuid("FEDD"),
            mfg(0x00C7),
        ),
    )

    private fun penguin() = Fleet(
        id = "fleet-penguin",
        name = "Penguin",
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Penguin 是 Flock 系列外置电池。通常依据 XUNTONG BLE 厂商 ID 识别；Penguin* 名称来自旧版固件。较新电池组常广播 10 位数字名称。如果厂商数据包含 TN 序列号，解码字段会显示它。",
        attentionNote = "Penguin 是 Flock 系列外置电池（XUNTONG 厂商 ID）。名称匹配对应旧固件，独特性较低。这里只是模式匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        decode = CatalogDecodes.penguin,
        rules = listOf(
            name("Penguin"),
            name("PENGUIN"),
            glob("Penguin*"),
            mfg(0x09C8),
        ),
    )

    private fun pigvision() = Fleet(
        id = "fleet-pigvision",
        name = "Pigvision",
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Pigvision 是 Flock 系列或路边摄像头使用的名称。",
        attentionNote = "Pigvision 是 Flock 系列或路边摄像头使用的名称。仅按名称匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Pigvision"),
            name("PigVision"),
            name("PIGVISION"),
            glob("Pigvision*"),
        ),
    )

    private fun fsExtBattery() = Fleet(
        id = "fleet-fs-ext-battery",
        name = "FS Ext Battery",
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "通常与 Flock 系列摄像杆配套的外置电池组。名称匹配的依据较强。当前杆装设备通常不发出 Wi-Fi 或 BLE 广播。",
        attentionNote = "通常与 Flock 系列摄像头配套，作为杆上的外置电池组。名称匹配的依据较强。当前杆装设备通常不发出 Wi-Fi 或 BLE 广播。这里只是模式匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = buildList {
            add(name("FS Ext Battery"))
            add(glob("FS_*"))
            add(glob("FS Ext*"))
            listOf(
                "04:0D:84", "1C:34:F1", "38:5B:44", "94:34:69",
                "B4:E3:F9", "F0:82:C0",
            ).forEach { add(oui(it)) }
        },
    )

    private fun appleDevice() = Fleet(
        id = "fleet-apple-device",
        name = "Apple Device",
        enabled = true,
        colorIndex = Hue.FIND_MY,
        kind = SignatureClass.PHONE,
        matchAny = true,
        notes = "发送连续互通广播（Nearby、接力、隔空投送、即时热点）的 iPhone、iPad 或 Mac。此设备上的“查找”广播用于定位手机自身，不代表另一个 AirTag。此项不包括 AirPods。",
        builtIn = true,
        rules = listOf(
            mfgData(0x004C, "10"),
            mfgData(0x004C, "0F"),
            mfgData(0x004C, "0B"),
            mfgData(0x004C, "05"),
            mfgData(0x004C, "0C"),
            mfgData(0x004C, "0D"),
            mfgData(0x004C, "0E"),
            mfgData(0x004C, "08"),
            mfgData(0x004C, "0A"),
            name("iPhone"),
            name("iPad"),
            name("MacBook"),
        ),
    )

    private fun appleAudio() = Fleet(
        id = "fleet-apple-audio",
        name = "Apple audio",
        enabled = true,
        colorIndex = Hue.AUDIO,
        kind = SignatureClass.AUDIO,
        matchAny = true,
        notes = "AirPods、Beats，或发送 AirPlay 广播的 Apple TV / 音箱。并非 AirTag，也不是 iPhone 本身。",
        builtIn = true,
        rules = listOf(
            mfgData(0x004C, "07"),
            mfgData(0x004C, "09"),
            bleName("AirPods"),
            bleName("Beats"),
        ),
    )

    private fun microsoftDevice() = Fleet(
        id = "fleet-microsoft",
        name = "Microsoft Device",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.PHONE,
        matchAny = true,
        notes = "发送快速配对或附近共享广播的 Windows 电脑、Surface 或 Xbox。",
        builtIn = true,
        rules = listOf(
            mfg(0x0006),
            bleName("Surface"),
            bleName("Xbox"),
        ),
    )

    private fun tesla() = Fleet(
        id = "fleet-tesla",
        name = "Tesla",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Tesla 手机钥匙、车辆、Wall Connector 或 TeslaGW Wi-Fi。iOS 还会收到车辆发送的 iBeacon 格式广播，仍归入 Tesla，而非商场信标。轮胎传感器单独归入 tsTPMS。",
        builtIn = true,
        rules = listOf(
            mfg(0x022B),
            uuid("FE96"),
            uuid("FE97"),
            mfgData(0x004C, TESLA_IBEACON_MFG_PREFIX),
            bleName("Tesla"),
            bleName("Cybertruck"),
            bleGlob("S????????????????C"),
            bleGlob("S????????????????D"),
            bleGlob("S????????????????P"),
            bleGlob("S????????????????R"),
            wifiGlob("TeslaGW*"),
            wifiGlob("tesla-vehicle"),
            wifiGlob("TeslaWallConnector*"),
            wifiGlob("Cybertruck*"),
        ),
    )

    private fun ford() = oemVehicle(
        id = "fleet-ford",
        name = "Ford",
        notes = "Ford 或 Lincoln 手机钥匙 / 车载信息娱乐系统。不匹配经销商的 Wi-Fi 名称。",
        rules = listOf(
            mfg(0x0723),
            bleName("Ford"),
            bleName("Lincoln"),
        ),
    )

    private fun hondaMotor() = oemVehicle(
        id = "fleet-honda",
        name = "Honda",
        notes = "Honda 或 Acura 手机钥匙 / 车载信息娱乐系统。",
        rules = listOf(
            mfg(0x0915),
            bleName("Honda"),
            bleName("Acura"),
        ),
    )

    private fun hyundaiMotor() = oemVehicle(
        id = "fleet-hyundai",
        name = "Hyundai",
        notes = "Hyundai 或 Genesis 手机钥匙 / 车载信息娱乐系统。不匹配经销商的 Wi-Fi 名称。",
        rules = listOf(
            mfg(0x0826),
            bleName("Hyundai"),
            bleName("Genesis"),
        ),
    )

    private fun toyota() = oemVehicle(
        id = "fleet-toyota",
        name = "Toyota",
        notes = "Toyota 或 Lexus 手机钥匙，或使用出厂 TOYOTA / LEXUS 名称的热点。",
        rules = listOf(
            mfg(0x0977),
            bleName("Toyota"),
            bleName("Lexus"),
            wifiGlob("TOYOTA*"),
            wifiGlob("LEXUS*"),
        ),
    )

    private fun nissanMotor() = oemVehicle(
        id = "fleet-nissan",
        name = "Nissan",
        notes = "Nissan 或 Infiniti 手机钥匙 / 车载信息娱乐系统。",
        rules = listOf(
            mfg(0x0BA6),
            bleName("Nissan"),
            bleName("Infiniti"),
        ),
    )

    private fun subaru() = oemVehicle(
        id = "fleet-subaru",
        name = "Subaru",
        notes = "Subaru 手机钥匙 / 车载信息娱乐系统。与 Starlink 卫星互联网无关。",
        rules = listOf(
            mfg(0x0A10),
            bleName("Subaru"),
        ),
    )

    private fun bmw() = oemVehicle(
        id = "fleet-bmw",
        name = "BMW",
        notes = "BMW 手机钥匙或车载热点。出厂 BMW_ Wi-Fi 名称来自车辆，而非经销商展厅。",
        rules = listOf(
            mfg(0x05EB),
            bleName("BMW"),
            wifiGlob("BMW_*"),
        ),
    )

    private fun volkswagen() = oemVehicle(
        id = "fleet-volkswagen",
        name = "Volkswagen",
        notes = "Volkswagen 手机钥匙或 My VW 热点。Skoda、SEAT 和 Porsche 分别列出。",
        rules = listOf(
            mfg(0x011F),
            uuid("FE30"),
            uuid("FE31"),
            bleName("Volkswagen"),
            bleName("VW"),
            wifiGlob("My VW*"),
        ),
    )

    private fun porsche() = oemVehicle(
        id = "fleet-porsche",
        name = "Porsche",
        notes = "Porsche 手机钥匙或使用出厂 Porsche_WLAN 名称的热点。与 Volkswagen 分开列出。",
        rules = listOf(
            mfg(0x0120),
            bleName("Porsche"),
            wifiGlob("Porsche_WLAN*"),
        ),
    )

    private fun jaguarLandRover() = oemVehicle(
        id = "fleet-jlr",
        name = "Jaguar Land Rover",
        notes = "Jaguar、Land Rover 或 Range Rover 手机钥匙 / 车载信息娱乐系统。",
        rules = listOf(
            mfg(0x020B),
            bleName("Jaguar"),
            bleName("Land Rover"),
            bleName("Range Rover"),
        ),
    )

    private fun bydAuto() = oemVehicle(
        id = "fleet-byd",
        name = "BYD",
        notes = "BYD 手机钥匙或车辆 BLE。这里只是模式匹配，无法确定具体车型。",
        rules = listOf(
            mfg(0x0C34),
            bleName("BYD"),
        ),
    )

    private fun oemVehicle(
        id: String,
        name: String,
        notes: String,
        rules: List<MatchRule>,
    ) = Fleet(
        id = id,
        name = name,
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = notes,
        builtIn = true,
        rules = rules,
    )

    private fun googleDevice() = Fleet(
        id = "fleet-google",
        name = "Google",
        enabled = true,
        colorIndex = Hue.FIND_MY,
        kind = SignatureClass.PHONE,
        matchAny = true,
        notes = "Pixel 手机或 Chromecast。Fast Pair 配件归入 Fast Pair。",
        builtIn = true,
        rules = listOf(
            mfg(0x00E0),
            bleName("Pixel"),
            bleName("Chromecast"),
            bleName("Google Pixel"),
        ),
    )

    private fun fastPair() = Fleet(
        id = "fleet-fast-pair",
        name = "Fast Pair",
        enabled = true,
        colorIndex = Hue.FIND_MY,
        kind = SignatureClass.PHONE,
        matchAny = true,
        notes = "发送 Fast Pair 广播的 Android 配件（耳机、手表、手机）。配对模式用于点按配对；较长广播通常是周围已配对设备的背景信号，不能代表某个人。可在筛选中隐藏这些背景标签。",
        builtIn = true,
        rules = listOf(
            uuid("FE2C"),
        ),
    )

    private fun sony() = Fleet(
        id = "fleet-sony",
        name = "Sony",
        enabled = true,
        colorIndex = Hue.AUDIO,
        kind = SignatureClass.AUDIO,
        matchAny = true,
        notes = "Sony 耳机、电视或相机。Bravia 电视还会为投屏发送通用 iBeacon 广播，Fieldwatch 仍将其归入 Sony。",
        builtIn = true,
        rules = listOf(
            mfg(0x012D),
            bleName("Sony"),
            bleName("WH-1000"),
            bleName("WF-1000"),
        ),
    )

    private fun bose() = Fleet(
        id = "fleet-bose",
        name = "Bose",
        enabled = true,
        colorIndex = Hue.AUDIO,
        kind = SignatureClass.AUDIO,
        matchAny = true,
        notes = "Bose 耳机或音箱。Quiet Charge / QC 耳机即使放在盒内也会广播。",
        builtIn = true,
        rules = listOf(
            mfg(0x009E),
            uuid("FE21"),
            uuid("FEBE"),
            bleName("Bose"),
        ),
    )

    private fun garmin() = Fleet(
        id = "fleet-garmin",
        name = "Garmin",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.WEARABLE,
        matchAny = true,
        notes = "Garmin 手表、自行车码表或 inReach 卫星通信器。",
        builtIn = true,
        rules = listOf(
            mfg(0x0087),
            uuid("FE1F"),
            bleName("Garmin"),
        ),
    )

    private fun amazon() = Fleet(
        id = "fleet-amazon",
        name = "Amazon",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "发送广播的 Amazon Echo、Fire 或 Kindle，并不涵盖所有 AmazonBasics 设备。",
        builtIn = true,
        rules = listOf(
            mfg(0x0171),
            bleName("Echo"),
            bleName("Amazon"),
            bleName("Fire TV"),
        ),
    )

    private fun fitbit() = Fleet(
        id = "fleet-fitbit",
        name = "Fitbit",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.WEARABLE,
        matchAny = true,
        notes = "Fitbit 手表或健身追踪器。广播仅用于身份识别，不包含步数。",
        builtIn = true,
        rules = listOf(
            mfg(0x018E),
            uuid("FD62"),
            uuid("FD63"),
            bleName("Fitbit"),
        ),
    )

    private fun oura() = Fleet(
        id = "fleet-oura",
        name = "Oura",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.WEARABLE,
        matchAny = true,
        notes = "Oura 健康戒指。佩戴时持续发送 BLE 广播。这里只是模式匹配，不能确定佩戴者。",
        builtIn = true,
        rules = listOf(
            mfg(0x02B2),
            bleName("Oura"),
        ),
    )

    private fun logitech() = Fleet(
        id = "fleet-logitech",
        name = "Logitech",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Logitech 鼠标、键盘或网络摄像头，常见的办公背景信号。",
        builtIn = true,
        rules = listOf(
            mfg(0x01DA),
            uuid("FE61"),
            bleName("Logitech"),
            bleName("Logi"),
        ),
    )

    private fun jblHarman() = Fleet(
        id = "fleet-jbl",
        name = "JBL / Harman",
        enabled = true,
        colorIndex = Hue.AUDIO,
        kind = SignatureClass.AUDIO,
        matchAny = true,
        notes = "JBL、Harman Kardon 或部分车载音响的 BLE，可能是耳机、音箱或车机。",
        builtIn = true,
        rules = listOf(
            mfg(0x0057),
            bleName("JBL"),
            bleName("Harman"),
        ),
    )

    private fun sonos() = Fleet(
        id = "fleet-sonos",
        name = "Sonos",
        enabled = true,
        colorIndex = Hue.AUDIO,
        kind = SignatureClass.AUDIO,
        matchAny = true,
        notes = "Sonos 家用或办公音箱，发送设置或空闲广播，并非追踪器。",
        builtIn = true,
        rules = listOf(
            mfg(0x05A7),
            uuid("FE07"),
            bleName("Sonos"),
        ),
    )

    private fun gopro() = Fleet(
        id = "fleet-gopro",
        name = "GoPro",
        enabled = true,
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "GoPro 运动相机。解码字段可显示是否唤醒、是否处于 Wi-Fi 热点模式或正在配对。",
        builtIn = true,
        decode = CatalogDecodes.gopro,
        rules = listOf(
            uuid("FEA5"),
            uuid("FEA6"),
            bleName("GoPro"),
            bleGlob("GoPro*"),
        ),
    )

    private fun osmo() = Fleet(
        id = "fleet-osmo",
        name = "Osmo",
        enabled = true,
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "DJI Osmo 手持或运动相机（Action、Pocket、360、Nano），并非飞行中的 DJI 无人机。",
        builtIn = true,
        decode = CatalogDecodes.djiModel,
        rules = OSMO_CAMERA_MFG_PREFIXES.map { mfgData(0x08AA, it) } + listOf(
            glob("OsmoAction*"),
            glob("Osmo Action*"),
            glob("OsmoPocket*"),
            glob("Osmo Pocket*"),
            glob("Osmo360*"),
            glob("Osmo 360*"),
            glob("OsmoNano*"),
            glob("Osmo Nano*"),
            glob("XtraEdgePro*"),
            glob("Xtra Edge Pro*"),
        ),
    )

    private fun insta360() = Fleet(
        id = "fleet-insta360",
        name = "Insta360",
        enabled = true,
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "Insta360 运动或全景相机。广播名称通常为型号加序列号。属于消费级相机，而非杆装摄像头。",
        builtIn = true,
        rules = listOf(
            mfg(0x10D7),
            name("Insta360"),
            glob("Insta360*"),
            glob("X3 *"),
            glob("X4 *"),
            glob("X5 *"),
            glob("Ace Pro*"),
            glob("GO 3*"),
            glob("GO3*"),
            glob("GO Ultra*"),
            glob("ONE X*"),
            glob("ONE RS*"),
            glob("ONE R *"),
        ),
    )

    private fun dji() = Fleet(
        id = "fleet-dji",
        name = "DJI",
        enabled = true,
        colorIndex = Hue.DRONE,
        kind = SignatureClass.DRONE,
        matchAny = true,
        notes = "DJI 飞行器、遥控器或设置用 Wi-Fi。手持 Osmo 相机单独归入 Osmo；飞行中的数字标识归入 Remote ID。",
        builtIn = true,
        decode = CatalogDecodes.djiModel,
        rules = listOf(
            mfg(0x08AA),
            bleName("DJI"),
            bleGlob("DJI*"),
            wifiName("DJI"),
            wifiGlob("DJI*"),
        ),
    )

    private fun netgear() = Fleet(
        id = "fleet-netgear",
        name = "NETGEAR",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "NETGEAR 或 Orbi 家用路由器 / Mesh。即使 SSID 已改名，仍可依据主板厂商匹配。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("NETGEAR*"),
                wifiGlob("Netgear*"),
                wifiGlob("Orbi*"),
                wifiName("NETGEAR"),
            ),
            ApVendorOuis.NETGEAR,
        ),
    )

    private fun tpLink() = Fleet(
        id = "fleet-tplink",
        name = "TP-Link",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "TP-Link 或 Deco 家用路由器 / Mesh。使用 TP-Link 主板的 Tapo 摄像头也可能匹配此项。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("TP-Link*"),
                wifiGlob("TP-LINK*"),
                wifiGlob("TPLink*"),
                wifiGlob("Deco*"),
                wifiName("TP-Link"),
            ),
            ApVendorOuis.TPLINK,
        ),
    )

    private fun asus() = Fleet(
        id = "fleet-asus",
        name = "ASUS",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "ASUS 家用路由器或 Mesh。ASUS 笔记本电脑的热点也可能匹配。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("ASUS*"),
                wifiGlob("ASUS_*"),
                wifiName("ASUS"),
            ),
            ApVendorOuis.ASUS,
        ),
    )

    private fun linksys() = Fleet(
        id = "fleet-linksys",
        name = "Linksys",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Linksys 或 Velop 家用 Mesh。部分 Velop 设备使用 Belkin 主板。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Linksys*"),
                wifiGlob("linksys*"),
                wifiGlob("Velop*"),
                wifiName("Linksys"),
            ),
            ApVendorOuis.LINKSYS,
        ),
    )

    private fun eero() = Fleet(
        id = "fleet-eero",
        name = "Eero",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Amazon Eero Mesh，并非 Echo 音箱。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiName("eero"),
                wifiGlob("eero*"),
                wifiGlob("Eero*"),
            ),
            ApVendorOuis.EERO,
        ),
    )

    private fun googleWifi() = Fleet(
        id = "fleet-google-wifi",
        name = "Google Wifi",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Google Wifi / Nest Wifi Mesh，并非 Pixel 手机或 Nest 摄像头。",
        builtIn = true,
        rules = listOf(
            wifiName("Google Wifi"),
            wifiName("GoogleWifi"),
            wifiGlob("Google Wifi*"),
            wifiName("Nest Wifi"),
            wifiGlob("Nest Wifi*"),
        ),
    )

    private fun huawei() = Fleet(
        id = "fleet-huawei",
        name = "Huawei",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Huawei 家用路由器，或使用 Huawei 公共地址的手机热点。随机地址热点需要保留出厂 SSID 才能匹配。不包括 Honor。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("HUAWEI*"),
                wifiGlob("Huawei*"),
                wifiName("HUAWEI"),
                wifiName("Huawei"),
            ),
            ApVendorOuis.HUAWEI,
        ),
    )

    private fun plume() = Fleet(
        id = "fleet-plume",
        name = "Plume",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Plume SuperPod / HomePass Mesh。运营商品牌的节点（如 xFi）往往使用运营商的代工主板。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Plume*"),
                wifiName("Plume"),
                wifiGlob("SuperPod*"),
                wifiGlob("Superpod*"),
            ),
            ApVendorOuis.PLUME,
        ),
    )

    private fun phoneHotspot() = Fleet(
        id = "fleet-phone-hotspot",
        name = "Phone hotspot",
        enabled = true,
        colorIndex = Hue.FIND_MY,
        kind = SignatureClass.PHONE,
        matchAny = true,
        notes = "使用出厂名称（AndroidAP、Galaxy、Pixel）的手机个人热点。自定义名称的热点不会匹配。iPhone 热点归入 Apple Device。",
        builtIn = true,
        rules = listOf(
            wifiGlob("AndroidAP*"),
            wifiGlob("Galaxy-*"),
            wifiGlob("Galaxy *"),
            wifiGlob("Galaxy_*"),
            wifiGlob("Pixel-*"),
            wifiGlob("Pixel *"),
            wifiGlob("Pixel_*"),
        ),
    )

    private fun dlink() = Fleet(
        id = "fleet-dlink",
        name = "D-Link",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "D-Link 家用路由器。即使 SSID 已改名，仍可依据主板厂商匹配。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("D-Link*"),
                wifiGlob("DLink*"),
                wifiGlob("dlink*"),
                wifiGlob("DIR-*"),
            ),
            ApVendorOuis.DLINK,
        ),
    )

    private fun dwnet() = Fleet(
        id = "fleet-dwnet",
        name = "DWnet",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "DWnet 消费级或中小企业接入点。云管理 SSID 通常由用户命名，因此依据主板厂商匹配。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.DWNET),
    )

    private fun belkin() = Fleet(
        id = "fleet-belkin",
        name = "Belkin",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Belkin 家用路由器。部分 Linksys Velop 设备也会匹配此项。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Belkin*"),
                wifiGlob("belkin*"),
                wifiName("Belkin"),
            ),
            ApVendorOuis.BELKIN,
        ),
    )

    private fun xfinity() = Fleet(
        id = "fleet-xfinity",
        name = "Xfinity",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Comcast xfinitywifi 热点，或使用 Xfinity / XFSETUP 名称的网关。多数设备由 Arris / Hitron / Technicolor 代工，也会匹配相应厂商条目。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiName("xfinitywifi"),
                wifiGlob("xfinitywifi*"),
                wifiGlob("XFSETUP*"),
                wifiGlob("Xfinity*"),
                wifiGlob("XFINITY*"),
            ),
            ApVendorOuis.COMCAST,
        ),
    )

    private fun spectrum() = Fleet(
        id = "fleet-spectrum",
        name = "Spectrum",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Charter Spectrum 设置网络或 Wi-Fi 热点。设备通常由 Arris / Hitron / Technicolor 代工。",
        builtIn = true,
        rules = listOf(
            wifiGlob("SpectrumSetup*"),
            wifiGlob("MySpectrumWiFi*"),
            wifiName("SpectrumWiFi"),
            wifiGlob("SpectrumWiFi*"),
            wifiName("Spectrum Mobile"),
            wifiGlob("Spectrum Mobile*"),
            wifiName("Spectrum Free Trial"),
            wifiGlob("Spectrum Free Trial*"),
        ),
    )

    private fun attWifi() = Fleet(
        id = "fleet-att",
        name = "AT&T",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "AT&T 热点或网关（attwifi、ATT-GUEST、Pace 风格出厂名称）。许多设备由 Pace / Arris 代工。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiName("attwifi"),
                wifiGlob("ATTWIFI*"),
                wifiGlob("ATTWifi*"),
                wifiGlob("ATT-WIFI*"),
                wifiGlob("ATT-Wifi*"),
                wifiGlob("ATT???????"),
                wifiGlob("ATT???????-*"),
                wifiGlob("ATT???????_*"),
                wifiGlob("ATT??????? *"),
                wifiGlob("ATT-GUEST*"),
                wifiGlob("ATT-Guest*"),
                wifiGlob("2WIRE*"),
                wifiGlob("2Wire*"),
            ),
            ApVendorOuis.ATT + ApVendorOuis.TWOWIRE,
        ),
    )

    private fun verizon() = Fleet(
        id = "fleet-verizon",
        name = "Verizon",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Verizon 或 Fios 热点 / 网关名称。许多 FiOS 设备由 Actiontec 代工。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Verizon-*"),
                wifiGlob("VerizonFiOS*"),
                wifiGlob("Fios-*"),
                wifiGlob("MyVerizon*"),
                wifiName("Verizon"),
            ),
            ApVendorOuis.VERIZON,
        ),
    )

    private fun starlink() = Fleet(
        id = "fleet-starlink",
        name = "Starlink",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Starlink 路由器。目前 BSSID 经常随机化，通常依据 STARLINK 名称匹配。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("STARLINK*"),
                wifiGlob("Starlink*"),
                wifiName("STARLINK"),
                wifiName("Starlink"),
            ),
            ApVendorOuis.SPACEX,
        ),
    )

    private fun meraki() = Fleet(
        id = "fleet-meraki",
        name = "Meraki",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Cisco Meraki 园区或云管理接入点。即使场所 SSID 已改名，仍可依据主板厂商匹配。并非摄像杆。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Meraki*"),
                wifiName("Meraki"),
            ),
            ApVendorOuis.MERAKI,
        ),
    )

    private fun glInet() = Fleet(
        id = "fleet-glinet",
        name = "GL.iNet",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "GL.iNet 便携路由器。没有 GL 名称的芯片模块主板不会匹配。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("GL-iNet*"),
                wifiGlob("GL-Inet*"),
                wifiGlob("GL-MT*"),
                wifiGlob("GL-AR*"),
                wifiGlob("GL-AXT*"),
                wifiName("GL.iNet"),
            ),
            ApVendorOuis.GLINET,
        ),
    )

    private fun chipolo() = Fleet(
        id = "fleet-chipolo",
        name = "Chipolo",
        enabled = true,
        colorIndex = Hue.FIND_MY,
        kind = SignatureClass.FINDER,
        matchAny = true,
        notes = "Chipolo 寻物标签（Find Hub /“查找”），可挂在钥匙或包上。",
        builtIn = true,
        rules = listOf(
            name("Chipolo"),
            glob("Chipolo*"),
        ),
    )

    private fun pebblebee() = Fleet(
        id = "fleet-pebblebee",
        name = "Pebblebee / moto tag",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.FINDER,
        matchAny = true,
        notes = "Pebblebee 或 Motorola moto tag 寻物标签，可挂在钥匙或包上。",
        builtIn = true,
        rules = listOf(
            name("Pebblebee"),
            glob("Pebblebee*"),
            name("moto tag"),
            name("Moto Tag"),
        ),
    )

    private fun findHub() = Fleet(
        id = "fleet-find-hub",
        name = "Google Find Hub",
        enabled = true,
        colorIndex = Hue.FIND_MY,
        kind = SignatureClass.FINDER,
        matchAny = true,
        notes = "Google Find Hub / Find My Device 网络标签（Chipolo、Pebblebee、moto tag 等合作品牌），包含附近和分离两类帧。分离模式可能维持同一 MAC 约一天，其他情况下地址会轮换。这里只是模式匹配，不能确定具体包袋。",
        builtIn = true,
        decode = CatalogDecodes.findHub,
        rules = listOf(
            svcData("FEAA", "40"),
            svcData("FEAA", "41"),
        ),
    )

    private fun dultTracker() = Fleet(
        id = "fleet-dult",
        name = "DULT tracker",
        enabled = true,
        colorIndex = Hue.FIND_MY,
        kind = SignatureClass.FINDER,
        matchAny = true,
        notes = "IETF DULT 定位广播（检测不受欢迎的位置追踪器）。Chipolo、Pebblebee、moto tag 等合作品牌标签可能同时匹配其他特征。载荷中的一个标志位区分靠近主人和分离状态。分离模式可能维持同一 MAC 约一天。这里只是模式匹配，不能确定具体包袋。",
        builtIn = true,
        decode = CatalogDecodes.dult,
        rules = listOf(
            svcAny("FCB2"),
        ),
    )

    private fun verkada() = Fleet(
        id = "fleet-verkada",
        name = "Verkada",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Verkada 云摄像头，包括支持车牌识别（LPR）的枪式摄像头，常用于建筑物及部分公共场所。",
        attentionNote = "Verkada 云摄像头，包括支持车牌识别的枪式摄像头，用于建筑物及部分公共场所，可拍摄视频，部分可识别车牌。仅按名称匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Verkada"),
            glob("Verkada*"),
        ),
    )

    private fun vigilant() = Fleet(
        id = "fleet-vigilant",
        name = "Motorola Vigilant",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "机构和停车场使用的 Motorola Vigilant 车牌识别设备。",
        attentionNote = "Motorola Vigilant 车牌识别（LPR）设备，用于机构和停车场。仅在广播名称时按名称匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Vigilant Solutions"),
            name("Motorola Vigilant"),
            name("Vigilant"),
        ),
    )

    private fun eufy() = Fleet(
        id = "fleet-eufy",
        name = "eufy Security",
        enabled = true,
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "eufy 家用摄像头或标签，常见于住宅，属于消费级设备，并非路边摄像杆。",
        builtIn = true,
        rules = listOf(
            name("eufy"),
            name("EufyCam"),
            glob("eufy*"),
            glob("Eufy*"),
        ),
    )

    private fun wyze() = Fleet(
        id = "fleet-wyze",
        name = "Wyze",
        enabled = true,
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "Wyze 家用摄像头，常见的消费级设备，并非路边摄像杆。",
        builtIn = true,
        rules = listOf(
            name("WyzeCam"),
            name("Wyze"),
            glob("Wyze*"),
        ),
    )

    private fun ring() = Fleet(
        id = "fleet-ring",
        name = "Ring",
        enabled = true,
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "Amazon Ring 门铃或摄像头，常见于住宅，属于消费级设备，并非路边摄像杆。",
        builtIn = true,
        rules = listOf(
            glob("Ring-*"),
            name("Ring Doorbell"),
            name("Ring Camera"),
            name("Ring Setup"),
        ),
    )

    private fun arlo() = Fleet(
        id = "fleet-arlo",
        name = "Arlo",
        enabled = true,
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "Arlo 家用摄像头或其基站 Wi-Fi，属于消费级设备，并非路边摄像杆。即使 SSID 已改名，仍可依据主板厂商匹配。",
        builtIn = true,
        rules = listOf(
            name("Arlo"),
            glob("Arlo*"),
            glob("ARLO_VMB_*"),
        ) + ApVendorOuis.ARLO.map { oui(it) },
    )

    private fun nest() = Fleet(
        id = "fleet-nest",
        name = "Nest",
        enabled = true,
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "Google Nest 家用摄像头。消费级摄像头，与 Nest 恒温器条目分开。",
        builtIn = true,
        rules = listOf(
            name("Nestcam"),
            name("Nest Cam"),
            name("Nest-Hello"),
            glob("Nest-*"),
        ),
    )

    private fun nestThermostat() = Fleet(
        id = "fleet-nest-thermostat",
        name = "Nest Thermostat",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.THERMOSTAT,
        matchAny = true,
        notes = "Nest 恒温器，部分代际的温度传感器也可能匹配此项。并非 Nest 摄像头。",
        builtIn = true,
        rules = listOf(
            mfg(0x01B5),
            bleName("Nest Thermostat"),
            bleGlob("Nest Thermostat*"),
        ),
    )

    private fun nestWeave() = Fleet(
        id = "fleet-nest-weave",
        name = "Nest Weave",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Nest Protect、恒温器或其他通过 BLE 使用 Weave 的家居设备。使用随机地址。解码字段可显示产品和配对状态。",
        builtIn = true,
        decode = CatalogDecodes.nestWeave,
        rules = listOf(
            uuid("FEAF"),
            uuid("FEB0"),
        ),
    )

    private fun ecobee() = Fleet(
        id = "fleet-ecobee",
        name = "ecobee",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.THERMOSTAT,
        matchAny = true,
        notes = "ecobee 恒温器，房间传感器也可能匹配。Premium 通过 BLE 进行设置或连接 Spotify。",
        builtIn = true,
        rules = listOf(
            mfg(0x07D6),
            bleName("ecobee"),
            bleGlob("ecobee*"),
            bleGlob("ecoBee*"),
        ),
    )

    private fun sensi() = Fleet(
        id = "fleet-sensi",
        name = "Sensi",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.THERMOSTAT,
        matchAny = true,
        notes = "处于 BLE 设置模式的 Sensi 恒温器。",
        builtIn = true,
        rules = listOf(
            bleName("Sensi"),
            bleGlob("Sensi*"),
        ),
    )

    private fun honeywellHome() = Fleet(
        id = "fleet-honeywell-home",
        name = "Honeywell Home",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.THERMOSTAT,
        matchAny = true,
        notes = "Honeywell Home / Lyric / Resideo 恒温器（包括 Amazon Smart Thermostat）。不包括 Honeywell 工业或烟雾报警设备。T9/T10 房间传感器使用 900 MHz，而非 BLE。",
        builtIn = true,
        rules = listOf(
            bleName("Honeywell Home"),
            bleGlob("Honeywell Home*"),
            bleName("Lyric Thermostat"),
            bleGlob("Lyric T*"),
            bleName("Amazon Smart Thermostat"),
            bleGlob("Amazon Smart Thermostat*"),
        ),
    )

    private fun haiku() = Fleet(
        id = "fleet-haiku",
        name = "Haiku Fan",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Big Ass Fans Haiku 或 Mammoth 吊扇。",
        builtIn = true,
        rules = listOf(
            uuid("E0FC1000-1FB1-4168-96DF-B3F057A86E01"),
            bleName("Haiku Fan"),
            bleGlob("Haiku Fan*"),
            bleName("Mammoth Fan"),
            bleGlob("Mammoth Fan*"),
        ),
    )

    private fun tuya() = Fleet(
        id = "fleet-tuya",
        name = "Tuya",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Tuya 插座、灯具、摄像头或传感器，在部分公寓中较密集。解码字段可显示绑定状态。",
        builtIn = true,
        decode = CatalogDecodes.tuya,
        rules = listOf(
            mfg(0x07D0),
            uuid("FD50"),
            bleName("TUYA"),
            bleGlob("TUYA*"),
            bleGlob("Tuya*"),
        ),
    )

    private fun seos() = Fleet(
        id = "fleet-seos",
        name = "ASSA ABLOY",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "ASSA ABLOY / HID Seos 或 Yale 门禁凭证。使用 HID Mobile Access 的手机可能广播 Seos 名称。",
        builtIn = true,
        rules = listOf(
            mfg(0x012E),
            mfg(0x0124),
            mfg(0x0BDE),
            uuid("FCBF"),
            uuid("00009800-0000-1000-8000-00177A000002"),
            bleName("Seos"),
            bleName("Yale"),
            bleGlob("Yale*"),
        ),
    )

    private fun augustLock() = Fleet(
        id = "fleet-august",
        name = "August",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "August 智能门锁（现属于 ASSA），并非摄像头。",
        builtIn = true,
        rules = listOf(
            mfg(0x01D1),
            uuid("FE24"),
            bleName("August"),
            bleGlob("August*"),
        ),
    )

    private fun schlage() = Fleet(
        id = "fleet-schlage",
        name = "Schlage",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "Schlage / Allegion 智能门锁（Encode 等系列）。",
        builtIn = true,
        rules = listOf(
            mfg(0x013B),
            uuid("FCF4"),
            bleName("Schlage"),
            bleGlob("Schlage*"),
            bleGlob("SCHLAGE*"),
        ),
    )

    private fun nuki() = Fleet(
        id = "fleet-nuki",
        name = "Nuki",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "Nuki 智能门锁或开门器（可改装于欧式锁芯）。",
        builtIn = true,
        rules = listOf(
            uuid("A92EE000-5501-11E4-916C-0800200C9A66"),
            uuid("A92EE100-5501-11E4-916C-0800200C9A66"),
            uuid("A92EE200-5501-11E4-916C-0800200C9A66"),
            uuid("A92EE300-5501-11E4-916C-0800200C9A66"),
            uuid("A92AE200-5501-11E4-916C-0800200C9A66"),
            bleName("Nuki"),
            bleGlob("Nuki*"),
        ),
    )

    private fun salto() = Fleet(
        id = "fleet-salto",
        name = "SALTO",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "SALTO 商用门禁锁或读卡器。",
        builtIn = true,
        rules = listOf(
            mfg(0x0199),
            bleName("SALTO"),
            bleGlob("SALTO*"),
            bleGlob("Salto*"),
        ),
    )

    private fun dormakaba() = Fleet(
        id = "fleet-dormakaba",
        name = "dormakaba",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "dormakaba、Saflok 或 Oracode 酒店 / 商用门锁。",
        builtIn = true,
        rules = listOf(
            mfg(0x0C64),
            bleName("dormakaba"),
            bleGlob("dormakaba*"),
            bleName("Saflok"),
            bleGlob("Saflok*"),
            bleName("Oracode"),
            bleGlob("Oracode*"),
        ),
    )

    private fun lockly() = Fleet(
        id = "fleet-lockly",
        name = "Lockly",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "Lockly 智能门锁，通常在 BLE 设置时出现。",
        builtIn = true,
        rules = listOf(
            bleName("LOCKLY"),
            bleGlob("LOCKLY*"),
            bleGlob("Lockly*"),
        ),
    )

    private fun kevo() = Fleet(
        id = "fleet-kevo",
        name = "Kevo",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "Kwikset Kevo 智能门锁。",
        builtIn = true,
        rules = listOf(
            mfg(0x015E),
            bleName("Unikey"),
            bleGlob("Unikey*"),
            bleName("Kevo"),
            bleGlob("Kevo*"),
        ),
    )

    private fun masterLock() = Fleet(
        id = "fleet-master-lock",
        name = "Master Lock",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "Master Lock 蓝牙挂锁。",
        builtIn = true,
        rules = listOf(
            mfg(0x014B),
            bleName("Master Lock"),
            bleGlob("Master Lock*"),
        ),
    )

    private fun igloohome() = Fleet(
        id = "fleet-igloohome",
        name = "igloohome",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "igloohome 钥匙盒或智能门锁。",
        builtIn = true,
        rules = listOf(
            mfg(0x05BA),
            bleName("igloohome"),
            bleGlob("igloohome*"),
            bleGlob("Igloohome*"),
        ),
    )

    private fun tedee() = Fleet(
        id = "fleet-tedee",
        name = "Tedee",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "Tedee 改装式智能门锁。",
        builtIn = true,
        rules = listOf(
            mfg(0x0725),
            bleName("Tedee"),
            bleGlob("Tedee*"),
        ),
    )

    private fun paxton() = Fleet(
        id = "fleet-paxton",
        name = "Paxton",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "Paxton / Net2 门禁读卡器或控制面板。",
        builtIn = true,
        rules = listOf(
            mfg(0x0196),
            bleName("Paxton"),
            bleGlob("Paxton*"),
            bleName("Net2"),
            bleGlob("Net2*"),
        ),
    )

    private fun kwikset() = Fleet(
        id = "fleet-kwikset",
        name = "Kwikset",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.LOCK,
        matchAny = true,
        notes = "Kwikset 智能门锁。Kevo 单独列出。",
        builtIn = true,
        rules = listOf(
            bleName("Kwikset"),
            bleGlob("Kwikset*"),
        ),
    )

    private fun myq() = Fleet(
        id = "fleet-myq",
        name = "myQ",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Chamberlain myQ 车库门中枢。",
        builtIn = true,
        rules = listOf(
            mfg(0x0878),
            uuid("26D91A37-C279-4D0F-96A1-532CE41CE0F6"),
            bleName("MyQ"),
            bleGlob("MyQ-*"),
        ),
    )

    private fun chevroletHotspot() = Fleet(
        id = "fleet-chevrolet",
        name = "Chevrolet hotspot",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Chevrolet 车载热点（myChevrolet）。Cadillac / GMC / Buick 归入 GM hotspot，并非经销商网络。",
        builtIn = true,
        rules = listOf(
            wifiName("myChevrolet"),
            wifiGlob("myChevrolet*"),
        ),
    )

    private fun uconnect() = Fleet(
        id = "fleet-uconnect",
        name = "Uconnect",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Stellantis Uconnect 车载热点（Chrysler、Jeep、Ram、Dodge、Fiat）。BSSID 经常随机化。",
        builtIn = true,
        rules = listOf(
            wifiGlob("Uconnect*"),
            wifiName("Uconnect"),
        ),
    )

    private fun carPlay() = Fleet(
        id = "fleet-carplay",
        name = "CarPlay",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "车载 CarPlay / Alpine 车机热点，名称来自仪表台出厂设置，并非运营商网络。",
        builtIn = true,
        rules = listOf(
            wifiGlob("CarPlay*"),
            wifiName("CarPlay"),
        ),
    )

    private fun carlink() = Fleet(
        id = "fleet-carlink",
        name = "CARLINK",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "后装 CarPlay / Android Auto 适配器热点（CARLINK-），属于车机适配器，而非汽车原装调制解调器。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("CARLINK-??????"),
            ),
            listOf("CC:57:63", "68:8F:C9"),
        ),
    )

    private fun rivian() = Fleet(
        id = "fleet-rivian",
        name = "Rivian",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Rivian 手机钥匙、露营音箱或传感器。手机也可能广播 Rivian Sensor。",
        builtIn = true,
        rules = listOf(
            mfg(0x0941),
            bleName("Rivian"),
            bleGlob("Rivian*"),
        ),
    )

    private fun govee() = Fleet(
        id = "fleet-govee",
        name = "Govee",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Govee 灯具或温湿度计。灯具通常只发送名称；温湿度计可在下方解码温度、湿度和电量。",
        builtIn = true,
        decode = CatalogDecodes.govee,
        rules = listOf(
            bleName("Govee"),
            bleGlob("Govee*"),
            bleGlob("GBK_*"),
            bleGlob("ihoment_*"),
            bleGlob("GV5108*"),
            bleGlob("GVH5*"),
            bleGlob("GVH5075*"),
        ),
    )

    private fun hpPrinter() = Fleet(
        id = "fleet-hp",
        name = "HP",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "HP 家用或办公打印机（ENVY、HP-Print），常见的办公背景信号。并非 HPE Aruba 园区 Wi-Fi。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                mfg(0x0065),
                uuid("FE78"),
                bleName("ENVY"),
                bleGlob("ENVY*"),
                wifiGlob("HP-Print*"),
            ),
            ApVendorOuis.HPINC,
        ),
    )

    private fun mercedesMbux() = Fleet(
        id = "fleet-mbux",
        name = "Mercedes MBUX",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Mercedes MBUX 车载热点，使用车辆出厂名称。",
        builtIn = true,
        rules = listOf(
            mfg(0x017C),
            bleName("Mercedes"),
            wifiName("MBUX"),
            wifiGlob("MBUX*"),
        ),
    )

    private fun motive() = Fleet(
        id = "fleet-motive",
        name = "Motive",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "卡车中的 Motive（KeepTruckin）电子行车记录设备或车队 Wi-Fi。",
        builtIn = true,
        rules = listOf(
            wifiGlob("Motive *"),
            wifiGlob("Motive_*"),
            wifiGlob("Motive Hotspot*"),
            wifiGlob("KeepTruckin*"),
        ),
    )

    private fun peopleNet() = Fleet(
        id = "fleet-peoplenet",
        name = "PeopleNet",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "PeopleNet 卡车电子行车记录设备或车队 Wi-Fi。与 Motive 分开列出。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("PNet*"),
            ),
            ApVendorOuis.PEOPLENET,
        ),
    )

    private fun goodyearTpms() = Fleet(
        id = "fleet-goodyear",
        name = "Goodyear TPMS",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Goodyear 智能轮胎 BLE，并非大多数汽车使用的 315/433 MHz 气门嘴胎压监测。这里只是模式匹配，不能确定具体车辆。",
        builtIn = true,
        rules = listOf(
            mfg(0x0B99),
        ),
    )

    private fun schraderTpms() = Fleet(
        id = "fleet-schrader",
        name = "Schrader TPMS",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Schrader 后装 BLE 胎压监测（AirCheck、拖车、房车），并非 315/433 MHz 原装气门嘴传感器。",
        builtIn = true,
        rules = listOf(
            mfg(0x0601),
        ),
    )

    private fun pacificTpms() = Fleet(
        id = "fleet-pacific-tpms",
        name = "Pacific TPMS",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Pacific Industrial 原装轮胎电子设备。部分新车型采用 BLE 胎压监测。",
        builtIn = true,
        rules = listOf(
            mfg(0x0E32),
        ),
    )

    private fun hufTpms() = Fleet(
        id = "fleet-huf",
        name = "Huf",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Huf 轮胎传感器或车辆门禁设备（门把手 / 无钥匙进入与启动），不一定是气门嘴。",
        builtIn = true,
        rules = listOf(
            mfg(0x070A),
        ),
    )

    private fun foboTpms() = Fleet(
        id = "fleet-fobo",
        name = "FOBO TPMS",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "FOBO 后装 BLE 胎压传感器，用于摩托车或汽车。这里只是模式匹配，不能确定具体车辆。",
        builtIn = true,
        rules = listOf(
            mfg(0x0127),
            uuid("00EE"),
            bleName("FOBO"),
            bleGlob("FOBO*"),
        ),
    )

    private fun aftermarketTpms() = Fleet(
        id = "fleet-tpms-ble",
        name = "Aftermarket TPMS",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "后装 BLE 气门帽胎压传感器（TPMS1 / FBB0 系列）。解码字段可显示轮位、压力、温度、电量和报警。这里只是模式匹配，不能确定具体车辆。",
        builtIn = true,
        decode = CatalogDecodes.tpmsAftermarket,
        rules = listOf(
            bleGlob("TPMS*"),
            uuid("FBB0"),
            mfgData(0x0001, "80"),
            mfgData(0x0001, "81"),
            mfgData(0x0001, "82"),
            mfgData(0x0001, "83"),
        ),
    )

    private fun sytpms() = Fleet(
        id = "fleet-sytpms",
        name = "SYTPMS",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "SYTPMS / BR 自行车或滑板车 BLE 胎压传感器。解码字段可显示表压、温度、电量和移动状态。这里只是模式匹配，不能确定具体车辆。",
        builtIn = true,
        decode = CatalogDecodes.sytpms,
        rules = listOf(
            bleGlob("BR"),
            uuid("27A5"),
        ),
    )

    private fun tireCheck() = Fleet(
        id = "fleet-tirecheck",
        name = "TireCheck",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "TireCheck BLE 胎压传感器。这里只是模式匹配，不能确定具体车辆。",
        builtIn = true,
        rules = listOf(
            mfg(0x0BA2),
            bleName("TireCheck"),
            bleGlob("TireCheck*"),
        ),
    )

    private fun tpmsService() = Fleet(
        id = "fleet-tpms-service",
        name = "TPMS service",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Bluetooth SIG 胎压监测系统服务。任何广播该标准服务的传感器均可匹配。",
        builtIn = true,
        rules = listOf(
            uuid("1860"),
        ),
    )

    private fun ruuvi() = Fleet(
        id = "fleet-ruuvi",
        name = "Ruuvi",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Ruuvi 广播式传感标签（温度、湿度、气压、运动）。本页解码字段可解析传感器载荷。",
        builtIn = true,
        decode = CatalogDecodes.ruuvi,
        rules = listOf(
            mfg(0x0499),
            bleName("Ruuvi"),
            bleGlob("Ruuvi*"),
        ),
    )

    private fun blueMaestro() = Fleet(
        id = "fleet-bluemaestro",
        name = "Blue Maestro",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Blue Maestro Tempo Disc 温湿度记录仪。解码字段可显示版本、电量和温度。",
        builtIn = true,
        decode = CatalogDecodes.blueMaestro,
        rules = listOf(
            mfg(0x0133),
        ),
    )

    private fun sensorPush() = Fleet(
        id = "fleet-sensorpush",
        name = "SensorPush",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "SensorPush 温湿度记录仪。",
        builtIn = true,
        rules = listOf(
            uuid("EF090000-11D6-42BA-93B8-9DD7EC090AA9"),
            uuid("EF090000-11D6-42BA-93B8-9DD7EC090AB0"),
            bleName("SensorPush"),
            bleGlob("SensorPush*"),
        ),
    )

    private fun samsara() = Fleet(
        id = "fleet-samsara",
        name = "Samsara",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Samsara 车队追踪器或车辆 Wi-Fi，用于卡车或厢式车的远程信息处理，与 Motive 同类。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                mfg(0x0B6B),
                bleName("Samsara"),
                bleGlob("Samsara*"),
                wifiGlob("Samsara*"),
            ),
            ApVendorOuis.SAMSARA,
        ),
    )

    private fun tapo() = Fleet(
        id = "fleet-tapo",
        name = "Tapo",
        enabled = true,
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "TP-Link Tapo 家用摄像头，属于消费级设备，并非路边摄像杆。",
        builtIn = true,
        rules = listOf(
            name("Tapo"),
            glob("Tapo*"),
        ),
    )

    private fun reolink() = Fleet(
        id = "fleet-reolink",
        name = "Reolink",
        enabled = true,
        colorIndex = Hue.CAMERA,
        kind = SignatureClass.CAMERA,
        matchAny = true,
        notes = "Reolink 家用或小型商用摄像头，属于消费级设备，并非路边摄像杆。",
        builtIn = true,
        rules = listOf(
            name("Reolink"),
            glob("Reolink*"),
        ),
    )

    private fun hikvision() = Fleet(
        id = "fleet-hikvision",
        name = "Hikvision",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Hikvision 摄像头，常见于商业闭路电视及部分公共摄像杆。",
        attentionNote = "Hikvision 摄像头，常见于商业闭路电视及部分公共摄像杆。仅按名称匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Hikvision"),
            name("HIKVISION"),
            glob("Hikvision*"),
        ),
    )

    private fun dahua() = Fleet(
        id = "fleet-dahua",
        name = "Dahua",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Dahua 摄像头，常见于商业闭路电视及部分公共摄像杆。",
        attentionNote = "Dahua 摄像头，常见于商业闭路电视及部分公共摄像杆。仅按名称匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Dahua"),
            name("DAHUA"),
            glob("Dahua*"),
        ),
    )

    private fun meshtastic() = Fleet(
        id = "fleet-meshtastic",
        name = "Meshtastic",
        enabled = true,
        colorIndex = Hue.MESH,
        kind = SignatureClass.MESH,
        matchAny = true,
        notes = "Meshtastic LoRa Mesh 节点，用于离网文字和位置通信，并非蜂窝网络。",
        builtIn = true,
        rules = listOf(
            name("Meshtastic"),
            glob("Meshtastic*"),
            glob("Meshtastic_*"),
            uuid("6ba1b218"),
        ),
    )

    private fun helium() = Fleet(
        id = "fleet-helium",
        name = "Helium",
        enabled = true,
        colorIndex = Hue.MESH,
        kind = SignatureClass.MESH,
        matchAny = true,
        notes = "广播名称的 Helium / LoRaWAN 热点。",
        builtIn = true,
        rules = listOf(
            name("Helium"),
            glob("Helium*"),
        ),
    )

    private fun meshCore() = Fleet(
        id = "fleet-meshcore",
        name = "MeshCore",
        enabled = true,
        colorIndex = Hue.MESH,
        kind = SignatureClass.MESH,
        matchAny = true,
        notes = "MeshCore LoRa 配套通信设备，用于离网文字和位置通信，并非蜂窝网络。仅按名称匹配；Nordic UART UUID 在 ESP32 串口板上很常见，不能据此识别本项。",
        builtIn = true,
        rules = listOf(
            bleName("MeshCore"),
            bleGlob("MeshCore*"),
        ),
    )

    private fun goTenna() = Fleet(
        id = "fleet-gotenna",
        name = "goTenna",
        enabled = true,
        colorIndex = Hue.MESH,
        kind = SignatureClass.MESH,
        matchAny = true,
        notes = "goTenna Mesh 或 Pro 配套通信设备。通过 BLE 配对；Mesh 本身使用 UHF，Fieldwatch 无法接收。Pro 面向机构销售。这里只是模式匹配，不能确定具体操作者。",
        builtIn = true,
        rules = listOf(
            uuid("1276aaee-df5e-11e6-bf01-fe55135034f3"),
            uuid("f0abaaee-ebfa-f96f-28da-076c35a521db"),
            bleName("goTenna"),
            bleGlob("goTenna*"),
            bleGlob("gotenna*"),
        ),
    )

    private fun senseCap() = Fleet(
        id = "fleet-sensecap",
        name = "SenseCAP",
        enabled = true,
        colorIndex = Hue.MESH,
        kind = SignatureClass.MESH,
        matchAny = true,
        notes = "Seeed SenseCAP LoRaWAN / Helium 室内网关的设置热点（SenseCAP_XXXXXX）。接入以太网后通常停止广播。使用 Helium 名称的设备也可能匹配 Helium 条目。",
        builtIn = true,
        rules = listOf(
            wifiName("SenseCAP"),
            wifiGlob("SenseCAP*"),
            wifiGlob("SenseCAP_*"),
        ),
    )

    private fun rakWisGate() = Fleet(
        id = "fleet-rak-wisgate",
        name = "RAK WisGate",
        enabled = true,
        colorIndex = Hue.MESH,
        kind = SignatureClass.MESH,
        matchAny = true,
        notes = "RAKwireless WisGate LoRaWAN 网关的设置热点（RAK7268_XXXX 等）。接入以太网后通常停止广播。",
        builtIn = true,
        rules = listOf(
            wifiGlob("RAK7*"),
            wifiGlob("RAK7268*"),
            wifiGlob("RAK7249*"),
            wifiGlob("RAK7289*"),
            wifiGlob("RAK7391*"),
            name("WisGate"),
            glob("WisGate*"),
        ),
    )

    private fun genetec() = Fleet(
        id = "fleet-genetec",
        name = "Genetec AutoVu",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Genetec AutoVu 停车场或路边车牌识别设备。",
        attentionNote = "Genetec AutoVu 市政或停车场车牌自动识别（ALPR）设备，用于读取停车场和路边车牌。仅在广播名称时匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Genetec"),
            name("AutoVu"),
            glob("Genetec*"),
            glob("AutoVu*"),
        ),
    )

    private fun blueToadSpectra() = Fleet(
        id = "fleet-bluetoad",
        name = "BlueTOAD Spectra",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Iteris 路边蓝牙行程时间采集设备（Vantage Velocity，现为 BlueTOAD Spectra / Spectra CV）。车辆经过时采样手机、耳机和车载蓝牙，通过在两处匹配同一 ID 估算速度，范围约 100 米。这是抽样而非完整车流计数。静默或仅接入以太网的机柜可能不广播。Spectra CV 还使用 Fieldwatch 无法接收的 5.9 GHz C-V2X。IEEE Iteris OUI 也可能匹配其他 Iteris 路侧设备。这里只是模式匹配，不能确认具体机柜。",
        builtIn = true,
        rules = listOf(
            // IEEE MA-L registered to Iteris, Inc.
            oui("00:14:7B"),
            name("BlueTOAD"),
            glob("BlueTOAD*"),
            name("Vantage Velocity"),
            glob("VantageVelocity*"),
            glob("Vantage-Velocity*"),
            name("Spectra CV"),
            glob("SpectraCV*"),
            glob("Spectra-CV*"),
            name("TrafficCast"),
            glob("TrafficCast*"),
            name("VantageARGUS"),
            glob("VantageARGUS*"),
            name("BlueARGUS"),
            glob("BlueARGUS*"),
        ),
    )

    private fun blipTrack() = Fleet(
        id = "fleet-bliptrack",
        name = "BlipTrack",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "BLIP Systems BlipTrack 路边蓝牙 / Wi-Fi 行程时间传感器，与 BlueTOAD Spectra 类似，通过两处采样经过的手机和车载无线设备估算速度。静默或仅接入以太网的机柜可能不广播。这里只是模式匹配，不能确认具体机柜。",
        builtIn = true,
        rules = listOf(
            // IEEE MA-L registered to BLIP Systems
            oui("00:0E:A5"),
            name("BlipTrack"),
            glob("BlipTrack*"),
            name("BLIP Systems"),
            glob("BLIP-Track*"),
        ),
    )

    private fun hanwhaWisenet() = Fleet(
        id = "fleet-hanwha-wisenet",
        name = "Hanwha Wisenet",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Hanwha Vision / Wisenet 摄像头（原 Samsung Techwin），常见于商业闭路电视及部分公共摄像杆。",
        attentionNote = "Hanwha Vision / Wisenet 摄像头，常见于商业闭路电视及部分公共摄像杆。*_WISENET 设置 SSID 是较强的匹配依据；IEEE 00:09:18 属于 Samsung Techwin。这里只是模式匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            oui("00:09:18"),
            name("Wisenet"),
            glob("Wisenet*"),
            glob("*_WISENET"),
            glob("*WISENET*"),
            name("Hanwha"),
            glob("Hanwha*"),
        ),
    )

    private fun uniview() = Fleet(
        id = "fleet-uniview",
        name = "Uniview",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Uniview / UNV / Uniarch 摄像头，常见于商业闭路电视及部分公共摄像杆。",
        attentionNote = "Uniview / UNV 摄像头，常见于商业闭路电视及部分公共摄像杆。依据浙江宇视的 IEEE OUI 或 Uniview / UNV- 名称匹配。这里只是模式匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = buildList {
            listOf(
                "14:BA:88", "48:EA:63", "6C:F1:7E", "88:26:3F", "C4:79:05",
            ).forEach { add(oui(it)) }
            add(name("Uniview"))
            add(glob("Uniview*"))
            add(glob("UNV-*"))
            add(name("Uniarch"))
            add(glob("Uniarch*"))
        },
    )

    private fun rhombus() = Fleet(
        id = "fleet-rhombus",
        name = "Rhombus",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Rhombus 云摄像头，未注册或离线时的 BLE 广播最明显。",
        attentionNote = "Rhombus 云摄像头，用于建筑物及部分公共场所。依据 IEEE CC:47:BD 或 Rhombus 名称匹配，通常仅在未注册或离线时发送 BLE 广播。这里只是模式匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            oui("CC:47:BD"),
            name("Rhombus"),
            glob("Rhombus*"),
        ),
    )

    private fun rekor() = Fleet(
        id = "fleet-rekor",
        name = "Rekor",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Rekor 公路或交通运输车牌识别设备。",
        attentionNote = "Rekor 公路或交通运输车牌自动识别（ALPR）设备，用于读取道路和检查站车牌。仅按名称匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Rekor"),
            glob("Rekor*"),
        ),
    )

    private fun axon() = Fleet(
        id = "fleet-axon",
        name = "Axon",
        enabled = true,
        colorIndex = Hue.LAW,
        kind = SignatureClass.LAW_ENFORCEMENT,
        matchAny = true,
        notes = "Axon 随身摄像头、车载系统、底座或 TASER。静默或仅使用 LTE 的设备不会出现。",
        attentionNote = "Axon 随身摄像头、车载系统（Fleet）、底座或 TASER 设备。IEEE OUI 00:25:DF 属于 Axon Enterprise。Body 3/4 佩戴时常使用此公共 OUI 发送 BLE 广播。Axon Body 等名称只是模式依据，不能确定具体人员。静默或仅使用 LTE 的设备不会出现。Axon 一词也可能匹配部分 ZTE 手机。请结合现场观察，不能据此确认身份。",
        builtIn = true,
        rules = listOf(
            oui("00:25:DF"),
            name("Axon Fleet"),
            name("Axon Body"),
            name("Axon Dock"),
            glob("Axon*"),
            uuid("FE6B"),
            uuid("FE6C"),
            uuid("FC81"),
            mfg(0x034D),
            svcContainsAscii("BWCDEVICE"),
        ),
    )

    private fun watchGuardVideo() = Fleet(
        id = "fleet-watchguard",
        name = "WatchGuard Video",
        enabled = true,
        colorIndex = Hue.LAW,
        kind = SignatureClass.LAW_ENFORCEMENT,
        matchAny = true,
        notes = "WatchGuard Video 随身或车载摄像头（现属于 Motorola），与 WatchGuard 防火墙公司无关。巡逻设备可能保持静默。",
        attentionNote = "WatchGuard Video 随身或车载摄像头（VISTA / V300 系列）。IEEE OUI 00:1D:96 属于 WatchGuard Video，与同名防火墙公司无关。巡逻设备可能保持静默。这里只是模式匹配，不能确认身份，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            oui("00:1D:96"),
            name("WatchGuard"),
            name("Watchguard"),
            glob("WatchGuard*"),
            name("VISTA WiFi"),
            name("VISTA XLT"),
        ),
    )

    private fun digitalAlly() = Fleet(
        id = "fleet-digital-ally",
        name = "Digital Ally",
        enabled = true,
        colorIndex = Hue.LAW,
        kind = SignatureClass.LAW_ENFORCEMENT,
        matchAny = true,
        notes = "Digital Ally 随身或车载摄像头（FirstVu / EVO）。静默或仅使用 LTE 的设备不会出现。",
        attentionNote = "Digital Ally 随身或车载摄像头（FirstVu / EVO 系列）。IEEE OUI 00:23:BD 属于摄像设备厂商 Digital Ally, Inc.，并非通用芯片厂商。巡逻设备可能仅使用 LTE 而保持静默。这里只是模式匹配，不能确定具体人员或身份，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            oui("00:23:BD"),
            name("Digital Ally"),
            glob("DigitalAlly*"),
            name("FirstVu"),
            glob("FirstVu*"),
            name("EVO-HD"),
            name("VuLink"),
        ),
    )

    private fun revealMedia() = Fleet(
        id = "fleet-reveal-media",
        name = "Reveal Media",
        enabled = true,
        colorIndex = Hue.LAW,
        kind = SignatureClass.LAW_ENFORCEMENT,
        matchAny = true,
        notes = "Reveal Media / BodyWorn 摄像头，常见于英国及部分美国机构。静默设备不会出现。",
        attentionNote = "Reveal Media 随身摄像头（D 系列 / BodyWorn）。仅在广播名称时匹配；巡逻设备可能保持静默。这里只是模式匹配，不能确定具体人员，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Reveal Media"),
            glob("Reveal D*"),
            glob("Reveal-D*"),
            name("BodyWorn"),
            glob("BodyWorn*"),
            glob("RS2-*"),
        ),
    )

    private fun wolfcom() = Fleet(
        id = "fleet-wolfcom",
        name = "Wolfcom",
        enabled = true,
        colorIndex = Hue.LAW,
        kind = SignatureClass.LAW_ENFORCEMENT,
        matchAny = true,
        notes = "Wolfcom 随身或车载摄像头。静默设备不会出现。",
        attentionNote = "Wolfcom 随身或车载摄像头。仅在广播名称时匹配；巡逻设备可能保持静默。这里只是模式匹配，不能确定具体人员，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Wolfcom"),
            glob("Wolfcom*"),
            glob("WOLFCOM*"),
        ),
    )

    private fun panasonicIpro() = Fleet(
        id = "fleet-panasonic-ipro",
        name = "Panasonic i-PRO",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Panasonic i-PRO 摄像头或 Arbitrator 车载系统。Panasonic 电视和手机使用其他名称。",
        attentionNote = "Panasonic i-PRO 摄像头或 Arbitrator 车载视频系统，用于建筑物和部分巡逻车，可拍摄视频，部分可识别车牌。仅按 i-PRO / Arbitrator 名称匹配，不涵盖所有 Panasonic 无线设备。这里只是模式匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("i-PRO"),
            glob("i-PRO*"),
            glob("iPRO*"),
            name("Arbitrator"),
            glob("Arbitrator*"),
        ),
    )

    private fun avigilon() = Fleet(
        id = "fleet-avigilon",
        name = "Avigilon",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Avigilon 建筑或市政摄像头，部分支持车牌识别。",
        attentionNote = "Motorola Avigilon 摄像头 / 车牌识别设备，用于市政摄像杆和商业场所，可拍摄视频，部分可识别车牌。仅按名称匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Avigilon"),
            glob("Avigilon*"),
        ),
    )

    private fun axis() = Fleet(
        id = "fleet-axis",
        name = "Axis",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Axis 摄像头，常见于市政摄像杆和公共闭路电视。",
        attentionNote = "Axis Communications 摄像头，常见于市政摄像杆和公共闭路电视。仅按 AXIS- 名称匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            glob("AXIS-*"),
            glob("Axis-*"),
            name("AXIS-"),
            name("Axis Camera"),
        ),
    )

    private fun haydenAi() = Fleet(
        id = "fleet-hayden-ai",
        name = "Hayden AI",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Hayden AI 公交车或其他车辆上的摄像头，用于停车和交通执法。",
        attentionNote = "Hayden AI 摄像头安装在公交车和市政车辆上，可拍摄视频和车牌。仅在广播名称时匹配；仅使用 LTE 的设备不会出现。这里只是模式匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Hayden AI"),
            glob("HaydenAI*"),
            glob("Hayden-AI*"),
        ),
    )

    private fun miovision() = Fleet(
        id = "fleet-miovision",
        name = "Miovision",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Miovision 路口或交通摄像头（SmartLink / Scout）。",
        attentionNote = "Miovision 路口交通摄像头，可拍摄视频，部分可识别车牌。仅在广播名称时匹配；许多设备仅使用蜂窝网络，保持静默。这里只是模式匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Miovision"),
            glob("Miovision*"),
        ),
    )

    private fun tattile() = Fleet(
        id = "fleet-tattile",
        name = "Tattile",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "Tattile 车牌自动识别（ALPR）摄像头，常见于欧洲道路及部分美国场所。",
        attentionNote = "Tattile 道路或出入口车牌识别设备。仅在广播名称时匹配，不能确认具体摄像头，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("Tattile"),
            glob("Tattile*"),
        ),
    )

    private fun liveViewLvt() = Fleet(
        id = "fleet-lvt",
        name = "LVT LiveView",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "LiveView Technologies（LVT）太阳能监控拖车。多数设备仅使用蜂窝网络，不会出现。",
        attentionNote = "LVT / LiveView 太阳能摄像拖车，用于停车场、工地和部分城市公园，可拍摄视频，部分可识别车牌。多数设备使用蜂窝网络，不发出 Wi-Fi / BLE 广播。LiveView 或 LVT- 名称只是模式依据，不能确认具体拖车，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("LiveView"),
            glob("LiveView*"),
            glob("LVT-*"),
            glob("LVT_*"),
        ),
    )

    private fun unifi() = Fleet(
        id = "fleet-unifi",
        name = "UniFi",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "使用 UniFi / Ubiquiti 名称的 Wi-Fi 或 BLE 设备。依据 BSSID 匹配时优先归入 UniFi AP。Instant 摄像头归入 UniFi Protect。",
        builtIn = true,
        rules = listOf(
            name("UniFi"),
            name("Ubiquiti"),
            glob("UniFi*"),
            glob("UAP-*"),
        ),
    )

    private fun unifiAp() = Fleet(
        id = "fleet-unifi-ap",
        name = "UniFi AP",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "UniFi / Ubiquiti Wi-Fi 接入点（包括 airMAX / AmpliFi）。即使 SSID 已改名，仍可依据主板厂商或 Ubiquiti 厂商标签匹配。Instant 摄像头归入 UniFi Protect。",
        builtIn = true,
        rules = buildList {
            add(wifiName("UniFi"))
            add(wifiName("Ubiquiti"))
            add(wifiName("UBNT"))
            add(wifiGlob("UniFi*"))
            add(wifiGlob("UAP-*"))
            add(wifiGlob("UBNT*"))
            // IEEE MA-L registered to Ubiquiti Inc (through 2026-06-17). Not the shared IAB 00:50:C2:B0:4.
            listOf(
                "00:15:6D", "00:27:22", "04:18:D6", "0C:EA:14", "18:E8:29", "1C:0B:8B",
                "1C:6A:1B", "24:5A:4C", "24:A4:3C", "28:70:4E", "2C:E5:BD", "44:D9:E7",
                "58:D6:1F", "60:22:32", "68:2E:3C", "68:72:51", "68:D7:9A", "6C:63:F8",
                "70:A7:41", "74:83:C2", "74:AC:B9", "74:F9:2C", "74:FA:29", "78:45:58",
                "78:8A:20", "80:2A:A8", "84:78:48", "8C:30:66", "8C:ED:E1", "90:41:B2",
                "94:2A:6F", "9C:05:D6", "A4:F8:FF", "A8:9C:6C", "AC:8B:A9", "B4:FB:E4",
                "CC:35:D9", "D0:21:F9", "D4:89:C1", "D8:B3:70", "D8:C2:62", "DC:9F:DB",
                "E0:63:DA", "E4:38:83", "F0:9F:C2", "F4:92:BF", "F4:E2:C6", "FC:EC:DA",
            ).forEach { add(wifiOui(it)) }
        },
    )

    private fun hobbyBleSerial() = Fleet(
        id = "fleet-hobby-ble",
        name = "Hobby BLE serial",
        enabled = true,
        colorIndex = Hue.HACKING,
        kind = SignatureClass.HACKING,
        matchAny = true,
        notes = "使用默认名称的廉价 DIY UART 模块（HM-10、JDY、CC41、ESP32 BLE），常见于打印机、汽车和自制设备。Fieldwatch 无法发现经典蓝牙 HC-05/HC-06。",
        attentionNote = "这些默认 BLE 串口名称通常来自廉价 DIY 模块。一些加油机或 ATM 的非法附加装置曾使用此类主板，让附近的人通过蓝牙读取数据；相同模块也广泛用于打印机、汽车和自制设备。如果读卡器附近此信号很强，请谨慎并结合现场观察，但这不能证明存在盗刷装置。未发现也不代表安全（可能改名、使用经典蓝牙 HC-05/HC-06 或蜂窝网络）。Fieldwatch 不连接设备，也不尝试默认 PIN，且无法发现经典蓝牙 HC-05/HC-06。",
        builtIn = true,
        rules = listOf(
            bleName("HMSoft"),
            bleGlob("HMSoft*"),
            bleName("HM-10"),
            bleGlob("HM-10*"),
            bleName("CC41-A"),
            bleGlob("CC41*"),
            bleName("AT-09"),
            bleGlob("AT-09*"),
            bleName("JDY-08"),
            bleName("JDY-10"),
            bleName("JDY-16"),
            bleName("JDY-31"),
            bleGlob("JDY-*"),
            bleName("BT05"),
            bleName("MLT-BT05"),
            bleName("ESP32"),
            bleGlob("ESP32-*"),
        ),
    )

    private fun metaGlasses() = Fleet(
        id = "fleet-meta-glasses",
        name = "Ray-Ban / Meta glasses",
        enabled = true,
        colorIndex = Hue.GLASSES,
        kind = SignatureClass.GLASSES,
        matchAny = true,
        notes = "Ray-Ban Meta / Oakley Meta 智能眼镜，或 Quest 等 Meta 可穿戴设备。",
        attentionNote = "Meta / Luxottica BLE，通常来自 Ray-Ban Meta 智能眼镜。相同公司 ID 也用于 Quest 头显和其他 Meta 可穿戴设备。不能证明有人正在录制；未发现也不代表没有（可能已配对且静默、休眠或属于其他品牌）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            mfg(0x01AB),
            mfg(0x058E),
            mfg(0x0D53),
            bleName("Ray-Ban"),
            bleName("RayBan"),
            bleGlob("Ray-Ban*"),
            bleGlob("RayBan*"),
            bleName("Meta View"),
            bleName("Oakley Meta"),
            uuid("FEB7"),
            uuid("FEB8"),
        ),
    )

    private fun snapSpectacles() = Fleet(
        id = "fleet-snap-spectacles",
        name = "Snap Spectacles",
        enabled = true,
        colorIndex = Hue.GLASSES,
        kind = SignatureClass.GLASSES,
        matchAny = true,
        notes = "Snap Spectacles 或其他 Snap BLE 产品。",
        attentionNote = "Snapchat BLE 公司 ID，用于 Snap Spectacles，其他 Snap BLE 产品也可能匹配。不能证明正在录制，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            mfg(0x03C2),
            bleName("Snap Spectacles"),
            bleName("Spectacles"),
            bleGlob("Spectacles*"),
            uuid("FE45"),
        ),
    )

    private fun vuzix() = Fleet(
        id = "fleet-vuzix",
        name = "Vuzix",
        enabled = true,
        colorIndex = Hue.GLASSES,
        kind = SignatureClass.GLASSES,
        matchAny = true,
        notes = "Vuzix 智能眼镜或其他 Vuzix BLE 可穿戴设备。",
        attentionNote = "Vuzix BLE 眼镜。不能证明正在录制；未发现也不代表没有（可能已配对且静默、休眠或属于其他品牌）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            mfg(0x060C),
            bleName("Vuzix"),
            bleGlob("Vuzix*"),
        ),
    )

    private fun brilliantFrame() = Fleet(
        id = "fleet-brilliant-frame",
        name = "Brilliant Frame",
        enabled = true,
        colorIndex = Hue.GLASSES,
        kind = SignatureClass.GLASSES,
        matchAny = true,
        notes = "Brilliant Labs Frame AR 眼镜。",
        attentionNote = "Brilliant Labs Frame AR 眼镜，BLE 服务为 7A230001。不能证明有人正在录制；未发现也不代表没有（可能已关闭或属于其他品牌）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            uuid("7A230001-5475-A6A4-654C-576174636800"),
            bleName("Brilliant Frame"),
            bleGlob("Brilliant Frame*"),
        ),
    )

    private fun evenG1() = Fleet(
        id = "fleet-even-g1",
        name = "Even G1",
        enabled = true,
        colorIndex = Hue.GLASSES,
        kind = SignatureClass.GLASSES,
        matchAny = true,
        notes = "Even Realities G1 眼镜。仅按名称 Even G1 匹配。Nordic UART 过于通用，不适合作为识别规则。",
        attentionNote = "Even Realities G1 眼镜。仅在广播 Even G1 名称时匹配。不能证明正在录制；未发现也不代表没有（可能已关闭、改名或已配对且静默）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            bleName("Even G1"),
            bleGlob("Even G1*"),
        ),
    )

    private fun hak5Pineapple() = Fleet(
        id = "fleet-hak5-pineapple",
        name = "Hak5 Pineapple",
        enabled = true,
        colorIndex = Hue.HACKING,
        kind = SignatureClass.HACKING,
        matchAny = true,
        notes = "Hak5 WiFi Pineapple 的设置或管理热点。PineAP 仿冒的咖啡店 SSID 看起来与普通 Wi-Fi 相同，不会匹配此项。",
        attentionNote = "Hak5 WiFi Pineapple 设置或管理热点（Pineapple_XXXX）。这是管理无线接口，不涵盖 PineAP 可能仿冒的所有热点，后者看起来与普通咖啡店 Wi-Fi 相同。未发现不代表没有（可能改名或仅仿冒）。这里只是模式匹配，不能确认身份，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            glob("Pineapple_*"),
            name("Pineapple_"),
            name("WiFi Pineapple"),
            name("Hak5"),
            glob("Hak5*"),
        ),
    )

    private fun flipperZero() = Fleet(
        id = "fleet-flipper",
        name = "Flipper Zero",
        enabled = true,
        colorIndex = Hue.HACKING,
        kind = SignatureClass.HACKING,
        matchAny = true,
        notes = "Flipper Zero 或其他 Flipper Devices 产品。默认名称以 Flipper 开头，自定义固件可隐藏名称。",
        attentionNote = "Flipper Zero 或其他 Flipper Devices 产品的 BLE。默认名称以 Flipper 开头；新设备使用 IEEE OUI 0C:FA:22。自定义固件可修改名称和 MAC。不能证明正在攻击；未发现也不代表没有（可能关闭蓝牙或改名）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            oui("0C:FA:22"),
            bleName("Flipper"),
            bleGlob("Flipper*"),
            bleName("Flipper Zero"),
        ),
    )

    private fun pwnagotchi() = Fleet(
        id = "fleet-pwnagotchi",
        name = "Pwnagotchi",
        enabled = true,
        colorIndex = Hue.HACKING,
        kind = SignatureClass.HACKING,
        matchAny = true,
        notes = "Pwnagotchi 类 Wi-Fi 握手采集器。经典型号使用独特 BSSID 和 pwnagotchi 名称。",
        attentionNote = "Pwnagotchi 类 Wi-Fi 握手采集器。经典型号广播 BSSID de:ad:be:ef:de:ad。pwnagotchi 名称只是模式依据，不能证明正在攻击，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            MatchRule(RuleKind.MAC_PREFIX, text = "DE:AD:BE:EF:DE:AD"),
            name("pwnagotchi"),
            glob("pwnagotchi*"),
        ),
    )

    private fun marauderDeauther() = Fleet(
        id = "fleet-marauder",
        name = "Marauder / Deauther",
        enabled = true,
        colorIndex = Hue.HACKING,
        kind = SignatureClass.HACKING,
        matchAny = true,
        notes = "使用默认名称的 ESP32 Marauder 或 Spacehuhn 类 Wi-Fi 断连工具。相同主板也用于 DIY；改名设备不会匹配。",
        attentionNote = "ESP32 Marauder 或 Spacehuhn 类 Wi-Fi 断连工具的默认名称。相同主板也用于 DIY。不能证明正在攻击；未发现也不代表没有（可能改名）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("MarauderAP"),
            name("Marauder"),
            glob("Marauder*"),
            name("ESP32 Marauder"),
            name("Deauther"),
            glob("Deauther*"),
        ),
    )

    private fun ghostEsp() = Fleet(
        id = "fleet-ghostesp",
        name = "GhostESP",
        enabled = true,
        colorIndex = Hue.HACKING,
        kind = SignatureClass.HACKING,
        matchAny = true,
        notes = "GhostESP ESP32 安全审计固件，默认设置热点为 GhostNet。相同主板也用于 DIY；改名设备不会匹配。",
        attentionNote = "GhostESP ESP32 安全审计固件的默认热点（GhostNet）。相同主板也用于 DIY。不能证明正在攻击；未发现也不代表没有（可能改名）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            wifiName("GhostNet"),
            wifiGlob("GhostNet*"),
        ),
    )

    private fun bruceFirmware() = Fleet(
        id = "fleet-bruce",
        name = "Bruce",
        enabled = true,
        colorIndex = Hue.HACKING,
        kind = SignatureClass.HACKING,
        matchAny = true,
        notes = "Bruce ESP32 渗透测试固件，默认设置热点为 BruceNet。相同主板也用于 DIY；改名设备及恶意门户 SSID 不会匹配。",
        attentionNote = "Bruce ESP32 渗透测试固件的默认热点（BruceNet）。相同主板也用于 DIY。恶意门户 SSID 看起来与普通 Wi-Fi 相同，不会匹配此项。不能证明正在攻击，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            wifiName("BruceNet"),
            wifiGlob("BruceNet*"),
        ),
    )

    private fun porkchop() = Fleet(
        id = "fleet-porkchop",
        name = "Porkchop",
        enabled = true,
        colorIndex = Hue.HACKING,
        kind = SignatureClass.HACKING,
        matchAny = true,
        notes = "运行于 Cardputer 或 Cheap Yellow Display 的 Porkchop 渗透测试固件。默认热点名称为 PORKCHOP。仿冒 Apple / Android 的 BLE 垃圾广播不归入此项。",
        attentionNote = "M5PORKCHOP / Porkchop 便携 Wi-Fi 渗透测试固件（Cardputer 或 Cheap Yellow Display）。默认 CYD 远程热点名称为 PORKCHOP。BACON 模式的伪造热点使用厂商 IE 50:52:4B。未发现不代表没有（可能改名、仅被动接收或未启用热点）。这里只是模式匹配，不能确认身份或证明攻击，请结合现场观察。",
        builtIn = true,
        rules = listOf(
            name("PORKCHOP"),
            glob("PORKCHOP*"),
            glob("M5PORKCHOP*"),
            vendorIe("50:52:4B"),
        ),
    )

    private fun pokemonGoPlus() = Fleet(
        id = "fleet-pokemon-go-plus",
        name = "Pokemon GO Plus",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.WEARABLE,
        matchAny = true,
        notes = "Nintendo Pokémon GO Plus 或 Plus + 腕戴配件，并非 Joy-Con 或 Switch。",
        builtIn = true,
        rules = listOf(
            uuid("138C35B6-0000-1000-8000-00805F9B34FB"),
            uuid("21c50462-67cb-63a3-5c4c-82b5b9939aeb"),
            bleName("Pokemon GO Plus"),
            bleGlob("Pokemon GO Plus*"),
        ),
    )

    private fun hatch() = Fleet(
        id = "fleet-hatch",
        name = "Hatch",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Hatch Rest / Restore / Mini 助眠音响，常见的婴儿房或卧室背景信号。",
        builtIn = true,
        rules = listOf(
            mfg(0x0434),
            oui("C8:FA:9C"),
            bleName("Hatch Rest"),
            bleGlob("Hatch Rest*"),
            bleGlob("Hatch Restore*"),
            bleGlob("Hatch Mini*"),
        ),
    )

    private fun bhyve() = Fleet(
        id = "fleet-bhyve",
        name = "Orbit B-hyve",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Orbit B-hyve 水管定时器 / 灌溉设备。",
        builtIn = true,
        rules = listOf(
            oui("44:67:55"),
            uuid("FE32"),
            bleName("bhyve"),
            bleGlob("bhyve*"),
            bleGlob("B-hyve*"),
        ),
    )

    private fun samsungAppliance() = Fleet(
        id = "fleet-samsung-appliance",
        name = "Samsung appliance",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Samsung Family Hub 冰箱、炉灶或烤箱的设置 Wi-Fi，并非 SmartTag。",
        builtIn = true,
        rules = listOf(
            wifiGlob("[fridge]*"),
            wifiGlob("[oven]*"),
            wifiGlob("[range]*"),
            wifiGlob("[cooktop]*"),
            wifiGlob("[refrigerator]*"),
        ),
    )

    private fun ecoWater() = Fleet(
        id = "fleet-ecowater",
        name = "EcoWater",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "EcoWater 或软水机设置 Wi-Fi，属于家庭供水物联网设备。",
        builtIn = true,
        rules = listOf(
            wifiGlob("H2O-????????????"),
        ),
    )

    private fun fieldy() = Fleet(
        id = "fleet-fieldy",
        name = "Fieldy",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.WEARABLE,
        matchAny = true,
        notes = "Fieldy 挂件，可穿戴 AI 笔记设备。",
        attentionNote = "Fieldy 可穿戴 AI 笔记挂件，可录制并转写对话。不能证明有人正在录制你；未发现也不代表没有（可能已关闭、已配对且静默或属于其他品牌）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            bleName("Fieldy"),
            bleGlob("Fieldy*"),
        ),
    )

    private fun plaud() = Fleet(
        id = "fleet-plaud",
        name = "Plaud Note",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.WEARABLE,
        matchAny = true,
        notes = "Plaud Note / NotePin AI 会议录音设备。",
        attentionNote = "Plaud Note / NotePin AI 录音设备，可录制会议。不能证明有人正在录制你；未发现也不代表没有（可能已关闭、改名或属于其他品牌）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            bleName("Plaud Note"),
            bleGlob("Plaud Note*"),
            bleGlob("Plaud NotePin*"),
        ),
    )

    private fun limitlessPendant() = Fleet(
        id = "fleet-limitless",
        name = "Limitless Pendant",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.WEARABLE,
        matchAny = true,
        notes = "Limitless / Rewind AI 挂件，可穿戴对话录音设备。",
        attentionNote = "Limitless Pendant 可穿戴录音设备，BLE 服务为 632de001，可录制对话。不能证明有人正在录制你；未发现也不代表没有（可能已关闭、已配对且静默或属于其他品牌）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            uuid("632DE001-604C-446B-A80F-7963E950F3FB"),
            bleName("Limitless"),
            bleGlob("Limitless*"),
        ),
    )

    private fun beePendant() = Fleet(
        id = "fleet-bee",
        name = "Bee Pendant",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.WEARABLE,
        matchAny = true,
        notes = "Bee Pioneer 可穿戴录音设备（现属于 Amazon），可持续采集音频。",
        attentionNote = "Bee Pioneer 可穿戴录音设备（Amazon），BLE 服务为 03d5d5c4，可录制对话。不能证明有人正在录制你；未发现也不代表没有（可能已关闭或属于其他品牌）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            uuid("03D5D5C4-A86C-11EE-9D89-8F2089A49E7E"),
            bleName("Bee Pioneer"),
            bleGlob("Bee Pioneer*"),
        ),
    )

    private fun omiPendant() = Fleet(
        id = "fleet-omi",
        name = "Omi",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.WEARABLE,
        matchAny = true,
        notes = "Omi / OpenGlass 可穿戴录音设备或摄像眼镜。Arduino 默认服务 19B10000 过于通用，不适合作为识别规则。",
        attentionNote = "Omi 挂件或 OpenGlass 摄像眼镜，依据名称或 BLE 服务 23ba7924 匹配。可录制音频，OpenGlass 还配有摄像头。不能证明有人正在录制你；未发现也不代表没有（可能已关闭、改名或是使用其他名称的 DIY 主板）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            uuid("23BA7924-0000-1000-7450-346EAC492E92"),
            bleGlob("Omi"),
            bleGlob("Omi-*"),
            bleName("OpenGlass"),
            bleGlob("OpenGlass*"),
        ),
    )

    private fun friendPendant() = Fleet(
        id = "fleet-friend-pendant",
        name = "Friend Pendant",
        enabled = true,
        colorIndex = Hue.TRACKER,
        kind = SignatureClass.WEARABLE,
        matchAny = true,
        notes = "Friend AI 项链，可聆听对话的可穿戴陪伴设备。",
        attentionNote = "Friend Pendant 挂件 / 项链，BLE 服务为 1a3fd0e7，可聆听对话。不能证明有人正在录制你；未发现也不代表没有（可能已关闭或属于其他品牌）。请结合现场观察。",
        builtIn = true,
        rules = listOf(
            uuid("1A3FD0E7-B1F3-AC9E-2E49-B647B2C4F8DA"),
            bleName("Friend Pendant"),
            bleGlob("Friend Pendant*"),
        ),
    )

    private fun retailLedSign() = Fleet(
        id = "fleet-retail-led-sign",
        name = "Retail LED sign",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.SIGNAGE,
        matchAny = true,
        notes = "BLE LED 信息显示屏，广播名称是显示文字，而非产品名。",
        builtIn = true,
        rules = listOf(
            uuid("56D63956-93E7-11EE-B9D1-0242AC120002"),
        ),
    )

    private fun electronicShelfLabel() = Fleet(
        id = "fleet-esl",
        name = "Electronic shelf label",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.SIGNAGE,
        matchAny = true,
        notes = "使用蓝牙 ESL 服务的电子货架标签（商店价签）。多数 Hanshow / SES-imagotag 标签采用专用无线协议，不会匹配此项。",
        builtIn = true,
        rules = listOf(
            uuid("1857"),
        ),
    )

    private fun unifiProtect() = Fleet(
        id = "fleet-unifi-protect",
        name = "UniFi Protect",
        enabled = true,
        colorIndex = Hue.SURVEILLANCE,
        kind = SignatureClass.SURVEILLANCE,
        matchAny = true,
        notes = "处于 BLE 设置模式的 UniFi Protect Instant 摄像头，并非 UniFi Wi-Fi 接入点。",
        builtIn = true,
        rules = listOf(
            bleGlob("UVC G* Instant"),
            bleName("UVC G3 Instant"),
            bleName("UVC G4 Instant"),
            bleName("UVC G6 Instant"),
        ),
    )

    private fun teslaTstpms() = Fleet(
        id = "fleet-tesla-tstpms",
        name = "Tesla tsTPMS",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Tesla BLE 轮胎传感器。传感器唤醒时，解码字段可显示胎压、温度和电量。这里只是模式匹配，不能确定具体车辆。手机钥匙归入 Tesla 条目。",
        builtIn = true,
        decode = CatalogDecodes.teslaTstpms,
        rules = listOf(
            bleName("tsTPMS"),
            bleGlob("tsTPMS*"),
        ),
    )

    private fun radiacode() = Fleet(
        id = "fleet-radiacode",
        name = "RadiaCode",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "RadiaCode 手持辐射检测仪。",
        builtIn = true,
        rules = listOf(
            uuid("E63215E5-7003-49D8-96B0-B024798FB901"),
            bleName("RadiaCode"),
            bleGlob("RadiaCode*"),
        ),
    )

    private fun lgWebosTv() = Fleet(
        id = "fleet-lg-webos",
        name = "LG webOS TV",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "LG webOS 电视，未命名的 LG 无线设备也可能匹配此项。",
        builtIn = true,
        rules = listOf(
            uuid("FEB9"),
            bleName("webOS TV"),
            bleGlob("[LG] webOS*"),
            bleGlob("webOS TV*"),
        ),
    )

    private fun roku() = Fleet(
        id = "fleet-roku",
        name = "Roku",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Roku 流媒体棒或 Roku 电视，常为遥控器提供隐藏的 Wi-Fi Direct 热点，并非运营商路由器。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("DIRECT-roku*"),
                wifiGlob("DIRECT-Roku*"),
                wifiGlob("Roku-*"),
            ),
            ApVendorOuis.ROKU,
        ),
    )

    private fun nespresso() = Fleet(
        id = "fleet-nespresso",
        name = "Nespresso",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Nespresso 咖啡机（Vertuo / Barista）。",
        builtIn = true,
        rules = listOf(
            mfg(0x0225),
            uuid("06AA1910-F22A-11E3-9DAA-0002A5D5C51B"),
            uuid("65241910-0253-11E7-93AE-92361F002671"),
            uuid("96600100-526E-4676-A11A-AF1EB848165B"),
            bleName("Vertuo"),
            bleGlob("Vertuo*"),
            bleGlob("Venus_*"),
        ),
    )

    private fun epson() = Fleet(
        id = "fleet-epson",
        name = "Epson",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Epson EcoTank 或 WorkForce 打印机（Wi-Fi Direct 或 BLE）。",
        builtIn = true,
        rules = listOf(
            wifiGlob("*EPSON-ET-*"),
            wifiGlob("*EPSON-WF-*"),
            bleGlob("EPSON-ET-*"),
            bleGlob("EPSON-WF-*"),
            bleName("EPSON-ET"),
            bleName("EPSON-WF"),
        ),
    )

    private fun shokz() = Fleet(
        id = "fleet-shokz",
        name = "Shokz",
        enabled = true,
        colorIndex = Hue.AUDIO,
        kind = SignatureClass.AUDIO,
        matchAny = true,
        notes = "Shokz 骨传导耳机（OpenRun / OpenFit），佩戴于头部，并非追踪器。",
        builtIn = true,
        rules = listOf(
            bleName("Shokz"),
            bleName("OpenRun"),
            bleName("OpenFit"),
            bleGlob("LE-OpenRun*"),
            bleGlob("OpenRun*"),
            bleGlob("OpenFit*"),
        ),
    )

    private fun remoteId() = Fleet(
        id = "fleet-remote-id",
        name = "Remote ID",
        enabled = true,
        colorIndex = Hue.DRONE,
        kind = SignatureClass.DRONE,
        matchAny = true,
        notes = "飞行中的无人机数字标识（ASTM / FAA Remote ID）。解码字段可显示 ID、位置、航向和操作者信息。这里只是模式匹配，不能确认航空器注册号。原生 Android 往往无法接收 Wi-Fi Remote ID。",
        builtIn = true,
        decode = CatalogDecodes.remoteId,
        rules = listOf(
            uuid("FFFA"),
            vendorIe("FA:0B:BC"),
        ),
    )

    private fun skydio() = Fleet(
        id = "fleet-skydio",
        name = "Skydio",
        enabled = true,
        colorIndex = Hue.DRONE,
        kind = SignatureClass.DRONE,
        matchAny = true,
        notes = "Skydio 无人机（常见于美国公共安全机构和企业）。飞行中的 Remote ID 通常通过 Wi-Fi 发送，容易漏检；数字标识单独归入 Remote ID 条目。",
        builtIn = true,
        rules = listOf(
            name("Skydio"),
            glob("Skydio*"),
            bleGlob("Skydio*"),
            wifiGlob("Skydio*"),
        ),
    )

    private fun autel() = Fleet(
        id = "fleet-autel",
        name = "Autel",
        enabled = true,
        colorIndex = Hue.DRONE,
        kind = SignatureClass.DRONE,
        matchAny = true,
        notes = "Autel 无人机、遥控器或设置 Wi-Fi。飞行中的数字标识归入 Remote ID 条目。",
        builtIn = true,
        rules = listOf(
            name("Autel"),
            glob("Autel*"),
            wifiGlob("Autel_*"),
            bleGlob("Autel*"),
        ),
    )

    private fun parrot() = Fleet(
        id = "fleet-parrot",
        name = "Parrot",
        enabled = true,
        colorIndex = Hue.DRONE,
        kind = SignatureClass.DRONE,
        matchAny = true,
        notes = "Parrot ANAFI 或 Bebop 无人机。飞行中的数字标识归入 Remote ID 条目，不包括 Parrot 车载套件。",
        builtIn = true,
        rules = listOf(
            name("ANAFI"),
            glob("ANAFI*"),
            name("Bebop"),
            glob("Bebop*"),
            bleGlob("ANAFI*"),
            wifiGlob("ANAFI*"),
            bleGlob("Bebop*"),
            wifiGlob("Bebop*"),
        ),
    )

    private fun hoverAir() = Fleet(
        id = "fleet-hoverair",
        name = "HOVERAir",
        enabled = true,
        colorIndex = Hue.DRONE,
        kind = SignatureClass.DRONE,
        matchAny = true,
        notes = "HOVERAir 便携自拍无人机。飞行中的数字标识（PRO / PROMAX）归入 Remote ID 条目。",
        builtIn = true,
        rules = listOf(
            name("HOVERAir"),
            glob("HOVERAir*"),
            wifiGlob("Hover*"),
            wifiGlob("HoverX1*"),
            bleGlob("Hover*"),
            bleGlob("HOVERAir*"),
        ),
    )

    private fun cradlepoint() = Fleet(
        id = "fleet-cradlepoint",
        name = "Cradlepoint",
        enabled = true,
        colorIndex = Hue.LAW,
        kind = SignatureClass.LAW_ENFORCEMENT,
        matchAny = true,
        notes = "Cradlepoint 车载路由器（IBR / R 系列），常见于警务、急救、公用事业及商业车队。隐藏 SSID 仍可依据主板厂商匹配。",
        attentionNote = "Ericsson Cradlepoint 车载路由器（IBR / R 系列），常见于美国警务和公共安全车队，也用于公用事业、急救及商业车队。隐藏或改名的 SSID 仍可依据 CradlePoint IEEE OUI 匹配。这里只是模式匹配，不能确定具体机构或车辆，请结合现场观察。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiName("Cradlepoint"),
                wifiGlob("Cradlepoint*"),
                wifiGlob("IBR*"),
                wifiGlob("IBR900*"),
                wifiGlob("IBR1100*"),
                wifiGlob("IBR1700*"),
                wifiGlob("IBR600*"),
                wifiGlob("IBR600C*"),
                wifiGlob("IBR650*"),
                wifiGlob("IBR950*"),
                wifiGlob("IBR200*"),
                wifiGlob("R1900*"),
                wifiGlob("R2100*"),
                wifiGlob("R2105*"),
                wifiGlob("R920*"),
            ),
            ApVendorOuis.CRADLEPOINT,
        ),
    )

    private fun airlink() = Fleet(
        id = "fleet-airlink",
        name = "AirLink",
        enabled = true,
        colorIndex = Hue.LAW,
        kind = SignatureClass.LAW_ENFORCEMENT,
        matchAny = true,
        notes = "Sierra Wireless AirLink 车载 / 车队网关，常见于公共安全及商业车队。隐藏 SSID 仍可依据主板厂商匹配。",
        attentionNote = "Sierra Wireless AirLink 车载网关，常见于美国警务、公共安全及商业车队。隐藏或改名的 SSID 仍可依据 Sierra Wireless IEEE OUI 匹配。这里只是模式匹配，不能确定具体机构或车辆，请结合现场观察。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiName("AirLink"),
                wifiGlob("AirLink*"),
                wifiGlob("AIRLINK*"),
            ),
            ApVendorOuis.AIRLINK,
        ),
    )

    private fun compex() = Fleet(
        id = "fleet-compex",
        name = "Compex",
        enabled = true,
        colorIndex = Hue.LAW,
        kind = SignatureClass.LAW_ENFORCEMENT,
        matchAny = true,
        notes = "Compex 车载或机构 Wi-Fi 接入点，相同主板也用于其他 Compex 无线设备。",
        attentionNote = "Compex Wi-Fi 接入点，部分美国公共安全机构用于车载设备。相同 IEEE OUI 也用于其他 Compex 无线设备。这里只是模式匹配，不能确定具体机构，请结合现场观察。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("114K-*"),
            ),
            ApVendorOuis.COMPEX,
        ),
    )

    private fun novatelWireless() = Fleet(
        id = "fleet-novatel",
        name = "Novatel Wireless",
        enabled = true,
        colorIndex = Hue.LAW,
        kind = SignatureClass.LAW_ENFORCEMENT,
        matchAny = true,
        notes = "Novatel Wireless / Inseego 车载无线设备。相同前缀也用于部分消费级 MiFi 热点。",
        attentionNote = "Novatel Wireless / Inseego OUI 28:80:A2，曾在公共安全车载热点观察中出现。相同前缀也用于部分 Inseego 消费级 MiFi 设备。这里只是模式匹配，不能确定具体机构，请结合现场观察。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.NOVATEL),
    )

    private fun utilityInc() = Fleet(
        id = "fleet-utility-inc",
        name = "Utility Inc",
        enabled = true,
        colorIndex = Hue.LAW,
        kind = SignatureClass.LAW_ENFORCEMENT,
        matchAny = true,
        notes = "Utility, Inc 车载或公共安全接入点。",
        attentionNote = "Utility, Inc 无线设备，曾在公共安全车载热点观察中出现。这里只是模式匹配，不能确定具体机构，请结合现场观察。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.UTILITY_INC),
    )

    private fun cisco() = Fleet(
        id = "fleet-cisco",
        name = "Cisco",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Cisco Aironet / Catalyst / Business 接入点。Fieldwatch 接收接入点信标，无法发现手机或交换机。Meraki 单独列出。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Cisco*"),
                wifiGlob("tsunami"),
            ),
            ApVendorOuis.CISCO + ApVendorOuis.CISCO_SPVTG,
        ),
    )

    private fun aruba() = Fleet(
        id = "fleet-aruba",
        name = "Aruba",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "HPE Aruba 园区或 Instant On Wi-Fi 接入点。此处 HPE BSSID 代表接入点，而非服务器，也不是 HP 打印机。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Aruba*"),
                wifiGlob("SetMeUp*"),
                wifiGlob("InstantOn*"),
            ),
            ApVendorOuis.HPE,
        ),
    )

    private fun ruckus() = Fleet(
        id = "fleet-ruckus",
        name = "Ruckus",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "RUCKUS Unleashed / ZoneFlex 园区接入点，并非 Arris 有线调制解调器系列。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Ruckus*"),
                wifiGlob("Configure.Me*"),
                wifiGlob("Config.Me*"),
            ),
            ApVendorOuis.RUCKUS,
        ),
    )

    private fun ruijie() = Fleet(
        id = "fleet-ruijie",
        name = "Ruijie",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Ruijie / Reyee 园区或中小企业接入点。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("@Reyee*"),
                wifiGlob("Reyee*"),
                wifiGlob("Ruijie*"),
            ),
            ApVendorOuis.RUIJIE,
        ),
    )

    private fun fortinet() = Fleet(
        id = "fleet-fortinet",
        name = "Fortinet",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Fortinet FortiAP / FortiWiFi 园区或分支机构接入点。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Fortinet*"),
                wifiGlob("FortiAP*"),
                wifiGlob("FAP-config*"),
            ),
            ApVendorOuis.FORTINET,
        ),
    )

    private fun mikrotik() = Fleet(
        id = "fleet-mikrotik",
        name = "MikroTik",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "MikroTik RouterOS 接入点或便携路由器。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("MikroTik*"),
            ),
            ApVendorOuis.MIKROTIK,
        ),
    )

    private fun engenius() = Fleet(
        id = "fleet-engenius",
        name = "EnGenius",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "EnGenius Cloud / ECW 接入点。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("EnGenius*"),
                wifiGlob("EnMGMT*"),
            ),
            ApVendorOuis.ENGENIUS,
        ),
    )

    private fun zyxel() = Fleet(
        id = "fleet-zyxel",
        name = "Zyxel",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Zyxel 家用或中小企业网关 / 接入点。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Zyxel*"),
            ),
            ApVendorOuis.ZYXEL,
        ),
    )

    private fun peplink() = Fleet(
        id = "fleet-peplink",
        name = "Peplink",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Peplink / Pepwave 便携或分支机构路由器。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Peplink*"),
                wifiGlob("Pepwave*"),
            ),
            ApVendorOuis.PEPLINK,
        ),
    )

    private fun openwrt() = Fleet(
        id = "fleet-openwrt",
        name = "OpenWrt",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "刷入固件后尚未改名、保留 OpenWrt 出厂 SSID 的便携或 DIY 路由器。",
        builtIn = true,
        rules = listOf(
            wifiGlob("OpenWrt*"),
        ),
    )

    private fun arris() = Fleet(
        id = "fleet-arris",
        name = "Arris",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Arris / SURFboard 有线网关。即使运营商已修改 Wi-Fi 名称，仍可依据主板厂商匹配。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Arris*"),
                wifiGlob("SURFboard*"),
            ),
            ApVendorOuis.ARRIS + ApVendorOuis.COMMSCOPE,
        ),
    )

    private fun mist() = Fleet(
        id = "fleet-mist",
        name = "Mist",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Juniper Mist 园区接入点。云管理 SSID 是场所名称，因此依据主板厂商匹配。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.MIST),
    )

    private fun tMobile() = Fleet(
        id = "fleet-tmobile",
        name = "T-Mobile",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "T-Mobile Home Internet 网关或热点。网关通常由 HUMAX / Arcadyan / Askey 代工。",
        builtIn = true,
        rules = listOf(
            wifiGlob("TMOBILE*"),
            wifiGlob("T-Mobile*"),
        ),
    )

    private fun humax() = Fleet(
        id = "fleet-humax",
        name = "HUMAX",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "HUMAX 5G 或有线网关，现场常见于 T-Mobile Home Internet。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.HUMAX),
    )

    private fun sagemcom() = Fleet(
        id = "fleet-sagemcom",
        name = "Sagemcom",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Sagemcom 运营商网关，常为 Comcast 等有线运营商代工。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.SAGEMCOM),
    )

    private fun arcadyan() = Fleet(
        id = "fleet-arcadyan",
        name = "Arcadyan",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Arcadyan 运营商网关或 Mesh，常为 Verizon / T-Mobile 代工。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.ARCADYAN),
    )

    private fun askey() = Fleet(
        id = "fleet-askey",
        name = "Askey",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Askey 5G / 运营商网关，常为 T-Mobile Home Internet 代工。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.ASKEY),
    )

    private fun calix() = Fleet(
        id = "fleet-calix",
        name = "Calix",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Calix 光纤网关（GigaSpire 系列）。改名后仍可依据主板厂商匹配。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.CALIX),
    )

    private fun nokiaNsn() = Fleet(
        id = "fleet-nokia",
        name = "Nokia",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Nokia 运营商网关或小型基站，并非 Nokia 手机。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.NOKIA_NSN),
    )

    private fun airties() = Fleet(
        id = "fleet-airties",
        name = "AirTies",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "AirTies 运营商 Mesh 扩展器，属于运营商提供的家庭 Mesh。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.AIRTIES),
    )

    private fun tenda() = Fleet(
        id = "fleet-tenda",
        name = "Tenda",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Tenda 消费级路由器或扩展器。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Tenda*"),
                wifiName("Tenda"),
            ),
            ApVendorOuis.TENDA,
        ),
    )

    private fun wavlink() = Fleet(
        id = "fleet-wavlink",
        name = "WAVLINK",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "WAVLINK 消费级便携或家用路由器。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("WAVLINK*"),
                wifiGlob("Wavlink*"),
            ),
            ApVendorOuis.WINSTARS,
        ),
    )

    private fun sercomm() = Fleet(
        id = "fleet-sercomm",
        name = "Sercomm",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Sercomm 运营商网关，常见的有线 / 光纤代工设备。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.SERCOMM),
    )

    private fun luxul() = Fleet(
        id = "fleet-luxul",
        name = "Luxul",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Luxul / Legrand 小型企业接入点。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.LUXUL),
    )

    private fun sophos() = Fleet(
        id = "fleet-sophos",
        name = "Sophos",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Sophos 防火墙或接入点，属于园区 / 中小企业 Wi-Fi，并非摄像杆。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.SOPHOS),
    )

    private fun aumovio() = Fleet(
        id = "fleet-aumovio",
        name = "AUMOVIO",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "采用 AUMOVIO（原 Continental）模块的车载 Wi-Fi，属于车辆接入点，并非运营商路由器。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.AUMOVIO),
    )

    private fun centuryLink() = Fleet(
        id = "fleet-centurylink",
        name = "CenturyLink",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "使用 CenturyLink 出厂名称的网关。改名的光纤 Wi-Fi 不会匹配此项。",
        builtIn = true,
        rules = listOf(
            wifiGlob("CenturyLink*"),
        ),
    )

    private fun gmHotspot() = Fleet(
        id = "fleet-gm-hotspot",
        name = "GM hotspot",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "GM 车载热点（Cadillac、GMC、Buick）。myChevrolet 单独列出。BSSID 经常随机化。",
        builtIn = true,
        rules = listOf(
            mfg(0x0068),
            wifiGlob("myCadillac*"),
            wifiGlob("myGMC*"),
            wifiGlob("myBuick*"),
            wifiGlob("CADILLAC*"),
            wifiGlob("BUICK*"),
            wifiGlob("CHEVROLET*"),
        ),
    )

    private fun audiMmi() = Fleet(
        id = "fleet-audi-mmi",
        name = "Audi MMI",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Audi 车载 MMI 热点，使用车辆出厂名称，并非经销商网络。",
        builtIn = true,
        rules = listOf(
            mfg(0x010E),
            bleName("Audi"),
            wifiGlob("Audi_MMI_*"),
            wifiGlob("Audi MMI*"),
        ),
    )

    private fun extremeNetworks() = Fleet(
        id = "fleet-extreme",
        name = "Extreme",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Extreme Networks 园区接入点。云管理 SSID 是场所名称，因此依据主板厂商匹配。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.EXTREME),
    )

    private fun adtran() = Fleet(
        id = "fleet-adtran",
        name = "Adtran",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Adtran 光纤网关，常为 CenturyLink / Lumen / Quantum Fiber 代工。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Adtran*"),
            ),
            ApVendorOuis.ADTRAN,
        ),
    )

    private fun cambium() = Fleet(
        id = "fleet-cambium",
        name = "Cambium",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Cambium 或 IgniteNet 室外 / 无线运营商接入点。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Cambium*"),
                wifiGlob("cnPilot*"),
                wifiGlob("IgniteNet*"),
            ),
            ApVendorOuis.CAMBIUM,
        ),
    )

    private fun trendnet() = Fleet(
        id = "fleet-trendnet",
        name = "TRENDnet",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "TRENDnet 消费级接入点。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("TRENDnet*"),
            ),
            ApVendorOuis.TRENDNET,
        ),
    )

    private fun cudy() = Fleet(
        id = "fleet-cudy",
        name = "Cudy",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Cudy 便携或家用路由器。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Cudy*"),
            ),
            ApVendorOuis.CUDY,
        ),
    )

    private fun snapAv() = Fleet(
        id = "fleet-snapav",
        name = "SnapAV",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.HOME,
        matchAny = true,
        notes = "Control4 / Wattbox 家庭影音处理器或电源设备。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Control4*"),
                wifiGlob("Wattbox*"),
                wifiGlob("WattBox*"),
            ),
            ApVendorOuis.SNAPAV,
        ),
    )

    private fun vantiva() = Fleet(
        id = "fleet-vantiva",
        name = "Vantiva",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Vantiva（原 Technicolor）运营商网关。即使运营商已修改 Wi-Fi 名称，仍可依据主板厂商匹配。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Technicolor*"),
                wifiGlob("THOMSON*"),
                wifiGlob("Vantiva*"),
            ),
            ApVendorOuis.VANTIVA,
        ),
    )

    private fun hitron() = Fleet(
        id = "fleet-hitron",
        name = "Hitron",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Hitron 有线网关，常为 Xfinity 代工，也可能匹配 Xfinity 名称条目。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Hitron*"),
            ),
            ApVendorOuis.HITRON,
        ),
    )

    private fun actiontec() = Fleet(
        id = "fleet-actiontec",
        name = "Actiontec",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Actiontec FiOS / Frontier 网关，常为 Verizon 设备，也可能匹配 Verizon 名称条目。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Actiontec*"),
            ),
            ApVendorOuis.ACTIONTEC,
        ),
    )

    private fun buffalo() = Fleet(
        id = "fleet-buffalo",
        name = "Buffalo",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Buffalo AirStation 家用路由器。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Buffalo*"),
                wifiGlob("AirStation*"),
            ),
            ApVendorOuis.BUFFALO,
        ),
    )

    private fun grandstream() = Fleet(
        id = "fleet-grandstream",
        name = "Grandstream",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Grandstream GWN 办公接入点。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Grandstream*"),
                wifiGlob("GWN*"),
            ),
            ApVendorOuis.GRANDSTREAM,
        ),
    )

    private fun edgecore() = Fleet(
        id = "fleet-edgecore",
        name = "Edgecore",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Edgecore 园区或开放式 Wi-Fi 接入点。云管理 SSID 是场所名称，因此依据主板厂商匹配。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.EDGECORE),
    )

    private fun watchGuard() = Fleet(
        id = "fleet-watchguard-ap",
        name = "WatchGuard AP",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "WatchGuard 防火墙或接入点，并非 WatchGuard Video 随身摄像头。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.WATCHGUARD),
    )

    private fun mojo() = Fleet(
        id = "fleet-mojo",
        name = "Mojo",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Mojo / Arista Cognitive Wi-Fi 园区接入点。",
        builtIn = true,
        rules = withWifiOuis(emptyList(), ApVendorOuis.MOJO),
    )

    private fun winegard() = Fleet(
        id = "fleet-winegard",
        name = "Winegard",
        enabled = true,
        colorIndex = Hue.VEHICLE,
        kind = SignatureClass.VEHICLE,
        matchAny = true,
        notes = "Winegard 房车或船用 Wi-Fi 天线 / 路由器。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Winegard*"),
            ),
            ApVendorOuis.WINEGARD,
        ),
    )

    private fun inseego() = Fleet(
        id = "fleet-inseego",
        name = "Inseego",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Inseego 5G / MiFi 热点。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Inseego*"),
            ),
            ApVendorOuis.INSEEGO,
        ),
    )

    private fun franklin() = Fleet(
        id = "fleet-franklin",
        name = "Franklin",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Franklin 5G / LTE 家庭互联网网关（通常由运营商提供）。访客 SSID 仍可匹配。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("RG3100*"),
            ),
            ApVendorOuis.FRANKLIN,
        ),
    )

    private fun synology() = Fleet(
        id = "fleet-synology",
        name = "Synology",
        enabled = true,
        colorIndex = Hue.HOME_CAM,
        kind = SignatureClass.ISP,
        matchAny = true,
        notes = "Synology NAS 或路由器接入点。",
        builtIn = true,
        rules = withWifiOuis(
            listOf(
                wifiGlob("Synology*"),
            ),
            ApVendorOuis.SYNOLOGY,
        ),
    )

    private fun honeywellXenonHc() = Fleet(
        id = "fleet-honeywell-xenon-hc",
        name = "Honeywell Xenon HC",
        enabled = true,
        colorIndex = Hue.HEALTH,
        kind = SignatureClass.HEALTH,
        matchAny = true,
        notes = "Honeywell Xenon 医疗条码扫描器或充电底座（白色、可消毒），用于诊所或医院。并非家用恒温器，也不是仅用于仓库的 Xenon。",
        builtIn = true,
        rules = listOf(
            bleGlob("Xenon_*HC*"),
            bleGlob("Xenon_CCB-U00-H*"),
            bleName("CCB-U00-HC"),
            bleGlob("1962h*"),
            bleGlob("1952h*"),
            bleGlob("1902h*"),
        ),
    )

    private fun omronHealthcare() = Fleet(
        id = "fleet-omron",
        name = "Omron",
        enabled = true,
        colorIndex = Hue.HEALTH,
        kind = SignatureClass.HEALTH,
        matchAny = true,
        notes = "Omron 血压计或体脂秤，用于家庭或诊所健康监测，并非 Omron 工业设备。",
        builtIn = true,
        rules = listOf(
            mfg(0x020E),
            bleName("OMRON"),
            bleGlob("OMRON*"),
            bleGlob("HEM-*"),
            bleGlob("BLESmart_*"),
        ),
    )

    private fun withings() = Fleet(
        id = "fleet-withings",
        name = "Withings",
        enabled = true,
        colorIndex = Hue.HEALTH,
        kind = SignatureClass.HEALTH,
        matchAny = true,
        notes = "Withings（Nokia Health）体重秤或 BPM Connect 血压计，并非 Nokia 手机或运营商网关。",
        builtIn = true,
        rules = listOf(
            bleName("Withings"),
            bleGlob("Withings*"),
            bleGlob("WBS0*"),
            bleName("BPM Connect"),
        ),
    )

    private fun dexcom() = Fleet(
        id = "fleet-dexcom",
        name = "Dexcom",
        enabled = true,
        colorIndex = Hue.HEALTH,
        kind = SignatureClass.HEALTH,
        matchAny = true,
        notes = "Dexcom 连续血糖监测仪（G6 / G7）。这里只是模式匹配，不能确定具体患者。",
        builtIn = true,
        rules = listOf(
            bleName("Dexcom"),
            bleGlob("Dexcom*"),
        ),
    )

    private fun oui(prefix: String) = MatchRule(RuleKind.OUI, text = prefix)
    private fun vendorIe(prefix: String) = MatchRule(RuleKind.VENDOR_IE_OUI, text = prefix)
    private fun name(text: String) = MatchRule(RuleKind.NAME_CONTAINS, text = text)
    private fun glob(pattern: String) = MatchRule(RuleKind.NAME_GLOB, text = pattern)
    private fun bleName(text: String) =
        MatchRule(RuleKind.NAME_CONTAINS, text = text, radio = RadioKind.BLE)
    private fun bleGlob(pattern: String) =
        MatchRule(RuleKind.NAME_GLOB, text = pattern, radio = RadioKind.BLE)
    private fun svcData(uuid: String, prefix: String) =
        MatchRule(RuleKind.SERVICE_DATA, text = uuid, dataPrefixHex = prefix, radio = RadioKind.BLE)
    /** Service data for [uuid] with any payload (DULT FCB2). */
    private fun svcAny(uuid: String) =
        MatchRule(RuleKind.SERVICE_DATA, text = uuid, dataPrefixHex = "", radio = RadioKind.BLE)
    private fun svcContainsAscii(text: String) = MatchRule(
        RuleKind.SERVICE_DATA,
        text = "",
        dataPrefixHex = text.encodeToByteArray().joinToString("") { "%02X".format(it) },
        radio = RadioKind.BLE,
    )
    private fun wifiName(text: String) =
        MatchRule(RuleKind.NAME_CONTAINS, text = text, radio = RadioKind.WIFI)
    private fun wifiGlob(pattern: String) =
        MatchRule(RuleKind.NAME_GLOB, text = pattern, radio = RadioKind.WIFI)
    private fun wifiOui(prefix: String) =
        MatchRule(RuleKind.OUI, text = prefix, radio = RadioKind.WIFI)
    private fun withWifiOuis(base: List<MatchRule>, ouis: List<String>) =
        base + ouis.map { wifiOui(it) }
    private fun uuid(short: String) = MatchRule(RuleKind.SERVICE_UUID, text = short)
    private fun mfg(id: Int) = MatchRule(RuleKind.MANUFACTURER_ID, companyId = id)
    private fun mfgData(id: Int, prefix: String) =
        MatchRule(RuleKind.MANUFACTURER_DATA, companyId = id, dataPrefixHex = prefix)

    fun newBlankFleet(): Fleet = Fleet(
        id = UUID.randomUUID().toString(),
        name = "新特征",
        enabled = true,
        matchAny = true,
        colorIndex = 0,
        kind = SignatureClass.OTHER,
        rules = emptyList(),
    )
}
