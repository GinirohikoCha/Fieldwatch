package app.fieldwatch.ui.screen

import android.app.ActivityManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.PowerManager
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import app.fieldwatch.ui.component.FieldwatchFilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import app.fieldwatch.ui.component.FieldwatchActionButton
import app.fieldwatch.ui.component.FieldwatchOutlinedField
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import app.fieldwatch.ui.component.FieldwatchSlider
import androidx.compose.material3.Surface
import app.fieldwatch.ui.component.FieldwatchSwitch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import app.fieldwatch.R
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import app.fieldwatch.domain.AlertVoiceWhat
import app.fieldwatch.domain.AppSettings
import app.fieldwatch.domain.ScanIntensity
import app.fieldwatch.domain.TakDefaults
import app.fieldwatch.domain.TakFeedStatus
import app.fieldwatch.domain.TakPublish
import app.fieldwatch.domain.TakUdpPreset
import app.fieldwatch.radio.WifiRadio
import app.fieldwatch.ui.NestedTabInsets
import app.fieldwatch.ui.NestedTopBar
import app.fieldwatch.ui.FieldwatchUi
import app.fieldwatch.ui.FieldwatchViewModel
import app.fieldwatch.ui.component.SectionCard
import app.fieldwatch.ui.component.FieldwatchFilterChip
import app.fieldwatch.ui.component.StableCaption
import app.fieldwatch.ui.component.StickyHeight
import java.net.Inet4Address
import java.net.NetworkInterface

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun SettingsScreen(
    state: FieldwatchUi,
    vm: FieldwatchViewModel,
    onRadioBookmarks: () -> Unit,
    onShowLiveTour: () -> Unit = {},
) {
    val context = LocalContext.current
    val settings = state.settings
    val saveSignatures = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("application/json"),
    ) { uri -> uri?.let(vm::saveSignaturesToUri) }
    val importSignatures = rememberLauncherForActivityResult(
        ActivityResultContracts.OpenDocument(),
    ) { uri -> uri?.let(vm::importSignaturesFromUri) }
    val saveSettings = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("application/json"),
    ) { uri -> uri?.let(vm::saveSettingsToUri) }
    val importSettings = rememberLauncherForActivityResult(
        ActivityResultContracts.OpenDocument(),
    ) { uri -> uri?.let(vm::importSettingsFromUri) }
    var confirmRestore by remember { mutableStateOf(false) }
    Scaffold(
        contentWindowInsets = NestedTabInsets,
        topBar = { NestedTopBar("设置") },
    ) { pad ->
        Column(
            Modifier
                .padding(pad)
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            SectionCard("外观") {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("夜间模式", Modifier.weight(1f))
                FieldwatchSwitch(settings.nightMode, { on -> vm.updateSettings { it.copy(nightMode = on) } })
            }
            Text(
                "默认关闭。使用黑底红色的现场显示，让标签、文字和信号标记" +
                    "在黑暗环境观测时不产生绿色或蓝色亮光。背景保持深色，" +
                    "手机亮度保持不变。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("保持屏幕常亮", Modifier.weight(1f))
                FieldwatchSwitch(settings.keepScreenOn, { on -> vm.updateSettings { it.copy(keepScreenOn = on) } })
            }
            Text(
                "默认开启。在 Fieldwatch 打开时防止屏幕休眠，避免熄屏后 BLE 被系统暂停。离开应用后仍会通过前台通知继续扫描。将手机放入口袋时可关闭。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("隐私模式", Modifier.weight(1f))
                FieldwatchSwitch(settings.demoMode, { on -> vm.updateSettings { it.copy(demoMode = on) } })
            }
            Text(
                "将实时、雷达、时间线、详情、信号追踪、命名设备和关注列表卡片中每个 MAC 的后三组字节隐藏为 **:**:**，使屏幕和观测报告不显示完整地址。最近 GPS 定位以及观测总结／AI 导出／详情分享中的坐标显示为“已隐藏”，这些报告也会省略街道名称。保留前三组字节（OUI／厂商前缀）。默认关闭。“在线地名与地图”开启时，“报告 → 轨迹”仍会加载地图。日志、匹配、筛选、追踪计算、随行和已保存特征仍使用真实 MAC 与 GPS。如已开启 TAK／CoT 推送，此模式会暂停推送，防止完整 MAC 和坐标发送到局域网。需要在屏幕上查看完整地址或坐标时，请关闭此模式。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            }

            SectionCard("扫描") {
            val label = when (settings.intensity) {
                ScanIntensity.SAVER -> "省电"
                ScanIntensity.BALANCED -> "均衡"
                ScanIntensity.PERFORMANCE -> "高性能"
            }
            Text("扫描强度 · $label")
            FieldwatchSlider(
                value = settings.intensity.ordinal.toFloat(),
                onValueChange = { v ->
                    val next = ScanIntensity.entries[v.toInt().coerceIn(0, 2)]
                    vm.updateSettings { it.copy(intensity = next) }
                },
                valueRange = 0f..2f,
                steps = 1,
            )
            Text(
                "Wi-Fi 采用批量扫描：手机一次获取所有 AP，然后必须等待。高性能模式约每 30 秒请求一次，这是不超过系统“每两分钟四次扫描”限制的最快频率。期间 BLE 仍持续接收。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            StableCaption(
                state.throttleHint.ifBlank { " " },
                "Wi-Fi 正等待系统",
                "Wi-Fi 正在扫描",
                "Wi-Fi 下次扫描 99 秒",
                " ",
            )

            val lifecycleOwner = LocalLifecycleOwner.current
            var osThrottled by remember { mutableStateOf(WifiRadio.osScanThrottled(context)) }
            var backgroundAllowed by remember { mutableStateOf(isBackgroundUsageAllowed(context)) }
            var unrestricted by remember { mutableStateOf(isIgnoringBatteryOptimizations(context)) }
            var needDevOptions by remember { mutableStateOf(false) }
            var batteryGate by remember { mutableStateOf<BatteryAndroidGate?>(null) }
            DisposableEffect(lifecycleOwner) {
                val obs = LifecycleEventObserver { _, event ->
                    if (event == Lifecycle.Event.ON_RESUME) {
                        osThrottled = WifiRadio.osScanThrottled(context)
                        backgroundAllowed = isBackgroundUsageAllowed(context)
                        unrestricted = isIgnoringBatteryOptimizations(context)
                    }
                }
                lifecycleOwner.lifecycle.addObserver(obs)
                onDispose { lifecycleOwner.lifecycle.removeObserver(obs) }
            }
            val fastActive = settings.wifiFastScan && !osThrottled
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("加快 Wi-Fi AP 扫描", Modifier.weight(1f))
                FieldwatchSwitch(
                    checked = settings.wifiFastScan,
                    onCheckedChange = { on ->
                        if (!on) {
                            vm.updateSettings { it.copy(wifiFastScan = false) }
                        } else if (!osThrottled) {
                            vm.updateSettings { it.copy(wifiFastScan = true) }
                        } else {
                            needDevOptions = true
                        }
                    },
                )
            }
            StableCaption(
                when {
                    Build.VERSION.SDK_INT < 30 ->
                        "需要 Android 11 及以上版本，Fieldwatch 才能读取系统是否仍在限制扫描。本机无法确认，因此此开关保持关闭。"
                    fastActive ->
                        "已开启。Fieldwatch 约每 8 秒请求一次新的 AP 列表，会增加耗电和发热。如果系统开始拒绝扫描，应用会降低频率。"
                    settings.wifiFastScan && osThrottled ->
                        "已保存为开启，但尚未生效：Android 的 Wi-Fi 扫描节流仍已开启。请在开发者选项中关闭后返回。"
                    else ->
                        "原生 Android 每两分钟约允许扫描 AP 四次。需在开发者选项中关闭“Wi-Fi 扫描节流”后，才能加快扫描。Fieldwatch 开启前会检查该系统开关，无法代你修改。"
                },
                "需要 Android 11 及以上版本，Fieldwatch 才能读取系统是否仍在限制扫描。本机无法确认，因此此开关保持关闭。",
                "已开启。Fieldwatch 约每 8 秒请求一次新的 AP 列表，会增加耗电和发热。如果系统开始拒绝扫描，应用会降低频率。",
                "已保存为开启，但尚未生效：Android 的 Wi-Fi 扫描节流仍已开启。请在开发者选项中关闭后返回。",
                "原生 Android 每两分钟约允许扫描 AP 四次。需在开发者选项中关闭“Wi-Fi 扫描节流”后，才能加快扫描。Fieldwatch 开启前会检查该系统开关，无法代你修改。",
            )
            if (needDevOptions) {
                AlertDialog(
                    onDismissRequest = { needDevOptions = false },
                    title = { Text("需要开发者选项") },
                    text = {
                        Text(
                            if (Build.VERSION.SDK_INT < 30) {
                                "本机系统早于 Android 11，Fieldwatch 无法读取系统的 Wi-Fi 扫描节流开关，因此保持关闭快速 AP 扫描。"
                            } else {
                                "Android 仍在限制 Wi-Fi 扫描（每两分钟约四次）。关闭该限制后，Fieldwatch 才能开启快速 Wi-Fi AP 扫描。\n\n" +
                                    "请启用开发者选项（在“关于手机”中连续点按“版本号”七次），然后进入“设置 → 开发者选项 → Wi-Fi 扫描节流”并关闭。返回后再次打开此开关。"
                            },
                        )
                    },
                    confirmButton = {
                        if (Build.VERSION.SDK_INT >= 30) {
                            TextButton(
                                onClick = {
                                    needDevOptions = false
                                    runCatching {
                                        context.startActivity(Intent(Settings.ACTION_APPLICATION_DEVELOPMENT_SETTINGS))
                                    }
                                },
                            ) { Text("打开开发者选项") }
                        } else {
                            TextButton(onClick = { needDevOptions = false }) { Text("确定") }
                        }
                    },
                    dismissButton = {
                        if (Build.VERSION.SDK_INT >= 30) {
                            TextButton(onClick = { needDevOptions = false }) { Text("暂不") }
                        }
                    },
                )
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("允许后台运行", Modifier.weight(1f))
                FieldwatchSwitch(
                    checked = backgroundAllowed,
                    onCheckedChange = { batteryGate = BatteryAndroidGate.BACKGROUND },
                )
            }
            Text(
                "对应 Android 的“允许后台运行”。点按打开 Fieldwatch 的电池页面，" +
                    "使用其中的开关，返回后 Fieldwatch 会更新状态。关闭时，系统可能在你离开应用后" +
                    "立即停止扫描。此设置独立于“保持屏幕常亮”。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("电池使用不受限制", Modifier.weight(1f))
                FieldwatchSwitch(
                    checked = unrestricted,
                    onCheckedChange = { batteryGate = BatteryAndroidGate.UNRESTRICTED },
                )
            }
            Text(
                "对应 Android 的“不受限制”电池模式。部分手机（包括三星）不会" +
                    "直接显示此选项。若只看到“允许后台运行”，请点按该行进入，" +
                    "再选择“不受限制”。返回后 Fieldwatch 会更新状态。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            if (batteryGate != null) {
                val background = batteryGate == BatteryAndroidGate.BACKGROUND
                AlertDialog(
                    onDismissRequest = { batteryGate = null },
                    title = {
                        Text(if (background) "允许后台运行" else "电池使用不受限制")
                    },
                    text = {
                        Text(
                            if (background) {
                                "下一页是 Fieldwatch 的电池设置，请使用“允许后台运行”开关。" +
                                    "返回后 Fieldwatch 会同步此设置。"
                            } else {
                                "部分手机（包括三星）不会直接显示“不受限制／" +
                                    "优化／受限制”。若只看到“允许后台运行”，" +
                                    "请点按该行文字（不是蓝色开关）进入，" +
                                    "然后选择“不受限制”。返回后 Fieldwatch 会同步此设置。"
                            },
                        )
                    },
                    confirmButton = {
                        TextButton(
                            onClick = {
                                val gate = batteryGate
                                batteryGate = null
                                openAppBatteryPage(
                                    context,
                                    highlightBackground = gate == BatteryAndroidGate.BACKGROUND,
                                )
                            },
                        ) { Text("打开 Android 设置") }
                    },
                    dismissButton = {
                        TextButton(onClick = { batteryGate = null }) { Text("暂不") }
                    },
                )
            }
            }

            SectionCard("关注列表") {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("关注警报", Modifier.weight(1f))
                FieldwatchSwitch(settings.alertsEnabled, { on -> vm.updateSettings { it.copy(alertsEnabled = on) } })
            }
            Text(
                "默认开启。这是已关注特征和设备的警报总开关。关闭后不发出提示音、不振动、不闪烁、不跳转，也不显示通知卡片。仍可关注设备，但设备出现时不会提醒。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            val radioWatchN = state.watchlist.count { it.deviceKey != null }
            FieldwatchActionButton(
                onClick = onRadioBookmarks,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("命名设备（$radioWatchN）") }
            Text(
                "为单个 MAC 设置自定义名称，可选择开启警报。“筛选 → 仅命名设备”可在实时页面只显示这些设备。已关注特征仍在“特征库”中。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("已关注特征提示音", Modifier.weight(1f))
                FieldwatchSwitch(
                    settings.alertBeep,
                    { on -> vm.updateSettings { it.copy(alertBeep = on) } },
                    enabled = settings.alertsEnabled,
                )
            }
            Text(
                "已关注特征或设备首次出现、离开后再次出现时，会按媒体音量播放两声提示音。持续存在的设备不会重复响铃。与语音独立，可单独或同时使用。若听不到声音，请提高媒体音量后点按“测试警报”。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("已关注特征语音提示", Modifier.weight(1f))
                FieldwatchSwitch(
                    settings.alertVoice,
                    { on -> vm.updateSettings { it.copy(alertVoice = on) } },
                    enabled = settings.alertsEnabled,
                )
            }
            Text(
                "默认开启，使用与提示音相同的媒体音量。与提示音独立：开启提示音时，语音在提示音之后播放；关闭提示音时只播放语音。不适用于信号追踪。正在播报时会跳过第二次触发。没有文字转语音功能的手机，在提示音开启时仍会响铃。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text("播报内容", style = MaterialTheme.typography.labelLarge)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                AlertVoiceWhat.entries.forEach { item ->
                    FieldwatchFilterChip(
                        selected = settings.alertVoiceWhat == item,
                        onClick = { vm.updateSettings { it.copy(alertVoiceWhat = item) } },
                        enabled = settings.alertsEnabled && settings.alertVoice,
                        label = { Text(item.label()) },
                    )
                }
            }
            Text(
                "对于已关注特征：“类别”对应实时页面的图标类别（寻物标签、音频等），“特征”对应特征库条目（Apple AirTags、Axon 等）。“类别 + 特征”（默认）会同时播报两者。开启警报的命名设备始终播报自定义名称，即使没有类别。“测试警报”会使用当前所选组合。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            FieldwatchActionButton(
                onClick = vm::testWatchBeep,
                modifier = Modifier.fillMaxWidth(),
                enabled = settings.alertsEnabled && (settings.alertBeep || settings.alertVoice),
            ) { Text("测试警报") }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("跳转至新发现的已关注设备", Modifier.weight(1f))
                FieldwatchSwitch(
                    settings.snapToBeep,
                    { on -> vm.updateSettings { it.copy(snapToBeep = on) } },
                    enabled = settings.alertsEnabled && (settings.alertBeep || settings.alertVoice),
                )
            }
            Text(
                "新发现已关注特征或设备时，实时列表会滚动到对应条目，以便查看闪烁提示。可配合提示音、语音或两者使用。按信号强度排序时，弱信号位于底部。不希望列表自动移动时可关闭。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("系统通知", Modifier.weight(1f))
                FieldwatchSwitch(
                    settings.alertShade,
                    { on -> vm.updateSettings { it.copy(alertShade = on) } },
                    enabled = settings.alertsEnabled,
                )
            }
            Text(
                "可选。已关注设备出现时，在通知栏显示静音卡片。默认关闭，提示音和闪烁通常已足够，省略卡片也可减轻扫描负担。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            }

            SectionCard("位置") {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("为探测结果添加 GPS 标记", Modifier.weight(1f))
                FieldwatchSwitch(settings.tagLocation, { on -> vm.updateSettings { it.copy(tagLocation = on) } })
            }
            Text(
                "默认开启。请求实时 GPS／网络位置更新，并为每次接收添加位置标记，供实时详情、随行、" +
                    "观测总结及新日志行的经纬度使用。超过 30 秒的上次已知位置会被忽略。" +
                    "这是接收时本机的 GPS 位置，不是对方无线设备的独立定位。" +
                    "请使用高精度定位，否则轨迹可能一直为 0。不希望日志记录操作者坐标时可关闭。" +
                    "“此处接收”的 TAK 标记也需要此功能，广播载荷中的坐标（Remote ID）则不需要。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("在线地名与地图", Modifier.weight(1f))
                FieldwatchSwitch(settings.onlineLookup, { on -> vm.updateSettings { it.copy(onlineLookup = on) } })
            }
            Text(
                "默认开启。有网络时，观测总结／AI 导出会将 GPS 标记反向解析为" +
                    "街道／城市，“报告 → 轨迹”会在轨迹下方加载 OpenStreetMap 地图瓦片。" +
                    "不使用 Fieldwatch 云端，也不需要 API 密钥。离线或无地理编码服务时，观测总结只使用坐标，轨迹保持北向朝上的线条，不弹出错误。" +
                    "关闭后，报告和轨迹不使用街道名称与地图瓦片。" +
                    "观测总结、观测导出、日志导出及重置／清除日志均在“报告”页。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            }

            SectionCard("TAK / CoT") {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("TAK／CoT 推送", Modifier.weight(1f))
                FieldwatchSwitch(settings.takEnabled, { on -> vm.updateSettings { it.copy(takEnabled = on) } })
            }
            Text(
                "默认关闭。向 ATAK、WinTAK 或 iTAK 发送 Cursor-on-Target UDP 标记。" +
                    "“本机”（${TakDefaults.LOOPBACK}:${TakDefaults.PORT}）指此手机上的 ATAK CIV。" +
                    "局域网组播地址为 ${TakDefaults.SA_HOST}:${TakDefaults.SA_PORT}。" +
                    "“自定义”使用单播 IPv4 或主机名。仅支持 UDP，不是 TAK 服务器的 TCP 8087 接口。" +
                    "“此处接收”标记位于本机接收到最强信号（最接近时）的 GPS 位置，并标注“（此处）”。" +
                    "走远时标记不随之移动，接收到更强信号时才更新。约每 10 秒刷新同一经纬度，避免 ATAK 移除标记。" +
                    "广播的经纬度（内置 Remote ID）表示飞行器位置；相同的 Remote ID " +
                    "保持一个随位置移动的标记，按 UAS ID 识别，而非轮换的 BLE MAC。" +
                    "解码出的操作员位置会显示为第二个标记。设备离开后会从 ATAK 移除，不再保留 120 秒。" +
                    "点按 ATAK 中的标记可查看备注（名称、MAC、RSSI、特征）。" +
                    "这不是无线测向，也不是 Remote ID 插件。隐私模式会暂停推送。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            if (settings.takEnabled && settings.demoMode) {
                Text(
                    "隐私模式已开启，推送已暂停，以免发送完整 MAC 和坐标。关闭隐私模式后可恢复推送。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
            if (settings.takEnabled) {
                TakFeedSettings(settings, vm, state.takStatus)
            }
            }

            SectionCard("日志") {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("将探测结果写入磁盘", Modifier.weight(1f))
                FieldwatchSwitch(settings.loggingEnabled, { on -> vm.updateSettings { it.copy(loggingEnabled = on) } })
            }
            StableCaption(
                if (settings.loggingEnabled) {
                    "日志已开启。新探测结果会追加到轮转文件。"
                } else {
                    "日志已关闭。扫描继续运行，重新开启前不写入新数据。"
                },
                "日志已开启。新探测结果会追加到轮转文件。",
                "日志已关闭。扫描继续运行，重新开启前不写入新数据。",
            )
            Text(
                "轮转文件采用 JSON lines 格式（每行一次接收）。在“报告 → 日志导出 → 格式”中选择后，分享或保存时可生成 CSV、JSON lines、GPX、KML 或 WiGLE 文件。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            var rotateDrag by remember { mutableIntStateOf(settings.logRotateKb) }
            var rotateDragging by remember { mutableStateOf(false) }
            LaunchedEffect(settings.logRotateKb) {
                if (!rotateDragging) rotateDrag = settings.logRotateKb
            }
            Text("达到 $rotateDrag KB 时轮转")
            FieldwatchSlider(
                value = rotateDrag.toFloat(),
                onValueChange = {
                    rotateDragging = true
                    rotateDrag = it.toInt().coerceIn(128, 4096)
                },
                onValueChangeFinished = {
                    vm.updateSettings { s -> s.copy(logRotateKb = rotateDrag) }
                    rotateDragging = false
                },
                valueRange = 128f..4096f,
            )
            var staleDrag by remember { mutableIntStateOf(settings.staleSec) }
            var staleDragging by remember { mutableStateOf(false) }
            LaunchedEffect(settings.staleSec) {
                if (!staleDragging) staleDrag = settings.staleSec
            }
            Text("${staleDrag} 秒后视为过期")
            FieldwatchSlider(
                value = staleDrag.toFloat(),
                onValueChange = {
                    staleDragging = true
                    staleDrag = it.toInt().coerceIn(15, 180)
                },
                onValueChangeFinished = {
                    vm.updateSettings { s -> s.copy(staleSec = staleDrag) }
                    staleDragging = false
                },
                valueRange = 15f..180f,
            )
            StickyHeight("log-stats") {
                Text(
                    "本次会话 ${state.logLines} 行 · 磁盘占用 ${vm.logBytes() / 1024} KB。" +
                        "分享、保存和重置／清除日志位于“报告”页。",
                    style = MaterialTheme.typography.bodySmall,
                )
            }
            }

            SectionCard("特征库") {
            Text(
                "导出特征库（包括内置条目及自行添加或编辑的内容），可分享给其他 Fieldwatch 用户或备份。导入会添加新条目和额外规则，不删除现有内容；相同 ID 或匹配规则会跳过，因此同一包可重复导入。“从 GitHub 更新内置特征库”使用仓库中的 v2 特征包替换内置条目（含重点关注），保留关注项目、设置和自建特征。此操作需要网络；离线时可从文件导入。下方“恢复默认值”仍会清除自定义内容。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            FieldwatchActionButton(
                onClick = vm::startSignatureShare,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("导出特征库") }
            FieldwatchActionButton(
                onClick = { saveSignatures.launch(vm.suggestedSignaturesName()) },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("将特征库保存到 SD 卡／存储空间…") }
            FieldwatchActionButton(
                onClick = {
                    importSignatures.launch(arrayOf("application/json", "text/plain", "*/*"))
                },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("导入特征库…") }
            FieldwatchActionButton(
                onClick = vm::updateStockCatalogFromGitHub,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("从 GitHub 更新内置特征库") }

            FieldwatchActionButton(
                onClick = { confirmRestore = true },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("恢复默认特征库与预设")
            }
            }

            SectionCard("设置备份") {
            Text(
                "包含设置开关、当前筛选、筛选预设、命名设备和已关注特征。" +
                    "不包含特征库（需单独导出）、日志或 GPS。" +
                    "导入会替换本机对应设置，特征库保持不变。" +
                    "可在恢复出厂设置或更换手机后使用。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            FieldwatchActionButton(
                onClick = vm::startSettingsShare,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("导出设置") }
            FieldwatchActionButton(
                onClick = { saveSettings.launch(vm.suggestedSettingsName()) },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("将设置保存到 SD 卡／存储空间…") }
            FieldwatchActionButton(
                onClick = {
                    importSettings.launch(arrayOf("application/json", "text/plain", "*/*"))
                },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("导入设置…") }
            }

            FieldwatchActionButton(
                onClick = onShowLiveTour,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("显示实时页面引导") }
            Text(
                "实时页面功能引导包括：调整显示（雷达、列表、按类别等）、暂停、筛选、特征库、报告和设置。首次同意许可后会显示，也可通过此按钮再次查看。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            Text(
                "Fieldwatch ${app.fieldwatch.BuildConfig.VERSION_NAME} · 特征库 ${state.catalogVersion}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                "仅被动接收 Wi-Fi + BLE。" +
                    "原生 Android 无法以混杂模式捕获 Wi-Fi 客户端；无线接口仅提供接入点和 BLE 广播设备。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            val footerLifecycle = LocalLifecycleOwner.current
            var ipv4 by remember { mutableStateOf(localIpv4Addresses()) }
            DisposableEffect(footerLifecycle) {
                val obs = LifecycleEventObserver { _, event ->
                    if (event == Lifecycle.Event.ON_RESUME) ipv4 = localIpv4Addresses()
                }
                footerLifecycle.lifecycle.addObserver(obs)
                onDispose { footerLifecycle.lifecycle.removeObserver(obs) }
            }
            Text(
                if (ipv4.isEmpty()) {
                    "本机 IPv4 · 无"
                } else {
                    "本机 IPv4 · ${ipv4.joinToString("  ·  ")}"
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(Modifier.height(24.dp))
            HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.45f))
            CreditFooter()
        }
    }
    if (confirmRestore) {
        AlertDialog(
            onDismissRequest = { confirmRestore = false },
            title = { Text("恢复默认值？") },
            text = {
                Text(
                    "将重写特征库（内置条目、类别颜色、解码字段）、内置关注项目、" +
                        "内置筛选预设和默认设置开关。你保存的自定义特征和预设" +
                        "将被清除。如需备份，请先导出特征库和设置。" +
                        "此操作无法撤销。",
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        confirmRestore = false
                        vm.restoreDefaults()
                    },
                ) { Text("恢复") }
            },
            dismissButton = {
                TextButton(onClick = { confirmRestore = false }) { Text("取消") }
            },
        )
    }
}

@Composable
private fun CreditFooter() {
    val context = LocalContext.current
    val muted = MaterialTheme.colorScheme.onSurfaceVariant
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 14.dp, bottom = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            "版权所有 (c) 2026 Off Grid Pete LLC。保留所有权利。",
            style = MaterialTheme.typography.labelSmall,
            color = muted,
        )
        Row(
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            SocialChip(
                icon = R.drawable.ic_instagram,
                label = "@OffGridPete",
                tint = muted,
                onClick = { openUrl(context, "https://instagram.com/OffGridPete") },
            )
            SocialChip(
                icon = R.drawable.ic_x,
                label = "@OGridPete",
                tint = muted,
                onClick = { openUrl(context, "https://x.com/OGridPete") },
            )
        }
    }
}

