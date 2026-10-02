package app.fieldwatch.domain

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class SettingsPack(
    val format: String,
    val formatVersion: Int = FORMAT_VERSION,
    val exportedAt: String = "",
    val appVersion: String = "",
    val settings: AppSettings = AppSettings(),
    val filter: FilterState = FilterState(),
    val presets: List<FilterPreset> = emptyList(),
    val watchlist: List<WatchTarget> = emptyList(),
    val hiddenPresetIds: Set<String> = emptySet(),
) {
    companion object {
        const val FORMAT = "fieldwatch-settings"
        const val FORMAT_VERSION = 1
    }
}

data class SettingsImportResult(
    val namedRadios: Int = 0,
    val signatureWatches: Int = 0,
    val presets: Int = 0,
    val error: String? = null,
) {
    fun summary(): String {
        error?.let { return it }
        return "已恢复设置、当前筛选条件和 $presets 个预设。" +
            "包含 $namedRadios 个命名设备、$signatureWatches 个已关注特征。"
    }
}

object SettingsExchange {
    val json = Json {
        prettyPrint = true
        ignoreUnknownKeys = true
        encodeDefaults = true
    }

    fun pack(
        settings: AppSettings,
        filter: FilterState,
        presets: List<FilterPreset>,
        watchlist: List<WatchTarget>,
        hiddenPresetIds: Set<String>,
        appVersion: String,
        exportedAt: String,
    ): SettingsPack = SettingsPack(
        format = SettingsPack.FORMAT,
        formatVersion = SettingsPack.FORMAT_VERSION,
        exportedAt = exportedAt,
        appVersion = appVersion,
        settings = settings,
        filter = filter,
        presets = presets,
        watchlist = watchlist,
        hiddenPresetIds = hiddenPresetIds,
    )

    fun encode(pack: SettingsPack): String = json.encodeToString(SettingsPack.serializer(), pack)

    fun parse(text: String): SettingsPack {
        val trimmed = text.trim().trimStart('\uFEFF')
        if (trimmed.isEmpty()) {
            throw IllegalArgumentException("文件为空。")
        }
        val pack = try {
            json.decodeFromString(SettingsPack.serializer(), trimmed)
        } catch (e: Exception) {
            throw IllegalArgumentException(
                "这不是 Fieldwatch 设置备份。请在“设置 → 导出设置”中导出。",
                e,
            )
        }
        if (pack.format == SignaturePack.FORMAT || pack.format == SignaturePack.LEGACY_FORMAT) {
            throw IllegalArgumentException(
                "这是特征包，请使用“导入特征库”。",
            )
        }
        if (pack.format != SettingsPack.FORMAT) {
            throw IllegalArgumentException(
                "这不是 Fieldwatch 设置备份，请打开 fieldwatch-settings JSON 文件。",
            )
        }
        return pack
    }

    /**
     * Replace Settings, the current filter, presets, and watchlist.
     * Keep the catalog, logs, GPS, already-seen keys, the local disclaimer click-through,
     * and whether this phone already showed the Live tour.
     */
    fun apply(local: PersistedConfig, pack: SettingsPack): Pair<PersistedConfig, SettingsImportResult> {
        val next = local.copy(
            settings = pack.settings.copy(
                disclaimerAccepted = local.settings.disclaimerAccepted,
                disclaimerRev = local.settings.disclaimerRev,
                liveTourDone = local.settings.liveTourDone,
                darkTheme = true,
                scanControlsExpanded = false,
            ),
            filter = pack.filter,
            presets = pack.presets,
            watchlist = pack.watchlist,
            hiddenPresetIds = pack.hiddenPresetIds,
        )
        val result = SettingsImportResult(
            namedRadios = pack.watchlist.count { !it.deviceKey.isNullOrBlank() },
            signatureWatches = pack.watchlist.count { !it.fleetId.isNullOrBlank() },
            presets = pack.presets.size,
        )
        return next to result
    }
}
