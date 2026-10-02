#!/usr/bin/env python3
"""生成 Fieldwatch 中文工作原理图（可打印 PNG）。"""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "how-it-works.png")

NIGHT = (11, 15, 20, 255)
INK = (232, 238, 242, 255)
MUTED = (154, 166, 178, 255)
RULE = (46, 58, 72, 255)
CARD = (18, 26, 34, 255)
CARD2 = (24, 34, 44, 255)
PHOS = (61, 255, 154, 255)
PHOS_DIM = (18, 92, 56, 255)
AMBER = (232, 168, 64, 255)
WIFI = (110, 178, 255, 255)
BLE = (186, 154, 255, 255)

W, H = 2400, 1180
PAD = 52

FONT = next((path for path in (
    os.environ.get("FIELDWATCH_CJK_FONT", ""),
    "C:/Windows/Fonts/msyh.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
) if path and os.path.isfile(path)), None)
if FONT is None:
    raise RuntimeError("找不到中文字体，请将 FIELDWATCH_CJK_FONT 设为可用中文 TrueType 字体路径。")
BOLD = os.environ.get("FIELDWATCH_CJK_BOLD_FONT") or (
    "C:/Windows/Fonts/msyhbd.ttc" if os.path.isfile("C:/Windows/Fonts/msyhbd.ttc") else FONT
)