@Composable
private fun SocialChip(
    icon: Int,
    label: String,
    tint: Color,
    onClick: () -> Unit,
) {
    Surface(
        shape = RoundedCornerShape(99.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.65f),
        modifier = Modifier.clickable(onClick = onClick),
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                painter = painterResource(icon),
                contentDescription = label,
                tint = tint,
                modifier = Modifier.size(14.dp),
            )
            Spacer(Modifier.width(6.dp))
            Text(label, style = MaterialTheme.typography.labelMedium, color = tint)
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun TakFeedSettings(settings: AppSettings, vm: FieldwatchViewModel, status: TakFeedStatus) {
    val muted = MaterialTheme.colorScheme.onSurfaceVariant
    var hostText by remember { mutableStateOf(settings.takHost) }
    var portText by remember { mutableStateOf(settings.takPort.toString()) }
    LaunchedEffect(settings.takHost) { hostText = settings.takHost }
    LaunchedEffect(settings.takPort) { portText = settings.takPort.toString() }
    val preset = TakPublish.udpPreset(settings.takHost, settings.takPort)
    Text("目标", style = MaterialTheme.typography.labelLarge)
    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        FieldwatchFilterChip(
            selected = preset == TakUdpPreset.THIS_PHONE,
            onClick = {
                val (host, port) = TakPublish.applyPreset(TakUdpPreset.THIS_PHONE)
                vm.updateSettings { it.copy(takHost = host, takPort = port) }
            },
            enabled = !settings.demoMode,
            label = { Text("本机") },
        )
        FieldwatchFilterChip(
            selected = preset == TakUdpPreset.LAN_MULTICAST,
            onClick = {
                val (host, port) = TakPublish.applyPreset(TakUdpPreset.LAN_MULTICAST)
                vm.updateSettings { it.copy(takHost = host, takPort = port) }
            },
            enabled = !settings.demoMode,
            label = { Text("局域网组播") },
        )
        FieldwatchFilterChip(
            selected = preset == TakUdpPreset.CUSTOM,
            onClick = {
                if (preset != TakUdpPreset.CUSTOM) {
                    val (host, port) = TakPublish.applyPreset(TakUdpPreset.CUSTOM)
                    vm.updateSettings { it.copy(takHost = host, takPort = port) }
                }
            },
            enabled = !settings.demoMode,
            label = { Text("自定义") },
        )
    }
    Text(
        "本机：${TakDefaults.LOOPBACK}:${TakDefaults.PORT}（此手机上的 ATAK CIV）。" +
            "局域网组播：${TakDefaults.SA_HOST}:${TakDefaults.SA_PORT}（同一 Wi-Fi 中的其他 ATAK）。" +
            "自定义：输入单播 IPv4 或主机名。仅支持 UDP，不是 TAK 服务器的 TCP 8087 接口。" +
            "若“本机”无法显示标记，请改用“自定义”，输入页脚中的本机 Wi-Fi IPv4 和端口 ${TakDefaults.PORT}。",
        style = MaterialTheme.typography.bodySmall,
        color = muted,
    )
    FieldwatchOutlinedField(
        value = hostText,
        onValueChange = { value ->
            hostText = value
            val trimmed = value.trim()
            if (trimmed.isNotEmpty()) {
                vm.updateSettings { it.copy(takHost = trimmed) }
            }
        },
        label = "主机",
        placeholder = TakDefaults.HOST,
        enabled = !settings.demoMode,
    )
    FieldwatchOutlinedField(
        value = portText,
        onValueChange = { value ->
            val filtered = value.filter { it.isDigit() }.take(5)
            portText = filtered
            filtered.toIntOrNull()?.let { n ->
                if (n in 1..65_535) {
                    vm.updateSettings { it.copy(takPort = n) }
                }
            }
        },
        label = "端口",
        placeholder = TakDefaults.PORT.toString(),
        supportingText = "UDP。ATAK CIV 端口 ${TakDefaults.PORT}，SA 组播端口 ${TakDefaults.SA_PORT}。不是 TCP 8087。",
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
        enabled = !settings.demoMode,
    )
    Text(takStatusLine(status), style = MaterialTheme.typography.bodySmall, color = muted)
    Text("发送内容", style = MaterialTheme.typography.labelLarge)
    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        FieldwatchFilterChip(
            selected = settings.takAttention,
            onClick = { vm.updateSettings { it.copy(takAttention = !it.takAttention) } },
            enabled = !settings.demoMode,
            label = { Text("重点关注") },
        )
        FieldwatchFilterChip(
            selected = settings.takPayloadFix,
            onClick = { vm.updateSettings { it.copy(takPayloadFix = !it.takPayloadFix) } },
            enabled = !settings.demoMode,
            label = { Text("载荷位置") },
        )
        FieldwatchFilterChip(
            selected = settings.takWatchlist,
            onClick = { vm.updateSettings { it.copy(takWatchlist = !it.takWatchlist) } },
            enabled = !settings.demoMode,
            label = { Text("关注列表") },
        )
        FieldwatchFilterChip(
            selected = settings.takAllSignatures,
            onClick = { vm.updateSettings { it.copy(takAllSignatures = !it.takAllSignatures) } },
            enabled = !settings.demoMode,
            label = { Text("全部特征") },
        )
    }
    Text(
        "各选项独立。“重点关注”（默认开）：执法记录仪、眼镜、录音录像可穿戴设备、渗透测试设备、公共安全 AP。" +
            "“载荷位置”（默认开）：解码映射得到的广播经纬度。内置 Remote ID 没有重点关注标记，因此需开启此项。" +
            "“关注列表”（默认关）：已关注特征，以及已开启警报的命名设备。" +
            "“全部特征”（默认关）：所有已标注设备，在公共场所可能较多。未匹配设备始终不会发送。" +
            "标记仍需要坐标：来自广播载荷，或带实时定位的 GPS 标记。" +
            "“此处接收”保留最强信号时的位置，而非最后一次位置，呼号以“（此处）”结尾。" +
            "Remote ID 保留一个按 UAS ID 识别的飞行器标记，解码出操作员位置时另加一个标记。",
        style = MaterialTheme.typography.bodySmall,
        color = muted,
    )
}

