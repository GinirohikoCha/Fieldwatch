package app.fieldwatch.ui.screen

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.Spacer
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Person
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.graphics.vector.rememberVectorPainter
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import app.fieldwatch.ui.component.FieldwatchActionButton
import androidx.compose.material3.Scaffold
import app.fieldwatch.ui.component.FieldwatchOutlinedField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import app.fieldwatch.domain.MacUtil
import app.fieldwatch.ui.RadioClassBadge
import app.fieldwatch.ui.RadioKindMark
import app.fieldwatch.domain.LogExportKind
import app.fieldwatch.domain.LogExportRadios
import app.fieldwatch.domain.Sit
import app.fieldwatch.domain.SitDiff
import app.fieldwatch.domain.SitPathPlot
import app.fieldwatch.ui.component.AircraftAmber
import app.fieldwatch.ui.component.FieldwatchDropdownField
import app.fieldwatch.ui.component.SitPathCanvas
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import app.fieldwatch.ui.NestedTabInsets
import app.fieldwatch.ui.NestedTopBar
import app.fieldwatch.ui.FieldwatchUi
import app.fieldwatch.ui.FieldwatchViewModel
import app.fieldwatch.ui.component.FieldwatchSwitch
import app.fieldwatch.ui.component.SectionCard
import app.fieldwatch.ui.theme.Cyan
import app.fieldwatch.ui.theme.LocalNightMode
import app.fieldwatch.ui.theme.nightIf

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportsScreen(
    state: FieldwatchUi,
    vm: FieldwatchViewModel,
    exporting: Boolean,
    onSaveToStorage: () -> Unit,
    onSaveSitToStorage: () -> Unit,
    onSignatureCandidates: () -> Unit,
    onOpenPathRadio: (String) -> Unit = {},
) {
    val settings = state.settings
    var confirmClear by remember { mutableStateOf(false) }
    var startSit by remember { mutableStateOf(false) }
    var sitNameDraft by remember { mutableStateOf("") }
    var renameSitId by remember { mutableStateOf<String?>(null) }
    var renameDraft by remember { mutableStateOf("") }
    var deleteSitId by remember { mutableStateOf<String?>(null) }
    var confirmDeleteAll by remember { mutableStateOf(false) }
    Scaffold(
        contentWindowInsets = NestedTabInsets,
        topBar = { NestedTopBar("报告") },
    ) { pad ->
        Column(
            Modifier
                .padding(pad)
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            if (settings.demoMode) {
                Text(
                    "隐私模式已开启。观测总结、观测对比、AI 导出（观测或对比）及详情分享中的 MAC 地址末尾显示为 **:**:**，GPS 坐标已隐藏。日志、观测导出及 GPX／KML／WiGLE 文件仍包含完整地址和经纬度。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary,
                )
            }

            SectionCard("观测") {
                Text(
                    "观测是为一段时间内在此接收到的无线设备建立的命名记录。下方选择决定轨迹、观测总结和对比中的“本次观测”：可以是正在进行的观测、选中的已保存观测，或未开始观测时的最近 15 分钟。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                val open = state.sit.open
                if (open != null) {
                    val dur = Sit.fmtDuration(open.durationMs())
                    Text(
                        "本次观测：${open.name} · $dur · ${state.sit.radioCount} 个无线设备",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    FieldwatchActionButton(
                        onClick = vm::endSit,
                        enabled = !exporting,
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("结束观测") }
                } else {
                    FieldwatchActionButton(
                        onClick = {
                            sitNameDraft = vm.defaultSitName()
                            startSit = true
                        },
                        enabled = !exporting,
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("开始观测") }
                    Text(
                        if (state.sit.closed.isEmpty()) {
                            "当前没有进行中的观测。可在此开始；开始前，轨迹和观测总结使用最近 15 分钟的数据。"
                        } else {
                            "当前没有进行中的观测。可在此开始。轨迹和观测总结使用选中的观测。"
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                if (state.sit.closed.isEmpty() && open == null) {
                    Text(
                        "暂无已保存的观测。",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                if (state.sit.closed.isNotEmpty()) {
                    val pickEnabled = open == null && !exporting
                    SitChoiceRow(
                        selected = state.sit.selectedId == null,
                        enabled = pickEnabled,
                        title = "最近 15 分钟",
                        subtitle = "轨迹和观测总结使用内存中的数据，不读取已保存的观测。",
                        onSelect = { vm.selectSit(null) },
                    )
                    state.sit.closed.forEach { row ->
                        val dur = Sit.fmtDuration(row.durationMs())
                        val extra = if (row.extraAttentionCount > 0) {
                            " · 重点关注 ${row.extraAttentionCount} 个"
                        } else {
                            ""
                        }
                        SitChoiceRow(
                            selected = state.sit.selectedId == row.id,
                            enabled = pickEnabled,
                            title = row.name,
                            subtitle = "${Sit.defaultName(row.startAt)} · $dur · ${row.radioCount} 个无线设备$extra",
                            onSelect = { vm.selectSit(row.id) },
                        )
                    }
                    if (open != null) {
                        Text(
                            "结束当前观测后，才能为轨迹和观测总结选择已保存的观测。",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    val picked = state.sit.closed.firstOrNull { it.id == state.sit.selectedId }
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        FieldwatchActionButton(
                            onClick = {
                                if (picked != null) {
                                    renameSitId = picked.id
                                    renameDraft = picked.name
                                }
                            },
                            enabled = !exporting && picked != null,
                            modifier = Modifier.weight(1f),
                        ) { Text("重命名") }
                        FieldwatchActionButton(
                            onClick = { if (picked != null) deleteSitId = picked.id },
                            enabled = !exporting && picked != null,
                            modifier = Modifier.weight(1f),
                        ) { Text("删除") }
                    }
                    FieldwatchActionButton(
                        onClick = { confirmDeleteAll = true },
                        enabled = !exporting,
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("删除所有观测") }
                }
            }

            val pathModel by vm.sitPath.collectAsStateWithLifecycle()
            LaunchedEffect(state.sit.selectedId, state.sit.open?.id) {
                while (true) {
                    vm.refreshSitPath()
                    kotlinx.coroutines.delay(3_000L)
                }
            }
            SectionCard("轨迹") {
                Text(
                    "上方为北。线条表示本机轨迹，黑点为起点，蓝点为你所在的最新位置。MAC 或特征警报显示为类别图标。解码出的经纬度采用设备最近发送的位置。数字表示该处有多个设备，粗绿线表示停留，时间刻度沿轨迹显示。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                val model = pathModel
                val showWalk = model != null && model.emptyHint == null
                val showAircraft = model != null && model.aircraftCards.isNotEmpty()
                if (model == null || (!showWalk && !showAircraft)) {
                    Text(
                        model?.emptyHint ?: "开启“为探测结果添加 GPS 标记”后走动，或打开记录了轨迹的观测。",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                } else {
                    val pathTiles by vm.pathTiles.collectAsStateWithLifecycle()
                    val aircraftTiles by vm.pathAircraftTiles.collectAsStateWithLifecycle()
                    if (!showWalk) {
                        Text(
                            model.emptyHint ?: "开启“为探测结果添加 GPS 标记”后走动，或打开记录了轨迹的观测。",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    if (showWalk) {
                    val stopN = model.dots.size
                    Text(
                        buildString {
                            append("${model.title} · 轨迹 ${model.lengthM.toInt()} 米 · 跨度 ${model.spanM.toInt()} 米")
                            if (stopN > 0) {
                                append(" · $stopN 条警报")
                            }
                        },
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    SitPathCanvas(model, tiles = pathTiles, onOpenRadio = onOpenPathRadio)
                    Text(
                        "点按数字查看该处设备，点按单个图标查看对应设备，再次点按可关闭。点按弹出列表或下方列表中的条目，可打开设备详情。",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    if (model.craft.isNotEmpty() || model.pilots.isNotEmpty()) {
                        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            if (model.craft.isNotEmpty()) {
                                val multi = model.craft.any { it.samples.size >= 2 }
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                                ) {
                                    if (multi) AdvertisedTrackSwatch() else AdvertisedRingSwatch()
                                    Text(
                                        if (multi) {
                                            "= 距此轨迹 2 公里内的广播轨迹"
                                        } else {
                                            "= 距此轨迹 2 公里内的单个广播位置"
                                        },
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurface,
                                    )
                                }
                            }
                            if (model.pilots.isNotEmpty()) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                                ) {
                                    PilotSwatch()
                                    Text(
                                        "= 操作员",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    )
                                }
                            }
                        }
                    }
                    val alertsOnACard = model.aircraftCards.any { it.dots.isNotEmpty() }
                    if (model.dots.isEmpty() && !alertsOnACard) {
                        Text(
                            "此轨迹上没有带 GPS 标记的 MAC 或特征警报。",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    } else if (model.dots.isNotEmpty()) {
                        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            model.dots.forEachIndexed { i, dot ->
                                PathRadioRow(
                                    index = i + 1,
                                    dot = dot,
                                    demoMode = settings.demoMode,
                                    onOpen = { onOpenPathRadio(dot.key) },
                                )
                            }
                        }
                    }
                    }
                    model.aircraftCards.forEachIndexed { index, card ->
                        val fixes = card.craft.sumOf { it.samples.size }
                        Text(
                            card.title,
                            style = MaterialTheme.typography.titleSmall,
                            color = AircraftAmber,
                            modifier = Modifier.padding(top = 12.dp),
                        )
                        Text(
                            buildString {
                                append(
                                    if (fixes == 1) "1 个广播定位点" else "$fixes 个广播定位点",
                                )
                                if (card.lengthM >= 1.0) append(" · ${card.lengthM.toInt()} 米")
                            },
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        if (card.dots.isNotEmpty()) {
                            Text(
                                if (card.dots.size == 1) "1 条警报" else "${card.dots.size} 条警报",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                        SitPathCanvas(
                            card,
                            tiles = aircraftTiles.getOrElse(index) { emptyList() },
                            onOpenRadio = onOpenPathRadio,
                        )
                        if (card.dots.isNotEmpty()) {
                            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                card.dots.forEachIndexed { i, dot ->
                                    PathRadioRow(
                                        index = i + 1,
                                        dot = dot,
                                        demoMode = settings.demoMode,
                                        onOpen = { onOpenPathRadio(dot.key) },
                                    )
                                }
                            }
                        }
                        if (card.caption.isNotBlank()) {
                            Text(
                                card.caption,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                    if (model.looseAdvertised > 0) {
                        Text(
                            if (model.looseAdvertised == 1) {
                                "观测报告中包含一个没有 UAS ID 的广播位置。"
                            } else {
                                "观测报告中包含没有 UAS ID 的广播位置。"
                            },
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }

            SectionCard("观测报告") {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                FieldwatchActionButton(
                    onClick = vm::startFieldDebrief,
                    enabled = !exporting,
                    modifier = Modifier.weight(1f),
                ) { Text("观测总结（文本）") }
                FieldwatchActionButton(
                    onClick = vm::startFieldDebriefPdf,
                    enabled = !exporting,
                    modifier = Modifier.weight(1f),
                ) { Text("观测总结（PDF）") }
            }
            Text(
                sitReportCaption(state),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    "显示未匹配的轮换地址 BLE",
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.bodyMedium,
                )
                FieldwatchSwitch(
                    settings.debriefShowUnmatchedRandomBle,
                    { on -> vm.updateSettings { it.copy(debriefShowUnmatchedRandomBle = on) } },
                )
            }
            Text(
                "默认关闭：文本／PDF 观测总结列表跳过未匹配的随机地址 BLE，但计数仍包含它们。保留重点关注、命名特征、已关注设备和载荷位置标记。观测导出包含全部设备。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            FieldwatchActionButton(
                onClick = vm::startAiExport,
                enabled = !exporting,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("AI 导出") }
            Text(
                "可直接粘贴的补充信息：接收速率、RSSI 区间、重点关注和跟踪 ID，不重复观测总结清单。单个设备的 AI 导出位于详情页。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            }

            SectionCard("观测导出") {
            val sitKind by vm.sitExportKind.collectAsStateWithLifecycle()
            val sitRadios by vm.sitExportRadios.collectAsStateWithLifecycle()
            ExportFormatBlock(
                kind = sitKind,
                radios = sitRadios,
                exporting = exporting,
                onKind = vm::setSitExportKind,
                onRadios = vm::setSitExportRadios,
                onShare = vm::startSitExport,
                onSave = onSaveSitToStorage,
                hint = "本次观测（或最近 15 分钟）中的每个唯一设备各占一行。CSV／JSON lines 包含匹配特征和重点关注系列，不是轮转日志。GPX／KML 包含本机轨迹及接收点。Fieldwatch 不上传数据。隐私模式不会遮蔽此文件。",
            )
            }

            SectionCard("对比观测") {
                Text(
                    compareThisCaption(state),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                val thisSaved = SitDiff.thisSavedId(state.sit.open, state.sit.selectedId)
                val choices = SitDiff.secondSitChoices(state.sit.closed, thisSaved)
                if (choices.isEmpty()) {
                    Text(
                        "先开始并结束一次观测，保存第二次观测后即可对比。“最近 15 分钟”也可作为本次观测。",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                } else {
                    Text(
                        "第二次观测",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    choices.forEach { row ->
                        val dur = Sit.fmtDuration(row.durationMs())
                        SitChoiceRow(
                            selected = state.sit.compareId == row.id,
                            enabled = !exporting,
                            title = row.name,
                            subtitle = "${Sit.defaultName(row.startAt)} · $dur · ${row.radioCount} 个无线设备",
                            onSelect = { vm.selectCompareSit(row.id) },
                        )
                    }
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    FieldwatchActionButton(
                        onClick = vm::startSitCompare,
                        enabled = !exporting && state.sit.compareId != null,
                        modifier = Modifier.weight(1f),
                    ) { Text("对比（文本）") }
                    FieldwatchActionButton(
                        onClick = vm::startSitComparePdf,
                        enabled = !exporting && state.sit.compareId != null,
                        modifier = Modifier.weight(1f),
                    ) { Text("对比（PDF）") }
                }
                Text(
                    "同一报告提供两种格式，仅按无线类型和 MAC 对比出现情况：仅本次、仅第二次、两次都有。重点关注和命名设备会标注。这不代表设备定位。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                FieldwatchActionButton(
                    onClick = vm::startSitCompareAiExport,
                    enabled = !exporting && state.sit.compareId != null,
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("AI 导出") }
                Text(
                    "可直接粘贴的补充信息：交集、各自独有的重点关注／命名设备，以及增加一次观测可缩小哪些范围。不重复对比清单。观测报告的 AI 导出仅包含当前时间窗口。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            SectionCard("特征库") {
            FieldwatchActionButton(
                onClick = onSignatureCandidates,
                enabled = !exporting,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("候选特征") }
            Text(
                "查找日志中共享独特标识的未匹配设备，并非列出所有未知设备。由你审核，保存后才会添加。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            }

            SectionCard("日志导出") {
            Text(
                "本次会话 ${state.logLines} 行 · 磁盘占用 ${vm.logBytes() / 1024} KB" +
                    if (settings.loggingEnabled) "" else "  ·  日志已关闭",
                style = MaterialTheme.typography.bodySmall,
            )
            val logKind by vm.logExportKind.collectAsStateWithLifecycle()
            val logRadios by vm.logExportRadios.collectAsStateWithLifecycle()
            ExportFormatBlock(
                kind = logKind,
                radios = logRadios,
                exporting = exporting,
                onKind = vm::setLogExportKind,
                onRadios = vm::setLogExportRadios,
                onShare = vm::startExport,
                onSave = onSaveToStorage,
                hint = "轮转文件采用 JSON lines 格式，CSV 可将相同记录作为表格打开。GPX（GPS 交换格式）、KML（Google Earth）和 WiGLE CSV（wigle.net）记录的是接收点，即本机接收到设备时的位置，不是设备的定位。请开启 GPS 标记和日志记录。分享使用 Android 系统分享面板，Fieldwatch 不上传数据。",
            )
            FieldwatchActionButton(
                onClick = { confirmClear = true },
                enabled = !exporting,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("重置／清除日志")
            }
            if (confirmClear) {
                AlertDialog(
                    onDismissRequest = { confirmClear = false },
                    title = { Text("清除日志？") },
                    text = {
                        Text("这会删除手机上所有轮转的 CSV／JSON 文件，无法撤销。实时扫描将创建新的空日志。")
                    },
                    confirmButton = {
                        TextButton(onClick = {
                            confirmClear = false
                            vm.clearLogs()
                        }) { Text("清除日志") }
                    },
                    dismissButton = {
                        TextButton(onClick = { confirmClear = false }) { Text("取消") }
                    },
                )
            }
            }
        }
    }
    if (startSit) {
        AlertDialog(
            onDismissRequest = { startSit = false },
            title = { Text("开始观测") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    FieldwatchOutlinedField(
                        value = sitNameDraft,
                        onValueChange = { sitNameDraft = it.take(Sit.NAME_MAX) },
                        label = "名称",
                    )
                    Text(
                        "结束观测前，观测总结和 AI 导出使用此时间窗口。实时列表保持不变。",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Sit.dropWarning(state.sit.closed)?.let { warn ->
                        Text(
                            warn,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = {
                    startSit = false
                    vm.startSit(sitNameDraft)
                }) { Text("开始") }
            },
            dismissButton = {
                TextButton(onClick = { startSit = false }) { Text("取消") }
            },
        )
    }
    val renaming = renameSitId
    if (renaming != null) {
        AlertDialog(
            onDismissRequest = { renameSitId = null },
            title = { Text("重命名观测") },
            text = {
                FieldwatchOutlinedField(
                    value = renameDraft,
                    onValueChange = { renameDraft = it.take(Sit.NAME_MAX) },
                    label = "名称",
                )
            },
            confirmButton = {
                TextButton(onClick = {
                    renameSitId = null
                    vm.renameSit(renaming, renameDraft)
                }) { Text("保存") }
            },
            dismissButton = {
                TextButton(onClick = { renameSitId = null }) { Text("取消") }
            },
        )
    }
    val deleting = deleteSitId
    if (deleting != null) {
        AlertDialog(
            onDismissRequest = { deleteSitId = null },
            title = { Text("删除本次观测？") },
            text = { Text("从手机移除这次已保存的观测。日志保持不变。") },
            confirmButton = {
                TextButton(onClick = {
                    deleteSitId = null
                    vm.deleteSit(deleting)
                }) { Text("删除") }
            },
            dismissButton = {
                TextButton(onClick = { deleteSitId = null }) { Text("取消") }
            },
        )
    }
    if (confirmDeleteAll) {
        AlertDialog(
            onDismissRequest = { confirmDeleteAll = false },
            title = { Text("删除所有观测？") },
            text = { Text("从手机移除所有已保存的观测。正在进行的观测不会被删除，日志保持不变。") },
            confirmButton = {
                TextButton(onClick = {
                    confirmDeleteAll = false
                    vm.deleteAllSits()
                }) { Text("全部删除") }
            },
            dismissButton = {
                TextButton(onClick = { confirmDeleteAll = false }) { Text("取消") }
            },
        )
    }
}

@Composable
private fun SitChoiceRow(
    selected: Boolean,
    enabled: Boolean,
    title: String,
    subtitle: String,
    onSelect: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .selectable(
                selected = selected,
                enabled = enabled,
                onClick = onSelect,
                role = Role.RadioButton,
            )
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        RadioButton(
            selected = selected,
            onClick = null,
            enabled = enabled,
        )
        Column(Modifier.padding(start = 8.dp).fillMaxWidth()) {
            Text(
                title,
                style = MaterialTheme.typography.bodyMedium,
                color = if (selected && enabled) MaterialTheme.colorScheme.primary
                else MaterialTheme.colorScheme.onSurface,
            )
            Text(
                subtitle,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun AdvertisedTrackSwatch() {
    Canvas(Modifier.width(28.dp).height(10.dp)) {
        val dash = 3.dp.toPx()
        val gap = 4.5.dp.toPx()
        drawLine(
            Color.White,
            start = Offset(0f, size.height / 2f),
            end = Offset(size.width, size.height / 2f),
            strokeWidth = 2.2.dp.toPx(),
            cap = StrokeCap.Round,
            pathEffect = PathEffect.dashPathEffect(floatArrayOf(dash, gap), 0f),
        )
    }
}

@Composable
private fun AdvertisedRingSwatch() {
    Canvas(Modifier.size(12.dp)) {
        drawCircle(
            Color.White,
            radius = size.minDimension / 2f - 1.dp.toPx(),
            style = Stroke(width = 1.6.dp.toPx()),
        )
    }
}

@Composable
private fun PilotSwatch() {
    val painter = rememberVectorPainter(Icons.Outlined.Person)
    Canvas(Modifier.size(18.dp)) {
        val radius = size.minDimension / 2f
        val disc = radius * 0.86f
        drawCircle(Color.White, radius = radius)
        drawCircle(Color(0xFFF4F7FB), radius = disc)
        drawCircle(Color(0xFF3D4A55), radius = disc, style = Stroke(width = 1.2.dp.toPx()))
        val icon = disc * 1.35f
        translate((size.width - icon) / 2f, (size.height - icon) / 2f) {
            with(painter) {
                draw(Size(icon, icon), colorFilter = ColorFilter.tint(Color(0xFF3D4A55)))
            }
        }
    }
}

@Composable
private fun PathRadioRow(
    index: Int,
    dot: SitPathPlot.Dot,
    demoMode: Boolean,
    onOpen: () -> Unit,
) {
    val mac = MacUtil.screenMac(dot.mac, demoMode)
    val named = dot.label.isNotBlank() && !dot.label.equals(mac, ignoreCase = true)
    val fleets = dot.fleetNames.joinToString(" · ")
    val note = dot.observerNotes.trim()
    val accent = (if (dot.accentArgb != 0) Color(dot.accentArgb) else MaterialTheme.colorScheme.onSurfaceVariant)
        .nightIf(LocalNightMode.current)
    Row(
        Modifier
            .fillMaxWidth()
            .clickable(onClick = onOpen)
            .padding(vertical = 2.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            "$index",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.width(22.dp),
        )
        RadioClassBadge(dot.classKind, accent, compact = true)
        Spacer(Modifier.width(8.dp))
        Column(Modifier.weight(1f)) {
            if (named) {
                Text(
                    dot.label,
                    style = MaterialTheme.typography.bodyMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            if (mac.isNotBlank()) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    RadioKindMark(dot.kind, size = 13.dp)
                    Spacer(Modifier.width(4.dp))
                    Text(
                        mac,
                        style = MaterialTheme.typography.bodySmall.copy(
                            fontFamily = FontFamily.Monospace,
                            fontSize = 12.sp,
                        ),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                }
            }
            if (fleets.isNotEmpty()) {
                Text(
                    fleets,
                    style = MaterialTheme.typography.bodySmall,
                    color = accent,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            if (note.isNotEmpty()) {
                Text(
                    note,
                    style = MaterialTheme.typography.bodySmall,
                    color = Cyan.nightIf(LocalNightMode.current),
                )
            }
        }
    }
}

private fun compareThisCaption(state: FieldwatchUi): String {
    val open = state.sit.open
    if (open != null) {
        return "本次观测：${open.name} — 命名时间窗口（最多 ${Sit.RADIO_CAP} 个设备），与观测总结一致。"
    }
    val selected = state.sit.closed.firstOrNull { it.id == state.sit.selectedId }
    if (selected != null) {
        return "本次观测：${selected.name} — 命名时间窗口（最多 ${Sit.RADIO_CAP} 个设备），与观测总结一致。"
    }
    return "本次观测：内存中的最近 15 分钟（约 400 个设备），与观测总结一致。"
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ExportFormatBlock(
    kind: LogExportKind,
    radios: LogExportRadios,
    exporting: Boolean,
    onKind: (LogExportKind) -> Unit,
    onRadios: (LogExportRadios) -> Unit,
    onShare: () -> Unit,
    onSave: () -> Unit,
    hint: String,
) {
    var openFormat by remember { mutableStateOf(false) }
    ExposedDropdownMenuBox(
        expanded = openFormat,
        onExpandedChange = { openFormat = it },
        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
    ) {
        FieldwatchDropdownField("格式", kind.label, openFormat)
        ExposedDropdownMenu(openFormat, { openFormat = false }) {
            LogExportKind.entries.forEach { item ->
                DropdownMenuItem(
                    text = { Text(item.label) },
                    onClick = {
                        onKind(item)
                        openFormat = false
                    },
                )
            }
        }
    }
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        LogExportRadios.entries.forEach { item ->
            Row(
                modifier = Modifier
                    .weight(1f)
                    .selectable(
                        selected = radios == item,
                        onClick = { onRadios(item) },
                        role = Role.RadioButton,
                    ),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                RadioButton(
                    selected = radios == item,
                    onClick = { onRadios(item) },
                    enabled = !exporting,
                )
                Text(item.label, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
    FieldwatchActionButton(
        onClick = onShare,
        enabled = !exporting,
        modifier = Modifier.fillMaxWidth(),
    ) { Text("分享") }
    FieldwatchActionButton(
        onClick = onSave,
        enabled = !exporting,
        modifier = Modifier.fillMaxWidth(),
    ) { Text("保存到 SD 卡／存储空间…") }
    Text(
        hint,
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

private fun sitReportCaption(state: FieldwatchUi): String {
    val open = state.sit.open
    if (open != null) {
        return "本次观测（${open.name}）— 与轨迹使用相同时间窗口。开启 GPS 标记并移动后可进行随行检测，不构成法律认定。"
    }
    val selected = state.sit.closed.firstOrNull { it.id == state.sit.selectedId }
    if (selected != null) {
        return "观测：${selected.name} — 与轨迹使用相同时间窗口。开启 GPS 标记并移动后可进行随行检测，不构成法律认定。"
    }
    return "内存中的最近 15 分钟 — 与轨迹使用相同时间窗口，提供两种格式。开启 GPS 标记并移动后可进行随行检测，不构成法律认定。"
}