def F(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def M(size):
    return ImageFont.truetype(FONT, size)


def rr(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def wrap(d, s, f, max_w):
    # 中文不依赖空格分词，按字符测宽以避免整段越过卡片边界。
    words = list(s)
    lines, cur = [], ""
    for w in words:
        trial = cur + w
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur.rstrip())
            cur = w.lstrip()
    if cur:
        lines.append(cur)
    return lines


def body(d, x, y, s, f, fill, max_w, leading):
    for line in wrap(d, s, f, max_w):
        d.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def chevron(d, x, y, color=PHOS):
    d.polygon([(x, y - 10), (x + 16, y), (x, y + 10)], fill=color)


def arrow_h(d, x1, x2, y, color=PHOS):
    d.line((x1, y, x2 - 18, y), fill=color, width=4)
    chevron(d, x2 - 16, y, color)


def arrow_v(d, x, y1, y2, color=PHOS):
    d.line((x, y1, x, y2 - 16), fill=color, width=4)
    d.polygon([(x, y2), (x - 10, y2 - 16), (x + 10, y2 - 16)], fill=color)


def card(d, box, kicker, title, lines, accent=PHOS, files=None):
    x1, y1, x2, y2 = box
    rr(d, box, 18, fill=CARD2, outline=RULE, width=2)
    d.rectangle((x1, y1, x1 + 8, y2), fill=accent)
    d.text((x1 + 28, y1 + 20), kicker.upper(), font=F(16, True), fill=accent)
    d.text((x1 + 28, y1 + 48), title, font=F(28, True), fill=INK)
    yy = y1 + 92
    for para in lines:
        yy = body(d, x1 + 28, yy, para, F(20), MUTED, x2 - x1 - 56, 28) + 8
    if files:
        d.line((x1 + 24, y2 - 52, x2 - 24, y2 - 52), fill=RULE, width=1)
        d.text((x1 + 28, y2 - 28), files, font=M(15), fill=PHOS, anchor="lm")
    return box


def build():
    img = Image.new("RGBA", (W, H), NIGHT)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 10, H), fill=PHOS)

    d.text((PAD + 10, 40), "技术规格 · 工作原理", font=F(20, True), fill=PHOS)
    d.text((PAD + 10, 78), "FIELDWATCH", font=F(52, True), fill=INK)
    body(
        d,
        PAD + 10,
        142,
        "手机接收 Wi-Fi 接入点信标与 Bluetooth LE 广播。Fieldwatch 在本机匹配特征、显示实时视图，"
        "记录观测、生成总结，并可推送 TAK 标记。",
        F(24),
        MUTED,
        W - PAD * 2 - 20,
        32,
    )

    # 三列两行网格。
    grid_top = 218
    grid_bot = H - 88
    gap_x, gap_y = 40, 40
    cw = (W - PAD * 2 - gap_x * 2) / 3
    ch = (grid_bot - grid_top - gap_y) / 2

    cells = []
    for r in range(2):
        for c in range(3):
            x1 = PAD + c * (cw + gap_x)
            y1 = grid_top + r * (ch + gap_y)
            cells.append((x1, y1, x1 + cw, y1 + ch))

    # 上排：信号、扫描、匹配；下排：显示、关注、保存与分享。
    x1, y1, x2, y2 = cells[0]
    rr(d, cells[0], 18, fill=CARD2, outline=RULE, width=2)
    d.rectangle((x1, y1, x1 + 8, y2), fill=WIFI)
    d.text((x1 + 28, y1 + 20), "01  空中信号", font=F(16, True), fill=WIFI)
    d.text((x1 + 28, y1 + 48), "信标与广播", font=F(28, True), fill=INK)
    inner_h = (y2 - 60 - (y1 + 96) - 16) / 2
    iy = y1 + 96
    for accent, kick, title, blurb in (
        (WIFI, "Wi-Fi", "接入点信标", "SSID、BSSID、信道、厂商 IE；不包含 Wi-Fi 客户端。"),
        (BLE, "Bluetooth LE", "低功耗蓝牙广播", "名称、公司 ID、UUID、厂商数据；无需配对。"),
    ):
        ib = (x1 + 24, iy, x2 - 24, iy + inner_h)
        rr(d, ib, 12, fill=CARD, outline=RULE, width=1)
        d.text((ib[0] + 16, ib[1] + 12), kick.upper(), font=F(14, True), fill=accent)
        d.text((ib[0] + 16, ib[1] + 36), title, font=F(22, True), fill=INK)
        body(d, ib[0] + 16, ib[1] + 68, blurb, F(18), MUTED, ib[2] - ib[0] - 32, 24)
        iy += inner_h + 12
    d.line((x1 + 24, y2 - 52, x2 - 24, y2 - 52), fill=RULE, width=1)
    d.text((x1 + 28, y2 - 28), "radio/WifiRadio.kt  ·  BleRadio.kt", font=M(15), fill=PHOS, anchor="lm")
    card(
        d,
        cells[1],
        "02  本手机",
        "扫描服务 ScanService",
        [
            "前台服务显示“Fieldwatch 正在扫描”通知。按 Home 保持运行，划掉最近任务或点停止结束采集。",
            "Wi-Fi 分批接收，高性能约每 30 秒一批，受系统限频；BLE 在批次之间持续接收。",
        ],
        PHOS,
        files="radio/ScanService.kt  ·  Permissions.kt",
    )
    card(
        d,
        cells[2],
        "03  识别模式",
        "特征库匹配",
        [
            "SignatureEngine 按内置和自定义规则匹配 OUI、名称通配符、UUID 与厂商数据。",
            "匹配后，解码字段将明文 BLE 字节转换为有意义的值；加密内容仍显示十六进制。",
        ],
        BLE,
        files="domain/SignatureEngine.kt  ·  DefaultCatalog.kt",
    )
    card(
        d,
        cells[3],
        "04  实时画面",
        "实时与显示调整",
        [
            "FilterEngine 决定显示哪些设备。右上角“显示”可选雷达、强度列表、时间线、混合、按分类，以及排序与字段。",
            "实时集合约 400 台设备。筛选隐藏设备；显示设置调整每行内容。",
        ],
        PHOS,
        files="ui/LiveScreens.kt  ·  domain/FilterEngine.kt",
    )
    card(
        d,
        cells[4],
        "05  关注信号",
        "关注列表与信号追踪",
        [
            "关注特征可触发提示音和 / 或语音。重点关注系列与无人机默认已关注。信号追踪依据 RSSI 引导接近一台 BLE 设备。",
            "命名设备给单个 MAC 设置别名，可选择开启提醒。",
        ],
        AMBER,
        files="alert/Alerter.kt  ·  domain/Hunt.kt",
    )
    card(
        d,
        cells[5],
        "06  保存与分享",
        "日志、观测与 TAK",
        [
            "滚动日志写入磁盘。观测记录命名窗口内全部设备。观测总结与 AI 导出使用选中观测，或内存最近 15 分钟。",
            "TAK / CoT 默认关闭。隐私模式遮蔽画面并暂停推送，日志仍保留完整 MAC 与 GPS。",
        ],
        PHOS,
        files="data/LogStore.kt  ·  data/SitStore.kt  ·  domain/TakPublish.kt",
    )

    # 卡片间的流程箭头。
    def mid_right(box):
        return box[2], (box[1] + box[3]) / 2

    def mid_left(box):
        return box[0], (box[1] + box[3]) / 2

    def mid_bot(box):
        return (box[0] + box[2]) / 2, box[3]

    def mid_top(box):
        return (box[0] + box[2]) / 2, box[1]

    for a, b in ((0, 1), (1, 2), (3, 4), (4, 5)):
        x1, y = mid_right(cells[a])
        x2, _ = mid_left(cells[b])
        arrow_h(d, x1 + 6, x2 - 6, y)

    # 页脚。
    d.line((PAD, H - 58, W - PAD, H - 58), fill=RULE, width=1)
    d.text(
        (PAD + 8, H - 30),
        "不支持：Wi-Fi 客户端 · 经典蓝牙 · 蜂窝 / LTE / C-V2X     优先离线，无 Fieldwatch 服务器、账号或遥测。",
        font=F(18),
        fill=MUTED,
        anchor="lm",
    )
    d.text((W - PAD, H - 30), "app.fieldwatch", font=M(16), fill=PHOS, anchor="rm")

    img.save(OUT, "PNG")
    print("已生成", OUT, img.size)


if __name__ == "__main__":
    build()