private fun takStatusLine(status: TakFeedStatus): String {
    if (status.paused) return "推送状态 · 已暂停（隐私模式）"
    if (status.error != null) {
        val whenAt = takStatusWhen(status.at)
        return "推送状态 · 错误：${status.error}" + if (whenAt.isNotEmpty()) "  ·  $whenAt" else ""
    }
    if (status.at <= 0L) {
        return "推送状态 · 本次会话尚未发送"
    }
    val bits = ArrayList<String>(5)
    bits += "推送中 ${status.onFeed} 个"
    bits += "已发送 ${status.sent} 个"
    if (status.gone > 0) {
        bits += if (status.gone == 1) "1 个已离开" else "${status.gone} 个已离开"
    }
    if (status.dest.isNotBlank()) bits += status.dest
    val whenAt = takStatusWhen(status.at)
    if (whenAt.isNotEmpty()) bits += whenAt
    val head = "推送状态 · ${bits.joinToString("  ·  ")}"
    return if (status.detail.isNotBlank() && status.sent == 0 && status.gone == 0) {
        "$head  ·  ${status.detail}"
    } else {
        head
    }
}

private fun takStatusWhen(at: Long): String {
    if (at <= 0L) return ""
    return java.time.Instant.ofEpochMilli(at)
        .atZone(java.time.ZoneId.systemDefault())
        .format(java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss"))
}

private fun localIpv4Addresses(): List<String> {
    val found = LinkedHashSet<String>()
    val nifs = runCatching {
        java.util.Collections.list(NetworkInterface.getNetworkInterfaces())
    }.getOrDefault(emptyList())
    for (nif in nifs) {
        if (!nif.isUp || nif.isLoopback) continue
        for (addr in java.util.Collections.list(nif.inetAddresses)) {
            if (addr is Inet4Address && !addr.isLoopbackAddress && !addr.isLinkLocalAddress) {
                addr.hostAddress?.let { found += it }
            }
        }
    }
    return found.toList()
}

private fun isIgnoringBatteryOptimizations(context: Context): Boolean =
    context.getSystemService(PowerManager::class.java)
        ?.isIgnoringBatteryOptimizations(context.packageName) == true

private fun isBackgroundUsageAllowed(context: Context): Boolean =
    context.getSystemService(ActivityManager::class.java)?.isBackgroundRestricted != true

private enum class BatteryAndroidGate { BACKGROUND, UNRESTRICTED }

/**
 * Fieldwatch’s per-app Battery page. Samsung keeps Allow background usage and
 * Unrestricted on this same screen. [highlightBackground] asks Settings to
 * focus the background-usage switch when the OEM supports it.
 */
private fun openAppBatteryPage(context: Context, highlightBackground: Boolean) {
    val pkgUri = Uri.fromParts("package", context.packageName, null)
    val attempts = listOf(
        Intent("android.settings.VIEW_ADVANCED_POWER_USAGE_DETAIL").apply {
            data = pkgUri
            addCategory(Intent.CATEGORY_DEFAULT)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            putExtra("request_ignore_background_restriction", highlightBackground)
            if (!highlightBackground) {
                putExtra(":settings:fragment_args_key", "unrestricted_pref")
            }
        },
        Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = pkgUri
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        },
    )
    for (intent in attempts) {
        if (intent.resolveActivity(context.packageManager) == null) continue
        if (runCatching { context.startActivity(intent) }.isSuccess) return
    }
}

private fun openUrl(context: android.content.Context, url: String) {
    runCatching {
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
    }
}
