package app.fieldwatch.data

import android.content.Context
import android.location.Address
import android.location.Geocoder
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import app.fieldwatch.domain.DebriefPlaces
import app.fieldwatch.domain.GpsSample
import app.fieldwatch.domain.Sighting
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import java.util.Locale
import kotlin.coroutines.resume

/**
 * Optional Debrief enrichment: system reverse-geocoder only (no API key, no
 * cloud account). Never throws to the caller; offline or missing geocoder
 * becomes a note in the report.
 */
object PlaceLookup {
    data class Fix(val label: String, val lat: Double, val lon: Double)

    fun online(context: Context): Boolean {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
            ?: return false
        val net = cm.activeNetwork ?: return false
        val caps = cm.getNetworkCapabilities(net) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    suspend fun lookup(
        context: Context,
        path: List<GpsSample>,
        devices: List<Sighting>,
        now: Long = System.currentTimeMillis(),
        onProgress: ((String) -> Unit)? = null,
    ): DebriefPlaces = withContext(Dispatchers.IO) {
        runCatching { lookupInner(context, path, devices, now, onProgress) }
            .getOrElse { DebriefPlaces(attempted = true, available = false, note = "在线查询未成功，仅显示坐标。") }
    }

    private suspend fun lookupInner(
        context: Context,
        path: List<GpsSample>,
        devices: List<Sighting>,
        now: Long,
        onProgress: ((String) -> Unit)?,
    ): DebriefPlaces {
        if (!online(context)) {
            return DebriefPlaces(
                attempted = true,
                available = false,
                note = "已跳过在线查询：网络不可用，仅显示坐标。",
            )
        }
        if (!Geocoder.isPresent()) {
            return DebriefPlaces(
                attempted = true,
                available = false,
                note = "已跳过在线查询：此手机没有系统地理编码服务（需要 Google Play / 网络定位），仅显示坐标。",
            )
        }
        val fixes = collect(path, devices, now)
        if (fixes.isEmpty()) {
            return DebriefPlaces(
                attempted = true,
                available = true,
                note = "在线查询已开启，但本次观测没有可查询地名的 GPS 记录。",
            )
        }
        val geocoder = Geocoder(context, Locale.getDefault())
        val cache = LinkedHashMap<String, String>()
        val lines = ArrayList<String>(fixes.size)
        for ((i, fix) in fixes.withIndex()) {
            onProgress?.invoke("正在查询地名（${i + 1}/${fixes.size}）…")
            val key = app.fieldwatch.domain.Geo.cellKey(fix.lat, fix.lon)
            val name = cache[key] ?: reverse(geocoder, fix.lat, fix.lon)?.also { cache[key] = it }
            val coord = "%.5f, %.5f".format(Locale.US, fix.lat, fix.lon)
            lines += if (name.isNullOrBlank()) {
                "  · ${fix.label}  $coord（未返回地名）"
            } else {
                "  · ${fix.label}  $name  ($coord)"
            }
        }
        val named = cache.size
        return DebriefPlaces(
            attempted = true,
            available = named > 0,
            note = if (named > 0) {
                "在线查询：系统地理编码服务为 $named 个不同的 GPS 网格返回地名。街道名称由手机网络地理编码服务提供，Fieldwatch 没有云端服务。结果仅为近似位置。"
            } else {
                "在线查询已完成，但系统地理编码服务未返回街道名称，仅显示坐标。"
            },
            lines = lines,
            namesByCell = cache.toMap(),
        )
    }

    fun collect(path: List<GpsSample>, devices: List<Sighting>, now: Long = System.currentTimeMillis()): List<Fix> {
        val out = ArrayList<Fix>(8)
        val seen = HashSet<String>()
        fun add(label: String, lat: Double, lon: Double) {
            if (lat == 0.0 && lon == 0.0) return
            val key = app.fieldwatch.domain.Geo.cellKey(lat, lon)
            if (!seen.add(key)) return
            out += Fix(label, lat, lon)
        }
        val legs = app.fieldwatch.domain.Geo.legs(path, now = now)
        var stayN = 0
        legs.forEach { leg ->
            if (leg.stay) {
                stayN++
                add("停留 $stayN", leg.lat, leg.lon)
            } else {
                add("移动起点", leg.lat, leg.lon)
                add("移动终点", leg.endLat, leg.endLon)
            }
        }
        if (out.isEmpty() && path.isNotEmpty()) {
            add("轨迹起点", path.first().lat, path.first().lon)
            if (path.size > 1) add("轨迹终点", path.last().lat, path.last().lon)
        }
        if (out.size < 8) {
            devices.filter { it.gpsTrail.isNotEmpty() && it.rssi >= -70 }
                .sortedByDescending { it.rssi }
                .take(4)
                .forEach { d ->
                    val p = d.gpsTrail.last()
                    add(d.listTitle().take(28), p.lat, p.lon)
                }
        }
        return out.take(8)
    }

    private suspend fun reverse(geocoder: Geocoder, lat: Double, lon: Double): String? {
        val async = withTimeoutOrNull(8_000L) {
            runCatching {
                if (Build.VERSION.SDK_INT >= 33) {
                    suspendCancellableCoroutine { cont ->
                        geocoder.getFromLocation(
                            lat, lon, 1,
                            object : Geocoder.GeocodeListener {
                                override fun onGeocode(addresses: MutableList<Address>) {
                                    if (cont.isActive) cont.resume(format(addresses.firstOrNull()))
                                }
                                override fun onError(errorMessage: String?) {
                                    if (cont.isActive) cont.resume(null)
                                }
                            },
                        )
                    }
                } else {
                    @Suppress("DEPRECATION")
                    format(geocoder.getFromLocation(lat, lon, 1)?.firstOrNull())
                }
            }.getOrNull()
        }
        if (!async.isNullOrBlank()) return async
        return runCatching {
            @Suppress("DEPRECATION")
            format(geocoder.getFromLocation(lat, lon, 1)?.firstOrNull())
        }.getOrNull()
    }

    private fun format(addr: Address?): String? {
        if (addr == null) return null
        addr.getAddressLine(0)?.trim()?.takeIf { it.isNotEmpty() }?.let { return it }
        val parts = listOfNotNull(
            listOfNotNull(addr.subThoroughfare, addr.thoroughfare).joinToString(" ").ifBlank { null },
            addr.locality,
            addr.adminArea,
            addr.postalCode,
        )
        return parts.joinToString(", ").ifBlank { null }
    }
}
