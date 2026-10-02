#!/usr/bin/env python3
"""生成 Fieldwatch 简体中文用户手册与技术文档 PDF。"""

from __future__ import annotations

import os
import shutil
import sys
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable, ImageAndFlowables
from reportlab.platypus.tableofcontents import TableOfContents

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DOC_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DOC_DIR, "Fieldwatch_User_Manual.pdf")
DIST_OUT = os.path.join(os.path.dirname(DOC_DIR), "dist", "Fieldwatch_User_Manual.pdf")
ICON = os.path.join(os.path.dirname(DOC_DIR), "app", "src", "main", "res", "mipmap-xxxhdpi", "ic_launcher.png")
SHOTS = os.path.join(DOC_DIR, "screenshots")
DIAGRAMS = os.path.join(DOC_DIR, "diagrams")
SCREENSHOT_NOTE = "（上游英文界面示例，操作名称以中文版为准。）"

INK = colors.HexColor("#12171C")
MUTED = colors.HexColor("#4A5560")
RULE = colors.HexColor("#C5CDD4")
PANEL = colors.HexColor("#F4F6F8")
ACCENT = colors.HexColor("#0B7A48")
ACCENT_DK = colors.HexColor("#063D26")
NIGHT = colors.HexColor("#0B0F14")
PHOS = colors.HexColor("#3DFF9A")
AMBER = colors.HexColor("#C47A00")
WARN_BG = colors.HexColor("#FFF6E5")
NOTE_BG = colors.HexColor("#E8F5EE")
HEADER_BG = colors.HexColor("#E6EEE9")
PAGE_W, PAGE_H = letter


def register_chinese_fonts():
    """嵌入中文 TrueType 字体；也可通过环境变量指定本机字体。"""
    candidates = (
        os.environ.get("FIELDWATCH_CJK_FONT", ""),
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    )
    regular = next((p for p in candidates if p and os.path.isfile(p)), None)
    if regular is None:
        raise RuntimeError("找不到中文字体，请设置 FIELDWATCH_CJK_FONT 为中文 TrueType 字体路径。")
    bold = os.environ.get("FIELDWATCH_CJK_BOLD_FONT") or (
        "C:/Windows/Fonts/msyhbd.ttc" if os.path.isfile("C:/Windows/Fonts/msyhbd.ttc") else regular
    )
    pdfmetrics.registerFont(TTFont("FWText", regular, subfontIndex=0))
    pdfmetrics.registerFont(TTFont("FWText-Bold", bold, subfontIndex=0))
    pdfmetrics.registerFontFamily(
        "FWText", normal="FWText", bold="FWText-Bold",
        italic="FWText", boldItalic="FWText-Bold",
    )


register_chinese_fonts()


def styles():
    base = getSampleStyleSheet()
    s = {
        "cover_kicker": ParagraphStyle(
            "cover_kicker", fontName="FWText", fontSize=9, leading=12,
            textColor=PHOS, alignment=TA_CENTER, tracking=2, letterSpacing=1.4,
        ),
        "h1": ParagraphStyle(
            "H1", fontName="FWText-Bold", fontSize=16, leading=20,
            textColor=ACCENT_DK, spaceBefore=16, spaceAfter=8, keepWithNext=0,
        ),
        "h2": ParagraphStyle(
            "H2", fontName="FWText-Bold", fontSize=12.5, leading=16,
            textColor=INK, spaceBefore=12, spaceAfter=5, keepWithNext=0,
        ),
        "h3": ParagraphStyle(
            "H3", fontName="FWText-Bold", fontSize=11, leading=14,
            textColor=ACCENT_DK, spaceBefore=9, spaceAfter=4, keepWithNext=0,
        ),
        "body": ParagraphStyle(
            "Body", fontName="FWText", fontSize=9.5, leading=13,
            textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7,
        ),
        "body_left": ParagraphStyle(
            "BodyLeft", fontName="FWText", fontSize=9.5, leading=13,
            textColor=INK, alignment=TA_LEFT, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet", fontName="FWText", fontSize=9.5, leading=13,
            textColor=INK, leftIndent=14, bulletIndent=0, spaceAfter=3,
        ),
        "caption": ParagraphStyle(
            "Caption", fontName="FWText", fontSize=8, leading=10,
            textColor=MUTED, spaceBefore=2, spaceAfter=10,
        ),
        "cell": ParagraphStyle(
            "Cell", fontName="FWText", fontSize=8, leading=10.5, textColor=INK,
        ),
        "cell_b": ParagraphStyle(
            "CellB", fontName="FWText-Bold", fontSize=8, leading=10.5, textColor=INK,
        ),
        "toc1": ParagraphStyle(
            "TOC1", fontName="FWText-Bold", fontSize=10.5, leading=16,
            textColor=INK, spaceBefore=3,
        ),
        "toc2": ParagraphStyle(
            "TOC2", fontName="FWText", fontSize=9.5, leading=13,
            textColor=MUTED, leftIndent=14,
        ),
        "callout": ParagraphStyle(
            "Callout", fontName="FWText", fontSize=9, leading=12.5,
            textColor=INK, leftIndent=4, rightIndent=4,
        ),
        "mono": ParagraphStyle(
            "Mono", fontName="FWText", fontSize=8, leading=11, textColor=INK,
            backColor=PANEL, leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=8,
        ),
        "footer": ParagraphStyle(
            "Footer", fontName="FWText", fontSize=8, textColor=MUTED,
        ),
    }
    for style in s.values():
        style.wordWrap = "CJK"
    return s


S = styles()


def P(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(i, S["body_left"]), leftIndent=12, bulletColor=ACCENT) for i in items],
        bulletType="bullet",
        start="•",
        leftIndent=16,
        bulletFontName="FWText",
        bulletFontSize=9,
        spaceBefore=2,
        spaceAfter=8,
    )


def numbered(items):
    return ListFlowable(
        [ListItem(Paragraph(i, S["body_left"]), leftIndent=16) for i in items],
        bulletType="1",
        leftIndent=18,
        bulletFontName="FWText",
        bulletFontSize=9,
        spaceBefore=2,
        spaceAfter=8,
    )


def callout(title, body, kind="note"):
    bg = NOTE_BG if kind == "note" else WARN_BG
    bar = ACCENT if kind == "note" else AMBER
    data = [[P(f"<b>{title}.</b> {body}", "callout")]]
    t = Table(data, colWidths=[6.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.4, bar),
        ("LINEBEFORE", (0, 0), (0, -1), 3, bar),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return KeepTogether([Spacer(1, 4), t, Spacer(1, 8)])


def _phone(name, width):
    path = os.path.join(SHOTS, name)
    ir = ImageReader(path)
    iw, ih = ir.getSize()
    img = Image(path, width=width, height=width * ih / float(iw))
    img.hAlign = "CENTER"
    return img


def figure(name, caption, width=2.45 * inch):
    return KeepTogether([
        Spacer(1, 8),
        _phone(name, width),
        P(caption + SCREENSHOT_NOTE, "caption"),
    ])


def _diagram(name, width):
    path = os.path.join(DIAGRAMS, name)
    ir = ImageReader(path)
    iw, ih = ir.getSize()
    img = Image(path, width=width, height=width * ih / float(iw))
    img.hAlign = "CENTER"
    return img


def diagram(name, caption, width=6.9 * inch):
    return KeepTogether([
        Spacer(1, 8),
        _diagram(name, width),
        P(caption, "caption"),
        Spacer(1, 8),
    ])


class CaptionedPhone(Flowable):
    """截图与图注堆叠；ImageAndFlowables 需要 _restrictSize。"""

    def __init__(self, name, caption, width, privacy=True):
        super().__init__()
        self.img = _phone(name, width)
        self.cap = P(caption + SCREENSHOT_NOTE, "caption")
        self._box_w = width

    def _restrictSize(self, availWidth, availHeight):
        return self.wrap(availWidth, availHeight)

    def _unRestrictSize(self):
        return None

    def wrap(self, availWidth, availHeight):
        iw, ih = self.img.wrap(self._box_w, availHeight)
        cw, ch = self.cap.wrap(iw, availHeight)
        self._iw, self._ih, self._ch = iw, ih, ch
        return iw, ih + 6 + ch

    def draw(self):
        self.img.drawOn(self.canv, 0, self._ch + 6)
        self.cap.drawOn(self.canv, 0, 0)


def figure_wrap(name, caption, *items, width=2.2 * inch, privacy=True):
    """右侧截图、左侧环绕正文；后续同节段落继续使用图片旁空白。"""
    flows = []
    for it in items:
        if isinstance(it, str):
            flows.append(P(it))
        else:
            flows.append(it)
    if not flows:
        flows.append(P(""))
    return ImageAndFlowables(
        CaptionedPhone(name, caption, width, privacy=privacy),
        flows,
        imageSide="right",
        imageLeftPadding=12,
        imageRightPadding=0,
        imageTopPadding=2,
        imageBottomPadding=10,
    )


_WRAP_STYLES = {"Body", "BodyLeft"}
_HEADING_STYLES = {"H1", "H2", "H3"}
# 为标题和数行正文保留空间，不将后续跨页长表强制绑定到标题。
_HEADING_KEEP = {"H1": 2.35 * inch, "H2": 2.15 * inch, "H3": 1.95 * inch}


def _is_heading(item):
    return isinstance(item, Paragraph) and item.style.name in _HEADING_STYLES


def _contains_image(item):
    if isinstance(item, (Image, ImageAndFlowables, CaptionedPhone)):
        return True
    content = getattr(item, "_content", None) or getattr(item, "content", None)
    if content:
        return any(_contains_image(sub) for sub in content)
    if isinstance(item, Table):
        for row in getattr(item, "_cellvalues", []) or []:
            for cell in row:
                if _contains_image(cell):
                    return True
    return False


def prevent_orphan_headings(flow):
    """避免页末孤立标题：图片与标题同行分页，其他标题保留数行正文空间。"""
    out = []
    i = 0
    n = len(flow)
    while i < n:
        item = flow[i]
        if _is_heading(item):
            item.keepWithNext = 0
            keep = _HEADING_KEEP.get(item.style.name, 2.1 * inch)
            j = i + 1
            skipped = []
            while j < n and isinstance(flow[j], Spacer):
                skipped.append(flow[j])
                j += 1
            nxt = flow[j] if j < n else None
            if isinstance(nxt, ImageAndFlowables):
                nxt._content = [item] + list(nxt._content or [])
                out.append(nxt)
                i = j + 1
                continue
            if nxt is not None and _contains_image(nxt) and isinstance(nxt, KeepTogether):
                nxt._content = [item] + skipped + list(nxt._content or [])
                out.append(nxt)
                i = j + 1
                continue
            out.append(CondPageBreak(keep))
            out.append(item)
            i += 1
            continue
        out.append(item)
        i += 1
    return out


def wrap_body_around_figures(flow):
    """继续环绕同节正文和列表；遇到标题、表格、提示框、分页或新图时结束。"""
    out = []
    i = 0
    n = len(flow)
    while i < n:
        item = flow[i]
        if isinstance(item, ImageAndFlowables):
            extra = []
            j = i + 1
            while j < n:
                nxt = flow[j]
                if isinstance(nxt, Paragraph) and nxt.style.name in _WRAP_STYLES:
                    extra.append(nxt)
                    j += 1
                    continue
                if isinstance(nxt, ListFlowable):
                    extra.append(nxt)
                    j += 1
                    continue
                break
            if extra:
                item._content = list(item._content) + extra
            out.append(item)
            i = j
            continue
        out.append(item)
        i += 1
    return out


def figure_pair(left_name, left_cap, right_name, right_cap, width=2.48 * inch):
    left = _phone(left_name, width)
    right = _phone(right_name, width)
    t = Table(
        [
            [left, right],
            [P(left_cap + SCREENSHOT_NOTE, "caption"), P(right_cap + SCREENSHOT_NOTE, "caption")],
        ],
        colWidths=[3.25 * inch, 3.25 * inch],
    )
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return KeepTogether([Spacer(1, 8), t, Spacer(1, 6)])


NOTICE_SHORT = (
    '实验性软件，使用风险自负。Fieldwatch 不保证发现追踪器、摄像头、标签或任何其他设备。手机的无线硬件和厂商限制无法由本应用消除。请勿将 Fieldwatch 用于任何涉及安全的场合，包括危及生命的情形。'
)


def table(headers, rows, widths):
    head = [Paragraph(f"<b>{h}</b>", S["cell_b"]) for h in headers]
    body = [[Paragraph(str(c), S["cell"]) for c in row] for row in rows]
    t = Table([head] + body, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), ACCENT_DK),
        ("FONTNAME", (0, 0), (-1, 0), "FWText-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PANEL]),
    ]))
    return t


def draw_ig_mark(c, x, y, s, color=PHOS):
    '绘制相机轮廓图标；原点位于图形左边，y 为垂直中心。'
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(0.9)
    c.roundRect(x, y - s * 0.55, s * 1.15, s * 1.1, s * 0.22, fill=0, stroke=1)
    c.circle(x + s * 0.58, y, s * 0.28, fill=0, stroke=1)
    c.circle(x + s * 0.92, y + s * 0.32, s * 0.08, fill=1, stroke=0)
    c.restoreState()


def draw_x_mark(c, x, y, s, color=PHOS):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.15)
    c.setLineCap(1)
    c.line(x, y + s * 0.5, x + s, y - s * 0.5)
    c.line(x, y - s * 0.5, x + s, y + s * 0.5)
    c.restoreState()


def draw_cover(c, doc):
    c.saveState()
    c.setFillColor(NIGHT)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(PHOS)
    c.rect(0, 0, 10, PAGE_H, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#1A222C"))
    c.setLineWidth(0.6)
    cx, cy, r = PAGE_W / 2, PAGE_H * 0.58, 92
    for i in range(1, 5):
        c.circle(cx, cy, r * i / 4, fill=0, stroke=1)
    c.line(cx - r, cy, cx + r, cy)
    c.line(cx, cy - r, cx, cy + r)
    c.setStrokeColor(PHOS)
    c.setLineWidth(1.4)
    c.line(cx, cy, cx + 62, cy + 62)
    c.setFillColor(AMBER)
    c.circle(cx + 54, cy + 54, 3.2, fill=1, stroke=0)
    if os.path.exists(ICON):
        try:
            c.drawImage(ICON, PAGE_W - 92, PAGE_H - 92, width=56, height=56,
                        mask="auto", preserveAspectRatio=True)
        except Exception:
            pass
    c.setFillColor(PHOS)
    c.setFont("FWText", 9)
    c.drawString(48, PAGE_H - 52, '用户手册 · 技术文档')
    c.setFillColor(colors.HexColor("#E8EEF2"))
    c.setFont("FWText-Bold", 42)
    c.drawString(48, PAGE_H - 118, "FIELDWATCH")
    c.setFillColor(PHOS)
    c.setFont("FWText", 13)
    c.drawString(48, PAGE_H - 142, '面向 Android 的被动无线信号观察工具')
    c.setStrokeColor(colors.HexColor("#2A3340"))
    c.setLineWidth(0.8)
    c.line(48, PAGE_H - 160, PAGE_W - 48, PAGE_H - 160)
    c.setFillColor(colors.HexColor("#C8D0D8"))
    c.setFont("FWText", 10)
    y = 210
    for line in (
        '仅接收公开广播的 Wi-Fi 与 Bluetooth LE 信号。',
        '优先离线运行，无云端、账号或遥测。',
        '提供特征匹配、可视化、提醒与本地日志。',
        '实验性软件，风险自负，请勿用于关键安全用途。',
    ):
        c.drawString(48, y, line)
        y -= 16
    c.setFillColor(MUTED)
    c.setFont("FWText", 9)
    c.drawString(48, 108, '版本 1.1.17-zh-CN · 简体中文版')
    c.drawString(48, 94, '2026 年 10 月 1 日')
    c.drawString(48, 80, '应用包名 app.fieldwatch · Android 10+（API 29）· 目标 API 35')
    c.setStrokeColor(colors.HexColor("#2A3340"))
    c.setLineWidth(0.6)
    c.line(48, 68, PAGE_W - 48, 68)
    c.setFillColor(colors.HexColor("#E8EEF2"))
    c.setFont("FWText", 10)
    c.setFillColor(MUTED)
    c.setFont("FWText", 8)
    c.drawString(48, 50, "Copyright (c) 2026 Off Grid Pete LLC. All rights reserved.")
    c.setFillColor(PHOS)
    c.setFont("FWText", 8)
    draw_ig_mark(c, 48, 20, 7)
    c.setFillColor(colors.HexColor("#C8D0D8"))
    c.setFont("FWText", 8)
    c.drawString(62, 18, "@OffGridPete")
    draw_x_mark(c, 148, 20, 6.5)
    c.setFillColor(colors.HexColor("#C8D0D8"))
    c.drawString(162, 18, "@OGridPete")
    c.setFillColor(PHOS)
    c.setFont("FWText", 8)
    c.drawRightString(PAGE_W - 48, 50, '现场参考文档')
    c.restoreState()


def draw_body(c, doc):
    c.saveState()
    c.setFillColor(NIGHT)
    c.rect(0, PAGE_H - 28, PAGE_W, 28, fill=1, stroke=0)
    c.setFillColor(PHOS)
    c.setFont("FWText-Bold", 8)
    c.drawString(48, PAGE_H - 18, "FIELDWATCH")
    c.setFillColor(colors.HexColor("#9AA6B2"))
    c.setFont("FWText", 8)
    c.drawRightString(PAGE_W - 48, PAGE_H - 18, '用户手册与技术文档')
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    c.line(48, 40, PAGE_W - 48, 40)
    c.setFillColor(MUTED)
    c.setFont("FWText", 8)
    c.drawString(48, 28, "v1.1.17-zh-CN  ·  Off Grid Pete LLC")
    draw_ig_mark(c, 230, 30, 5.2, MUTED)
    c.setFillColor(MUTED)
    c.setFont("FWText", 8)
    c.drawString(242, 28, "@OffGridPete")
    draw_x_mark(c, 330, 30, 5.0, MUTED)
    c.setFillColor(MUTED)
    c.drawString(342, 28, "@OGridPete")
    c.drawRightString(PAGE_W - 48, 28, f"{doc.page}")
    c.restoreState()


class FieldwatchDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        def consider(item):
            if isinstance(item, Paragraph):
                name = item.style.name
                text = item.getPlainText()
                if name == "H1" and text != '目录':
                    self.notify("TOCEntry", (0, text, self.page))
                elif name == "H2":
                    self.notify("TOCEntry", (1, text, self.page))
            elif isinstance(item, (ImageAndFlowables, KeepTogether)):
                for inner in list(getattr(item, "_content", []) or []):
                    consider(inner)

        consider(flowable)


def toc():
    t = TableOfContents()
    t.levelStyles = [S["toc1"], S["toc2"]]
    t.dotsMinLevel = 0
    return t


def story():
    flow = []
    flow += [NextPageTemplate("body"), PageBreak()]
    flow += [
        P('须知：安全与免责声明', "h1"),
        callout(
            '使用风险自负',
            'Fieldwatch 是按 MIT 许可证“原样”提供的实验性软件，不提供任何明示或默示担保，仅用于实验与教学目的下观察公开广播的 Wi-Fi 和 Bluetooth LE。<b>请勿用于任何涉及安全的场合</b>，包括危及生命的情形、人身安全决策或应急响应。列表为空、没有匹配特征或观测总结中没有异常，均不代表安全；匹配成功也不代表已经识别某个人、车辆或威胁。',
            "warn",
        ),
        P(
            '这是一个业余项目，按 MIT 许可证“原样”提供，使用风险自负。您须自行承担使用 Fieldwatch 的责任。在法律允许的最大范围内，Off Grid Pete LLC 不对因使用或无法使用本项目而产生的间接、附带、特殊、后果性或惩罚性损害承担责任。'
        ),
        P(
            '本软件不保证能够发现、命名或报告追踪器、摄像头、标签、接入点或其他设备。已关闭、仅使用蜂窝网络、休眠、使用随机地址、静默或未由手机操作系统公开的无线设备不会出现。每台手机都有各自的无线硬件、固件、扫描配额和厂商电池策略，软件无法消除这些限制。'
        ),
        P(
            '特征匹配、GPS 同行判断（“随行”“疑似尾随”）、观测总结中的描述与 AI 导出结果都只是推测，并非身份认定、法律结论或完整射频采集。您须对使用本应用、本文档及遵守当地法律承担全部责任。使用软件或本手册即表示接受这些条款及 MIT 许可证。本中文说明仅为阅读辅助，许可法律原文见下文。'
        ),
        P(
            '开启位置标记后，位置数据表示接收数据包时<b>本手机</b>所在的位置，并非另一台无线设备的位置。Fieldwatch 没有服务器，位置记录留在手机内，直到您主动分享。隐私模式虽会遮蔽屏幕和观测报告中的坐标，日志仍保留完整坐标。观测总结、日志导出、AI 导出（整次观测或单台设备）及设备详情中的“分享为文本”都可能将轨迹带出手机。开启 TAK / CoT 推送后，完整 MAC 和坐标标记会发送到您配置的局域网；隐私模式会暂停推送。在线地名使用系统地理编码服务（通常由手机厂商或 Google 提供），而非 Fieldwatch 云端。如何保存、分享和发布这些文件由您负责。'
        ),
        P('MIT 许可证（法律原文）', "h2"),
        P("Copyright (c) 2026 Off Grid Pete LLC"),
        P(
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files (the “Software”), to deal "
            "in the Software without restriction, including without limitation the rights "
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
            "copies of the Software, and to permit persons to whom the Software is "
            "furnished to do so, subject to the following conditions:"
        ),
        P(
            "The above copyright notice and this permission notice shall be included in all "
            "copies or substantial portions of the Software."
        ),
        P(
            "THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
            "SOFTWARE."
        ),
        P(
            'AndroidX、Kotlin 及相关库仍采用 Apache-2.0 许可证。应用中打包的 IEEE 与 Bluetooth SIG 编号分配表须遵守各组织的条款，详见源代码目录中的 NOTICE。'
        ),
        PageBreak(),
        P('目录', "h1"),
        toc(),
        P('本手册的阅读顺序', "h3"),
        P(
            '建议先读第 4、5 章。第 4 章介绍安装、权限、快速入门（五个标签页和显示调整）及最大采集量检查表（§4.5）；第 5 章说明各个页面。第 8 章介绍筛选，即实时页面显示哪些设备，包括随行判断（§8.5）；第 9 章介绍特征库及匹配标签；第 12 章给出具体现场问题的操作流程；第 14 章用一页说明信号如何变成列表行。其余章节供查阅，涉及无线原理、日志、现场操作规范与内置特征库。'
        ),
        table(
            ['您的需求', '阅读位置'],
            [
                ['安装、首次启动与快速入门', '第 4 章，然后 §4.4'],
                ['信号如何变成列表行（处理流程）', '第 14 章'],
                ['尽量提高采集频率（会增加耗电）', "§4.5"],
                ['了解各标签页与显示调整图标', '§4.4，然后第 5 章'],
                ['减少实时页面中的设备数量', '第 8 章，然后 §5.3 的“实时 → 显示”'],
                ['了解哪些设备与我一起步行或乘车', '§8.5（判断原理）与 §12.2（操作流程）'],
                ['开启或关闭某个特征系列', '第 9 章'],
                ['读取明文 BLE 字节（温度、Remote ID 等）', '§9.6 解码字段'],
                ['查看标签的分离状态或无人机的空中、地面、紧急状态', "§5.4.1"],
                ['接收 BLE 和 Wi-Fi 上的 Remote ID', "§5.8.3, §9.6.6, §12.16"],
                ['根据载荷规范建立自己的解码映射', "§9.6.1–§9.6.5"],
                ['在 ATAK / TAK 上叠加设备标记（CoT 推送）', '§5.8（配置）、§12.15（观测）、§12.16（Remote ID）'],
                ['轨迹、观测对比与日志导出', '§5.6，然后第 11 章'],
                ['自定义名称与观测备注', '§5.5，“设置 → 命名设备”'],
                ['尾随、新到设备、信号追踪与摄像头', '第 12 章'],
                ['查找不熟悉的术语', '附录术语表'],
            ],
            [3.2 * inch, 3.3 * inch],
        ),
        Spacer(1, 6),
        callout(
            '截图说明',
            '本手册使用从上游原版 PDF 恢复的真实手机截图，画面为<b>英文界面示例</b>，并非中文版重新拍摄；中文操作名称以本手册正文和中文版应用为准。原图拍摄于 Galaxy A54，并开启了<b>设置 → 隐私模式</b>；MAC 后半部分显示为 **:**:**，详情中的最近 GPS 坐标也被遮蔽，手机内的日志保持完整。需要在屏幕上查看完整 MAC 或坐标时，请关闭隐私模式。',
            "note",
        ),
        PageBreak(),
    ]

    # 1 Introduction
    flow += [
        P('1. 简介与背景', "h1"),
        P('1.1 Fieldwatch 的用途', "h2"),
        P(
            '我最初将 Fieldwatch 做成个人工具，用来查看手机能接收到的 Wi-Fi 接入点和 Bluetooth LE 广播，更好地了解周围正在使用的设备。它以被动方式工作，只接收信号；无需外接适配器、账号或后端服务器。我希望它能在现场离线使用。'
        ),
        P(
            '我想要一个现代、易用且可按任务调整的界面；用筛选减少无关信息；随时扩展特征库；并为所观察到的设备生成报告。'
        ),
        P(
            '经过一段时间的使用和迭代，它已经足够实用，因此我决定与大家分享。'
        ),
        P(
            '这是我在业余时间出于兴趣制作的项目。Fieldwatch 没有后端、没有广告，所有数据都留在手机上，通过 APK 侧载安装。'
        ),
        P(
            '如果发现应用或文档中的错误、不合理之处，或有功能建议，请在 GitHub 提交 issue，帮助项目改进。希望它对您也有用，也欢迎反馈使用体验。'
        ),
        P(
            '使用本应用不需要掌握无线电专业术语。本手册采用应用中的名称并解释其含义；如 §5.5 这样的编号指向详细章节。先读第 4、5 章，现场遇到具体问题时查阅第 12 章；想先了解架构，可读第 14 章的一页处理流程。'
        ),
        P(
            '请务必阅读封面后的须知。Fieldwatch 属于实验性工具，会漏检设备，不能作为安全系统。'
        ),
        P('可以看到什么，哪些设备不会出现', "h2"),
        P(
            '实时列表每行最醒目的标记是<b>带分类图标的圆圈</b>，如定位标签、手机 / 电脑、音频、家庭物联网等。未匹配的设备显示问号。筛选分类按钮和“按分类”标题也使用相同图标。无线类型仍只有两种；它们以副标题行（较小的第二行）开头的 <b>Wi-Fi</b> 或<b>蓝牙</b>小图标表示，不使用 AP/LE 两字母标签，也不是该行的主图标：'
        ),
        bullets([
            '<b>AP（Wi-Fi 接入点）。</b>广播网络名称（SSID）的无线设备，例如家用路由器、咖啡馆热点、Mesh 节点、开启热点的手机，以及广播 Wi-Fi 的部分摄像头和物联网设备。只是<i>连接到</i>其他 Wi-Fi 网络的笔记本或手机<b>不会</b>出现，原生 Android 无法显示这些客户端。',
            '<b>LE（低功耗蓝牙广播设备）。</b>广播 BLE 数据包的设备，例如耳机、手机、AirTag 类定位器、音箱、手表，以及大量未命名设备。Fieldwatch 只监听，不为检测而配对或连接。',
        ]),
        P(
            '“显示 → 副标题行 → 无”会隐藏第二行及无线类型小图标，以容纳更多设备；分类图标和标题仍保留。详情页会写明“Wi-Fi 接入点”或“BLE 广播设备”。扫描通知仍显示“Wi-Fi N 个 · BLE N 个 · 特征 N 个”。参见 §5.3、§5.4。'
        ),
        P(
            '列表右侧的 <b>RSSI</b> 以 dBm 表示该设备信号<i>在本手机处</i>的强弱，不是距离。数值越接近 0，信号越强，例如 -40 远强于 -90。墙壁、人体、车辆及设备发射功率都会影响它。信号追踪（§5.5、§12.8、§12.13）依据强弱变化，而不是米数。'
        ),
        P('贯穿本手册的常用术语', "h2"),
        bullets([
            "<b>分类图标。</b>实时列表的圆形图标，表示首个匹配特征的分类；未匹配时显示 <font face='FWText'>?</font>，便于快速浏览。参见 §5.4、§9.5。",
            '<b>AP / LE。</b>两种无线类型：AP 是广播网络的 Wi-Fi 接入点（不是客户端），LE 是 BLE 广播设备。实时页面中使用副标题行内的 Wi-Fi / 蓝牙小图标表示，不是两字母标签或圆形分类图标。副标题行设为“无”后，小图标也会隐藏，完整含义见前文。',
            '<b>MAC。</b>无线地址，默认位于实时列表第一行（“显示 → 标题行”）。可移至副标题行，也可隐藏第二行。手机的 BLE 地址常会随机变化，因此“新”MAC 可能仍是同一实体设备换了地址。',
            '<b>特征。</b>Fieldwatch 查找的命名模式，例如 AirTag、Flock、Tile。行上的标签表示模式匹配成功，并不意味着确认了人员身份或设备序列号。特征始终参与标注，筛选决定实时页面显示什么。',
            '<b>筛选与日志。</b>筛选只改变实时页面；开启日志后，滚动日志仍记录听到的信号。在页面隐藏 AirTag 不会从文件中删除它们。',
            '<b>观测总结与日志。</b>未选择命名观测时，观测总结读取仍在内存中的最近 15 分钟设备（约 400 台）。日志导出读取滚动会话文件，观测导出则给出该时间窗口的设备清单。驾车且未开启命名观测时，应多次生成观测总结。参见 §5.6、§11.4.1。',
            '<b>过期 / 消失。</b>超过“设置 → 过期时间”及“显示 → 短暂保留”指定时间没有收到数据包。列表行可能仍以暗色保留，不表示设备永久关机。',
            '<b>关注 / 书签。</b>某特征系列或某 MAC 出现时，发出提示音和 / 或语音。语音可读分类、特征名称或两者（“设置 → 播报内容”）。详情页的书签只关注一台设备，设备离开后不会自动删除。参见 §5.5、§10.1-10.2.1。',
            '<b>观测。</b>一次在房间、步行或驾车过程中观察无线设备的会话。“报告 → 开始观测”为该窗口命名；轨迹、观测总结、观测导出、对比中的本次观测和 AI 导出都使用它。未开始命名观测时，报告使用内存中的最近 15 分钟。日志导出仍读取会话日志文件。参见 §5.6。',
            '<b>标签。</b>实时列表上有颜色的特征名称，表示模式命中而非身份认定。同色的第二个标签可能显示解码状态，如“分离”“空中”等。参见 §5.4.1。',
            '<b>OUI。</b>分配给厂商的 MAC 前三个字节。同一模块厂商的产品会用于许多设备，因此只匹配 OUI 的判断较弱。',
        ]),
        P('1.2 设计理念', "h2"),
        bullets([
            '<b>仅被动接收。</b>Fieldwatch 只监听；检测过程不会发送取消认证、注入探测、配对、连接或加入网络。',
            '<b>优先离线。</b>配置、特征定义、关注列表和日志都保存在应用私有目录，无账号或后端。',
            '<b>注重隐私。</b>清单文件禁用了备份，也不包含分析统计 SDK。',
            '<b>命名模式并非身份。</b>命中表示 OUI、名称、UUID、厂商数据或共同出现模式匹配，不是人员、车辆或某个设备序列号的证明。',
            '<b>默认值可修改。</b>首次启动会写入完整特征库，此后每条特征和预设都可修改或删除。',
            '<b>列表显示可调整。</b>实时页面并非固定罗列全部字段。实时页的显示调整图标可控制每台设备展示多少内容。筛选隐藏设备，“显示”隐藏行内字段；同一次观测中，两人可以使用不同列表布局，详情页仍保留完整解码信息。',
        ]),
        P('1.3 预期使用场景', "h2"),
        table(
            ['场景', 'Fieldwatch 的作用'],
            [
                ['隐私感知', '查看周围广播 Wi-Fi 或 BLE 的设备，以及它们是否符合已知追踪器或摄像头模式。'],
                ['反监视检查', '观察命名特征何时出现、停留，以及移动后是否再次出现。应结合 RSSI 趋势和持续存在情况，不凭单个数据包下结论。开启 GPS 标记后步行，观测总结中的追踪部分仍覆盖最近 15 分钟，即使后来切换实时视图或筛选。'],
                ['现场观察', '在某处停留或步行，查看实时强度，导出带时间戳的日志供后续复核。'],
                ['特征模式识别', '根据已观察到的设备定义并复用特征：OUI 系列、SSID 通配符、BLE UUID 或厂商载荷。'],
                ['事后复盘', '结合时间线、设备历史及“报告 → 日志”（CSV / JSON lines / GPX / KML / WiGLE），还原信号源的出现与消退时间。'],
                ['现场操作流程', '第 12 章包括步行尾随、房间新到设备、BLE 信号追踪和车辆检查、单一特征系列、隐藏杂波、自有设备与疑似标签、摄像头 / ALPR 观测、重点关注（读卡器 / 渗透测试设备），以及观测总结、AI 导出和日志导出。'],
            ],
            [1.7 * inch, 4.8 * inch],
        ),
        Spacer(1, 8),
        callout(
            '不具备攻击能力',
            'Fieldwatch 是观察工具，不能关闭摄像头、解锁追踪器或识别人员。请把匹配当作需要旁证的假设，例如目视确认、另一台接收设备或稍后重访。',
            "note",
        ),
        P('1.4 软件状态', "h2"),
        callout('实验性工具，不用于关键安全场景', NOTICE_SHORT, "warn"),
        P(
            '完整条款位于封面之后的须知页。§1.3 的用途是实验性观察与事后复盘，不是人身防护或应急决策。'
        ),
    ]

    # 2 Research
    flow += [
        PageBreak(),
        P('2. 研究依据与设计决策', "h1"),
        P('2.1 研究资料', "h2"),
        P(
            '默认特征库和匹配规则来自公开资料，并非厂商专有文档。组件厂商的 OUI 应视为推测，因为同一芯片会出现在许多产品中。'
        ),
        table(
            ['资料类别', '提供的信息'],
            [
                ['IEEE MA-L 注册表', 'B4:1E:52 于 2024 年 5 月 9 日注册给 Flock Safety，是默认集合中唯一高置信度的 Flock 自有 OUI。'],
                ['独立 ALPR / DeFlock 研究', '现场记录了 Flock 硬件常见的 LiteOn 摄像头无线模块、Silicon Labs 电池包 OUI，以及 Flock-XXXXXX、FS Ext Battery、Penguin、Pigvision 等 SSID 模式。'],
                ['GainSec / 固件分析文章', 'Raven BLE 服务 UUID 范围为 0x3100-0x3500。XUNTONG 厂商 ID 0x09C8 对应 Penguin / Flock 外部电池，而非 Raven 声学传感器。'],
                ['BLE 定位标签惯例', 'Apple 0x004C 的离线查找类型 0x12；Samsung SmartTag FD5A / 0x0075；Tile 0x00C7 和 FEED/FEDD。Chipolo 与 Pebblebee/moto tag 使用名称匹配，属于默认启用的 Find Hub 定位器。IETF DULT 启用定位的广播使用 FCB2 服务数据，包含网络 ID 和靠近主人标志位。'],
                ['Android 平台文档', 'WifiManager 扫描限频、BLE ScanSettings、位置 / NEARBY_WIFI_DEVICES / BLUETOOTH_SCAN 权限模型及前台服务类型。'],
            ],
            [1.9 * inch, 4.6 * inch],
        ),
        Spacer(1, 6),
        P('2.2 为何选择这些检测方式', "h2"),
        P(
            '普通应用无需 root，即可使用原生 Android 公开提供的两类接收接口：'
        ),
        bullets([
            '<b>Wi-Fi 扫描结果：</b>BSSID、SSID（或隐藏）、RSSI、频率 / 信道、能力标志；较新 API 还提供 Wi-Fi 标准 / 信道宽度提示。每项结果均为接入点类信标，如基础设施 AP、热点、Mesh 节点、物联网软 AP，不包含已连接的客户端。',
            '<b>BLE 广播：</b>地址、本地名称、RSSI、服务 UUID、厂商专用数据、原始广播字节，以及协议栈提供时的 PHY / TX 元数据。',
        ]),
        P(
            "采集仅使用这两类接口。Fieldwatch 不执行 Bluetooth Classic 搜索（<font face='FWText'>startDiscovery()</font>），因为该 API 会发送查询包，且不同于 BLE 广播。仅响应 Classic 的 HC-05 / HC-06 等模块不会出现。参见 §3.5、§7.2。"
        ),
        P(
            '这些字段足以实现命名特征引擎，但不足以测向、嗅探 Wi-Fi 客户端或解密。引擎支持 OUI / MAC 前缀、名称或通配符、16 位或 128 位服务 UUID、厂商公司 ID、厂商数据前缀、无线类型、隐藏 SSID，以及可选的多设备共同出现规则（共享 OUI 和 / 或连续 MAC 尾部）。'
        ),
        P('2.3 为何选择这些视图', "h2"),
        P(
            '五种视图共享同一组筛选后的设备，因此改变显示方式不会改变采集内容。实时页的显示调整图标可选择身份字段、顺序和附加信息。筛选决定<i>哪些设备</i>出现，“显示”决定每台设备<i>展示多少内容</i>，均不影响日志。'
        ),
        bullets([
            '<b>经典雷达</b>以极坐标表示 RSSI，不是具有真实方位角的雷达平面显示，便于快速观察数量、强弱和特征。角度由 MAC 的稳定哈希决定，同一设备保持在相同扇区。亮线在前、渐暗扇形拖尾在后；雷达标签使用简短特征 / 推测名称，不采用标题行与副标题行设置。',
            '<b>强度列表</b>适合排查。默认第一行 MAC、第二行名称与类型，右侧 RSSI，可附信号条和特征标签。标题行、副标题行（含“无”）、排序、短暂保留、RSSI 下的频率、首次 / 最近出现及其他开关均在“显示”中。厂商信息位于详情页，不在列表。可简化到单行名称，也可显示名称、MAC、信号条、迷你曲线和时间。',
            '<b>时间线</b>以 15 分钟条带回答何时出现与离开。持续广播形成连续条；实际中断约 45 秒后重新出现会开启新段。标题行 / 副标题行与列表相同。',
            '<b>混合视图</b>保留排序列表，并添加占满行宽的 RSSI 迷你曲线：固定 -30 至 -100 dBm 网格，按包顺序排列，最新在右侧，并显示相同趋势标记。',
            '<b>按分类</b>以层级展示同一筛选结果：分类名称 A-Z、分类内特征 A-Z，再列设备。默认“显示全部”保留空分类，避免列表跳动；“折叠空分类”隐藏零项。这些按钮位于列表顶部并随之滚动。依次点击分类、特征、设备进入详情，未匹配设备排最后。设备行采用相同显示开关。匹配两类的设备会在两类中计数，页头仍显示去重后的设备总数。',
        ]),
        P('2.4 Android 手机与专用嗅探硬件的取舍', "h2"),
        table(
            ['维度', 'Android 手机（Fieldwatch）', '典型 ESP32 嗅探器'],
            [
                ['无线硬件', '独立 Wi-Fi（2.4/5/6 GHz）与 BLE 5.x，可同时运行。', '通常只有一套 2.4 GHz 无线硬件，Wi-Fi 与 BLE 需要分时运行。'],
                ['Wi-Fi 可见范围', '仅接入点。原生 Android 不提供混杂模式的 STA / 探测帧采集。', '混杂模式可看到站点、探测帧及隐藏 SSID 客户端。'],
                ['扫描频率', '受操作系统限频；前台运行并开启位置有帮助，后台受限。', '操作者可控制跳频。'],
                ["BLE", '低延迟观察、扩展广播、厂商与服务数据。', '可进行观察，但用于历史数据的内存较少。'],
                ['持久化', '较大的本地存储，可通过系统分享面板导出，并使用通知。', 'microSD / LittleFS，界面能力有限。'],
                ['方向', '无（没有 AoA API）。', '未增加额外硬件时无。'],
                ['法律 / 服务条款', '使用公开扫描 API，仍须遵守当地法律。', '若固件不发射信号，也受仅接收的约束。'],
            ],
            [1.35 * inch, 2.55 * inch, 2.6 * inch],
        ),
        Spacer(1, 6),
        P(
            'Fieldwatch 利用手机的双无线硬件、5 GHz AP、通知、不限规则数与历史记录等优势，但不具备 ESP32 的 Wi-Fi 混杂模式视野。需要客户端侧帧时，应配合专用嗅探器，将 Fieldwatch 作为 BLE 与 AP 信息的补充。'
        ),
    ]

    # 3 Limitations
    flow += [
        PageBreak(),
        P('3. 限制', "h1"),
        P('3.1 Android 平台限制', "h2"),
        bullets([
            '<b>Wi-Fi 扫描限频。</b>Android 将 WifiManager.startScan() 限制为约每两分钟四次。Fieldwatch 按高性能 / 均衡 / 省电分别间隔约 30 / 40 / 55 秒请求，并跟踪配额以避免集中请求后长时间无结果。原生 Android 的 AP 扫描始终是分批接收再等待，没有连续数据流。“设置 → 加快 Wi-Fi AP 扫描”可缩短至约 8 秒，但必须先关闭开发者选项中的 Wi-Fi 扫描限频，并由 Fieldwatch 读取该系统开关（Android 11+）。未满足时，默认节奏就是上限。两批之间错过的 AP 也无法匹配特征；Cradlepoint IBR*、AirLink OUI、UniFi、Cisco、隐藏车队 SSID 等只有在有效范围内实际扫描到才会标注，驾车时这个窗口很短。参见 §7.1.1、§10.3.1。',
            '<b>必须开启系统位置服务。</b>否则 BSSID 及部分 BLE 地址会被隐藏或进一步随机化。即使 Fieldwatch 不是地图应用，也需要精确位置权限。',
            '<b>NEARBY_WIFI_DEVICES 与 BLUETOOTH_SCAN</b>分别在较新的 Android 13 / 12+ 上必需。Fieldwatch 不设置 neverForLocation，因为该标志会去除特征引擎所需的标识符。',
            '<b>厂商电池管理</b>（尤其 Samsung One UI）可能冻结未获豁免的后台无线扫描。依次设置“允许后台使用”和“不受限制的电池使用”。部分手机不会直接打开“不受限制”页面，需点击“允许后台使用”文字行进入选择。',
            '<b>Samsung BLE 暂停。</b>持续低延迟、无筛选扫描几分钟后可能被暂停。Fieldwatch 会周期性重启扫描器（约运行 70 秒后休息几秒），并在约 18 秒没有广播时重启。状态可能显示“BLE 周期重启”或“BLE 已暂停 · 正在重启”。',
            '<b>看不到 Wi-Fi 客户端。</b>每条 Wi-Fi 记录都是 AP 或类似广播设备，如手机热点、Mesh 节点、摄像头 / 物联网软 AP。仅作为其他网络客户端的手机、笔记本或摄像头不会出现。',
            '<b>没有混杂或监听模式。</b>原生 Android 不向普通应用开放 802.11 监听接口。Fieldwatch 无法开启混杂模式、捕获原始帧、锁定某信道跟踪 BSSID，也无法看到操作系统扫描未返回的管理帧。USB 嗅探器或 root / 自定义协议栈属于另一类工具。',
            '<b>不采集蜂窝射频。</b>Fieldwatch 不扫描 LTE/5G。仅通过运营商网络通信的摄像头，即使就在头顶也不可见。',
            '<b>密集人群。</b>手机会轮换 BLE 地址。为控制内存，实时集合约限制为 400 台（硬上限 900），未命名 BLE 约三分钟后移除。观测总结读取同一内存映射，因此在城市驾车几公里后，行程开始的数据可能已被替换。参见 §11.4.1。',
        ]),
        callout(
            'Wi-Fi 检测结果都是接入点',
            'Wi-Fi 行副标题行开头的小图标确实表示 Wi-Fi，圆形主图标仍表示分类。原生 Android 只报告广播 SSID 的设备；隐藏 SSID 的 AP 名称为空并带 HIDDEN 标志。Fieldwatch 看不到关联客户端、通配探测请求或使用 Wi-Fi 但未广播网络的设备。手机处于热点或 Wi-Fi Direct 群组所有者模式时会出现，同一手机仅连接咖啡馆网络时不会出现。客户端侧采集需要专用嗅探器。',
            "note",
        ),
        P('3.2 无测向能力', "h2"),
        P(
            '手机未提供到达角。雷达角度由 MAC 哈希决定，只为让设备在图上位置稳定，并非北向、左侧或真实方位。距中心远近表示 RSSI，与实际距离仅弱相关，墙壁、人体衰减和发射功率影响很大。信号追踪（§5.5、§12.13）用相同 RSSI 指示靠近 / 远离；贴身拿手机转身可借身体遮挡粗略判断方向，但这不是测向仪或指南针。'
        ),
        P('3.3 依赖主动广播', "h2"),
        P(
            '已关机、休眠超过过期窗口，或使用协议栈未报告的 PHY / 信道的设备不会出现。许多 Flock 等 ALPR 设备主要使用 LTE/5G，仅在配置、维护或备用场景开启 Wi-Fi；新款静默安装甚至从不广播。没有匹配不代表没有摄像头。BLE 标签常以低占空比广播，因此可能在实时集合中时隐时现。参见 §7.6.1。'
        ),
        P('3.4 电量', "h2"),
        P(
            '高性能采用 BLE SCAN_MODE_LOW_LATENCY（约每 70 秒重启）和约每 30 秒一次 Wi-Fi 扫描，这是不超过系统每两分钟四次限制的最快节奏。均衡为约 40 秒 / SCAN_MODE_BALANCED，省电为约 55 秒 / SCAN_MODE_LOW_POWER。只有关闭系统 Wi-Fi 扫描限频后，“加快 Wi-Fi AP 扫描”才会改为约 8 秒，增加耗电与发热，BLE 节奏不变。“保持屏幕常亮”会在 Fieldwatch 前台运行时保持亮屏，避免 Samsung 在熄屏后暂停 BLE。扫描通知是 Android 保持服务运行所必需的，不是装饰。'
        ),
        P('3.5 Fieldwatch 无法做到的事', "h2"),
        bullets([
            '截获、解密或读取业务载荷流量。',
            '取消认证、干扰、配对或以其他方式操控目标。',
            '仅凭射频识别人员、车牌或具体摄像头序列号。',
            '保证 OUI 匹配就是 Flock 硬件。只有 B4:1E:52 由 IEEE 分配给 Flock Safety；其他前缀属于用于多种产品的组件厂商。',
            '看到关联 Wi-Fi 客户端、隐藏 SSID 站点、通配探测请求或发往 Flock MAC 的帧。这里只接收 AP 信标。',
            '进入混杂或 802.11 监听模式、采集原始帧或锁定单一信道。原生接口是 startScan() 返回的 AP 批次。',
            '接收摄像头的 LTE/5G 回传，蜂窝网络不在应用采集范围。',
            '接收 Bluetooth Classic（BR/EDR）。Fieldwatch 不执行 Classic 查询，因此仅 Classic 的 HC-05 / HC-06 不会出现。业余 BLE 串口特征只匹配 BLE 广播名称。参见 §7.2、§12.14。',
            '生成带真实方位的射频地图。',
            '在未获位置、附近设备和通知权限时正常运行。',
            '保证追踪器、摄像头或其他设备一定存在或不存在。漏检正常，不能将 Fieldwatch 当作安全系统。',
        ]),
        callout(
            '置信度原则',
            'B4:1E:52 加 Flock-* SSID，或 Raven UUID 0x3100-0x3500，可视为高置信度。LiteOn / Silicon Labs / Raspberry Pi OUI 仅能低置信度推测，除非名称、UUID 或厂商 ID 提供旁证；这些组件 OUI 广泛用于数百万台无关设备。',
            "warn",
        ),
    ]

    # 4 Getting started
    flow += [
        PageBreak(),
        P('4. 入门', "h1"),
        P(
            "本章介绍安装与首次启动。简体中文版需先按本仓库 README 的构建说明生成本地 APK，再侧载安装；原作者 GitHub 的 <font face='FWText'>Fieldwatch.apk</font> 是上游构建，不代表本次中文版本。"
        ),
        P('4.1 安装', "h2"),
        P(
            "Fieldwatch 未在 Play 商店发布，需要自行安装 APK（侧载）。包名为 <font face='FWText'>app.fieldwatch</font>，最低 Android 10（API 29），此构建目标 API 35。上游在 Galaxy A54 上测试，面向多数 Android 10+ 手机。应用不会自动更新，请保留可信 APK 的副本。"
        ),
        P(
            '<b>从本地构建安装中文版。</b>按 README 构建后，将生成的 APK 复制到手机（USB、Drive 或“文件”）。打开文件管理器或下载目录并点击 APK。若被阻止，进入“设置 → 应用 → 特殊应用权限 → 安装未知应用”（Samsung：“设置 → 安全和隐私 → 安装未知应用”），允许用于打开 APK 的“文件”、Chrome、Drive 等应用，然后重试。侧载时 Play Protect 可能提示来源不是 Play；只有信任该文件时才选择继续安装。若发行方提供 SHA-256，应与下载文件核对。不同签名的本地与上游构建不能直接相互覆盖，卸载前应导出所需数据。'
        ),
        P(
            '<b>通过电脑（adb）。</b>开启 USB 调试后，将命令中的文件名替换为实际 APK 路径：'
        ),
        P("adb install -r Fieldwatch.apk", "mono"),
        P(
            '安装完成后从启动器打开 Fieldwatch。请保留常驻“Fieldwatch 正在扫描”通知；点击通知中的“停止”会结束采集。'
        ),
        P('4.2 必需权限', "h2"),
        table(
            ['权限', '申请原因'],
            [
                ['位置（精确与粗略）', '没有位置权限，Android 不会返回 BSSID 或有效 BLE 地址。默认开启的“为检测结果添加 GPS 标记”会在扫描时请求实时 GPS / 网络定位（忽略超过 30 秒的最近已知位置），用于日志、随行判断和观测总结。'],
                ['附近的 Wi-Fi 设备（13+）', '用于新版 Android 的 Wi-Fi 扫描。'],
                ['蓝牙扫描与连接（12+）', '用于 BLE 观察。某些设备的名称读取要求协议栈具备连接权限；Fieldwatch 不为检测建立 ACL 连接。'],
                ['通知（13+）', '常驻扫描状态与关注提醒。'],
                ['振动', '关注列表的触觉提醒。'],
                ['前台服务（位置与已连接设备）', '界面不在前台时，保持两种无线扫描运行。'],
                ['互联网（安装时授予）', '用于在线地名与地图（观测总结 / AI 导出的地理编码，轨迹中的 OSM 地图瓦片），以及可选的 TAK / CoT UDP 推送（§5.8）。Fieldwatch 没有账号，也不连接 Fieldwatch 服务器。'],
                ['忽略电池优化', '可选，在设置中申请，防止厂商后台管理冻结服务。'],
            ],
            [2.1 * inch, 4.4 * inch],
        ),
        Spacer(1, 6),
        P('4.3 首次启动', "h2"),
        figure_wrap(
            "fig-tour.png",
            '实时页面导览：显示调整、暂停与五个标签页。',
            numbered([
            '首次会出现<b>免责声明与许可</b>页面。勾选<b>我已阅读并同意</b>，点击“继续”，随后才能扫描。授予权限后，实时页会显示一次导览，介绍显示调整、暂停及五个标签页；点击“知道了”关闭。“设置 → 显示实时页导览”可再次打开。参见 §4.4。',
            '在权限页授予权限。必需权限齐全之前，Fieldwatch 不会启动无线扫描。',
            '出现前台通知 <b>Fieldwatch 正在扫描</b>。请保留它，点击“停止”会结束采集。',
            "首次运行会写入 <font face='FWText'>files/config.json</font>，载入内置特征库、预设、关注项和设置。以后启动读取该文件。“设置 → 导出特征 / 导出设置”分别分享特征库和开关状态，两个文件均不包含日志或 GPS。参见 §5.7、§9.3。",
            '实时页打开上次使用的视图，默认“按分类”。RSSI 信号条、特征名称、频率及首次 / 最近出现默认开启。页头的三个小图标分别显示 Wi-Fi 接入点、BLE 广播设备和当前特征命中数，最后一个与特征库标签页图标相同；计数后可能附无线状态提示。',
            '系统位置或蓝牙未开启时请开启。实时页头和设置中会提示“Wi-Fi N 秒后扫描”“等待系统”“BLE 周期重启”等。默认保持屏幕常亮。离开应用前，设置“允许后台使用”和“不受限制的电池使用”；部分 Samsung 等手机需点击“允许后台使用”文字行继续进入“不受限制”。',
            ]),
            privacy=False,
        ),
        callout(
            '保持扫描',
            '首次启动后，在 Fieldwatch 设置中启用“允许后台使用”，再选择“不受限制的电池使用”；部分手机需点击前者的文字行进入。默认常亮可避免观察时熄屏导致 BLE 暂停，放入口袋时可关闭。还应避免把 Fieldwatch 加入“让未使用的应用休眠”。权限、厂商电池、高性能及加快 Wi-Fi 的完整检查表见 §4.5。',
            "warn",
        ),
        P(
            '<b>初始配置。</b>首次启动及恢复默认值会载入内置特征库，每条规则命中时均标注。默认开启：保持屏幕常亮、GPS 标记、在线地名、关注提醒、提示音、关注特征语音（播报“分类 + 特征”）及跳转到新关注检测。默认关注重点关注项：Axon、WatchGuard Video、Ray-Ban / Meta、Snap Spectacles、Fieldy、Plaud Note、业余 BLE 串口、Hak5 Pineapple、Flipper Zero、Pwnagotchi、Marauder / Deauther、GhostESP、Bruce、Porkchop、Cradlepoint、AirLink、Compex、Novatel Wireless、Utility Inc，以及路边 / 公共摄像头与 ALPR（Flock、Penguin、Pigvision、FS Ext Battery、Genetec AutoVu、Rekor、Motorola Vigilant、Verkada、Avigilon、Axis、Hikvision、Dahua、Hanwha Wisenet、Uniview、Rhombus）；还包括所有内置无人机项（DJI、Remote ID、Skydio、Autel、Parrot、HOVERAir）。隐私模式、通知栏提醒和 TAK / CoT 推送默认关闭。标签颜色按分类设置（§9.5）。'
        ),
        P('4.4 快速入门', "h2"),
        P(
            '主要控件是底部五个标签页和实时页右上角的图标。首次接受许可后会出现导览；点击<b>知道了</b>关闭。随时可在“设置 → <b>显示实时页导览</b>”重新打开。'
        ),
        table(
            ['控件', '用途'],
            [
                ['实时 / 暂停', '显示当前接收到的设备，可用雷达、列表、时间线、混合或按分类视图。已在此页时再次点击标签可<b>暂停</b>画面，Wi-Fi / BLE 和日志仍运行；再点“实时”恢复。从其他标签页点击时只返回此页。'],
                ['筛选', '决定实时页显示哪些设备：预设（仅 BLE、仅已关注等）、分类“仅显示 / 隐藏这些”、指定特征的“仅显示 / 隐藏所选”，以及 RSSI、名称、OUI 条件。特征仍可标注并提醒，不改变日志。'],
                ['特征库', '决定设备如何命名的模式目录。点击编辑，添加书签可在该系列出现时提示音和 / 或语音提醒。隐藏某系列应在“筛选”中操作。'],
                ['报告', '命名观测、轨迹、观测总结、观测导出、对比、AI 导出、候选特征和日志导出；开始与结束观测也在这里。'],
                ['设置', '外观（夜间模式、常亮、隐私模式）、扫描强度、GPS 标记、关注语音、TAK / CoT、日志、特征导入导出、从 GitHub 更新内置特征库、恢复默认值及实时页导览。行布局位于“实时 → 显示”。'],
                ['显示调整（实时页右上角）', '滑块图标，打开覆盖实时页面的<b>显示</b>面板：视图（雷达、强度列表、时间线、混合、按分类）、排序、短暂保留、标题行、副标题行，以及 RSSI 信号条、特征名、频率、首次 / 最近出现等开关。它控制外观、顺序和每行字段。再次点击图标或变暗区域关闭。该控件不在设置页，参见 §5.3。'],
            ],
            [1.7 * inch, 4.8 * inch],
        ),
        Spacer(1, 6),
        callout(
            '筛选隐藏设备，显示隐藏字段',
            '雷达、列表或按分类的切换位于实时页右上角的显示调整图标，不在设置页。筛选决定列表中有<i>谁</i>，“显示”决定列表<i>如何呈现</i>。',
            "note",
        ),
        figure_wrap(
            "fig-display.png",
            '显示面板：点击实时页右上角的显示调整图标打开。',
            '视图、排序、短暂保留、标题行、副标题行和附加字段开关都在这里。再次点击图标或变暗的设备列表可关闭。请依次熟悉下列操作：',
        ),
        numbered([
            '确认页头 Wi-Fi、蓝牙和特征计数正在变化。两种无线计数都为 0 时，通常是系统位置、Wi-Fi 或蓝牙未开启；开启后等待约 30 秒接收首批 Wi-Fi。',
            '实时页默认“按分类”。依次点击分类、特征和设备。每行代表一台设备，圆圈内是分类图标，未匹配显示 ?。AP / LE 分别是 Wi-Fi 接入点 / BLE 广播设备（§1.1），以副标题行开头的小图标表示，不占标题。默认第一行是半粗体 MAC，第二行是图标、名称与类型（SSID / BLE 名称 / Apple · AirTag 等推测）以及随机 / 消失标记。信号条、特征名、频率及首次 / 最近出现默认开启。厂商位于详情页。右侧 RSSI 是此处信号强度，不是距离；-50 比 -90 强。',
            '点击右上角显示调整图标打开<b>显示</b>。先选视图，再选排序、短暂保留、标题行、副标题行和附加字段；满意后点击图标或面板后的暗区关闭。拥挤广场中可把副标题行设为“无”并关闭附加字段，设备数量不变，只减少每行信息。参见 §5.3。',
            '点击一行进入设备详情：自定义名称为大标题，广播名称较小，下面是青色观测备注；还包括“可能是什么设备”、重点关注、特征系列、信号、解码、BLE 可选解码字段（§9.6）、关注此 MAC 的书签、BLE 信号追踪及“从设备创建特征”。随机 / 隐私 BLE MAC 不显示名称与备注编辑。返回键回到实时页。',
            '逐一查看另外四页：筛选（尝试仅 BLE，再恢复全部流量）、特征库（分类 A-Z，点开分类）、报告（观测、轨迹、总结、对比、日志）和设置（夜间 / 隐私 / 常亮外观选项，需要时重开实时页导览）。',
            '房间内并非所有设备都能出现。未开热点、仅连接咖啡馆 Wi-Fi 的手机，仅蜂窝网络摄像头和休眠标签不会出现，这是手机能力限制，不是安装损坏。理解列表后可继续第 12 章。',
        ]),
        P('4.5 最大采集量（代价是耗电）', "h2"),
        P(
            '§4.3 已足够开始观察。本节适合希望在静坐、步行或驾车时尽量提高原生 Android 扫描频率，并接受发热耗电的人。口袋携带或通宵放包中则选择省电模式并参见 §13.2。持续数小时使用时，外接电源比反复调整自适应电池更有效。'
        ),
        P(
            '高性能、屏幕常亮、GPS 标记和日志默认开启。本检查表补充完整授权、防止厂商暂停扫描、观察时保持亮屏，以及驾车时可选的加快 Wi-Fi AP 扫描。它不能突破原生限制，仍无监听模式、Wi-Fi 客户端、经典蓝牙或测向能力，只是减少手机对无线扫描的休眠。'
        ),
        P('4.5.1 系统无线开关', "h3"),
        P(
            '即使 Fieldwatch 内开关已打开，未开启系统位置时 Android 仍不会提供 Wi-Fi BSSID 或有效 BLE 数据。请在手机系统设置中操作。'
        ),
        numbered([
            '<b>位置开启</b>，并选择<b>精确位置</b>，不能只给大致位置。使用高精度 / GPS + Wi-Fi + 移动网络（Samsung：位置 → 定位方式或位置服务）。GPS 标记需要实时定位，否则轨迹距离为 0。',
            '<b>Wi-Fi 开启</b>。接收 AP 信标需要无线硬件工作。',
            '<b>蓝牙开启</b>。这里只接收 BLE，HC-05 / HC-06 等 Classic 设备仍不会出现。',
            '若“位置 / 提高精度 / 位置服务”下有 <b>Wi-Fi 扫描</b>和<b>蓝牙扫描</b>，也请开启。它们允许系统辅助定位，不能代替 Wi-Fi 与蓝牙主开关。',
            '采集时关闭系统<b>省电模式</b>或豁免 Fieldwatch。即使应用设为不受限制，全局省电仍可能限制扫描。',
        ]),
        P('4.5.2 Fieldwatch 请求的权限', "h3"),
        P(
            '首次权限页显示<b>Fieldwatch 需要无线权限</b>，点击“授予权限”。必需项齐全前不会扫描，名称因 Android 版本而异。若曾拒绝，可在“系统设置 → 应用 → Fieldwatch → 权限”补授。精确位置必需，大致位置不足。'
        ),
        table(
            ['授予项目', '用途'],
            [
                ['位置：精确（使用应用时允许）', '用于 Wi-Fi 扫描与 BLE 地址。“Fieldwatch 正在扫描”是前台服务，因此“使用应用时”足够；若系统提供“始终允许”也可选择。应用不请求仅后台位置权限。'],
                ['附近的 Wi-Fi 设备（Android 13+）', '允许执行 Wi-Fi AP 扫描。'],
                ['附近设备 / 蓝牙扫描与连接（Android 12+）', '用于 BLE 观察，读取某些名称需要连接权限；应用不为检测建立蓝牙连接。'],
                ['通知（Android 13+）', '显示常驻“Fieldwatch 正在扫描”状态及可选关注提醒。请允许扫描通知；其“停止”按钮会结束采集。'],
            ],
            [2.4 * inch, 4.1 * inch],
        ),
        Spacer(1, 6),
        P(
            '首次权限页不包含电池豁免；应在设置中使用<b>允许后台使用</b>和<b>不受限制的电池使用</b>（§4.5.3）。振动权限安装时授予；互联网用于默认开启的在线地名与地图，无需账号。'
        ),
        P('4.5.3 避免厂商暂停扫描', "h3"),
        P(
            '锁屏或被判断为闲置时，厂商电池管理可能冻结 BLE。不同手机名称不同，首次启动后完成下列设置，并保留扫描通知。'
        ),
        numbered([
            'Fieldwatch：“设置 → <b>允许后台使用</b>”打开系统电池页，开启相应开关；再选“<b>不受限制的电池使用</b>”。Pixel / 原生系统通常直接列出不受限制、优化、受限制；选择前者。部分 Samsung 等手机只显示允许后台使用，需要点击文字行而非开关，继续进入<b>不受限制</b>。返回应用后，各开关会反映系统授权。',
            '“系统设置 → 应用 → Fieldwatch → 电池（或应用电池用量）”，选择<b>不受限制</b>。若首页没有此项，点击“允许后台使用”文字行进入。',
            'Samsung：“系统设置 → 电池 → <b>后台使用限制</b>”（或让未使用应用休眠）。不要让 Fieldwatch 休眠；若在休眠列表中，移除它，也可加入“从不休眠的应用”。',
            '保留最近任务中的 Fieldwatch。划掉任务或点击扫描通知的“停止”会结束服务；按 Home 则保持扫描。',
            '保留 <b>Fieldwatch 正在扫描</b>通知，以便界面不在前台时无线扫描仍运行。',
        ]),
        callout(
            '观察时保持屏幕常亮',
            '“设置 → 保持屏幕常亮”默认开启。查看实时页或信号追踪时应保留，避免 Samsung 熄屏暂停 BLE。若放入口袋、只需通知后台扫描且不要求低延迟，可关闭。不受限制的后台使用是另一项设置，不负责亮屏，也不会放宽扫描配额。',
            "note",
        ),
        P('4.5.4 本次观测的应用设置', "h3"),
        numbered([
            '<b>扫描强度：高性能</b>（默认）。BLE 低延迟，约每 70 秒重启；Wi-Fi 约每 30 秒，启用加快扫描后更快。均衡和省电是折中方案。参见 §10.3。',
            '<b>加快 Wi-Fi AP 扫描</b>（可选，初始关闭）：适合驾车捕捉已知特征 AP。① 设置 → 关于手机，连续点击版本号开启开发者选项；② 开发者选项 → <b>Wi-Fi 扫描限频 → 关闭</b>；③ Fieldwatch 设置中开启加快 Wi-Fi AP 扫描。AP 批次由约 30 秒缩至约 8 秒，更耗电且更热。系统仍限频时应用不会启用此开关。行程结束后可关闭。参见 §7.1.1、§10.3.1。',
            '<b>保持屏幕常亮：</b>查看实时页 / 信号追踪时开启。',
            '<b>为检测结果添加 GPS 标记：</b>需要随行判断、总结距离或日志经纬度时开启，并使用高精度定位；获得实时定位前轨迹为 0。',
            '<b>写入磁盘 / 日志：</b>需要日志导出、候选特征或超过 15 分钟总结窗口的记录时开启；只有设备极密集、界面明显延迟时才考虑关闭。',
            '<b>过期时间：</b>繁忙列表用默认 45 秒即可；广播慢的标签可设 90-120 秒，避免两次广播间闪为消失。',
        ]),
        P('4.5.5 确认扫描确实运行', "h3"),
        numbered([
            '通知栏应有 <b>Fieldwatch 正在扫描</b>及 Wi-Fi / BLE / 特征计数。通知消失代表服务未运行，请重新打开应用。',
            '实时页两种无线计数不应一直为 0。若如此，检查系统位置、Wi-Fi、蓝牙（§4.5.1），等待首批 Wi-Fi 约 30 秒；加快扫描生效时约 8 秒。',
            '观察时页头不应持续显示 <b>BLE 已暂停 · 正在重启</b>。若出现，开启常亮和不受限制后台，禁止应用休眠。参见 §13.2。',
            '启用加快扫描后，“Wi-Fi N 秒后扫描”的倒计时应较短。若显示<b>加快 Wi-Fi 扫描需要开发者选项</b>，说明系统重新开启了限频，修正后返回设置。',
            '持续使用会因无线扫描和亮屏而发热，并非一定发生故障。长时间观测请接电源或移动电源。',
        ]),
        callout(
            '这些设置无法解决的问题',
            '静默或仅蜂窝网络摄像头、未开热点的联网手机、休眠标签，以及随机 BLE 地址离开范围，仍会漏检。完整权限和电池豁免不会把手机变成监听模式无线设备，列表为空也不代表安全。参见第 3 章及须知。',
            "warn",
        ),
    ]

    # 5 Navigation
    flow += [
        PageBreak(),
        P('5. 应用导航与界面', "h1"),
        P(
            '本章说明各页面，尚未启动应用请先读 §4.4。底部第一项为<b>实时</b>，本手册称<b>实时页面</b>，以区别实时 GPS 或录制。行内圆圈为分类图标，无线类型是 Wi-Fi 接入点与 BLE 广播设备（§1.1），在副标题行显示小图标。RSSI 是本手机处的 dBm 强度，越接近 0 越强；127 表示蓝牙“测量不可用”，不是发射功率。筛选改变设备集合，显示（§5.3）改变行布局。暂停只冻结画面，扫描和日志继续，新筛选在恢复实时画面后显示。'
        ),
        P('5.1 主界面', "h2"),
        figure_wrap(
            "fig-live.png",
            '图 1：实时页面（混合视图）。',
            '一个主屏、五个标签页，以及叠加的设备详情页。底部为实时、筛选、特征库、报告、设置。特征库定义模式，报告包含轨迹、观测总结、对比、观测导出、AI 导出和日志导出。顶部 FIELDWATCH 后显示 Wi-Fi 接入点、BLE 广播设备、当前特征命中三个计数，可能附“Wi-Fi 27 秒后扫描”“等待系统”“BLE 周期重启 / 已暂停”等提示。扫描通知也显示这三个计数。导出功能集中在报告页。本手册原截图使用隐私模式，MAC 尾部为 **:**:**，另有说明除外。',
        ),
        figure_wrap(
            "fig-signatures.png",
            '图 2：特征库。',
            '特征库标题显示已载入的内置与自定义特征总数。每行有分类图标，具有解码字段映射时显示六边形（§9.6），书签表示关注。支持名称 A-Z 或分类 A-Z，分类初始折叠。点击编辑，“+”新增空白特征。没有匹配总开关，要隐藏某系列请在筛选页操作。详见第 9 章。',
        ),
        P('5.2 底部导航', "h2"),
        table(
            ['标签页', '功能'],
            [
                ['实时', '显示雷达、列表、时间线、混合或按分类视图；右上角打开显示面板。再次点击可暂停，扫描和日志继续；点击实时恢复。双击 FIELDWATCH 跳到顶部。观测进行中标题显示 FIELDWATCH · 观测，开始与结束在报告页。'],
                ['筛选', '决定显示哪些设备，顺序为预设、无线类型、随行、仅新检测、仅特征匹配、仅已关注、仅命名设备、隐藏 Fast Pair 账号密钥、分类仅显示 / 隐藏、所选特征仅显示 / 隐藏，以及 RSSI / 名称 / OUI。特征仍标注并可提醒。参见第 8 章及图 15-17。'],
                ['特征库', '模式目录；标题显示内置和自定义特征数。每行有分类图标，具解码映射时有六边形（§9.6）。可按名称或分类 A-Z，分类初始折叠。点击编辑规则、颜色及 BLE 解码字段；书签表示关注，触发提示音和 / 或分类语音。隐藏在筛选页操作，“+”新增空白特征。参见图 2、§9.6。'],
                ['报告', '观测（可选命名窗口）、轨迹、观测总结（文本 / PDF）、观测导出、观测对比、AI 导出、候选特征、日志导出（格式及无线类型）、重置 / 清空日志。选中观测决定轨迹、总结、观测导出和对比的本次一侧。候选特征分析滚动日志；GPS、地名和日志总开关仍在设置页。'],
                ['设置', '外观（夜间、常亮、隐私）、扫描强度、GPS、TAK / CoT（默认关闭）、地名、日志、提示音 / 语音 / 可选通知提醒、测试提醒、命名设备、电池豁免、特征导入导出、GitHub 更新、设置备份、恢复默认值及导览。行布局在“实时 → 显示”，TAK 见 §5.8。'],
            ],
            [1.2 * inch, 5.3 * inch],
        ),
        Spacer(1, 6),
        table(
            ['需求', '位置'],
            [
                ['减少实时页的设备数', '筛选（第 8 章）'],
                ['切换雷达 / 列表 / 按分类', '实时页右上角显示调整（§4.4、§5.3）'],
                ['减少每行文字', '实时 → 显示调整 → 显示（§5.3）'],
                ['不显示某个系列', '筛选 → 隐藏这些（分类）或隐藏所选（单个系列）'],
                ['遮蔽屏幕上的 MAC 尾部', '设置 → 隐私模式'],
                ['在 ATAK 地图显示设备', '设置 → TAK / CoT 推送（§5.8、§12.15）'],
            ],
            [2.4 * inch, 4.1 * inch],
        ),
        Spacer(1, 6),
        P('5.3 显示面板（实时页面）', "h2"),
        P(
            '实时条目内容可按任务调整，适合拥挤广场、观测、信号追踪或抄录 MAC。视图、排序和行字段统一位于实时页右上角<b>显示调整</b>图标。点击后在列表上方打开<b>显示</b>面板，后方设备变暗；点暗区或再次点图标关闭。选择会保存，直到再次修改；此项不在设置页。'
        ),
        figure_wrap(
            "fig-display.png",
            '图 3：显示面板，通过实时页右上角图标打开。',
            '第一个下拉框选择雷达、强度列表、时间线、混合或按分类；之后是排序、短暂保留、标题行、副标题行，其余使用开关。雷达标签保持简短的特征名或类型推测，不采用标题行 / 副标题行设置。',
        ),
        callout(
            '筛选隐藏设备，显示隐藏字段',
            '筛选（§8）决定<i>谁</i>出现，显示决定<i>每行如何呈现</i>。副标题行设为“无”仅隐藏第二行，不移除设备。厂商、载荷和完整解码仍在详情页，日志不变。同一次观测中不同操作者可使用不同布局。',
            "note",
        ),
        P('身份字段：每行显示什么', "h3"),
        bullets([
            '<b>标题行：</b>列表、混合及时间线的第一行，MAC 也使用粗体。默认<b>MAC 地址</b>便于抄录或按 BSSID 追踪，无需第二行。<b>广播名称</b>显示 SSID / BLE 本地名，无名称时显示“&lt;隐藏&gt; / 未命名 LE”，不加类型推测。<b>名称 + 类型</b>优先用广播名，否则使用详情页相同推测，如 Apple, Inc. · AirTag 或 Find My 配件，其中 Apple, Inc. 是类型推测；IEEE 厂商仅在详情。标题行不能设为“无”，无线类型图标位于副标题行。',
            '<b>副标题行：</b>较小的等宽第二行，开头为 Wi-Fi（接入点）或蓝牙（BLE）图标，然后显示广播名、默认<b>名称 + 类型</b>或 MAC，以及随机 / 消失状态。选<b>无</b>隐藏第二行，状态移至标题行，类型图标不移，以便行高缩小且名称可读。“名称 + 类型”或“广播名称”中，无名 BLE 只写“未命名”，蓝牙图标已表明 LE。IEEE 主板 / 芯片厂商始终位于详情，不在列表。',
        ]),
        P('视图与保留时间', "h3"),
        bullets([
            '<b>视图：</b>经典雷达、强度列表、时间线、混合 + 迷你曲线、按分类（默认）。设备集合相同，只改变画面。排序影响列表 / 混合 / 时间线及按分类中特征下的设备；雷达仍以 RSSI 半径摆放。参见第 6 章。',
            '<b>短暂保留：</b>关闭（只按过期时间）或最后一个包后保留 10 / 30 / 60 秒。行保留最近 RSSI、排名和雷达环位置，数值不衰减；新包更新它们。实际屏幕保留时间取过期时间和短暂保留的较大值。“筛选 → 仅新检测”也将它用作最后一个包后的最短停留时间。',
        ]),
        P('排序：列表顺序', "h3"),
        P(
            '“显示 → 排序”控制强度列表、混合、时间线及按分类中的设备顺序，不隐藏设备，也不改变日志或观测总结。默认<b>最强信号（30 秒均值）</b>，共有八个选项：'
        ),
        table(
            ['排序', '效果', '适用情形'],
            [
                ['最强信号', '最近一个包最强的排顶部，右侧数值是瞬时 RSSI。', '即时排查、选择信号追踪目标，或在广场发现突然变强而均值尚未反映的标签。'],
                ['最强信号（30 秒均值）', '按最近 30 秒 RSSI 样本均值排序，无样本时用最后一个包。RSSI 下显示“均值 N”，雷达环也使用均值。此项为默认。', '静止观察每次扫描波动的 Wi-Fi，或走向某标签时减少排名跳动。'],
                ['最近接收', '最后收到包的时间越近越靠前，再按强度。', '查看谁刚广播；持续广播的固定设备仍靠前。'],
                ['最近提醒', '按最近关注提醒（声音 / 语音 / 闪烁）时间排序，再按最近接收。本会话未提醒的设备靠后，同设备再次提醒会回到顶部；列表中保留荧光铃铛。', '关注观测：先看刚提醒的设备，再看上一个。'],
                ['最新出现', '按本会话首次出现时间从新到旧，再按最近接收。已停留一小时的设备即使很强也靠后。', '找最新到达的设备，而不是当前最强设备。'],
                ['新设备在底部', '首次出现最早的排顶部，新行追加，消失行移除；未手动向上滚动时列表跟随底部。', '像日志一样阅读静坐或驾车观测；只有此排序自动跟随列表末尾。'],
                ['名称 A-Z', '按标题行文字字母顺序，再按 MAC。标题行默认为 MAC，因此未改标题行时相当于按 MAC 排序。', '查找已知 SSID、复制地址、对照两份列表。'],
                ['特征优先', '有特征匹配的排在未匹配前，再按强度（沿用上次最强信号的瞬时 / 均值规则）。', '突出特征命中，同时保留未匹配设备；无需开启“仅特征匹配”。'],
            ],
            [1.45 * inch, 2.4 * inch, 2.65 * inch],
        ),
        Spacer(1, 4),
        P(
            '选择瞬时或 30 秒均值最强排序，会恢复强度顺序。其余六项仅在需要时将上次强度规则用于次序比较，例如最近接收、特征优先。最近提醒按关注闪烁时间排序，不按 RSSI。排序不等于筛选：弱的已命名标签仍在，只是不一定靠前，除非选择特征优先、最新出现或最近提醒。',
            "body_left",
        ),
        P('附加信息：按任务开启', "h3"),
        bullets([
            '<b>RSSI 信号条：</b>默认开启，填充条表示最近接收强度，与右侧瞬时值一致，不采用 30 秒均值。',
            '<b>特征名称：</b>默认开启，独立于信号条。列表、混合和时间线最多显示三个匹配标签；雷达只用首个匹配作点标签；详情列出全部。关闭仅隐藏标签，匹配仍进行。',
            "<b>频率：</b>默认开启，信道与 MHz 位于右侧 RSSI 下，避免被长名称挤掉，例如 <font face='FWText'>ch6 · 2437MHz</font>。BLE 广播通常没有频率。",
            '<b>首次 / 最近出现：</b>默认开启，显示本会话首次及最近包距现在的时间，每秒更新。',
        ]),
        P(
            '<b>默认行：</b>按分类、30 秒均值最强、标题行 MAC、副标题行名称 + 类型、信号条 / 特征 / 频率 / 首次最近开启、短暂保留 10 秒。圆圈为分类（未匹配 ?），第一行 MAC，第二行类型图标、名称或推测与随机 / 消失；右侧实时 RSSI、趋势及均值，下方可有信号条和标签。新关注命中提醒时行闪烁一秒，此后荧光绿铃铛在本会话一直保留。',
            "body_left",
        ),
        P('按任务调整列表行', "h3"),
        table(
            ['任务', '常用显示配置'],
            [
                ['熟悉周边环境', '保留默认 MAC / 名称 + 类型、信号条与特征名；强度列表，30 秒均值最强排序。'],
                ['广场 / 列表过密', '副标题行“无”，关闭信号条、频率与首次 / 最近；使用强度列表。所有筛选后的设备仍在，只显示 MAC，无线图标随副标题行隐藏。'],
                ['抄录 MAC / BSSID', '默认标题行已是 MAC；副标题行设为“无”可容纳更多行。先暂停，再阅读或长按。'],
                ['Wi-Fi 信道观测', '开启频率，标题行保留 MAC，按强度排序；需要快速看强弱时开启信号条。'],
                ['追踪一台 BLE', '混合 + 迷你曲线，标题行 MAC，开启首次 / 最近，关闭 BLE 通常没有的频率，再从详情打开信号追踪。'],
                ['观测设备何时来去', '时间线，按最新出现或新设备在底部排序，开启首次 / 最近；需抄地址时保留 MAC 标题行。'],
                ['仅特征匹配、简洁列表', '开启特征名，副标题行“无”（仅 MAC）；同时使用“筛选 → 仅特征匹配”（第 8 章）。'],
            ],
            [1.9 * inch, 4.6 * inch],
        ),
        Spacer(1, 6),
        P(
            '这些显示控件不会在设置页重复出现。仅新检测是筛选，其“标记已见 / 重置已见”按钮位于标签栏上方（§5.3.2）。停留顶部时新强设备会把列表往下推；已滚离顶部则不会强制跳动。双击 FIELDWATCH 标题 / 计数行可约 140 毫秒线性滚到顶部。'
        ),
        P('5.3.1 暂停实时画面', "h3"),
        P(
            '已在实时页时，底部按钮是切换状态。列表运行时显示<b>暂停</b>，点击后固定行、RSSI 和标签，标题显示 FIELDWATCH · 已暂停。Wi-Fi、BLE 和日志仍继续；按钮变为<b>实时</b>（播放），再次点击恢复。从其他标签页点击只返回实时页，不自动解除暂停，需在此页再点一次。'
        ),
        P(
            '暂停期间筛选和设置仍可更新；分类按钮、仅显示 / 隐藏及恢复默认值仍生效，但冻结画面直到恢复才改变，暂停提示会说明。列表移动过快时可先暂停再点设备，详情显示被冻结的那次观察，即使设备已在实时集合过期。仅新检测开启时，标签栏上的“标记已见 / 重置已见”仍可用；标记已见只吸收冻结列表，不包含冻结后到达的设备。'
        ),
        P('5.3.2 实时页面中的新检测', "h3"),
        P(
            '开关位于“筛选 → 仅新检测”。开启后实时页显示两个额外控件，它们不在显示面板或筛选标签页内。'
        ),
        bullets([
            '<b>仅新检测：</b>显示面板下方的一行提示，暂停时位于暂停条下，显示“仅新检测”“已隐藏 N 个”或“正在学习静止 Wi-Fi”。',
            '<b>标记已见 / 重置已见：</b>始终可见于底部标签栏上方，无需滚动列表；关闭筛选后隐藏。',
        ]),
        P(
            '首次开启时，Fieldwatch 将当前设备及下一批扫描中的静止 Wi-Fi 记为已见。已见集合仅在这次快照或“标记已见”时增长；后者加入当前实时画面，暂停时只加入冻结列表。“重置已见”将集合清零，让这些设备重新算作新设备；清空日志不会重置它。随机 BLE 地址仍可能看起来是新的。新设备接收期间保持显示，最后一包后至少保留“显示 → 短暂保留”的时长。'
        ),
        P('5.3.3 实时页面中的随行判断', "h3"),
        P(
            '开关在筛选页“显示的无线设备”下，其后是仅新检测，再下方为仅特征匹配、仅已关注、仅命名设备和分类。开启随行会启动跟随判断，并清除上述三个“仅”开关及分类“仅显示”，避免列表被筛空；用于隐藏自有标签的“隐藏这些”保留。顶部“随行”预设以相同方式替换整套筛选。实时页显示“随行 · 轨迹 N 米”，标签栏上方有<b>重新开始</b>，与仅新检测按钮共用一栏。重新开始清除操作者和各设备 GPS 轨迹，不清空实时列表或日志；距离回到 0，重新移动约 50 米观察谁回来。包中标签应重现，住宅 AP 不应出现。关闭筛选不清轨迹；开启后仍可额外选择只显示随行的定位标签。'
        ),
        P(
            '判断不是固定半径。每次接收都记录本手机 GPS，“仍在附近”的容许范围会随移动速度增大：步行约一栋房屋长度；车内标签不会因几秒跨越数百米而被立即移除。Wi-Fi 的广播保留策略会考虑系统 AP 批次比 BLE 慢；当前随行筛选排除 Wi-Fi AP，避免经过固定 AP 造成假象。完整条件、速度表及门口住宅 AP 为何不符合见 §8.5。'
        ),
        P(
            '实时页只是当前画面，不是录像。“报告 → 观测总结”（文本 / PDF）仍从内存中设备（约 400 上限，§11.4.1）分析最近 15 分钟的疑似随行追踪器 / 尾随，排除仅路过的设备。无论使用哪种视图、是否开启随行或其他筛选，都适用。必须此前已开启 GPS 标记并实际移动，否则报告说明未进行随行测试。参见 §11.4、§12.2。',
            "body_left",
        ),
        P('5.4 状态指示', "h2"),
        bullets([
            '圆圈内<b>分类图标</b>：首个匹配特征的分类，如定位标签、手机 / 电脑、音频等；未匹配为问号。筛选分类按钮和按分类标题使用相同图标。',
            '副标题行开头的<b>无线类型</b>图标：Wi-Fi 接入点或 BLE 广播设备。AP 表示广播网络、热点或软 AP，不是 Wi-Fi 客户端。详情会写明名称；副标题行设为“无”后该图标也隐藏。',
            '<b>彩色标签：</b>开启特征名称时显示匹配名称。列表、混合和时间线最多三个，雷达仅首个，更多匹配在详情中查看。',
            '<b>解码六边形：</b>仅出现在具有解码字段映射（§9.6）的那个特征标签内，颜色与标签相同。多特征设备只标有映射的名称。它表示有映射，不是解析值。“!”是独立重点关注标签；青色备注标签表示观测备注，荧光铃表示本会话已提醒。关闭特征名称会隐藏名称和六边形，但“!”、备注、铃铛及实时值标签仍显示。',
            '<b>实时值：</b>以特征颜色显示单个解码词，如分离、靠近主人、空中、紧急。解码字段启用<b>实时条目</b>且当前广播解析出该值时出现；设为<b>突出</b>的值使用更醒目的标签。强度列表、混合、时间线和按分类支持，雷达不显示。参见 §5.4.1。',
            '<b>&gt;&gt; &gt; = &lt; &lt;&lt;</b>：近期 RSSI 趋势，依次为明显增强、增强、稳定、减弱、明显减弱；增强绿色，减弱红色。样本不足时留空。',
            '<b>仅新检测 · 已隐藏 N 个：</b>仅新检测开启时的实时提示；标记已见 / 重置已见位于标签栏上方。',
            '<b>随行 · 轨迹 N 米：</b>随行开启时的提示；上方的重新开始清除 GPS 轨迹。',
            '<b>新 N 秒：</b>仅新检测开启时，表示首次出现距今时间。',
            '<b>随机：</b>地址的本地管理 / 随机标志位已设置。',
            '<b>消失</b>或暗色雷达点：最后一个包超过过期时间（默认 45 秒）与短暂保留中的较大值。保留的 Wi-Fi AP 和 BLE 周期重启不算消失。',
            '<b>首次 / 最近：</b>可选行，表示本会话首次和最后收到包距今时间；刚收到时最近显示“现在”。',
            '<b>chN · MHz：</b>开启频率时位于 RSSI 下；BLE 通常无此信息。',
            '<b>扫描通知：</b>“Wi-Fi N 个 · BLE N 个 · 特征 N 个”，约每 2.5 秒更新。Home 保持扫描；从最近任务划掉 Fieldwatch 或点击通知的停止会结束服务，避免后台继续提醒。',
            '<b>关注提醒：</b>使用媒体音量播放提示音和 / 或语音，并闪行、可选跳转。两种声音独立设置；语音可播分类、特征名或两者，不用于信号追踪。关注设备初次出现或消失后返回时提醒一次。闪烁一秒后，列表 / 混合 / 时间线 / 按分类中的荧光铃保持到会话结束，它不是“!”。最近提醒排序使用同一事件。按分类会展开相应分类与特征，使行能闪烁，跳转尽量保留标题。雷达会以扩散圆环和亮心提示，纯语音也有效，之后保留置顶荧光环。测试提醒按当前设置播放；系统通知卡片默认关闭。',
        ]),
        P('5.4.1 列表中的解码值', "h3"),
        P(
            '部分特征在名称旁直接显示一个解码词，无需打开详情。六边形仍只表示有映射，附加标签才是具体值；值随广播内容变化，不随每次 RSSI 更新。它仍是模式判断，不是身份或事实认定。'
        ),
        P(
            '<b>支持协议的标签：</b>DULT（FCB2 服务数据）及 Google Find Hub（FEAA 40 / 41 帧）在行中显示模式。<b>分离</b>更醒目，<b>靠近主人</b>和<b>附近</b>较低调。AirTag、SmartTag 和 Tile 没有该位，仍只显示名称。Chipolo、Pebblebee 可同时显示自身名称和 DULT / Find Hub 解码模式。'
        ),
        P(
            '分离标签可能约一天保持相同 MAC，因此值得快速关注。持续与您随行的分离标签需要解释；整个观测都在的靠近主人标签常是自有设备，途中才出现的常是带着自己钥匙加入的人。仅路过的分离标签不代表尾随。详情显示该值的特征库说明，观测总结和对比也引用相同句子；两次观测间模式变化会明确说明，例如分离变为靠近主人。'
        ),
        P(
            '<b>无人机：</b>当前保留的 Remote ID 广播是 Location 消息时，列表显示未声明、地面、空中、紧急或 RID 故障，<b>紧急</b>更醒目。地面 / 空中是飞行器当前广播状态。后续 Basic ID 或 System 包会清除标签，下一条 Location 再出现。BLE 消息包内部的 Location 不触发实时标签；Wi-Fi 消息包会拆分，因此可显示。详情仍显示当前有效的纬度、航向、速度和 UAS ID。TAK 标记不依赖此标签。'
        ),
        P(
            '<b>使用方式：</b>采用强度列表、混合、时间线或按分类。要同时看系列名就开启特征名称；关闭时实时值仍显示。“筛选 → 仅显示 → 定位标签 / 无人机”可缩小范围。要保留广播轨迹，应在飞行前开始观测；观测总结和对比会在“所在位置”后增加<b>飞行器</b>部分，报告轨迹也显示相同路径。距离您的行走轨迹 2 km 内，以白色点线叠加；最新位置用分类图标，点击查看设备。与其他提醒重合时计数列出全部。更远且有 UAS ID 的飞行器各有独立地图，最多三张；飞手为人形图标。旧版观测只有最后位置，最近 15 分钟只标当前位置不存轨迹。参见 §5.6.1、§11.4、§12.6、§12.16。'
        ),
        P('5.5 设备详情', "h2"),
        figure_wrap(
            "fig-detail.png",
            '图 4：设备详情。自定义名称为标题，广播名称较小，青色观测备注位于名称下方；隐私模式遮蔽 MAC 尾部。',
            '点击列表行或雷达点进入详情。利用本地打包的 IEEE 和 Bluetooth SIG 表离线解析，无需联网。术语会转换为易懂描述，如 BR/EDR 不支持表示仅 BLE、无经典蓝牙。RSSI 使用很强 / 强 / 中 / 弱 / 很弱短标签，避免数值变化导致布局跳动。127 表示蓝牙测量不可用，不是发射功率，在当前强度、会话范围、曲线、信号追踪和分享中忽略。消失设备的当前强度为不可用，最近接收仍显示最后有效 dBm。',
            "<b>可能是什么设备：</b>顶部给出谨慎推测。特征库系列优先于通用 SSID 规则，例如 <font face='FWText'>DIRECT-rR-Raven-*</font> 为 Raven / ShotSpotter 传感器，而非泛称 Wi-Fi Direct 手机或电视。其次参考 GAP Appearance、设备类别、服务 UUID、Apple / Google 厂商字节及 Fast Pair 型号 ID。描述使用最可能 / 可能 / 或许等措辞，依据广播而非目视。未匹配设备也会据这些字段推测，或低置信度称 Wi-Fi 接入点 / BLE 广播设备。",
        ),
        P(
            '<b>说明：</b>位于重点关注下方，没有重点关注则在推测卡下。显示各匹配特征编辑器中的说明，即产品用途与背景，不是匹配方法；公司 ID、UUID 和通配符仍在身份 / 厂商数据。它不同于琥珀重点关注卡或实时“!”。多特征分别列出，无说明则不显示。文本分享与 AI 导出包含此内容。',
        ),
        P(
            '<b>重点关注：</b>只有<i>已匹配</i>特征的独立重点关注字段有文字时才显示琥珀卡。内置覆盖业余 BLE 串口、Axon、WatchGuard Video、Digital Ally、Reveal Media、Wolfcom、Ray-Ban / Meta、Snap、Brilliant Frame、Even G1、Fieldy、Plaud Note、Limitless、Bee、Omi、Friend、Hak5 Pineapple、Flipper Zero、Pwnagotchi、Marauder / Deauther、GhostESP、Bruce、Porkchop、Cradlepoint、AirLink、Compex、Novatel Wireless、Utility Inc、Panasonic i-PRO / Arbitrator，以及路边 / 公共摄像头与 ALPR：Flock、Penguin、Pigvision、FS Ext Battery、Genetec AutoVu、Rekor、Motorola Vigilant、Verkada、Avigilon、Axis、Hikvision、Dahua、Hanwha Wisenet、Uniview、Rhombus、Hayden AI、Miovision、Tattile、LVT LiveView。这些通常默认关注；许多仅按名称匹配，仅蜂窝设备仍静默。实时“!”提示打开详情阅读。它不是身份、盗刷器检测或安全结论；任意特征都可自行填写重点关注。'
        ),
        P(
            '<b>特征系列：</b>位于“从设备创建特征”之前，针对<b>本设备</b>执行与“报告 → 候选特征”（§5.6.4）相同的分析。选取最佳独特广播标识：名称通配符、厂商 IE、服务 UUID、厂商数据前缀或稳定 OUI，统计日志和当前广播中共享它的不同 MAC 数，不按包数。跳过没有其他 ID 的随机地址、住宅名称、芯片模块 OUI、协议 IE、通用 UUID，以及 Apple 0x004C、Google、Samsung、Microsoft 等操作系统级公司 ID；这些大量出现不代表产品系列。仍是模式推断。'
        ),
        bullets([
            '<b>明确系列：</b>约八台以上不同设备共享同一 ID，荧光卡并突出计数。候选是系列模式，而非此 MAC。',
            '<b>可能的系列：</b>两至七台，琥珀色；样本少，但可构成系列。',
            '<b>仅此设备：</b>没有其他 MAC 共享独特 ID，或没有可聚类的唯一信息。从这里创建特征通常主要标记本地址。',
            '<b>已标注：</b>已匹配特征库，卡片列出名称；仍可添加第二个特征，一台设备可有多个标签（§7.4）。',
        ]),
        P(
            '常见双标签是<b>协议 + 场所</b>。内置 iBeacon 是 Apple 0x004C、类型 0x02/0x15，任何厂商可发送，不代表商店。店内数百个 iBeacon 常共享一个 proximity UUID，用于导航、购物篮或资产。按 UUID 创建自定义特征后，同一设备同时显示 iBeacon 和商店标签，实时最多三个，详情全部列出。内置 <b>Target Atrius basket</b> 就是 UUID 5993A94C-… 与服务 0xB1BB 的此类模式；即使在商场静音通用 iBeacon，Target UUID 仍可标记购物篮。Minew / Estimote / Kontakt.io 也可双标签。只有已识别为<i>非信标</i>产品，如 Sony TV、Tesla 手机钥匙时，Fieldwatch 才移除 iBeacon 标签。'
        ),
        P(
            '该卡只给出判断。<b>从设备创建特征</b>仍按本设备起草并包含 MAC 固定规则（§9.2），已标注也可使用。未匹配设备若属明确 / 可能系列，可在“报告 → 候选特征”创建<b>共享</b>规则且不固定 MAC（§9.2.1）。候选列表跳过已标注设备，因此满屋 iBeacon 不会出现；需从详情创建并将厂商前缀收紧到 UUID。日志关闭时实时计数仍有效，读取滚动日志后才补充日志计数。'
        ),
        bullets([
            '<b>身份：</b>广播名称、MAC、公共出厂 / 随机隐私地址类型。通用地址按 IEEE OUI、MA-M、MA-S 查厂商，随机 BLE 跳过 OUI。厂商数据中的蓝牙公司 ID 使用 SIG 表（约 4,012 项）命名。',
            '<b>信号：</b>RSSI、本会话最小 / 最大值、声明的发射功率、信道 / MHz，以及系统提供时的 Wi-Fi 标准和信道宽度。',
            '<b>BLE：</b>PHY（1M / 2M / Coded）、可连接性、广播间隔、标志位、GAP Appearance、设备类别（主类 / 子类 / 服务类）、16 位服务 UUID 名称、服务数据和厂商载荷。只要该设备曾广播可连接，就保持“是”；同 MAC 的不可连接扫描响应不会再反复改变该行。',
            '<b>已知载荷：</b>iBeacon（UUID / major / minor / 校准 TX）；Google Fast Pair（配对模式 24 位型号 ID 及本地名称表，或账号密钥广播）；Apple Continuity（AirPods / Beats 型号、电池、入耳 / 入盒，Find My / Offline Finding、Nearby Info 活动、Nearby Action、AirDrop、Handoff、Hey Siri、AirPlay、Instant Hotspot）。Eddystone UID / URL / TLM / EID（0xFEAA）会<b>累积</b>保留各类帧，在原始行标注类型，不互相覆盖。有数据时也显示 Microsoft Swift Pair / Nearby Sharing。未知 0xFF 数据仍以公司名 + 十六进制显示，专有载荷没有统一官方数据库。',
            '<b>解码字段：</b>特征库映射读取<i>当前</i> BLE 厂商 / 服务数据（§9.6），显示温度、型号、Remote ID 位置等。Remote ID 在 BLE FFFA 与封装为 FFFA 的 Wi-Fi FA:0B:BC 上使用同一映射，含 UAS ID、位置经纬度 / 航向 / 速度及操作者。标题有相同六边形。加密或过短载荷保留十六进制，有映射但不适用时提示，例如 Govee 灯常只发名称。匹配列表也在有映射的名称旁加六边形。实时值及其特征库说明显示在此（§5.4.1）。Apple / Fast Pair / Eddystone / Microsoft 留在已知载荷与厂商数据。文本分享、AI 导出及总结中的值得关注 BLE 使用相同内容。',
            '<b>Wi-Fi AP：</b>SSID（或隐藏）、从信息元素读取并用易懂语言说明的 RSN/WPA/AKM/加密算法、支持速率、能力串，以及按 IEEE OUI/CID 查询的厂商 IE（OUI + 类型 + 载荷）。',
            '<b>会话：</b>首次 / 最近出现、接收次数、可选 GPS（接收时本手机位置）、<b>全部</b>匹配特征（不限三个）、原始广播字节、RSSI 曲线和 15 分钟出现区间。顶部书签关注此设备；BLE 可信号追踪；下方是特征系列卡和从设备创建特征。',
        ]),
        P(
            '身份、信号、蓝牙广播、服务（含 Eddystone）、厂商数据、会话和特征系列等区块会保留该设备曾达到的最大高度，避免短帧或短推测导致追踪 / 分享按钮上下跳动。'
        ),
        P(
            '从暂停列表进入详情会使用冻结快照，即使设备已经过期；创建特征也根据该快照起草。'
        ),
        P(
            '<b>自定义名称：</b>点击名称行编辑图标。保存后作为大标题，SSID / BLE 广播名在下方较小显示。它只标记<b>此 MAC</b>，保存到“设置 → 命名设备”，默认不开提醒，添加书签才开启。名称用于实时页和报告，“仅命名设备”保留这些行；“仅已关注”还要求该设备提醒开启或匹配已关注特征。BLE 地址为随机 / 隐私（IEEE 本地位或 Android Random）时隐藏编辑，因为名称不能跟随地址轮换。Wi-Fi 即使是本地管理的车载 / Mesh / 访客 BSSID 也提供编辑，通常稳定。已存名称仍显示，右上书签仍可关注随机 MAC，并提示轮换限制。',
            "body_left",
        ),
        P(
            '<b>观测备注：</b>名称下的青色区块，与金色重点关注和特征库说明不同。最多 280 字符，与名称绑定同一 MAC，可在详情或“设置 → 命名设备”编辑。观测总结、对比和 AI 导出列出听到的设备与备注；轨迹仅在该设备被关注时列备注。实时条目显示青色备注标签，靠近“!”。仅存备注也会建立命名设备行，使用建议名称、提醒关闭；BLE 隐藏编辑规则相同。设置备份包含备注。',
            "body_left",
        ),
        P(
            '<b>右上书签</b>只关注<b>此无线设备</b>（类型 + MAC），不是特征系列。空心为未关注，实心为已关注；点击时以广播名称或类型推测预填名称。保存名作为大标题，广播名在下。可在命名设备中改名、备注、开关提醒或删除。离开实时范围或过期不会删除关注；消失期间不提醒，相同 MAC 返回才再次提醒，持续停留不会重复。随机 BLE 换地址后关注仍留在旧键，不自动跟随；需手动移除或清空。随机地址仍可添加书签，因为无法判断是静态随机还是会轮换。特征库书签则关注任意匹配该系列的设备，不列在命名设备中。详见 §10.1。',
            "body_left",
        ),
        figure_wrap(
            "fig-hunt.png",
            '图 5：信号追踪。',
            '<b>信号追踪</b>仅用于 BLE，从详情打开全屏页面。显示大号 RSSI 及非常近、靠近、远离、基本不变、静默或消失。非常近约为 -45 dBm 或更强；127 为不可用，忽略不计。靠近 / 远离依据几秒平滑样本约 3 dB 的变化。“您”周围圆环随靠近收缩、远离扩张，旁有本次最强值和专用曲线。提示位置固定，避免数值跳动。底部重置 / 返回下有提示音与振动（默认关闭，记忆选择），信号越强节奏越快，声音是短点击，不是关注提示；静默或消失时无声。页面保持亮屏，即使实时页暂停也读取实时 BLE。它不表示米数、指南针或目标地图位置。Wi-Fi 约 30 秒一批，加快后约 8 秒仍太慢，故无追踪按钮。随机 BLE 可途中消失。本功能为实验性，现场方法见 §12.13。',
        ),
        P(
            '页面底部在追踪与系列卡之后，是<b>从设备创建特征</b>及两个仅分享<b>本设备</b>的按钮，并非 15 分钟观测。都使用 Android 分享面板，不构成法律身份认定；MAC、SSID、载荷及 GPS 等内容应按敏感现场信息处理。',
            "body_left",
        ),
        bullets([
            '<b>分享为文本：</b>导出本页身份、推测、重点关注、说明、信号与近期 RSSI 样本、广播解码、会话时间、可选最近定位、匹配特征、原始字节及 15 分钟出现区间；曲线变为数值列表。开头注明实验性、非法律身份及原生 Android 限制。',
            '<b>AI 导出：</b>生成可粘贴到聊天中的<b>单设备</b>提示词，包含与观测导出相同的实验免责声明，并要求模型重复说明、不给安全建议。附上文本详情，要求依据 IEEE OUI、Bluetooth SIG、GAP Appearance 和已知格式等公开资料，注明每条判断由哪个字段支持；讨论可能产品类、其他解释、不可见信息，以及不能推断的所有者、尾随或距离。在线地名与 GPS 都开启时可能加入最近位置地名，仍是<i>手机</i>位置。它不是整次观测清单。',
        ]),
        P('5.6 报告标签页', "h2"),
        figure_wrap(
            "fig-reports.png",
            '图 6：报告 → 观测。选择决定轨迹、总结、导出和对比的本次一侧；图中开启隐私提示。',
            '位于底栏设置旁，包含可选命名观测、轨迹、总结、观测导出、对比、AI 导出、候选特征和日志导出。GPS、地名、日志开关及轮转大小仍在设置。此处选中的观测决定各报告窗口；未开启命名观测则使用内存中的最近 15 分钟。',
        ),
        P('命名观测', "h3"),
        figure_wrap(
            "fig-sit.png",
            '图 6：实时页面，观测进行中。',
            '观测是保存<b>全部接收设备</b>的命名时间窗口，实时列表移除 MAC 后仍保留。报告页开始 / 结束观测，名称可空，空白使用时间戳。当前接收设备先复制进来，随后持续记录新接收；同时只能一次。结束后冻结，最多保留 10 次，达到上限再开始时会警告结束后删除最旧项。无需开启日志，设置备份不包含观测，恢复默认值不删除观测，不具测向能力。',
        ),
        P(
            '<b>最多 6,000 台独立设备。</b>实时内存约 400、硬上限 900；命名观测允许 6,000 个类型 + MAC，适合较长车程。随机 BLE 每次轮换算新设备，密集场景 30-40 分钟仍可能满。观测是内存快照，约每 10 秒保存到应用存储；不是滚动日志，导出前也不在下载目录。Android 报告低内存时，即使未满也不再添加新未匹配设备。'
        ),
        P(
            '<b>满额后的保留策略：</b>重点关注、广播位置（Remote ID）、已关注 MAC 及匹配已关注特征的设备优先保留。先按最早最近接收时间移除无名称且无特征 BLE，再移除其他未固定设备。已有设备仍更新 RSSI 与时间；磁盘日志开启时仍记录每次接收。'
        ),
        P(
            '<b>总结清单与计数：</b>文本和 PDF 是同一报告。默认清单不列<b>未匹配的轮换 BLE</b>，包括值得关注 BLE、持续出现样本及停留点“此处接收”；但概览、环境和隐私计数仍含全部 BLE 及随机地址数。重点关注、命名特征、书签和载荷位置保留。“报告 → 观测报告 → <b>显示未匹配的轮换 BLE</b>”可恢复清单。CSV / JSON 观测导出仍含全部保留设备，包括 RAND。'
        ),
        bullets([
            '<b>进行中：</b>实时标题显示 FIELDWATCH · 观测及状态条，轨迹、总结、观测导出、对比本次和 AI 导出采用此窗口，不限 15 分钟。筛选、信号追踪、TAK 及约 400 台实时列表不变，起止按钮仍在报告页。',
            '<b>结束后：</b>观测出现在报告列表，可选作轨迹 / 总结 / 导出 / 对比本次，也可选最近 15 分钟；列表下可改名或删除。',
            '<b>轨迹：</b>北向朝上的当前、已保存或最近 15 分钟图。报告页保持前台可看进行中的轨迹增长或 15 分钟轨迹滑动；命名观测中的飞行器广播轨迹为白色点线。详见 §5.6.1。',
            '<b>观测总结（文本 / PDF）：</b>同一报告两种格式，选中观测最多 6,000 台，或内存最近 15 分钟约 400 台、硬上限 900。默认省略未匹配轮换 BLE 清单但计数保留，可用卡片开关恢复；观测导出始终含全部。开头有业余项目 / 原样声明，使用自定义名称，“所在位置”后有观测备注，存在广播位置时加飞行器部分（§5.4.1）。不受实时视图或筛选影响。驾车未开观测时应多次生成（§11.4.1）。PDF 使用粗体停留 / 移动行、字段引导词及 letter 版式轨迹图；附近飞行轨迹黑色点线、最后位置分类图标、飞手人形图标。',
            '<b>对比（文本 / PDF）：</b>本次窗口与第二次已存观测，仅按类型 + MAC 比较只在本次、只在另一次、两次都有。观测备注位于窗口之后，实时值变化会写明，如分离 → 靠近主人、空中 → 地面。最近 15 分钟与命名观测容量不同（约 400 与 6,000）。两者有 GPS 时 PDF 叠加路线，本次广播轨迹黑点、第二次蓝点。',
            '<b>对比 AI 导出：</b>聊天用补充分析提示词，嵌入机内对比，再附重叠率（交集 / 并集）、各组 Wi-Fi / BLE、独有随机 BLE、独有重点关注 / 命名设备及备注，要求模型不重抄清单。观测报告 AI 导出仍只针对当前窗口。',
            '<b>AI 导出：</b>针对当前 / 选中观测，否则最近 15 分钟并带 5 分钟切片。原样嵌入机内总结，再提供速率、RSSI 分段、重点关注、定位标签 ID 和备注，要求补充分析而非重写清单。<i>单设备</i>应从详情页导出。',
            '<b>观测导出：</b>位于观测报告下的独立卡片，格式选项与日志相同，但文件内容不同，详见 §5.6.2。',
            '<b>候选特征：</b>从滚动日志查找共享独特广播 ID 的未匹配系列。“创建特征”起草共享规则，不固定 MAC；保存后返回并重新分析。离线可用，参见 §5.6.4、§11.5。',
            '<b>日志导出：</b>独立卡片，选择滚动会话文件的格式和无线类型，参见 §5.6.3、§11.6。',
            '<b>重置 / 清空日志：</b>报告页底部，删除手机上的轮转文件，不重置已见集合，也不删除观测。',
        ]),
        P('5.6.1 轨迹', "h3"),
        figure_wrap(
            "fig-path.png",
            '图 6：报告 → 轨迹，北向朝上的本手机观测路线。隐私模式遮蔽 MAC 尾部，地图瓦片遵循在线地名与地图开关。',
            '显示所选当前 / 已存 / 最近 15 分钟内<b>本手机</b>的北向路线。此前必须开启 GPS 且有定位，否则卡片提示。一个点或短观测仍显示约 400 米地面范围，便于读街道；长路线充满图框。需要长于 15 分钟时开始命名观测。隐私模式仍绘线，只遮蔽坐标文字。',
        ),
        P(
            '<b>实时查看：</b>步行驾车时保持报告前台，约每 3 秒重绘；手机移动约 10 米或经过约 5 秒存新点，因此路线分步更新。最近 15 分钟是滑动窗口，尾部移除、头部为现在；开放观测从开始持续长到现在，结束前不能选已存或 15 分钟。MAC / 特征提醒每设备绘一次；解码经纬度采用设备最后广播位置，其他用至今最强 RSSI 点。只有重点关注但未加书签不会画。离开报告保留上次画面，回来再更新；结束后选已存观测看静态，头部标结束，已存飞行轨迹随路线重绘。'
        ),
        P(
            '实线是本手机，黑点起点，蓝点最新位置即您；页头计提醒数。MAC / 特征提醒绘一次，解码坐标用最后广播点，否则在最强接收处用分类图标。单图标无数字框，点击看单设备；深色圆盘计数代表同处多提醒。仅自定义名称且提醒关闭不绘，重点关注也需该特征被关注。列表 MAC 旁有无线类型，分类图标与地图一致，并列备注；实时列表仍只显示青色备注标签。粗绿线是约 40 米内停留，与总结一致，路径有 HH:mm 时间刻度。点击计数 / 图标打开，再点关闭；点弹出或下方设备行进详情。下方有比例尺，路线留边避免起终点压框。往返尖跳或暗示速度超过约 150 km/h 的 GPS 点会剔除。'
        ),
        P(
            '开放 / 已存观测中的白色点线表示飞行器广播轨迹，距本手机路线 2 km 内共享地图；末位用分类图标，单点只有图标，无线。与其他提醒重合则显示计数并列全部。更远且有 UAS ID 的飞行器在路线下有独立图，最多三张；飞手距飞行轨迹 2 km 内时用人形图标，不加文字。远处且无 UAS ID 的位置仅留在报告。旧观测只保留末位，最近 15 分钟只标当前位置不存路线。这些位置均为设备自行广播。'
        ),
        P(
            '默认开启的“设置 → <b>在线地名与地图</b>”在联网时加载 OpenStreetMap 瓦片，填满图框再裁切，路线四周留出地图。离线或无瓦片时只显示北向线图，不报错，飞行模式可用。隐私模式不隐藏地图；关闭此开关可同时停用报告地名与轨迹地图。'
        ),
        P(
            '总结和对比 PDF 包含占满 letter 报告框宽度的同一路线图。联网且在线地图开启时铺 OSM 瓦片；粗绿为停留，MAC / 特征提醒与应用轨迹一致，每设备一次，坐标优先最后广播、否则最强接收。重点关注红色，MAC 提醒蓝色，其他特征提醒绿色；同处设备共用轨迹索引号。广播飞行器在索引中用无人机图标而非数字，并列状态、UAS ID、最后位置、运动及飞手坐标。飞行轨迹黑点，末位分类图标，飞手人形且无文字。离线只画线。对比双方 GPS 充足时叠加本次实线、第二次虚线；对应飞行轨迹为黑点 / 蓝点，图注保留框内。'
        ),
        P('观测对比', "h3"),
        figure_wrap(
            "fig-compare.png",
            '图 6：报告 → 观测对比。本次与总结窗口相同，再选第二次已保存观测。',
            '本次窗口对比第二次已存观测，文本与 PDF 使用相同 letter 版式。第二次默认选次新的保存项。仅比较类型 + MAC 的此处独有、彼处独有和共有，用自定义名称替代广播名，窗口后列备注。15 分钟内存约 400 台，命名观测最多 6,000 台，采集容量不同。双方有 GPS 时 PDF 叠加本次实线和第二次虚线。',
        ),
        P('5.6.2 观测导出', "h3"),
        P(
            '报告页观测报告下的独立卡片，具有与日志导出相同的格式、全部 / Wi-Fi / BLE 选项及分享 / 保存，但它<b>不是</b>滚动日志。使用与轨迹和总结相同的当前 / 已存 / 最近 15 分钟窗口。'
        ),
        P(
            '<b>观测与日志导出：</b>日志是会话流水，覆盖开启记录时写入磁盘的每次接收并轮转，可跨全天。观测是该窗口的设备清单，按类型 + MAC 每台一行，命名最多 6,000，15 分钟内存约 400。听到一台设备一百次，观测一行、日志许多行。观测自存设备和 GPS，不需要日志开启；日志导出需要写入磁盘。清日志不删观测，删观测不动日志。候选特征仍分析日志。'
        ),
        bullets([
            '<b>CSV / JSON lines：</b>每设备一行，含类型、MAC、广播名、自定义名、备注、RSSI 最小 / 最大、信道、首次 / 最近、次数、可选经纬度、重点关注、匹配特征及重点关注系列。',
            '<b>GPX / KML：</b>包含手机轨迹及每设备一个最强 GPS 样本接收点；日志导出的这两种格式只有接收航点，没有操作者轨迹。',
            '<b>WiGLE CSV：</b>每设备在接收点一行，信息密度低于含多次接收的日志 WiGLE；使用广播 SSID，不使用自定义名。',
        ]),
        P(
            '隐私模式<b>不会</b>遮蔽观测导出文件，与日志导出一样保留完整 MAC 与经纬度；总结 / 对比 / AI 导出仍遮蔽。应用不上传。地图格式筛选 Wi-Fi 或 BLE 后无有效点时会提示开启 GPS 标记。'
        ),
        P('5.6.3 日志导出', "h3"),
        figure_wrap(
            "fig-log.png",
            '图 6：日志导出。格式和无线类型选择；磁盘轮转文件是 JSON lines，CSV / GPX / KML / WiGLE 在分享 / 保存时转换，应用不上传。',
            "磁盘文件为 <font face='FWText'>files/logs/fieldwatch-NNN.jsonl</font>，每次接收一行，属于会话流水而非观测清单。设置页只控制日志开关和轮转大小，分享 / 保存时在这里选格式。旧 CSV 轮转部分仍支持读取。应用不上传，观测导出是另一个卡片（§5.6.2）。",
        ),
        bullets([
            '<b>CSV 日志：</b>相同事实转为表格列，合并轮转文件并去除重复表头。',
            '<b>JSON lines 日志：</b>与磁盘文件相同的行。',
            '<b>GPX：</b>本手机接收各设备时的航点，标题使用自定义名。需开启 GPS 标记，无位置的行省略。',
            '<b>KML（Google Earth）：</b>同样的接收点，以 Placemark 表示。',
            '<b>WiGLE CSV（wigle.net）：</b>WigleWifi-1.4 上传格式，使用广播 SSID 以匹配实际空中信息，而非自定义名。上传由您执行，应用不上传。',
        ]),
        P(
            '无线类型可选全部、仅 Wi-Fi、仅 BLE。地图格式没有有效 GPS 点时给出对应类型提示：开启位置或选全部。隐私模式<b>不遮蔽</b>日志和地图文件，保留完整 MAC、经纬度；总结 / 对比 / AI 仍遮蔽。分享用 Android 面板，保存用系统文件选择器；进度使用动态条，不停在 0%。字段见 §11.1-11.3，操作见 §11.6，观测导出见 §5.6.2。'
        ),
        P('5.6.4 候选特征', "h3"),
        P(
            "实时页有大量未匹配设备、希望找<b>系列</b>而非逐个问号时使用。读取曾开启记录的磁盘滚动日志，不是 15 分钟总结内存；按类型 + MAC 去重，并<b>使用手机当前特征库重新匹配</b>，忽略写入时的 <font face='FWText'>fleets</font>。对剩余设备按独特名称通配符、Wi-Fi 厂商 IE、BLE UUID、厂商数据或稳定 OUI 聚类，至少两台才算系列。无其他 ID 的随机地址、住宅名称、芯片模块 OUI、WPA / RSN / P2P 等协议 IE 跳过，顶部显示数量。详情特征系列卡对单设备做同样分析。已标注设备不列入；第二个商店 UUID 标签应从详情创建（§5.5、§9.2）。"
        ),
        figure_wrap(
            "fig-candidates.png",
            '图 7：候选特征。',
            '每卡一个系列：建议名称、分类推测、设备数量及无线图标、等宽规则、为何不是住宅 SSID 的说明和若干示例，隐私模式遮蔽示例 MAC。<b>创建特征</b>用共享规则打开编辑草稿，不固定 MAC；可改名和分类，只有保存才新增为<b>自定义</b>特征，不修改内置库。保存后返回重算，已匹配系列应消失；取消则返回原列表不重算。全程离线，无网络查询，结果仍是模式推断。',
        ),
        P(
            "厂商 IE 系列（例如随机 BSSID 上的 Roku 类 ID）需要日志的 <font face='FWText'>vendor_ie</font> 列，只有此功能发布后写入的行才有。名称通配符和稳定 OUI 可分析旧文件。空列表可能因未开日志、记录过短或剩余全是噪声。参见 §11.5。",
            "body_left",
        ),
        P('5.7 设置页面', "h2"),
        figure_wrap(
            "fig-settings.png",
            '图 8：设置 → 外观。',
            '设置负责无线、日志和外观，不负责隐藏设备或生成总结。某个 OUI / 名称误匹配可关闭该特征的单条规则；隐藏整个系列用筛选。参见 §7.6、第 8 章。',
        ),
        bullets([
            '<b>外观：</b>夜间模式默认关闭，开启后文字、标签、RSSI、信号追踪和重点关注都转为黑底红色，减少暗处绿蓝光，手机亮度不变，恢复默认值会关闭（图 9）。常亮默认开启，仅应用前台保持屏幕，避免 Samsung 暂停 BLE，放入口袋可关。隐私默认关闭，开启后实时、雷达、时间线、详情、追踪、命名设备和关注卡的 MAC 后三字节显示 **:**:**，保留 OUI。详情最近定位及总结 / AI / 文本分享坐标显示已遮蔽，观测报告不含街道名。日志、匹配、随行及已保存特征仍用完整 MAC/GPS；TAK / CoT 暂停，避免发送完整信息到局域网（§5.8）。',
        ]),
        figure_wrap(
            "fig-settings-night.png",
            '图 9：设置 → 外观，夜间模式开启。',
            '夜间模式是外观第一项，将文字、标签、RSSI、信号追踪与重点关注转为不同红色，降低暗处绿蓝光。手机亮度不变，恢复默认值会关闭。',
        ),
        P('无线、关注、日志与备份', "h3"),
        bullets([
            '<b>无线：</b>扫描强度分高性能 / 均衡 / 省电，Wi-Fi 约 30 / 40 / 55 秒。加快 Wi-Fi AP 扫描是独立开关，Android 11+ 先读取系统限频；系统未关时不能启用。关闭开发者选项限频后再开启应用开关，约 8 秒一批，增加 AP 在范围内被接收并命中特征的机会，尤其驾车短暂经过路边或车载 AP。更耗电发热；系统重新限频时页头提示需要开发者选项，应用不能代改系统。参见 §7.1.1、§10.3.1。',
            '<b>关注列表：</b>关注提醒为总开关，关闭后无声音、语音、闪烁、跳转或系统通知，但可继续添加书签。提示音与语音独立，可单独或先音后语。语音默认开，可读分类、特征名或两者，默认分类 + 特征，不用于信号追踪；正在播报时忽略第二次命中。新关注跳转默认开，系统通知默认关，测试提醒按当前设置播放。<b>命名设备（N）</b>管理单 MAC 名称、备注、提醒和删除 / 清空，特征系列关注仍在特征库。默认关注重点关注系列（执法记录仪、摄录眼镜、穿戴录音、渗透测试、公共安全车载 AP、路边 / 公共摄像头和 ALPR）及全部无人机（DJI、Remote ID、Skydio、Autel、Parrot、HOVERAir）。不需要则取消特征书签，Flock LiteOn / Espressif OUI 可能噪声较多。参见 §10.1-10.2.1。',
            '<b>为检测结果添加 GPS 标记：</b>默认开，扫描中请求实时 GPS / 网络位置，为每次接收加标记，用于详情、随行、总结和日志经纬度。忽略超过 30 秒的旧定位；获得实时定位前轨迹为 0，应使用高精度。总结距离 / 跟随、随行筛选及 TAK 此处接收点需要此项，Remote ID 广播位置不需要。开启时日志导出包含操作者坐标。',
            '<b>TAK / CoT 推送：</b>默认关，通过 UDP 向 ATAK / WinTAK / iTAK 发送 Cursor-on-Target。目的地可选本机 127.0.0.1:10011、局域网组播 239.2.3.1:6969 或自定义；仅 UDP，不是 TAK 服务器 TCP 8087。“此处接收”固定在信号最强时操作者 GPS，呼号带“此处”；Remote ID 广播点位于飞行器，持久 UAS ID 保持一个移动标记，飞手坐标另一个点。有效航向 / 速度写入 ATAK track。Android 11+ 的 Wi-Fi FA:0B:BC 与 BLE FFFA 同样支持，消失设备移除，设置显示最近发送。默认发送重点关注和载荷位置，关注列表和全部特征默认关。隐私模式暂停，配置见 §5.8，观测见 §12.15。',
            '<b>在线地名与地图：</b>默认开。观测总结 / AI 导出使用系统地理编码，轨迹加载 OpenStreetMap 瓦片，无 Fieldwatch 云端或 API 密钥。离线、无地理编码器或无瓦片时，总结仅坐标、轨迹仅北向线图，不报错。隐私模式不隐藏地图。关闭此开关同时停用报告街道名和轨迹底图；生成按钮在报告页（§5.6、§5.6.1）。',
            '<b>日志：</b>写入磁盘、轮转大小、过期时间滑块，以及行数 / 磁盘统计。滚动文件为 JSON lines；格式（CSV、JSON lines、GPX、KML、WiGLE）、无线类型和分享 / 保存 / 清空在报告页。',
            '<b>允许后台使用：</b>打开系统 Fieldwatch 电池页，允许应用不在前台时扫描；开关跟随系统授权，与保持屏幕常亮不同。',
            '<b>不受限制的电池使用：</b>打开电池页，选择不受限制而非优化。部分 Samsung 等手机需先点击“允许后台使用”文字行进入，返回后应用显示授权状态。',
            "<b>特征导出 / 导入：</b>导出 JSON 包含完整内置、自定义及修改特征，包括解码字段；保存到 SD / 存储使用系统文件选择器写同一文件。导入其他 Fieldwatch 包时跳过相同 ID 或相同规则，重复导入不复制；内置项额外规则合并，缺失解码映射可补齐。重名新项加“（已导入）”。不含关注、筛选、设置、日志或 GPS；设置包须使用导入设置。完成与错误都有确定对话框。文件名 <font face='FWText'>fieldwatch-signatures-YYYYMMDD.json</font>。",
            "<b>从 GitHub 更新内置特征库：</b>需联网。1.1.12+ 读取 <font face='FWText'>dist/fieldwatch-signatures-v2.json</font>，1.1.11 读 <font face='FWText'>dist/fieldwatch-signatures.json</font>。替换内置项及重点关注文字，保留书签、设置、已静音内置项、自加规则和自定义特征。对话框区分无网络、无法连接、导入失败、已最新及更新完成。遇到当前 APK 不识别的解码来源，仍导入特征，只跳过该映射，并再次提示安装新版 APK。离线可从文件导入。新 APK 仍应用默认关注，而此按钮不做。设置页脚版本下显示特征库 N。上游目录中的描述可能为英文，中文版请使用本地随应用提供的中文特征内容。",
            '<b>恢复默认特征与预设：</b>重写内置特征、分类颜色、解码映射、默认书签（重点关注与无人机）、全部默认筛选按钮（含曾长按删除的）、命名设备及默认设置：常亮 / GPS / 地名 / 分类 + 特征语音 / 跳转开启，TAK / 夜间关闭。会清除自定义特征和自存预设；需要备份时先导出特征与设置。它不是撤销单规则；仅删一个预设应长按筛选按钮，没有另一套出厂设置按钮。',
            "<b>设置备份：</b>用于恢复出厂或换机，导出 JSON 或经系统选择器保存。导入会替换本机设置开关、当前筛选、预设、命名设备及特征关注；特征库不变，需另行导入。日志、GPS 和仅新检测的已见集合不包含；首次免责声明不会覆盖，因此不会因此停止扫描。重复导入结果相同，误选特征包会提示使用导入特征。成功或错误均有确定对话框。文件名 <font face='FWText'>fieldwatch-settings-YYYYMMDD.json</font>，不是 Spectre 配置导入。",
            '<b>显示实时页导览：</b>再次打开初次启动的遮罩，介绍显示调整、暂停、筛选、特征库、报告和设置，点击知道了关闭。',
        ]),
        P(
            '实时视图、排序、标题行、副标题行、RSSI 条、特征标签、频率、首次 / 最近和短暂保留都在“实时 → 显示调整”，不在设置。仅新检测是筛选项。'
        ),
        P(
            '设置页脚版本下显示当前 IPv4 或无地址，返回设置时刷新。同机 ATAK CIV 可用此地址作为 TAK 主机（§5.8）。'
        ),
        P('5.8 TAK / CoT 推送', "h2"),
        callout(
            '默认关闭：此功能会向局域网发送坐标',
            'TAK / CoT 向配置的主机和端口发送 UDP 标记，供 ATAK、WinTAK 或 iTAK 接收。包含完整 MAC，以及本机 GPS 或载荷广播经纬度。隐私模式暂停发送。没有 Fieldwatch TAK 服务器或账号；网络参与者与当地法规由您负责。请勿用该叠加图作安全、拦截或目标指示决策。',
            "warn",
        ),
        P(
            '“设置 → <b>TAK / CoT</b>”位于 GPS 标记下方，总开关默认关。开启不改变实时显示、筛选、日志或关注声音，而是并行推送已标注设备。'
        ),
        P('5.8.1 功能含义与边界', "h3"),
        P(
            "CoT 是 ATAK 支持的 XML 事件。每设备一个小事件，包含 uid、类型、点、呼号和备注，以 UDP 数据报发送。目的地<b>本机</b>为 <font face='FWText'>127.0.0.1:10011</font>，<b>局域网组播</b>为 <font face='FWText'>239.2.3.1:6969</font>，<b>自定义</b>可填单播 IPv4 / 主机名。未选按钮前主机默认 239.2.3.1、端口 10011。仅 UDP，不连接 TAK 服务器 TCP 8087；已登录服务器的 ATAK 是否转发注入 CoT 取决于客户端。"
        ),
        bullets([
            '它是在 Fieldwatch 已有坐标上，叠加本机接收到的无线设备。',
            '<b>此处接收</b>是至今最强信号时本手机 GPS，近似最接近的接收点；设备只是在可接收范围内，不一定位于该点，走远不会拖动标记。',
            "<b>广播位置</b>是设备编码的 WGS84 坐标：内置 BLE FFFA / Wi-Fi FA:0B:BC Remote ID，或字段 ID 为 <font face='FWText'>latitude</font> / <font face='FWText'>longitude</font> 的自定义映射。它是设备声明，不是 Fieldwatch 测向定位。",
            '它不是 Remote ID 插件、无人机追踪系统、测向、配对、GATT 或 Wi-Fi 监听模式，也不加入组播组，只发送。设备离开时发送 stale=now，让 ATAK 立即移除，不等约 120 秒。隐私暂停不发送离开事件，只停流，由 ATAK 超时移除。',
            '它与实时画面独立，筛选不会缩小推送；被隐藏的设备只要符合发送类别且有位置，仍会发布。',
        ]),
        P('5.8.2 两类标记', "h3"),
        P(
            '每个发布事件都需要坐标，按以下优先级选择：'
        ),
        numbered([
            "<b>广播载荷：</b>已有持久 <font face='FWText'>latitude</font> 与 <font face='FWText'>longitude</font> 时优先使用；来源可为 BLE FFFA、Wi-Fi FA:0B:BC 的 Remote ID 解码或同 ID 自定义映射。GPS 标记可关闭，两种 Remote ID 均使用此路径。",
            '<b>操作者 GPS（此处接收）：</b>否则用带位置的接收记录，固定在至今最强 RSSI 点而非最后一次。GPS 标记必须开且有实时定位，忽略超过 30 秒的旧定位。既无 GPS 标记又无载荷坐标时不发送。',
        ]),
        callout(
            '“此处接收”仍是本手机位置',
            'Axon、Flipper、Pineapple 标在您的 GPS，意思是“我在此接收到它”，不是目标坐标。只有新的接收比上次发送更强才更新点；走远保留。每约 10 秒刷新同一坐标保活，避免 ATAK 丢弃。无测向能力；Remote ID Location 例外，它是飞行器广播位置，可距您数公里。',
            "note",
        ),
        P('5.8.3 Remote ID：BLE 与 Wi-Fi', "h3"),
        P(
            'Remote ID 即 ASTM F3411 / OpenDroneID，是飞行器广播的数字身份信息。Fieldwatch 支持<b>低功耗蓝牙和 Wi-Fi</b>两种接收，实时标签、解码字段和 TAK 广播点走同一流程。它不是尾号、测向或专用 Remote ID 插件。'
        ),
        P(
            'Location 消息在列表加入未声明、地面、空中、紧急或 RID 故障状态，紧急更醒目。它只跟随当前 Location 包；后续 Basic ID / System 会清除，下一条 Location 再恢复。参见 §5.4.1。'
        ),
        P(
            'BLE FFFA 与 Wi-Fi 厂商 IE FA:0B:BC 都可匹配内置 Remote ID，统一映射解码协议 0-2 的 Basic ID、Location、System、Self ID。Wi-Fi 消息包封装为 FFFA，因此详情和 TAK 与 BLE 一致，仅 Wi-Fi 的 Location 也可标飞行器。'
        ),
        P('<b>两种接收方式：</b>', "body_left"),
        bullets([
            "<b>BLE：</b>FFFA 服务数据，每条广播一个 25 字节消息，轮换 Basic ID、Location、System、Self ID、Operator ID；支持协议 0、1、2。BLE 地址常轮换，Basic ID 的 <font face='FWText'>uas_id</font> 用作持久身份键。",
            '<b>Wi-Fi：</b>普通 AP 信标中的厂商 IE FA:0B:BC、类型 0x0D。Android 11+ 提供该 IE，Android 10 不提供，因此仅 Wi-Fi 无人机在 10 上不匹配。信标可包含单个 25 字节消息或类型 0xF 的 ASTM 多消息包。解析器将每个消息封装为 BLE FFFA（应用码 0x0D、计数器、消息），供同一映射、详情和 TAK 使用。',
        ]),
        P('<b>仍会漏掉：</b>', "body_left"),
        bullets([
            'Wi-Fi Neighbor Awareness Networking（NAN）填充信标，原生 Android 不能可靠提供。',
            '快速飞越，受系统 Wi-Fi 扫描限频影响；悬停或缓慢经过更易收到。',
            'Android 10 上的 Wi-Fi RID。最低 API 仍为 29，但厂商 IE 需要 API 30。',
            'STA / 客户端帧、探测请求、监听模式帧，以及未出现在 ScanResult 的 Wi-Fi Direct；Wi-Fi 仍只接收 AP 信标。',
        ]),
        P(
            "<b>保留的信息：</b>Location 包含经纬度 / 高度，随后 Basic ID 常不含位置。Fieldwatch 在会话中保留上次<i>有效</i>坐标，避免 ATAK 随消息类型闪烁；Basic ID 的 <font face='FWText'>uas_id</font> 也保留，作为 TAK uid，使一架飞机保持一个移动标记。首个 Basic ID 前仍以 MAC 为键，之后切换一次并删除旧 MAC 标记。System 的 <font face='FWText'>op_lat</font> / <font face='FWText'>op_lon</font> 表示<b>飞手 / 操作者</b>，用关联的橙色第二标记，不替代飞行器。"
        ),
        P(
            "<b>航迹：</b>航向为方向字节加东西标志，置位时 +180°。水平速度根据 SpeedMult 为每单位 0.25 m/s，或每单位 0.75 m/s 加偏移。无效方向 / 速度值 255 会省略。有效值写 ATAK <font face='FWText'>track</font>，用于图标朝向与运动；飞手和此处接收不含 track。支持时也解码垂直速度与气压高度。0,0、非有限数或超出纬度 ±90 / 经度 ±180 的坐标拒绝，不覆盖之前有效点。"
        ),
        P(
            '<b>同一解码映射：</b>两种传输都走 FFFA Remote ID 映射。Wi-Fi IE FA:0B:BC、类型 0x0D 解包后封装 FFFA，填 UAS ID、经纬度、航向、速度和操作者；TAK 载荷位置读取这些持久字段。其他特征不会自动获得通用厂商 IE 解码映射。'
        ),
        P('5.8.4 TAK 读取的字段 ID', "h3"),
        P(
            "TAK 按稳定字段 <b>ID</b> 查找，不按特征名。内置 Remote ID 的 BLE FFFA 和 Wi-Fi FA:0B:BC 同一映射填这些 ID，支持协议 0-2；自定义 BLE 映射使用相同 ID 也可发布坐标。解码字段没有单独 TAK 勾选框，标签可写“飞行器纬度”，ID 必须是 <font face='FWText'>latitude</font>。"
        ),
        table(
            ['字段 ID', '用途'],
            [
                ['latitude（别名 lat）', '广播的 WGS84 纬度，载荷标记需与经度成对。'],
                ['longitude（别名 lon、lng）', '广播的 WGS84 经度，需与纬度成对。'],
                ['alt_geo（别名 altitude、alt、hae）', '可选，CoT 点的椭球面高度，米；随坐标一起保留。'],
                ['op_lat / op_lon（别名 operator_lat / operator_lon）', 'Remote ID System 飞手位置，关联飞行器的第二 TAK 点；不可把这些 ID 用作飞行器坐标。'],
                ['heading（别名 course、direction）', 'Location 航向，度，用于飞行器 track course；方向字节 0-179，加上东西标志置位时的 180（opendroneid.c），不是乘 2。'],
                ['speed（别名 hspeed）', '水平速度 m/s，用于 track speed。内置 ID 是 hspeed：×0.25，SpeedMult 置位时 ×0.75 + 63.75。'],
                ['uas_id（别名 serial）', 'Remote ID Basic ID，持久保留；清理后至少四字符时作为 TAK 飞行器 uid。'],
                ["self_id", 'Remote ID Self ID，持久保留；存在时优先用作广播呼号。'],
            ],
            [2.4 * inch, 4.1 * inch],
        ),
        Spacer(1, 6),
        P(
            "自定义映射配置：“特征库 → 目标项 → 解码字段 → 经纬度卡片的更多”，将 ID 设为 <font face='FWText'>latitude</font> / <font face='FWText'>longitude</font>，比例按协议，例如 Remote ID 为 i32 小端、1e-7、单位 °。保存，打开 TAK / CoT 及载荷位置即可，无其他 TAK 设置。参见 §9.6.3。"
        ),
        P('5.8.5 开启步骤', "h3"),
        numbered([
            '组播 239.2.3.1 要求手机与 TAK 客户端在<b>同一局域网</b>。蜂窝和多数访客 Wi-Fi 不传该组；AP 屏蔽组播时改用单播。',
            'ATAK CIV 的 Manage Inputs 应有 UDP CoT 监听，通常 0.0.0.0:10011；原版 ATAK 也监听 self-SA 的 239.2.3.1:6969。无需安装 Fieldwatch 插件。',
            'Fieldwatch 设置中<b>关闭隐私模式</b>，否则推送暂停。',
            '打开 TAK / CoT。目标选本机 127.0.0.1:10011、同 Wi-Fi 的局域网组播 239.2.3.1:6969，或自定义单播 IPv4。本机选项不出图时，改填设置页脚的本机 Wi-Fi IPv4 和 10011。仅 UDP，不能填 TCP 8087。',
            '保留默认的重点关注和载荷位置：前者通常在本机 GPS，后者如 Remote ID 在设备广播点。',
            '开始扫描。有 GPS 的重点关注设备或 Remote ID Location 应在几秒内出现在 TAK。此处接收呼号带“此处”；Remote ID 优先 Self ID，再 UAS ID，再特征名。主机字段下显示发送数、目标和时间。',
        ]),
        P('5.8.6 主机与端口', "h3"),
        table(
            ['设置项', '默认值', '填写内容'],
            [
                ['本机', "127.0.0.1:10011", '同手机的 ATAK CIV；无标记时自定义填页脚 IPv4 和端口 10011。'],
                ['局域网组播', "239.2.3.1:6969", '本 Wi-Fi 的其他 ATAK，SA 组播，TTL 1；隔离客户端的访客网络会失败。'],
                ['自定义主机', "239.2.3.1", '单播 IPv4 / 主机名，或默认组播地址配端口 10011。保存时去首尾空格，空值忽略，避免存入空主机。'],
                ['端口', "10011", 'UDP 1-65535，仅数字。本机 ATAK CIV 用 10011，SA 组播用 6969，不是 TAK 服务器 TCP 8087。'],
            ],
            [1.2 * inch, 1.3 * inch, 4.0 * inch],
        ),
        Spacer(1, 6),
        bullets([
            '<b>组播（默认）：</b>只发送不加入组，TTL 1，仅此局域网不路由。手机与 ATAK 必须在实际转发 239.2.3.1 的同一 Wi-Fi 或共享以太网。热点隔离客户端会失败，可改用 ATAK 设备 IP 单播。',
            '<b>单播：</b>本机用 127.0.0.1:10011，自定义填一台终端 IPv4。应用不建立 TAK 服务器 8087 TCP 流；同机 ATAK 已登录服务器时是否转发注入 CoT，要在一次观测中确认后再依赖。',
            '应用已有用于在线地名的安装时 INTERNET 权限，UDP 使用同一权限。没有 Fieldwatch 云端，只发送到配置主机。',
            '恢复默认特征与预设会重置主机 / 端口并关闭推送。',
        ]),
        P('5.8.7 发送内容', "h3"),
        P(
            '总开关开启后显示四个独立选项，设备符合<i>任意</i>选项且有坐标才发送。未匹配特征的设备通常不发，除非其 MAC 已命名、提醒开启且选了关注列表。'
        ),
        table(
            ['选项', '默认', '选中对象'],
            [
                ['重点关注', '开启', '任意匹配特征的重点关注字段非空。内置例：业余 BLE 串口、Axon、WatchGuard Video、Ray-Ban / Meta、Snap、Fieldy、Plaud Note、Hak5 Pineapple、Flipper Zero、Pwnagotchi、Marauder / Deauther、GhostESP、Bruce、Porkchop、Cradlepoint、AirLink、Compex、Novatel Wireless、Utility Inc、Flock、Penguin、Pigvision、FS Ext Battery、Genetec AutoVu、Rekor、Motorola Vigilant、Verkada、Avigilon、Axis、Hikvision、Dahua、Hanwha Wisenet、Uniview、Rhombus。通常标在此处接收 GPS。'],
                ['载荷位置', '开启', '解码映射或 OpenDroneID 解析器已保留广播经纬度的设备。此项默认开是因为 Remote ID 没有重点关注，否则不会发布；BLE FFFA、Wi-Fi FA:0B:BC 和相同字段 ID 的自定义 BLE 映射均支持。'],
                ['关注列表', '关闭', '已关注特征及提醒开启的命名设备；仅命名、提醒关闭的不发。'],
                ['全部特征', '关闭', '所有有标签设备，广场可能让 ATAK 填满；适合短观测，不宜长步行。'],
            ],
            [1.45 * inch, 0.7 * inch, 4.35 * inch],
        ),
        Spacer(1, 6),
        P(
            '设备可同时符合多项，如 Remote ID 属载荷位置，已关注 Axon 属重点关注和关注列表；仍只有一个 uid / 标记。同时合格过多时每轮最多约 24 台，优先重点关注和载荷位置，再按较强 RSSI。'
        ),
        P('5.8.8 隐私、GPS 与不发送的情况', "h3"),
        bullets([
            '<b>总开关关闭</b>（默认）：不发送数据报。',
            '<b>隐私开启：</b>即使总开关开也暂停，设置下方显示提示。不会发送遮蔽后的 MAC 或坐标；发布需关闭隐私，不推送时可开隐私截图。',
            '<b>GPS 标记关闭：</b>停止此处接收点，Remote ID 等载荷位置仍发。',
            '<b>没有实时 GPS：</b>此处接收效果同关闭标记；实时轨迹 0 米是提示，需高精度位置、扫描运行并等待定位。',
            '<b>未选对应类别：</b>Ruuvi、手机或未匹配 AP 默认不发，需开启全部特征或将它加书签并选关注列表。',
            '<b>广播坐标无效：</b>0,0、NaN 或越界忽略，之前有效位置保留。',
            '<b>扫描停止：</b>通知停止按钮终止循环，已有 ATAK 标记约 120 秒后过期。',
        ]),
        P(
            "飞行器、飞手及本机位置首次合格、移动约 30 米或经过约 10 秒时发送。此处接收点只有新信号比上次更强才移动，弱接收约 10 秒仍刷新原坐标保活；峰值强度跨保活保留，后来更强仍可更新。站在角落不会不断刷屏。设备消失或不再符合类别时发送 <font face='FWText'>stale</font> 为当前时间，立即移除；受 24 台轮次限制或短暂 GPS 异常不算消失。隐私暂停不发送离开事件。"
        ),
        P('5.8.9 ATAK 显示内容', "h3"),
        bullets([
            "<b>uid：</b>有持久 UAS ID 时为 <font face='FWText'>FIELDWATCH-RID-</font> 加该 ID，一机一移动标记；否则为 FIELDWATCH-BLE- 或 FIELDWATCH-WIFI- 加无冒号 MAC。飞手为 FIELDWATCH-PILOT- 加同 ID；无 UAS ID 的 BLE 换地址仍是新标记。",
            "<b>type：</b>广播无人机（Remote ID / DJI 类）为 <font face='FWText'>a-u-A-M-H-Q</font>，未知无人机、黄色；此处接收重点关注为 <font face='FWText'>a-u-G</font>、栗红；飞手同类型、橙色；其他地面为青色，不表示敌友。",
            '<b>callsign：</b>依次优先命名设备、Self ID / UAS ID、重点关注特征名、首个匹配特征、广播名、MAC 尾部；此处接收带相应后缀。',
            "<b>point：</b>按前述经纬度；<font face='FWText'>hae</font> 为已知广播高度，否则 CoT 未知值 9999999；ce/le 未知。",
            "<b>track：</b>仅广播飞行器，有效时 <font face='FWText'>course</font> 为度、<font face='FWText'>speed</font> 为 m/s。飞手和此处接收省略；航向与速度均无时省略。",
            '<b>remarks：</b>检查标记时显示多行短卡：呼号、Wi-Fi / BLE、完整 MAC、RSSI、已知 Wi-Fi 信道、广播 / 此处接收 / 飞手位置、UAS ID、尚未用作呼号的广播名、最多三特征和重点关注文字，约 800 字符上限。地图标签仍是最多 32 字符呼号。隐私开启时暂停，不发送这些备注。',
            "<b>how：</b><font face='FWText'>m-g</font>（机器 / GPS），time / start / stale 为 UTC。",
        ]),
        P(
            '这不是 TAK 数据包、KML 或 GeoJSON 分享。地图空白时检查隐私、总开关、局域网、AP 组播过滤及是否有合格设备坐标。另见故障排查附录。'
        ),
        P('5.8.10 常见限制', "h3"),
        bullets([
            'Remote ID 支持 BLE FFFA 和 Android 11+ 的 Wi-Fi AP IE FA:0B:BC、0x0D，解码与 TAK 相同；NAN 填充信标仍不可靠，Android 10 不标仅 Wi-Fi 无人机。BLE 静默但 Wi-Fi 有 Location 仍可定位广播飞行器。',
            'Wi-Fi 受系统限频，悬停 / 慢过比快速飞越更容易收到。',
            '无测向或测距。此处接收为可接收期间信号最强的操作者 GPS，不是方向；广播位置可能含飞行器自身错误 GPS。',
            '不配对、不读 GATT、不解密；经纬度若仅连接后可得，就不会标点。',
            'BLE 换地址产生新 uid，除非已有 Remote ID Basic ID 的持久 UAS ID；手机和包中标签通常没有。',
            '广场开启全部特征会将咖啡馆 AP、耳机等填满 ATAK，这是该选项正常行为，关闭即可。',
            '组播不穿互联网，LTE 上的同伴收不到手机的 239.2.3.1。此 UDP 推送不登录 TAK 服务器；让 ATAK 接同 LAN，或先确认它是否转发注入事件。',
        ]),
        P('5.8.11 现场检查表', "h3"),
        P(
            '主机字段下显示推送中的标记数、当前轮次发送数、目标、错误和时间。发送数短暂变化后归零是保活等待（约 10 秒，广播 / 本机位置也可 30 米触发），推送中的标记数应保留。ATAK 无人机观测见 §12.15；执法记录仪 / 眼镜 / 渗透测试等重点关注使用相同开关，载荷位置可选。解码 ID 见 §9.6。'
        ),
    ]

    # 6 Views
    flow += [
        PageBreak(),
        P('6. 可视化模式', "h1"),
        P(
            '五种视图显示相同筛选设备。雷达空而列表不空时先查筛选；过期设备仍以暗点显示，停留筛选页不会使雷达全空。列表、混合、时间线共用标题行 / 副标题行；雷达标签保持简短特征名或类型推测。显示面板可调整每行密度，不改变采集集合（§5.3）。'
        ),
        P('6.1 经典雷达', "h2"),
        figure_wrap(
            "fig-radar.png",
            '图 10：经典雷达。',
            '<b>显示内容：</b>极坐标图，以您为中心，每台筛选设备一个点。',
        ),
        bullets([
            '半径代表最近 RSSI，环标 -40、-60、-80、-100 dBm，越强越靠近您。短暂保留固定环位置，不缓慢向外衰减。',
            '角度是 MAC 哈希，仅用于稳定位置，不是指南针方位。',
            '匹配设备用首个特征的分类颜色（§9.5）；未匹配按 RSSI：≥-55 绿，-55 至 -70 琥珀，-70 至 -85 橙，其他红。',
            '有特征的点更大、带光环，并显示首个特征名，列表最多可显示三个。',
            '关注命中时一秒内显示两个扩散环和亮心，对应列表闪烁及提示音 / 语音；之后荧光环保留到会话结束，与列表铃铛对应。已提醒点绘于上层，区别于分类颜色光环。',
            '暗点表示超过过期窗口后的最后位置。',
            '旋转扫描线只是视觉提示，亮线在前、阴影扇形在后，不进行方位扫描。',
            '点击点进入详情。',
        ]),
        P('<b>解读：</b>密集、亮且靠中心的点表示周围信号多且强，常来自当前房间和附近 AP。某特征光环逐渐内移只表示更强，不一定沿直线靠近。全部暗点表示过期窗口内未收到，检查扫描和系统位置。', "body_left"),
        P('<b>适用：</b>走访、介绍广场繁忙程度，或无需读 MAC 就观察某特征是否在附近。', "body_left"),
        table(
            ['优点', '局限'],
            [
                ['快速感知密度与相对强度，特征颜色突出。', '无真实方向，拥挤 2.4 GHz 环境可能重叠，未命名设备超过 24 时省略标签。'],
                ['与列表共用筛选，“仅特征匹配”可形成简洁的特征视图。', '容易把半径误读为米数，室内多径会让点内外跳动。'],
            ],
            [3.25 * inch, 3.25 * inch],
        ),
        Spacer(1, 8),
        P('6.2 按信号强度排列的实时列表', "h2"),
        figure_wrap(
            "fig-list.png",
            '图 11：强度列表。隐私遮蔽 MAC 尾部；有观测备注的设备在重点关注“!”附近显示青色备注标签。',
            '<b>显示内容：</b>按显示面板排序，默认 30 秒均值最强（全部选项见 §5.3）。一设备一行，密度可调；分类圆圈未匹配为 ?，标题默认 MAC，副标题行为无线图标、名称 + 类型及随机 / 消失。副标题行“无”会隐藏图标并把状态移至标题行。厂商仅详情可见，频率在右侧 RSSI 下，可附趋势、信号条、首次 / 最近和最多三个特征标签。六边形表示有解码映射，值在详情（§5.4、§9.6）。关注新命中闪一秒后保留荧光铃。配置示例见 §5.3。',
        ),
        P('<b>解读：</b>通常自上向下读，“新设备在底部”则看末尾。强度 / 最新排序下突然靠前的新行是新出现的强设备。&lt;隐藏&gt; 为隐藏 SSID AP；副标题行无名 BLE 只写未命名，由图标表示 LE，标题广播名仍可写未命名 LE。Apple, Inc. · AirTag 等是名称 + 类型推测，IEEE 厂商在详情；右侧是 RSSI。', "body_left"),
        P('<b>适用：</b>默认工作视图，用于排查、打开详情、确认筛选及选择关注。广场中过密时先设副标题行无、关闭附加字段，再考虑筛选设备。', "body_left"),
        table(
            ['优点', '局限'],
            [
                ['标识易读，方便点击详情 / 关注，每行信息量可调。', '没有空间直觉，只看顶部容易错过较弱的已命名设备。'],
                ['消失行仍可看历史，副标题行无可增加行数而不减少设备。', '极密环境仍需长滚动，此时应使用筛选。'],
            ],
            [3.25 * inch, 3.25 * inch],
        ),
        Spacer(1, 8),
        P('6.3 时间线', "h2"),
        figure_wrap(
            "fig-timeline.png",
            '图 12：时间线。',
            '<b>显示内容：</b>最近 15 分钟内每个筛选设备一张卡，按显示面板排序，标题行、副标题行、分类和无线图标与列表一致。下方条带左为 15 分钟前、右为现在，实段为出现区间，空隙为真实中断。数值为当前 RSSI，不是条带平均，频率开启时位于其下。约每秒更新，持续设备的条带向右增长直到占满。',
        ),
        P('<b>解读：</b>持续增长实条常是固定 AP 或不断广播手机。Wi-Fi 批次等待不算中断，固定 AP 保持一条；只有超过过期与短暂保留较大值后再回来才开新段。重复短条可能是低占空广播。转角出现、离开结束常是传播几何变化，并非设备彻底消失。连续 15 分钟后条满宽，不越过左边界。', "body_left"),
        P('<b>适用：</b>静坐、乘车，以及判断设备是否与自己同时出现和离开。', "body_left"),
        table(
            ['优点', '局限'],
            [
                ['出现与消失清楚，便于和日志关联。', '固定 15 分钟窗口，应用内没有多小时条带，需导出日志。'],
                ['不依赖雷达的半径隐喻，标题行 / 副标题行与列表一致。', 'UUID 仍需详情，信道 / MHz 需开启频率。'],
            ],
            [3.25 * inch, 3.25 * inch],
        ),
        Spacer(1, 8),
        P('6.4 混合视图', "h2"),
        figure_wrap(
            "fig-hybrid.png",
            '图 13：混合视图。',
            '<b>显示内容：</b>强度列表附每设备最多 40 点的全宽近期 RSSI 迷你曲线及趋势符号。尺度固定，上 -30、下 -100 dBm，淡色 10 dB 网格、左侧 -30 / -50 / -70 / -100 标度和四个纵向分区，圆点表示最新包，127 不可用点省略。没有额外说明条，网格即图例。广场拥挤可改强度列表及副标题行无。',
        ),
        P('<b>解读：</b>左旧右新，上强下弱。平线表示同一强度持续，Wi-Fi 30 秒批次之间通常如此，只有 RSSI 变化才升降；40 样本后向左滚。趋势符号为明显增强约 +8 dB、增强约 +3 dB、稳定、减弱、明显减弱。锯齿常是 BLE 周期广播，不一定运动。', "body_left"),
        P('<b>适用：</b>跟踪一两台候选同时看全场，判断信号是否增强比雷达直观。', "body_left"),
        table(
            ['优点', '局限'],
            [
                ['身份与趋势同屏，固定尺度让平线保持实际 dBm 高度。', '仍无方位，详情有同图的大版本。'],
                ['与列表相同，可点击详情。', '曲线按数据包顺序而非时钟绘制，Wi-Fi 扫描间保持平线。'],
            ],
            [3.25 * inch, 3.25 * inch],
        ),
        Spacer(1, 8),
        P('6.5 按分类', "h2"),
        figure_wrap(
            "fig-by-class.png",
            '图 14：按分类。',
            '<b>显示内容：</b>以层级呈现同一实时筛选集合。音频、穿戴、摄像头等分类按名称 A-Z，带分类图标。默认显示全部，将空类暗显为 0，减少跳动；折叠空分类隐藏零项。顶部按钮随滚动离开，不固定。点分类列特征（名称 A-Z，有解码映射显示六边形），点特征列设备，设备行与强度列表共用标题行 / 副标题行、信号条、特征、频率和时间，点设备进入同一详情，返回回到层级。未匹配最后。它是显示视图，不是报告，总结仍在报告页按窗口生成。',
        ),
        P(
            '<b>解读：</b>计数是设备而非包。双特征 / 分类设备如 TP-Link OUI 的 Tapo，会在各匹配类出现；页头仍统计独立设备，并提示 N 台属于多类。筛选仍生效，只看摄像头时其他类和未匹配为 0，除非折叠空类。点击分类不会启用仅显示。暂停、仅新检测、随行与列表一致。关注命中会展开对应类与特征让行闪烁，启用跳转时尽量保留标题；之后荧光铃在本会话保留。',
            "body_left",
        ),
        P('<b>适用：</b>先看每个系列有多少，再选设备；广场杂波主要体现在未匹配计数。', "body_left"),
        table(
            ['优点', '局限'],
            [
                ['无需逐行浏览即可看分类总数，与实时集合一致。', '无 RSSI 图，双分类设备在两类展开时出现两次。'],
                ['可进入相同详情，附加字段设置作用于设备行。', '摄像头筛选使其他类为 0，要看整个广场先选全部流量。'],
            ],
            [3.25 * inch, 3.25 * inch],
        ),
    ]

    # 7 Detection
    flow += [
        PageBreak(),
        P('7. 检测方法', "h1"),
        P('7.0 采集流程', "h2"),
        P(
            '本章说明 Fieldwatch 如何利用原生 Android 接收无线设备。普通使用可略过 API 名称，技术读者可据此了解系统公开与未公开的能力。'
        ),
        P(
            '处理链为<b>接收</b>（本章）→ <b>匹配</b>特征（§7.3-7.4、第 9 章）→ <b>筛选</b>实时设备（第 8 章）→ <b>显示与日志</b>（实时、关注、JSON lines）→ <b>报告</b>（轨迹、总结、对比、AI、候选特征，第 11 章）。筛选不改变接收内容，显示不改变筛选。未选命名观测时，总结忽略实时筛选并读最近 15 分钟内存；候选特征读取磁盘滚动日志。'
        ),
        P(
            '只有两类采集：Wi-Fi <b>接入点</b>扫描结果与 BLE 广播。无蜂窝、Wi-Fi 客户端、经典蓝牙查询或测向。'
        ),
        P('7.1 Wi-Fi 被动扫描', "h2"),
        P(
            "Fieldwatch 注册 <font face='FWText'>SCAN_RESULTS_AVAILABLE_ACTION</font> 和 ScanResultsCallback，按配额感知间隔调用 <font face='FWText'>WifiManager.startScan()</font>。每个 ScanResult 转为 WIFI 观察，包含 BSSID、清理后的 SSID、RSSI、由 2.4 / 5 / 6 GHz MHz 推导的信道、隐藏 SSID 标志、能力信息，以及 API 30+ 的 wifiStandard / channelWidth。"
        ),
        P(
            '一次成功扫描成批返回所有 AP，随后系统要求等待。高性能约 30 秒、均衡 40、省电 55；startScan 被拒时退避最长 45 秒，并显示等待系统。缓存结果不算新批次；等待时保留上批 AP，忽略空结果。只有批次中收到的设备才匹配；两次之间驾车错过的 AP 不标注、不记新接收、不提醒，即使 OUI 已在库中。关闭系统限频后可用加快扫描缩短空档（§7.1.1、§10.3.1）。'
        ),
        P('7.1.1 加快 Wi-Fi AP 扫描（可选）', "h2"),
        P(
            "瓶颈在原生 Android。Cradlepoint IBR、AirLink OUI、UniFi IE、Cisco BSSID 或隐藏车队 SSID，只有实际包含该 BSSID 的 <font face='FWText'>startScan()</font> 批次才能标注，批次间特征库没有新输入。静坐通常可等住宅 / 园区 AP 每 30 秒回来，驾车则可能因此完全错过车辆或路边 AP。"
        ),
        P(
            '两批之间大约行驶距离：'
        ),
        table(
            ['速度', '默认高性能（约 30 秒）', '加快扫描（约 8 秒）'],
            [
                ['25 mph（城市，约 40 km/h）', '约 335 米', '约 90 米'],
                ['45 mph（约 72 km/h）', '约 600 米', '约 160 米'],
                ['65 mph（高速，约 105 km/h）', '约 870 米', '约 230 米'],
            ],
            [1.7 * inch, 2.5 * inch, 2.3 * inch],
        ),
        Spacer(1, 6),
        P(
            '巡逻 / 车队网关如 Cradlepoint IBR600/1100/1700、Sierra Wireless AirLink 和部分 Compex / Novatel / Utility Inc，常仅在短暂经过的数百米内可接收，人体、玻璃和车辆遮挡会更短。隐藏 SSID 仍公开 MAC，通常靠 OUI 命中，但也必须在可听到时扫描。每 600-870 米一批可能错过全程，约每 8 秒一批增加接收 BSSID、匹配、显示标签及关注提醒的机会，这正是移动中更快识别特征 AP 的目的。'
        ),
        P(
            '它不让 Wi-Fi 连续化：仍是完整 AP 批次后等待，不看客户端，不改变 BLE，也不是信号追踪；追踪仍仅 BLE。驾车 RSSI 仍不是米数，要在轨迹和总结保留接收位置请开启 GPS。'
        ),
        P(
            "需 Android 11+。系统设置 → 关于手机，连续点击版本号开启开发者选项；关闭 <b>Wi-Fi 扫描限频</b>，再在 Fieldwatch 设置启用加快 AP 扫描。应用先读 <font face='FWText'>WifiManager.isScanThrottleEnabled()</font>；系统仍限制则保持关闭，并提供打开开发者选项的说明。应用不能代改系统。若系统限频后来重新开启，应用保存的开关可能仍开，但实际回到约 30 / 40 / 55 秒，页头提示需要开发者选项；返回设置时说明刷新。"
        ),
        P(
            '实际生效时跳过每两分钟四次配额，约每 8 秒请求；startScan 返回 false 时仍最长退避 45 秒，避免反复碰厂商限制。耗电和热量增加，适合车程或走廊初始几分钟，不宜全天口袋观测。BLE 仍遵循省电强度设置，不需要更多 AP 批次时请关闭。'
        ),
        P(
            '每条 WIFI 都是接入点类广播源：路由器、中继、Mesh、手机热点、物联网 / 摄像头 AP。仅关联为站点的手机、笔记本或摄像头，即使近在旁边也不出现在扫描结果。隐藏 SSID AP 因仍发信标会显示为空名称和 HIDDEN 标志；隐藏 SSID <i>客户端</i>不会。'
        ),
        P(
            '这不是混杂捕获，不打开监听接口，不额外发送超出系统扫描自身的探测请求。原生 Galaxy 没有连续 Wi-Fi 搜索。需要站点、探测或指定 MAC 帧时配合专用嗅探器。'
        ),
        P('7.2 低功耗蓝牙扫描', "h2"),
        P(
            "前台服务使用单个 <font face='FWText'>BluetoothLeScanner</font> 和匹配全部的 ScanFilter，防止 Samsung 将其当作熄屏无筛选扫描。广播进入丢弃最旧项的背压队列，服务批处理，不为每包启动协程。"
        ),
        table(
            ['强度', 'BLE ScanSettings', 'Wi-Fi 间隔'],
            [
                ['高性能', 'SCAN_MODE_LOW_LATENCY、CALLBACK_TYPE_ALL_MATCHES、MATCH_MODE_STICKY；约运行 70 秒、休息 2.5 秒。约 18 秒无广播表明系统暂停时，休息 8-12 秒后用 BALANCED 继续，直到恢复。', '30 秒 *'],
                ['均衡', 'SCAN_MODE_BALANCED，相同匹配策略，运行周期较长，约 180 秒。', '40 秒 *'],
                ['省电', 'SCAN_MODE_LOW_POWER，约每 20 分钟重启。', '55 秒 *'],
            ],
            [1.45 * inch, 3.55 * inch, 1.5 * inch],
        ),
        Spacer(1, 4),
        P(
            '* Wi-Fi 列为遵守系统配额的默认等待；关闭开发者限频并开启应用加快扫描时约 8 秒。参见 §7.1.1、§10.3.1。',
            "caption",
        ),
        Spacer(1, 6),
        P(
            '每条广播提供地址、本地名称、RSSI、服务 UUID（包括服务数据键）、首个厂商 ID 与简短十六进制，以及可选主 PHY、txPower、广播标志。检测不连接、配对或读 GATT。每几秒重启 BLE 曾导致 Samsung 上百次启停后列表停摆，因此当前不采用该方式。'
        ),
        P(
            "仅 BLE，不调用 <font face='FWText'>BluetoothAdapter.startDiscovery()</font>。Classic BR/EDR 查询会发射信号，通常暂停同适配器 BLE；Android 蓝牙设置通过它找到 HC-05 / HC-06，但它们不会出现在这里。BLE 的标志或设备类别可能<i>声称</i>双模，只是自我描述，不代表执行了 Classic 扫描。参见 §3.5。"
        ),
        P('7.3 匹配器使用的标识', "h2"),
        table(
            ['字段', '常见来源', '说明'],
            [
                ['OUI / MAC 前缀', '地址前 1-6 个字节', 'OUI 为 24 位。完整 MAC 更精确，但随机 BLE 上不稳定。'],
                ['名称 / SSID', 'Wi-Fi SSID 或 BLE AD 本地名称', '忽略大小写的子串或通配符（* 与 ?）。'],
                ['服务 UUID', 'BLE AD 类型 0x02/0x03/0x06/0x07 或服务数据键', '16 位值同时按短格式与 Bluetooth 基础 128 位格式比较。'],
                ['厂商 ID', 'BLE AD 类型 0xFF 的公司标识符', '如 Apple 0x004C、Samsung 0x0075、Tile 0x00C7、XUNTONG 0x09C8。'],
                ['厂商数据前缀', '公司 ID 之后的字节', 'AirTag Offline Finding 的首个载荷字节为 0x12。'],
                ['服务数据', 'BLE AD 类型 0x16/0x21 中 UUID 后的载荷', 'UUID 与前缀组合，如 Find Hub FEAA 40/41；前缀空时匹配该 UUID 的任意载荷，如 DULT FCB2。UUID 空时在任意服务载荷中查指定十六进制，也匹配反向字节，如 Axon BWCDEVICE。'],
                ['无线类型', 'WIFI 或 BLE', '不要在 OR 模式中单独加入，否则会匹配该类型全部设备。'],
                ['隐藏 SSID', 'Wi-Fi 结果中的空 SSID', '匹配隐藏 AP 类别；用 AND 结合完整 BSSID 可跟踪单台设备。'],
                ['厂商 IE OUI', '系统返回 IE 时的 802.11 元素 221', '例如 Flock 上的 LiteOn 00:80:19 / 00:0A:EB；很多手机会剔除扫描结果中的 IE。'],
                ['共同出现', '最少同组设备数 + 时间窗口 + 按 OUI / 连续 MAC 聚类', '自定义特征可选，内置项不使用聚类。'],
            ],
            [1.7 * inch, 2.0 * inch, 2.8 * inch],
        ),
        Spacer(1, 6),
        P('7.4 命名特征如何应用', "h2"),
        numbered([
            "每次新观察或更新按 <font face='FWText'>KIND:MAC</font> 为键保存。",
            '逐项计算所有特征；任意匹配开启时一条规则命中即可，关闭时所有启用规则都须命中。',
            '设置最少同组数量、按 OUI 或连续 MAC 聚类时，会对同组窗口内（默认 60 秒）的实时设备做第二轮检查。',
            '一台可匹配多个特征。实时最多三个标签，详情全部，日志以 + 连接全部名称。商店 iBeacon UUID 叠加通用 iBeacon 是常见双标签（§5.5、§9.2）。',
        ]),
        P(
            '保存特征或切换规则后会重新匹配内存设备，无需等下一个包。'
        ),
        P('7.5 内存集合与拥挤场所', "h2"),
        P(
            '广场手机轮换 BLE 地址，保留每个 MAC 会使“独立设备”无限增长。实时映射约 400 台，先删最旧未命名；无名 BLE 约三分钟过期，已命名 / 特征匹配可留至最后出现后 15 分钟。密集时列表仍满，但只是最强、最新的一组，不是所有路过随机 MAC。总结和 AI 读同一内存而非日志，驾车起点可能已丢（§11.4.1）。洪泛时日志也采样：新设备或每第 25 次命中，每批最多 16 行，避免磁盘互斥阻塞界面。短暂保留期内设备不因拥挤上限移除。'
        ),
        P('7.6 单条规则开关', "h2"),
        P(
            '每条特征规则在编辑器有独立开关；关闭保留规则但不匹配，内置与自定义相同。'
        ),
        P(
            '现场例：<b>Flock Safety Cameras</b> 使用 IEEE B4:1E:52 和 Flock-* / FLCK / Condor / Falcon / Sparrow 名称，并带重点关注。LiteOn / 模块前缀归<b>LiteOn camera radio</b>，摄像头类但不重点关注；当地噪声多可在筛选隐藏。Pigvision 仅名称匹配，全部名称规则关闭后不会命中，直到重新启用。'
        ),
        P(
            '原生 Android 看不到隐藏 Flock 站点的通配探测或发往 Flock MAC 的帧；现场匹配含义见 §7.6.1。'
        ),
        P('7.6.1 Flock / ALPR / 摄像头匹配的现场限制', "h3"),
        P(
            '“Flock Safety Cameras”彩色标签只是<b>公开广播的模式匹配</b>，不是目视识别、序列号或摄像杆位于 GPS 点的证据。用它提示观察，再记录真正看到的情况。'
        ),
        P('<b>限制不仅是特征库，更是手机无线能力。</b>应用使用原生 API，不能混杂 / 802.11 监听、原始帧、仅探测站点、锁信道或接收 LTE/5G。摄像头在 Wi-Fi / BLE 静默时不会凭空检测到。外接适配器 / 监听设备是另一采集系统，本应用不替代它。', "body_left"),
        P('<b>蜂窝优先与静默：</b>许多 Flock 类 ALPR 摄像杆以运营商模块为主，Wi-Fi 仅配置或备用，安装后可能关闭、隐藏或维护人员到场才开；BLE 即使存在也常是短程维护广播。安装当周可能听到 Flock-*，半年后同街区摄像仍工作但手机可见频段完全静默。<b>无标签不代表无摄像头；成熟部署静默很常见。</b>', "body_left"),
        P('<b>摄像头可能根本不用 Wi-Fi。</b>LTE/5G 回传而关闭 Wi-Fi 很正常。应用只看 AP 信标，只有调制解调器或仅连接市政 SSID 的客户端不会出现。', "body_left"),
        P('<b>看不到作为站点的摄像头。</b>系统不报告关联客户端、隐藏 SSID 站点或仅探测设备，无法观察 Flock 加入网络。只有它<i>广播 AP 信标</i>才可见；隐藏 AP 显示 &lt;隐藏&gt; 与 BSSID，SSID 可见前名称规则不命中。', "body_left"),
        P("<b>只有一个 OUI 真正属于 Flock。</b>IEEE MA-L <font face='FWText'>B4:1E:52</font> 注册给 Flock Safety，结合 Flock-* 名称时置信度高。早期库曾合并约 28 个 LiteOn、Espressif 等模块前缀，这些也用于打印机、插座、玩具和其他摄像头，单凭 3C:71:BF 等只属弱推测。Silicon Labs 电池模块 OUI 同样见于无关物联网。旧版整条特征的重点关注、书签和 TAK 可能也由弱 OUI 触发；当前目录已将 LiteOn 模块单独分出（§7.6）。重点关注及书签始终作用于整条特征，而非某一 OUI 规则。", "body_left"),
        P('<b>名称有帮助，也可误导。</b>配置中的 Flock-ABCDEF 较强，无关 SSID 中的 Flock 子串较弱；Pigvision 仅名称、唯一性低，Penguin 还匹配 XUNTONG 0x09C8。Verkada、Axis、Hikvision 等多为名称规则，任何 AP 自取相同词都可能命中；早期可选目录曾默认关闭这些项，当前状态应以库为准。不能仅因 SSID 含 Hikvision 就记录为已确认摄像头。', "body_left"),
        P('<b>Raven 是另一类无线设备。</b>ShotSpotter / Raven 是声学传感器，不是 ALPR 摄像头。较强指纹为 BLE UUID 0x3100-0x3500 与 OUI D4:11:D6；XUNTONG 0x09C8 属 Penguin 电池。单纯 RAVEN 名称更易重名。', "body_left"),
        P('<b>厂商 IE 常缺失。</b>元素 221 中 LiteOn 00:80:19 / 00:0A:EB 可作旁证，但 Samsung 经常不返回。IE 规则不触发很正常，不能证明 AP 无问题。', "body_left"),
        P('<b>几何关系不是身份。</b>RSSI 不是米数，雷达角是 MAC 哈希，GPS 是接收时<i>手机</i>坐标。强 Flock-* 只表示足够近可解信标，不表示杆就在坐标处。应移动、看强度并目视确认。', "body_left"),
        P('<b>有无匹配都容易过度解读。</b>占空比、约 30 秒 Wi-Fi 批次、5/6 GHz 消失而 2.4 GHz 仍在、隐藏名称、蜂窝优先 / 静默，以及关闭规则都可导致空列表。反过来，商业园区 LiteOn OUI 加通用摄像名称常属其他设备。可加书签提醒，但认定基础设施前仍需目视。已知摄像走廊里未发现匹配仍是有效观测，只表示本手机未收到匹配<b>广播</b>。', "body_left"),
        callout(
            '如何描述匹配结果',
            '高：B4:1E:52 和 / 或 Flock-* / FLCK，或 Raven UUID 0x3100-0x3500。中：FS Ext Battery 名称、Penguin 0x09C8，或无 IEEE OUI 的 Flock 名称。低：仅 LiteOn / Espressif / Silicon Labs OUI、Penguin / Pigvision 名称、仅名称摄像特征。没有目视、IEEE OUI 或清楚 Flock-* 名称时，不应据射频声称“这就是 Flock 摄像头”。模式不等于车牌、人员或序列号。',
            "warn",
        ),
        P('7.7 离线编号数据库', "h2"),
        P(
            "厂商和 UUID 名称不在运行时下载，而在 <font face='FWText'>assets/lookups/radiodb.bin</font> 打包并二分查找，源为官方 IEEE MA-L / MA-M / MA-S / CID CSV 和 Bluetooth SIG Assigned Numbers YAML（公司 ID、GAP 外观、16 位服务 UUID）。设备类别按 Core Assigned Numbers 位域解码。可用 <font face='FWText'>python3 scripts/build_lookups.py</font> 重建。随机 MAC 跳过 OUI；信标间隔不是 Android ScanResult 字段，未提供时省略。"
        ),
        P('7.8 广播载荷解码', "h2"),
        P(
            '标准 AD 头之后的厂商字节由厂商自定义。Fieldwatch 解读有公开规范或充分公开研究的格式，在详情原始十六进制上方显示字段：'
        ),
        bullets([
            '<b>iBeacon：</b>Apple 0x02 / 0x15，UUID、major、minor、校准 TX。',
            '<b>Google Fast Pair：</b>服务 0xFE2C；三字节型号 ID 表示配对模式，按本地已知列表命名；较长载荷是已配对账号密钥布隆过滤器，可在界面隐藏。',
            '<b>Apple Continuity：</b>公司 0x004C 的 TLV，含 Proximity Pairing / AirPods（0x07）、Find My（0x12）、Nearby Info（0x10）、Nearby Action（0x0F）、AirDrop、Handoff、Hey Siri、AirPlay、Instant Hotspot。',
            '<b>Eddystone：</b>0xFEAA 的 UID、URL、TLM、EID 各自保留并在原始行标注，不随帧轮换相互覆盖。',
            '<b>Microsoft：</b>识别到相应信标类型时，解析公司 0x0006 的 Nearby Sharing / Swift Pair 设备类别。',
        ]),
        P(
            "任意 0xFF 载荷没有统一官方目录。IEEE / SIG 表可用 <font face='FWText'>python3 scripts/build_lookups.py</font> 重建。Fast Pair 产品名是精选本地列表，不是 Google 完整合作伙伴目录。"
        ),
    ]

    # 8 Filters
    flow += [
        PageBreak(),
        P('8. 筛选系统', "h1"),
        figure_wrap(
            "fig-filters-top.png",
            '图 15：筛选、预设与无线类型。',
            '筛选位于实时旁的第二页，用于看完列表后减少无关设备，不会关闭无线扫描。观测总结、AI 导出和磁盘日志忽略实时筛选及当前视图，仍读取对应内存窗口或文件。列表变空时先撤销最后的开关，不要直接认为区域没有设备。',
        ),
        P(
            '如果只是信息<i>过密</i>，先用“实时 → 显示”隐藏副标题行、信号条、频率和时间，而不移除设备（§5.3、§12.11）。真正需要减少设备数量时再使用筛选。'
        ),
        P('8.1 架构', "h2"),
        figure_wrap(
            "fig-filters-mid.png",
            '图 16：筛选中的特征分类。',
            '接收与展示彼此分离。Fieldwatch 记录收到的观察，筛选只改变雷达、列表、时间线、混合和按分类的显示；日志仍记录被筛选隐藏的设备，因此精简画面不等于从文件删数据。',
        ),
        P(
            '筛选页从上到下为：预设、显示无线类型、随行、仅新检测、仅特征匹配、仅已关注、仅命名设备、隐藏 Fast Pair 账号密钥、特征分类（仅显示 / 隐藏与分类按钮）、仅显示所选特征、隐藏所选特征（分类 A-Z 列表）、RSSI / 名称 / OUI、额外逻辑 AND/OR。重置筛选清除全部条件、记住的显示 / 隐藏选择及仅新检测的已见集合。'
        ),
        P('按图 15-16 的页面顺序：', "body_left"),
        bullets([
            '<b>显示无线类型：</b>全部、仅 Wi-Fi 或仅 BLE；一条设备记录不会同时属于两种。',
            '<b>随行：</b>仅针对 <b>BLE</b> 的 GPS 同行判断，多数位置样本须约 -75 dBm 或更强。排除 Wi-Fi AP，因为驶过强 AP 时会沿您的接收位置留下数百米轨迹，看似随行。需要实时 GPS 及约 45 米移动；包内 / 车内标签可符合，“仍在附近”范围随速度变化（§8.5）。第二台手机常因 MAC 轮换、轨迹重置不符合。开启会清除仅特征 / 仅显示 / 仅命名 / 仅已关注，保留隐藏条件，始终按 AND。“实时 → 重新开始”清轨迹不清日志；关闭后总结仍可分析最近 15 分钟追踪。',
            '<b>仅新检测：</b>隐藏已经在场的设备，始终 AND。实时页提供标记已见 / 重置已见（§5.3.2）。首次开启记录当前广播，随机 BLE 仍可能是新的；全部流量或重置筛选会关闭并清已见。',
            '<b>仅特征匹配：</b>隐藏无特征设备。分类仅显示或仅显示所选特征已隐含此条件，因此此开关保持开启且不可操作，直到关闭前两者。',
            '<b>仅已关注：</b>保留匹配已关注特征或提醒开启的命名设备，始终 AND。隐藏条件仍有效，例如隐藏监控会移除已关注摄像头；仅标签名称应使用仅命名设备。实时页显示相应提示条。',
            '<b>仅命名设备：</b>只保留设置中有自定义名称的设备，提醒可关闭，区别于特征匹配 / 已关注。随机 MAC 的名称不跟随轮换，开启时实时页显示提示条。',
            '<b>隐藏 Fast Pair 账号密钥：</b>当 Fast Pair 是唯一匹配时，隐藏已配对广播；配对模式保留，标签为 Fast Pair 配对。还匹配 Google 的 Pixel 保留。它不同于隐藏整个 Fast Pair 系列，后者连配对模式也删；始终 AND。两种载荷含义见 §9.5。',
            '<b>特征分类：</b>只影响实时，匹配仍进行。<b>仅显示</b>保留选中类；<b>隐藏这些</b>去掉选中类，保留其他及未匹配。未选类的仅显示不改变列表。分类按钮两列，图标同实时；摄像头、无人机、定位标签、手机 / 电脑等可组合，想存预设再选择保存当前为。分类与颜色见 §9.5。',
            '<b>仅显示所选特征：</b>只保留选中系列。开关下按分类 A-Z 展开列表，点类查看特征，与特征库层级相同。空选择不额外限制，与隐藏所选分开记忆。',
            '<b>隐藏所选特征：</b>只隐藏一个系列，如包中 AirTag，而不隐藏整个定位标签类。下方按分类 A-Z 选择；空列表不隐藏，关闭后再开会记住选项。',
            '<b>RSSI / 名称 / OUI：</b>最近 RSSI 不低于滑块，默认 -100 dBm 等于不过滤；名称条件匹配名称或 MAC 子串，OUI 条件匹配 MAC 或厂商文字子串。',
        ]),
        P(
            '分类仅显示可得到仅标签 / 仅摄像头。隐藏这些或隐藏所选只移除实时画面，特征、日志、总结仍保留；关注提醒是否触发还取决于当前可见筛选规则（第 10 章）。'
        ),
        P('8.2 AND 与 OR', "h2"),
        P(
            '<b>AND</b> 默认要求每个有效条件通过，适合集中观测，例如 BLE + 仅特征匹配 + RSSI ≥ -70。'
        ),
        P(
            '<b>OR：</b>无线类型、仅特征 / 仅命名 / 仅已关注、分类隐藏、隐藏所选、随行、仅新检测仍强制适用。仅在名称、OUI、高于 -100 的 RSSI 下限及分类仅显示等可选条件中，任一通过即可，适合名称含 Flock 或 OUI 含 B41E52 的广搜。AND/OR 都不能覆盖隐藏条件，例如隐藏定位标签后 OR 也不显示 AirTag。'
        ),
        P('8.3 特征匹配、分类与所选系列', "h2"),
        figure_wrap(
            "fig-filters-selected.png",
            '图 17：所选特征。',
            '<b>仅特征匹配</b>保留所有分类中的模式命中，空列表表示范围内暂无匹配，特征一直在运行，筛选只影响显示。分类<b>仅显示</b>或仅显示所选已经隐藏未匹配，此开关因此开启且禁用。<b>隐藏这些</b>不隐藏未匹配，此时仅特征仍可切换，选择“命中特征减隐藏类”或“全部设备减隐藏类”。',
        ),
        P(
            '分类包括定位标签、零售信标、标牌、穿戴设备、监控、无人机、渗透测试、公共安全、车辆、眼镜、音频、摄像头、温控器、门禁、健康、家庭物联网、ISP / 路由器、Mesh、手机 / 电脑及其他，每条特征在编辑器设置一个类。公共安全包含 Axon / WatchGuard Video 和 Cradlepoint、AirLink、Compex、Novatel、Utility Inc 等车载 AP，常用于执法但非专属，也可能用于政府、市政和企业车队。仅显示保留选中类，隐藏这些移除；不会关闭特征匹配、日志或总结。要保存分类组合，使用保存当前为，而非寻找默认分类预设。内置项归类见 §9.5。'
        ),
        P(
            '<b>隐藏所选特征</b>只移除选中系列，其他及未匹配保留；例如隐藏自有 AirTag 而保留 Tile、Chipolo。开关打开后显示缩进列表，开启某特征即隐藏它。关闭总开关会收起列表、停止隐藏但记住选项；只有重置筛选忘记选择。可与分类隐藏并用。'
        ),
        P(
            '仅特征匹配加隐藏定位标签，可减少自有标签杂波；仅显示监控适合摄像头 / ALPR。选项并不互斥。<b>仅已关注</b>更窄，只保留关注特征与提醒开启的命名设备；仅特征匹配则保留未关注系列。隐藏条件始终生效。'
        ),
        P('8.4 预设', "h2"),
        P(
            '顶部两列预设按钮，点击会<b>替换整套筛选</b>，包括无线、随行、新检测、仅特征 / 已关注 / 命名、分类显示隐藏及选择、所选特征显示隐藏、RSSI、名称 / MAC / OUI、AND/OR。不改显示布局、GPS 或日志。内置按钮只是保存的筛选，不是第二套匹配引擎。'
        ),
        P(
            '<b>保存当前为：</b>输入名称保存为新按钮，快照包含分类、隐藏和仅新检测，不覆盖内置项。点按钮应用，当前高亮；长按并确认删除，只删按钮不改正在使用的筛选。删除的内置按钮在目录更新后仍不回来，恢复默认特征与预设才恢复短列表，并同时重写特征库。即使删了全部流量，底部<b>重置筛选</b>仍清全部条件并关闭仅新检测、清已见；不是撤销上个预设。应用全部流量效果相同。'
        ),
        P(
            '分类仅显示只展示已匹配设备。如果定位标签同时被隐藏，该观测会空，应关闭隐藏或取消对应类。摄像头、无人机、监控、定位标签等不是默认预设按钮，可选仅显示加分类后自行保存。'
        ),
        table(
            ['预设', '设置内容', '说明'],
            [
                ['全部流量', '两种无线，无 RSSI / 查询限制，关闭仅特征 / 已关注 / 命名、分类、隐藏所选、隐藏 Fast Pair 密钥、随行和仅新检测。', '显示全部，适合初看街区；同时清空已见集合。'],
                ['仅 Wi-Fi', '关闭 BLE 显示。', '仅 AP、热点、Mesh、软 AP，无 LE 行。'],
                ['仅 BLE', '关闭 Wi-Fi 显示。', '仅广播设备。'],
                ['强信号', '两种无线，RSSI 下限 -70 dBm。', '去掉较弱杂波，不是信号追踪；仍密集时配合副标题行无。'],
                ['随行', '开启 BLE 随行，排除 Wi-Fi AP；关闭仅特征、仅已关注、仅命名和分类仅显示。', '仍需 GPS 标记和约 50 米轨迹。包内 / 车内标签可符合，AP 因传播范围易像同行而排除；仍在附近范围随速度增长（§8.5）。开关会清相应仅显示限制，总结追踪分析独立（§12.2）。'],
                ['仅已关注', '开启仅已关注，两种无线，无分类或 RSSI 限制。', '关注特征及提醒开启的命名设备，仍遵循隐藏条件；仅有名称的用仅命名设备。'],
            ],
            [1.35 * inch, 2.55 * inch, 2.6 * inch],
        ),
        Spacer(1, 4),
        P(
            '内置预设均关闭仅新检测。保存自定义按钮后可一键恢复组合，如“广场 -80 + 隐藏定位标签”。显示排序、标题行和副标题行不随筛选预设保存，位于实时显示面板。',
            "body_left",
        ),
        P('8.5 随行判断原理', "h2"),
        P(
            '随行回答：步行或驾车时，哪些强设备持续跟随<i>本手机</i>，而非到达目的地才听到。它是实时筛选，不是信号追踪或测向。GPS 始终是接收时手机位置，RSSI 是此处强度，不是距离；特征标签仍不代表身份。'
        ),
        P(
            '排除 Wi-Fi AP，因为经过固定强 AP 可在数百米路程中持续接收，留下的其实是手机轨迹，看起来像同行。因此只筛 BLE：包中标签或车内音箱随路径增长反复收到；高速路过手机通常只强几秒便离开，应短暂出现后消失，真正随行 BLE 应持续。'
        ),
        P('8.5.1 启动判断的前提', "h3"),
        P(
            '开启 GPS 标记、系统高精度位置并保持扫描，提供实时定位；忽略超过 30 秒旧位置。操作者轨迹至少约 45 米才开始判断，静坐不算。筛选显示距离，实时页在开关开启时显示随行 · 轨迹 N 米。'
        ),
        P(
            '每台设备须通过全部条件，任一失败就不在此筛选列表，但仍可在日志及总结中出现。'
        ),
        bullets([
            '<b>近期接收：</b>最近 90 秒内有包。',
            '<b>当前足够强：</b>最后 RSSI 约 -75 dBm 或更强；低于门槛暂时隐藏，增强后可回来。',
            '<b>有轨迹而非单次信号：</b>至少两个 GPS 标记，手机移动约 8 米（或 30 秒内 18 米）才增加，静止人群不会堆出轨迹。',
            '<b>轨迹确实移动：</b>该设备的位置路径和包围框都至少覆盖约 27 米，即操作者 45 米的 60%。只在门口听到的设备轨迹太小，即使很强也失败。',
            '<b>沿途足够强：</b>至少三分之二 GPS 样本约 -75 dBm 或更强；多数车程很弱、到家才强的不符合。',
            '<b>按速度判断仍在附近：</b>比较最后接收时手机 GPS 与现在位置，容许中间移动距离随速度调整，见 §8.5.2。',
        ]),
        P(
            '车内第二部手机通常失败于轨迹而非速度：iOS 和许多 Android 轮换 BLE MAC，被视为新设备、轨迹为空。可用包中稳定 MAC 的 AirTag、Tile、SmartTag 验证筛选工作。'
        ),
        P('8.5.2 为什么“仍在附近”窗口随速度增长', "h3"),
        P(
            '最后 GPS 点是手机接收到设备时的位置，不是设备位置。设备几秒未广播，手机仍在走；步行是房屋长度，高速却可能数百米。若固定 50 米半径，车内杯架标签也会在广播间隙闪掉。'
        ),
        P(
            '因此判断的是“自上次接收后，手机是否走得超过合理静默期间的距离”，而非目标此刻距我是否 50 米。近期速度为轨迹长度除以用时，是跟随期间平均而非单次 GPS 速度，限制在 0-40 m/s（约 0-90 mph），避免跳点放宽到数公里。'
        ),
        P(
            '包内 BLE 通常每几秒广播。保留窗口 15 秒乘近期速度，低速至少 50 米；约快走 / 慢骑 7.5 mph 时开始超过下限。任何速度再加 25 米 GPS 余量，容纳普通抖动，不将 RSSI 当尺子。'
        ),
        P(
            '公式：<b>容许距离 = max（50 米，速度 × 15 秒）+ 25 米</b>。Wi-Fi AP 在条件检查前已排除，不适用。'
        ),
        table(
            ['近期速度', 'BLE 仍在附近窗口', '实际含义'],
            [
                ['步行（约 3 mph / 5 km/h）', '约 75 米', '约房屋尺度，50 米下限仍占主导。'],
                ['快走 / 骑车（约 7.5 mph / 12 km/h）', '约 75 米', '刚开始超过下限。'],
                ['街区慢行（约 15 mph / 24 km/h）', '约 125 米', '标签漏发几次广播仍可视为同行。'],
                ['城市道路（约 30 mph / 48 km/h）', '约 225 米', '几秒静默已跨数条街，不立刻判为离开。'],
                ['州际高速（约 55 mph / 89 km/h）', '约 400 米', '两秒已走约 50 米，保留时间涵盖若干次广播。'],
                ['高速（约 70 mph / 113 km/h）', '约 500 米', '车内标签应保持，路边 BLE 仍会因轨迹不足失败。'],
            ],
            [1.8 * inch, 1.5 * inch, 3.2 * inch],
        ),
        Spacer(1, 6),
        P(
            '这些距离是自设备最后 GPS 标记后<i>手机</i>可以移动的范围，不是围绕目标的检测半径，也不代表目标在 400 米外。持续广播的包内标签不断获得新位置，在 GPS 意义上仍接近此处。'
        ),
        P('8.5.3 高速行驶时仍会被排除的设备', "h3"),
        P(
            '较大窗口不会保留所有路过设备，轨迹移动与三分之二强信号条件不随速度改变。邻车手机通常强几秒，很少积累覆盖您约 27 米路径的两个 GPS 点，拉开后即静默，所以应短现后离开。车内标签沿高速持续打点，能通过同样条件。'
        ),
        P(
            'Wi-Fi AP 永不符合，若仍出现属错误。门口才遇见的住宅 BLE 轨迹不足。包内标签不显示可能因路太短、到目的地才开 GPS 或未达到约 45 米；在实时页重新开始后再移动。'
        ),
        P(
            '实时页标签栏上方的重新开始清操作者和所有设备 GPS 轨迹，不清列表或日志。关闭随行不清轨迹。无论筛选开启与否，总结仍可分析最近 15 分钟同行，参见 §11.4、§12.2。'
        ),
        callout(
            '这仍是启发式判断',
            '保留行只表示强信号的接收轨迹跟随手机，不证明有人尾随，漏检也不代表安全。静默标签、轮换 Find My 地址及系统未送达设备不会出现。涉及人身安全时应离开并求助，不要等待此列表。',
            "warn",
        ),
        P('8.6 现场配置示例', "h2"),
        P(
            '以下为简短配置；第 12 章逐项说明准备、预期画面及不能据此声称的结论。'
        ),
        table(
            ['情形', '建议筛选'],
            [
                ['快速查看街区', '全部流量、高性能、强度列表或混合，保留默认显示。先不要仅特征匹配，背景杂波也有助了解环境。'],
                ['长时间静坐 / 乘车', '均衡或省电、时间线。列表忙时先隐藏副标题行，再考虑提高 RSSI 门槛，保持日志。'],
                ['专看某系列', '仅显示加公共安全、摄像头、无人机、监控、定位标签等分类；匹配继续。需要一键恢复可保存当前为。'],
                ['命中特征但减少杂波', '仅特征匹配 + 隐藏定位标签，或只隐藏包内 AirTag 等单个系列。'],
                ['隐藏定位标签、保留其他', '筛选 → 隐藏这些 → 定位标签。'],
                ['追踪标签', '仅显示定位标签、仅 BLE，观察特征；标签广播慢，通常省电足够。'],
                ['SSID / OUI 线索', '名称或 OUI 查询、AND、两种无线；不要仅特征匹配，以免隐藏相关但未匹配 AP。'],
                ['哪些设备与我同行', '开启 GPS 和高精度，移动约 50 米直到轨迹不为 0；使用随行预设或单独开关，不叠加分类仅显示。包 / 车内标签可匹配，第二台 iPhone 通常因地址轮换不匹配。步行窗口较紧、驾车较宽（§8.5）。结束后生成总结，即使离开筛选或换视图仍分析最近 15 分钟。'],
                ['刚来了什么设备', '开启仅新检测；房间基线明确后在实时页标签栏上方标记已见，重置已见可重来，提示为仅新检测 · 已隐藏 N 个。'],
            ],
            [1.8 * inch, 4.7 * inch],
        ),
    ]

    # 9 Signatures
    flow += [
        PageBreak(),
        P('9. 命名特征与自定义特征', "h1"),
        P('9.1 什么是特征', "h2"),
        figure_wrap(
            "fig-signatures.png",
            '图 2（再次列出）：特征库。',
            '特征是一组命名匹配规则、颜色及可选聚类条件，不是厂商身份的证明。“内置”只表示来源，仍可编辑或删除。每条规则独立开关，可停用噪声 OUI / 名称而不删除。规则在此编辑，不在设置；命中始终标注，显示可隐藏标签，筛选可隐藏设备。目录默认名称 A-Z；分类 A-Z 以折叠层级方便直接打开公共安全、车辆等。',
            P('9.2 从已观察设备创建', "h2"),
            numbered([
                '在任意实时视图找到设备，点击进入详情。',
                '点击“从设备创建特征”。',
                '建议名称来自广播名、厂商 + OUI，或“BLE / Wi-Fi + MAC 尾部”。',
                '预填完整 MAC 前缀固定本设备；有名称则填名称 / 通配符；最多三个服务 UUID；存在时填厂商 ID 与首字节。只有除 MAC 外无其他信息才加 OUI。不自动加入单独“无线类型 = BLE / Wi-Fi”的 OR 规则，以免匹配整个类型。',
                '地址看似随机时说明字段会提示，宜优先名称 / UUID / 厂商规则，并考虑删除 MAC 规则。',
                '编辑名称，按需设任意匹配、颜色、最少同组数量，然后保存。',
                '已知 BLE 载荷布局时，再打开新项的解码字段映射字节（§9.6）。身份规则与解码映射分别保存。',
            ]),
        ),
        P(
            "先读详情的<b>特征系列</b>（§5.5）。明确 / 可能系列表示已有其他 MAC 共享 ID，但从设备创建仍固定<b>本 MAC</b>；需共享规则用候选特征（§9.2.1）。“仅此设备”才适合以 MAC 为主。<b>已标注仍可再建特征。</b>若解码显示全店共用 iBeacon UUID，可删除 MAC 固定规则，并将厂商前缀扩为类型 0x02、长度 0x15 加 UUID，即 <font face='FWText'>0215</font> + 32 个 UUID 十六进制数字，与 Target Atrius basket 一样。内置 iBeacon 保留，自定义成为第二标签。只用草稿首字节 02 会匹配全部 iBeacon，而非该店。"
        ),
        P('9.2.1 从候选特征创建', "h3"),
        P(
            '多台未匹配设备共享 H2O- 通配符、厂商 IE 或稳定 OUI 时，不应固定一个 MAC。详情系列卡是单设备版分析；“报告 → 候选特征”（§5.6.4、§11.5）起草<b>共享</b>规则并省略 MAC 固定。使用同一编辑器保存为自定义项，即可加系列而非某住宅 BSSID。只分析未匹配设备；已被内置 iBeacon 标注的整层设备不会列入，商店 UUID 的第二标签应按 §9.2 创建。'
        ),
        P('9.3 手动创建与编辑', "h2"),
        P(
            '特征库标题为内置加自定义总数，“+”创建空白项。编辑名称、说明、重点关注、AND / 任意匹配 OR、聚类、颜色和规则列表；各规则关闭后仍保留但不参与。BLE 特征在规则下有<b>解码字段</b>（无或 N 个），参见 §9.6；纯 Wi-Fi 项隐藏该控件。'
        ),
        P(
            '规则类型：OUI、MAC 前缀、名称包含、名称通配符、服务 UUID、厂商 ID、厂商数据、无线类型、隐藏 SSID、厂商 IE OUI。厂商 ID 用十六进制，例如 0x004C。'
        ),
        P(
            'Wi-Fi 的 MAC <b>就是</b> BSSID。完整 12 位十六进制固定单 AP，较短 B4:1E:52 匹配厂商地址块，与 OUI 一样。隐藏 SSID 匹配所有空名称 AP，配合 MAC 前缀 AND 才固定某台。原生 Android 不揭示隐藏的 SSID 文字。'
        ),
        P(
            '没有总匹配开关，规则命中始终标注。隐藏系列用分类隐藏或隐藏所选；显示中的特征名称只隐藏标签及六边形，不移除设备。书签申请该特征提醒，系统通知开启时也可显示静音通知卡。'
        ),
        P(
            '打开特征底部删除并确认。内置也可删，恢复默认特征会重新载入。“设置 → 导出特征”备份整个 JSON 目录；导入只加新项和额外规则，不删除，跳过相同 ID / 规则，重名加“（已导入）”。GitHub 更新替换内置及重点关注，保留书签和设置，需联网。恢复默认值会清自定义，需先导出特征及命名设备 / 开关的设置备份。'
        ),
        P('9.4 可靠的现场做法', "h2"),
        bullets([
            '先严格匹配完整 MAC 或公司 ID + 厂商数据，发现目标轮换地址时再放宽。',
            '不要在 OR 中单独加入 RADIO_KIND。',
            'Silicon Labs / LiteOn OUI 不唯一，配合名称、UUID 或最少同组数量。',
            '优先 0xFDxx / 厂商范围 UUID，而非通用 GAP UUID。',
            '系列可用任意匹配加多个 OUI 与名称通配符；单设备保留 MAC，并在加其他条件时关闭任意匹配。',
            '通用 DIRECT- / ANDROID- / ESP_ 名称保持未匹配，除非同时符合 Raven、Roku、Epson 等产品系列。',
            '噪声方法可关单规则，无需删除，例如旧 Flock 目录中的 LiteOn OUI。',
            '编辑后查看实时页；若半家咖啡馆都变成新名称，说明规则过宽，应立即修正。',
        ]),
        P('9.5 使用内置特征库', "h2"),
        P(
            '首次启动载入内置库，恢复默认特征与预设可重载。所有内置项都参与匹配，规则命中即标注。'
        ),
        P(
            '噪声系列可在筛选中按分类隐藏，或隐藏单特征；匹配、日志、总结和书签数据保留。'
        ),
        P(
            '每条特征有<b>分类</b>，如定位标签、监控、无人机、车辆。仅显示 / 隐藏这些按分类工作；实时标签颜色独立，可编辑。自定义默认“其他”。'
        ),
        P(
            '特征库和显示 / 隐藏所选列表按 A-Z 排序，包含自定义项。'
        ),
        P(
            '内置标签按分类配色，匹配用特征颜色，未匹配按 RSSI：≥-55 绿、-55 至 -70 琥珀、-70 至 -85 橙、其他红。升级可能一次性恢复内置颜色，自定义不变。'
        ),
        table(
            ['筛选分类', '内置特征（节选）'],
            [
                ['定位标签', 'Apple AirTags、Samsung SmartTags、Tile、Chipolo、Pebblebee / moto tag、Google Find Hub、DULT 追踪器'],
                ['零售信标', 'iBeacon、Target Atrius 购物篮、Minew、Estimote、Kontakt.io'],
                ['标牌', '零售 LED 标牌、电子价签'],
                ['穿戴设备', "Garmin, Fitbit, Oura, Pokemon GO Plus, Fieldy, Plaud Note"],
                ['监控', "Flock, Raven, Penguin, Pigvision, FS Ext Battery, Genetec, Rekor, Vigilant, Verkada, Avigilon, Axis, Hikvision, Dahua, Hanwha Wisenet, Uniview, Rhombus, UniFi Protect, BlueTOAD Spectra, BlipTrack"],
                ['无人机', "Remote ID, DJI, Skydio, Autel, Parrot, HOVERAir"],
                ['渗透测试', 'Hak5 Pineapple、Flipper Zero、Pwnagotchi、Marauder / Deauther、GhostESP、Bruce、Porkchop、业余 BLE 串口'],
                ['公共安全', 'Axon、WatchGuard Video、Cradlepoint、AirLink、Compex、Novatel Wireless、Utility Inc；用于执法但非专用，政府、市政及企业车队也可能使用相同装备。'],
                ['车辆', 'Tesla、Tesla tsTPMS、Rivian、Ford、Honda、Hyundai、Toyota、Nissan、Subaru、BMW、Volkswagen、Porsche、Jaguar Land Rover、BYD、Chevrolet / GM 热点、Audi MMI、Mercedes MBUX、Uconnect、CarPlay、CARLINK、Motive、PeopleNet、Samsara、AUMOVIO、Winegard，以及 Goodyear、Schrader、Pacific、Huf、FOBO、后装 TPMS、SYTPMS、TireCheck、TPMS 服务'],
                ['眼镜', 'Ray-Ban / Meta 眼镜、Snap Spectacles、Vuzix'],
                ['音频', 'Apple 音频、Sony、Bose、JBL / Harman、Sonos、Shokz'],
                ['摄像头', "Wyze, Ring, Arlo, eufy Security, Nest, Tapo, Reolink, GoPro, Osmo, Insta360"],
                ['温控器', "Nest Thermostat, ecobee, Sensi, Honeywell Home"],
                ['门禁', "August, Schlage, Nuki, Lockly, Kevo, Master Lock, igloohome, Tedee, Kwikset, ASSA ABLOY, SALTO, dormakaba, Paxton"],
                ['健康', "Honeywell Xenon HC, Omron, Withings, Dexcom"],
                ['家庭物联网', 'Nest Weave、Tuya、Govee、Haiku Fan、myQ、Hatch、Orbit B-hyve、Samsung 家电、EcoWater、Amazon、Logitech、HP、Epson、LG webOS TV、Roku、Nespresso、RadiaCode、Ruuvi、Blue Maestro、SensorPush、SnapAV'],
                ['ISP / 路由器', "UniFi, UniFi AP, Meraki, Cisco, Aruba, Ruckus, Ruijie, Fortinet, Mist, Sophos, Extreme, Edgecore, WatchGuard AP, Mojo, NETGEAR, TP-Link, ASUS, Linksys, Eero, Google Wifi, Huawei, Plume, D-Link, DWnet, Belkin, Xfinity, Spectrum, AT&amp;T, Verizon, Starlink, GL.iNet, MikroTik, EnGenius, Zyxel, Peplink, OpenWrt, Arris, T-Mobile, HUMAX, Sagemcom, Arcadyan, Askey, Calix, Nokia, AirTies, Tenda, WAVLINK, Sercomm, Luxul, CenturyLink, Adtran, Cambium, TRENDnet, Cudy, Vantiva, Hitron, Actiontec, Buffalo, Grandstream, Inseego, Franklin, Synology"],
                ["Mesh", "Meshtastic, MeshCore, Helium, goTenna, SenseCAP, RAK WisGate"],
                ['手机 / 电脑', 'Apple 设备、Fast Pair、Google、Microsoft 设备、手机热点'],
                ['其他', "—"],
            ],
            [1.7 * inch, 4.8 * inch],
        ),
        Spacer(1, 6),
        table(
            ['颜色', '分类', '内置特征'],
            [
                ['红色', '渗透测试 / 廉价串口', 'Hak5 Pineapple、Flipper Zero、Pwnagotchi、Marauder / Deauther、GhostESP、Bruce、Porkchop、业余 BLE 串口'],
                ['琥珀色', '监控与无人机（同色，以分类区分）', "Flock, Raven, Penguin, Pigvision, FS Ext Battery, Genetec, Rekor, Vigilant, Verkada, Avigilon, Axis, Hikvision, Dahua, Hanwha Wisenet, Uniview, Rhombus, UniFi Protect, BlueTOAD Spectra, BlipTrack, Remote ID, DJI, Skydio, Autel, Parrot, HOVERAir"],
                ['紫色', '手机 / Find My 标签', 'Apple 设备、Apple AirTags、Chipolo、Google Find Hub、DULT 追踪器、Fast Pair、Google（Pixel / 0x00E0）、手机热点'],
                ['青色', '穿戴追踪器', 'Samsung SmartTags、Tile、Pebblebee / moto tag、Garmin、Fitbit、Oura、Pokemon GO Plus、Fieldy、Plaud Note、iBeacon、Target Atrius 购物篮、Minew、Estimote、Kontakt.io'],
                ['绿色', "Mesh / LoRa", "Meshtastic, MeshCore, Helium, goTenna, SenseCAP, RAK WisGate"],
                ['橙色', '眼镜与音频（同色，以分类区分）', 'Ray-Ban / Meta 眼镜、Snap Spectacles、Apple 音频、Sony、Bose、JBL / Harman、Sonos、Shokz'],
                ['蓝绿色', '公共安全与车辆（同色，以分类区分）', 'Axon、WatchGuard Video、Cradlepoint、AirLink、Compex、Novatel Wireless、Utility Inc、Tesla、Tesla tsTPMS、Rivian、Ford、Honda、Hyundai、Toyota、Nissan、Subaru、BMW、Volkswagen、Porsche、Jaguar Land Rover、BYD、Chevrolet 热点、Mercedes MBUX、Uconnect、CarPlay、CARLINK、Motive、Samsara、Winegard、Goodyear / Schrader / Pacific / Huf / FOBO / 后装 / SYTPMS / TireCheck / TPMS 服务'],
                ['蓝色', '健康', "Honeywell Xenon HC, Omron, Withings, Dexcom"],
                ['银色', '摄像头 / 电脑 / 家庭物联网 / 家庭 Wi-Fi / 零售标牌 / 门禁', 'GoPro、Osmo、Insta360、eufy、Wyze、Ring、Arlo、Nest、Tapo、Reolink、Microsoft 设备、Amazon、Starlink、Logitech、HP、Epson、LG webOS TV、Nespresso、RadiaCode、Nest Thermostat、Nest Weave、ecobee、Sensi、Honeywell Home、Tuya、Govee、Haiku Fan、myQ、Hatch、Orbit B-hyve、August、Schlage、Nuki、Lockly、Kevo、Master Lock、igloohome、Tedee、Kwikset、ASSA ABLOY、SALTO、dormakaba、Paxton、Ruuvi、Blue Maestro、SensorPush、SnapAV、零售 LED 标牌、电子价签，以及 UniFi / Meraki / Cisco / Aruba / Ruckus / Fortinet / Mist / Sophos / Extreme / Edgecore / WatchGuard AP / Mojo / NETGEAR / TP-Link / ASUS / Linksys / Eero / Google Wifi / D-Link / Belkin / Xfinity / Spectrum / AT&amp;T / Verizon / GL.iNet / MikroTik / EnGenius / Zyxel / Peplink / OpenWrt / Arris'],
            ],
            [0.95 * inch, 1.7 * inch, 3.85 * inch],
        ),
        Spacer(1, 6),
        P(
            '特征的<b>说明</b>在匹配设备详情和分享 / AI 中显示产品背景，不是公司 ID / UUID 等规则，后者在身份 / 厂商数据。说明不会加实时“!”，也不是琥珀重点关注。<b>重点关注</b>是独立字段，多数为空；填入后匹配设备才有“!”、详情琥珀卡和总结 / AI 中的说明。'
        ),
        P(
            '内置重点关注包括业余 BLE 串口、Axon、WatchGuard Video、Digital Ally、Reveal Media、Wolfcom、Ray-Ban / Meta、Snap、Brilliant Frame、Even G1、Fieldy、Plaud Note、Limitless Pendant、Bee Pendant、Omi、Friend Pendant、Hak5 Pineapple、Flipper Zero、Pwnagotchi、Marauder / Deauther、GhostESP、Bruce、Porkchop、Cradlepoint、AirLink、Compex、Novatel Wireless、Utility Inc，以及 Flock Safety Cameras、Penguin、Pigvision、FS Ext Battery、Genetec AutoVu、Rekor、Motorola Vigilant、Verkada、Avigilon、Axis、Hikvision、Dahua、Hanwha Wisenet、Uniview、Rhombus、Panasonic i-PRO、Hayden AI、Miovision、Tattile、LVT LiveView。默认加书签，新命中会提示；覆盖执法记录仪、摄录眼镜、录音穿戴、渗透测试、公共安全车载 AP 和公共摄像 / 车牌设备，不含 Tesla、耳机、UniFi Protect、BlueTOAD、BlipTrack 或门禁锁。旧目录模块 OUI 可很吵，不需声音可取消书签。公共安全非执法专属，其他车队也使用相同装备。'
        ),
        P(
            '“!”只是模式，不证明身份、正在录制或攻击。Meta 公司 ID 也可能是 Quest；Fieldy / Plaud Note 是对话记录器，但不证明有人录您；PineAP 克隆可能看似普通 SSID。任何内置或自定义特征均可自行填写重点关注。'
        ),
        P(
            '<b>家庭与 ISP Wi-Fi：</b>NETGEAR、TP-Link、Xfinity、Starlink 等仅匹配 Wi-Fi，多数也按 IEEE OUI 匹配 BSSID，改 SSID 后仍有效。访客 / Mesh / 多 SSID 的本地管理虚拟 BSSID，若还原出的通用 OUI 在库中也可命中；不还原 Apple / Google / Samsung 前缀，避免把随机手机热点认成路由器。厂商 IE 仍可命中，噪声多可按系列隐藏。'
        ),
        P(
            '<b>Spectrum</b>也匹配 Spectrum Mobile / Spectrum Free Trial 热点，无 Charter OUI（硬件来自 OEM）。<b>Chevrolet hotspot</b> 的 myChevrolet*、<b>Mercedes MBUX</b> 的 MBUX*、<b>Motive</b> 的 Motive * / Motive_* 是车载 / 车队出厂名，不是经销商或咖啡馆名称。'
        ),
        P(
            '<b>UniFi AP</b>使用出厂 SSID 和 Ubiquiti OUI，属 ISP / 路由器；airMAX、AmpliFi、UISP 广播 AP 也可命中。另一个 <b>UniFi</b> 项匹配两种无线的 UniFi / Ubiquiti / UAP-* 名称。<b>UniFi Protect</b> 匹配设置中的 UVC G3/G4/G6 Instant BLE 名称，不匹配 AP BSSID，仍属监控。'
        ),
        P(
            '<b>Meraki</b>为 Meraki* 与 Cisco Meraki OUI，不是 Cisco Systems；<b>Cisco</b>为 Wi-Fi Cisco*（Aironet / Catalyst / Business / RV）、旧 Aironet tsunami 和 Cisco Systems OUI，不用 Cisco 子串以免命中 San Francisco。Wi-Fi 只看 AP，Cisco BSSID 也指 AP。Meraki 和 Cisco-Linksys 独立维护 OUI，均属 ISP / 路由器。Meraki 常带 Cisco 00:00:0C CCX / AP-name IE，此时仅保留 Meraki。'
        ),
        P(
            '<b>Aruba</b>为 Aruba* / SetMeUp* / InstantOn*，不匹配单独 instant 或 HPE OUI；<b>Ruckus</b>为 Ruckus* / Configure.Me* 与厂商 OUI；<b>Fortinet</b>为 Fortinet* / FortiAP* / FAP-config* 与 OUI。它们和 UniFi AP、Meraki、Cisco、Mist、Sophos、Extreme、Edgecore、WatchGuard AP、Mojo 都属校园 / 园区 AP 类 ISP / 路由器，不是摄像头。'
        ),
        P(
            '<b>MikroTik</b>使用 Routerboard.com OUI，EnGenius、Zyxel、Peplink / Pepwave 也用厂商 OUI。OpenWrt / GL.iNet 早期主要名称匹配，GL.iNet 板卡常用模块前缀，具体当前规则见附录。Arris / SURFboard 用 Arris OUI，不用混合 CommScope 地址块。Google Wifi 不表示 Pixel BLE、Nest-* 摄像头，也不用 Google Inc 手机 / 热点 OUI。'
        ),
        P(
            '品牌 BLE 包括 Tesla、Rivian、Google、Sony、Bose、Garmin、Amazon、Fitbit、Oura、Logitech、HP、Epson、JBL / Harman、Sonos、Shokz、GoPro、Osmo、Insta360、DJI、Microsoft / Apple 设备、Apple 音频、Fast Pair、Tuya、Govee、Haiku Fan、myQ、LG webOS TV、Nespresso、RadiaCode，确切 ID 见附录 B。Google 指 0x00E0 / Pixel / Chromecast，Fast Pair 单列。Apple Device 匹配 Continuity 而非 0x07 AirPods；iPhone 也发 Find My 0x12，同设备有 Continuity 时移除 AirTags 标签。Bose 含 FEBE、FE21、0x009E；Tuya 为 0x07D0 / FD50 / TUYA*，非 TY。Govee 身份仅名称，随后可解 H5074/5075（0xEC88）和 H510x/517x（0x0001）温湿度电量（§9.6）。Shokz 用 OpenRun / OpenFit 名称，非 Battery 0x180F。DJI 用 0x08AA / DJI*；Osmo Action / Pocket / 360 / Nano 为独立 Osmo 项（0x0006-0x0022 型号及 OsmoAction*），非 DJI。Insta360 为 Arashi Vision 0x10D7 与 X3 / Ace Pro / GO 3 名称。飞行无人机也可命中 BLE FFFA / Wi-Fi FA:0B:BC 的 Remote ID。Skydio、Autel、Parrot ANAFI-Bebop、HOVERAir 用名称，不用 Autel default-ssid 或 Parrot 0x0043。'
        ),
        P(
            '<b>Fast Pair 不等于 Android。</b>它是 Google 轻触配对 UUID FE2C，单列手机 / 电脑。iPhone 经常发 Continuity，许多口袋 Android 几乎不发可命名广播，仍是无名 BLE。Google 仅 Pixel / Chromecast；手机热点仅在广播出厂 SSID 时匹配。Fast Pair 的<b>配对模式</b>载荷三字节型号 ID，会让附近 Android 提供配对卡，常见 Pixel Buds / Galaxy Buds 等，较少见而值得看；实时显示 Fast Pair 配对及配对副标，之后即使发长载荷，该会话仍保留配对标记。<b>长载荷</b>是已加入账号设备的账号密钥过滤器，商场 / 车站中常见，通常是环境杂波而非新配对。“隐藏 Fast Pair 账号密钥”只在唯一匹配时隐藏它，还匹配 Google 的 Pixel 保留；隐藏整个 Fast Pair 或手机类则连配对模式一起隐藏。'
        ),
        P(
            '<b>公共安全与车辆：</b>公共安全为 Axon / WatchGuard Video 及 Cradlepoint、AirLink、Compex、Novatel、Utility Inc 车载 AP，执法常用但政府、市政和企业亦用，不能据此识别机构或警员。车辆包括 Tesla（Cybertruck 钥匙名 S…C）、Rivian、Ford 0x0723、Honda 0x0915、Hyundai 0x0826、Toyota 0x0977、Nissan 0x0BA6、Subaru 0x0A10、BMW 0x05EB、Volkswagen 0x011F / FE30/FE31、Porsche 0x0120、Jaguar Land Rover 0x020B、BYD 0x0C34、Chevrolet / GM 热点、Mercedes 0x017C / MBUX*、Audi 0x010E / MMI、Motive、Samsara，及 BLE 胎压：Goodyear 0x0B99、Schrader 0x0601、Pacific 0x0E32、Huf 0x070A、FOBO / Salutica 0x0127 / 00EE、TireCheck 0x0BA2、SYTPMS 的 BR / 0x27A5、后装 TPMS* / FBB0 / 0x0001 的 80-83 数据、服务 0x1860。Tesla tsTPMS 仅按名称，0x022B 留在 Tesla，0x1122 不唯一。原厂 315/433 MHz 胎压不可见，不匹配裸 Nokia 0x0001。库中 Kia / Volvo / Lucid / Polestar 无唯一 SIG ID；许多车不广播公司 ID，Classic 也不可见，漏检常见。'
        ),
        P(
            '<b>无人机与监控：</b>无人机为 Remote ID、DJI、Skydio、Autel、Parrot、HOVERAir；Osmo / Insta360 属摄像头。监控为杆体、ALPR 和商用读写器，不是飞行器或园区 AP。两类都琥珀色，以分类区分。'
        ),
        P(
            '<b>眼镜、音频与摄像头：</b>眼镜为 Ray-Ban / Meta、Snap；音频为 Apple、Sony、Bose、JBL / Harman、Sonos、Shokz；摄像头为 Wyze、Ring、Arlo、eufy、Nest、Tapo、Reolink、GoPro、Osmo、Insta360。Flock / UniFi Protect 属监控，Axon 属公共安全。'
        ),
        P(
            '<b>标牌与零售信标：</b>标牌为 LED 信息屏与 BLE ESL 0x1857，广播名可能就是标牌文字而非产品名。零售信标为 iBeacon、Target Atrius 购物篮、Minew、Estimote、Kontakt.io。iBeacon 是任意厂商可发的 Apple 0x004C、0x02/0x15；Target 为 5993A94C-… UUID 和 0xB1BB 服务，不是 Acuity 0x0346；Minew 用 OUI AC:23:3F，Estimote 0x015D，Kontakt.io 0x01FD。不用被 JBL、打印机等广泛共享的 Eddystone FEAA。'
        ),
        P(
            '<b>环境传感器（家庭物联网）：</b>Ruuvi 0x0499、Blue Maestro 0x0133、SensorPush 自定义 UUID。前两者自带广播温度 / 湿度 / 气压解码，SensorPush 只识别身份模式。'
        ),
        P(
            '<b>智能锁 / 门禁：</b>ASSA ABLOY（0x012E / HID 0x0124 / Yale 0x0BDE / FCBF / Seos / Yale*，不是 FCB2）、August（0x01D1 / FE24）、Schlage / Allegion（0x013B / FCF4）、Nuki（a92ee*）、SALTO 0x0199、dormakaba 0x0C64、Paxton 0x0196、Lockly 名称、Kevo / Unikey 0x015E、Master Lock 0x014B、igloohome 0x05BA、Tedee 0x0725、Kwikset 名称。属银色门禁，不是监控。'
        ),
        P(
            '<b>智能温控器：</b>ecobee 0x07D6；Nest Thermostat 的 Nest Labs 0x01B5，不是 Nest 摄像头；Sensi 仅名称，不用 Emerson 0x04DF；Honeywell Home / Lyric / Amazon Smart Thermostat 名称，不用 Honeywell 0x0526 或 Resideo 0x0B01。多数墙面设备设置后转 Wi-Fi，不持续 BLE，漏检正常。'
        ),
        P(
            '<b>健康、穿戴与家庭物联网：</b>健康为医疗 BLE，如 Honeywell Xenon 医疗扫码器 Xenon_*HC* / CCB-U00-H*，非仓库 CCB-U00-G；Omron Healthcare 0x020E 血压计 / 秤，非工业 OMRON 0x02D5；Withings 秤 / BPM Connect、Dexcom G6/G7。Garmin / Fitbit / Oura 属穿戴，Honeywell Home 属温控器。匹配不表示患者身份或具体医院。'
        ),
        P(
            '当地误报时，在筛选隐藏系列或关闭噪声规则，例如旧目录 Espressif 3C:71:BF 引发的 Flock 误报。恢复默认值会重建特征及解码、默认书签和设置：常亮、GPS、在线地名、分类 + 特征语音开启，TAK 关闭；并清自定义特征、预设和命名设备。需要保留时先导出特征与设置，不要把恢复默认值当单条规则撤销。'
        ),
        P(
            '只需停用 Flock 的噪声方法，如旧库 LiteOn OUI，可打开特征关闭对应规则，不必删整项。参见 §7.6、§7.6.1。'
        ),
        P('精确默认规则见附录 B。'),
        P('9.6 解码字段', "h2"),
        figure_wrap(
            "fig-decode-editor-row.png",
            '图 18：特征编辑器（Ruuvi）。',
            '特征命中后，可将广播中的<b>明文字节</b>映射为温度、型号、Remote ID 位置等。Remote ID 的 BLE FFFA 和封装为 FFFA 的 Wi-Fi FA:0B:BC 共用映射，自定义编辑器仍面向 BLE 厂商 / 服务数据（§5.8.3）。身份匹配由规则完成，解码不参与匹配，列表绘制不重新解析载荷。标签内同色六边形表示该特征有映射，多标签只标对应名称。关闭特征名称会隐藏名称和六边形；启用<b>实时条目</b>的当前词仍显示（§5.4.1）。其他值位于设备详情、文本分享、单设备 AI 导出及总结的值得关注 BLE 部分。',
        ),
        figure_wrap(
            "fig-decode-fields.png",
            '图 19：解码字段。',
            '只处理 BLE 广播，不配对、不连接 GATT、不解密。加密或未知内容仍以十六进制显示。Apple Continuity、Fast Pair、Eddystone 和 Microsoft 留在内置已知载荷 / 厂商数据；此功能补充其未覆盖的内置或自定义项。纯 Wi-Fi 特征隐藏编辑控件。'
        ),
        P(
            '先要有能匹配设备的特征，再根据厂商规范、逆向说明或详情字节中已理解的布局建立映射。不会把每个值都显示在列表；只为需要放在名称旁的字段开<b>实时条目</b>。六边形仅表示有映射。设备未匹配时先创建并保存特征（§9.2 / §9.3），再打开解码字段。'
        ),
        P('9.6.1 从已知载荷布局开始', "h3"),
        P(
            '例：实时页已有 BLE，详情有厂商 / 服务数据，您知道字节 0 为格式、1-2 为温度等。Fieldwatch 不会猜出布局，需要手动输入。'
        ),
        numbered([
            '先确认身份，在详情匹配特征中选择承载映射的项；没有则从设备创建（§9.2），保留 MAC 轮换后仍有效的厂商 ID / UUID / 名称并保存。仅 MAC 规则不适合系列映射。',
            '在详情读取将切片的十六进制。厂商数据的原始载荷是蓝牙公司 ID <b>之后</b>的字节，服务 FEAF 等是 UUID 之后的字节。每两个十六进制字符一字节，第一对偏移 0，下一对 1；不要把公司 ID 或 UUID 算入偏移。',
            '“特征库 → 目标项 → <b>解码字段</b>”（添加规则下），按读取的数据选厂商或服务。厂商应填公司 ID，如 0x0499、0xEC88，除非每台匹配设备只有一条厂商记录。服务填 FFFA、FE6A、FEAF、FEED 或完整 128 位 UUID。',
            '为所需值添加字段，标签决定详情名称，设置类型、偏移、长度、字节序和单位。新字段起点默认为上一字段偏移 + 长度。解码栏保存才写映射，未保存返回会丢弃。',
            '当前有匹配设备时看底部预览，再打开详情确认值符合规范。有原始字节却无解码，常因把公司 ID 算入偏移 0、选错数据源，或当前包未满足条件。',
        ]),
        P(
            "Ruuvi 格式 5 示例：数据源厂商、公司 0x0499。格式字段 u8、偏移 0、长度 1；温度 i16、偏移 1、长度 2、BE、比例 0.005、单位 °C，条件为偏移 0 长度 1 等于 <font face='FWText'>05</font>。湿度 u16 BE、偏移 3、比例 0.0025、单位 %，条件相同。格式 3 首字节 03 因此跳过，避免错解。内置 Ruuvi 已有映射，可借鉴创建库外传感器。"
        ),
        P('9.6.2 来源：厂商数据与服务数据', "h3"),
        P(
            '<b>厂商数据</b>读取 AD 0xFF，运行映射前去掉两字节公司 ID，所以字节 0 是 0x004C / 0x0499 / 0xEC88 等之后的首字节，与详情原始载荷一致。此页公司 ID 用于从该设备多条厂商记录中选取，空则首条。Govee 灯与温湿度计都可名称匹配，但温湿度映射只读 0xEC88（H5074/5075）和 0x0001（H510x）；灯没有合适载荷便不解码。'
        ),
        P(
            '<b>服务数据</b>读取指定 UUID 的块，字节 0 是该服务数据首字节，不是整条广播。UUID 必填，可 16 位 FEAA / FFFA 或带连字符 128 位；同设备多个块只解析指定那个。'
        ),
        P(
            '每条特征只有一个数据源。产品将传感器放厂商数据、序列号放服务数据时，选择所需部分或另建第二特征形成双标签，不能一个映射同时指向两类。'
        ),
        P('9.6.3 字段卡片', "h3"),
        P(
            '每张卡一个值。偏移越界、条件失败或 UTF-8 为空时，静默跳过该字段，其他照常，从而一个映射可兼容两种包格式。'
        ),
        table(
            ['控件', '效果'],
            [
                ['标签', '详情、总结、预览中的文字；在更多中自设 ID 前，改标签会同步生成 ID。'],
                ['类型', '切片的读取方式，见下表，选择后填默认长度。'],
                ['偏移', '源载荷的起始字节，0 表示公司 ID 后首字节或服务数据首字节。'],
                ['长度', '字节数，默认 u8=1、u16/i16=2、u24=3、u32/i32/f32=4、mac=6；utf8 / hex / bits 初始 1，需自行调整。'],
                ['单位', '追加在数字后，如 °C、%、hPa、mV、dBm；空则只显示数字。'],
                ['字节序', 'LE（默认，小端）或 BE（大端）；u8 / i8 / utf8 / hex / bool 隐藏此项，适用于整数、浮点和位域。'],
                ['位偏移 / 位宽', '仅 bits。按字节序先读无符号整数，再从最低有效位偏移，宽度 1-32。'],
                ['比例 / 加值', '仅数值类型。读取后先取模（若设），再乘比例，再加偏移值。温度常用 0.01 / 0.005；以（hPa - 500）×100 存储的气压用比例 0.01、加值 500。'],
                ['仅当……', '条件满足才显示该字段（§9.6.4）。'],
                ['命名值……', '将原始数值或十六进制映射为词语（§9.6.4）。'],
                ['更多', 'ID 为稳定键，除导出映射或 TAK 位置外可保留自动值。TAK 按 ID 而非标签读 latitude + longitude，可选 alt_geo；op_lat / op_lon 是飞手，不是飞机（§5.8.4）。取模在比例前计算，Govee 打包湿度用 modulo 1000。'],
            ],
            [1.45 * inch, 5.05 * inch],
        ),
        Spacer(1, 6),
        table(
            ['类型', '默认字节数', '结果'],
            [
                ["u8 / i8", "1", '无符号 0-255 或有符号 -128 至 127，无字节序。'],
                ["u16 / i16", "2", '16 位整数，Ruuvi / Blue Maestro 等规范要求大端时选 BE。'],
                ["u24", "3", '无符号 24 位，Govee H5075 将温度装入大端 24 位整数。'],
                ["u32 / i32", "4", '32 位整数，Remote ID 经纬度用 i32 LE × 1e-7 度。'],
                ["f32", "4", 'IEEE-754 浮点，广播中较少见。'],
                ["bits", '按位偏移 + 位宽决定', '切片内无符号位域，可将 0/1 映射为休眠 / 唤醒等命名值。'],
                ["bool", "1", '任意非零字节为是，全零为否。'],
                ["utf8", '自行设置', '文本，去除尾部 NUL 与空格，用于 Remote ID UAS ID / Self ID。'],
                ["hex", '自行设置', '以空格分隔的十六进制，例如 Tile 轮换私有 ID。'],
                ["mac", "6", '前六字节格式化为 AA:BB:CC:DD:EE:FF，例如 Ruuvi 载荷 MAC。'],
            ],
            [1.45 * inch, 1.2 * inch, 3.85 * inch],
        ),
        Spacer(1, 6),
        P(
            '计算顺序固定：读整数 / 浮点 → 取模 → 乘比例 → 加值，空设置跳过。命名值针对<b>原始</b>整数或 UTF-8 / hex 字符串，不针对缩放结果，例如把 65 映射为 HERO13 Black，而非对 0.005 乘积命名。'
        ),
        P('9.6.4 条件与命名值', "h3"),
        P(
            '<b>仅当</b>让一个特征处理多种布局，每字段独立条件，不满足只省略本字段，其余继续。'
        ),
        bullets([
            '<b>等于：</b>指定偏移 / 长度字节必须匹配 Hex。Ruuvi 格式 5 为偏移 0、长度 1、05。Remote ID 消息类型半字节与协议合并，Location（类型 1、协议 0-2）头为 10 / 11 / 12，OpenDroneID 在 BLE / Wi-Fi 读取同版本。',
            '<b>不等于：</b>字节等于 Hex 时跳过，适合无效 / 保留值。',
            '<b>掩码：</b>Hex 中每个 1 位在载荷中都须置位，即 payload AND Hex = Hex，适合只关心某标志开启。',
            '<b>各位均未置位：</b>Hex 中的 1 位在载荷均须清零，即 payload AND Hex = 0；Remote ID 东向与低档水平速度用此检查。',
            '<b>载荷长度：</b>条件选长度后，整个源载荷须恰好为指定字节数，忽略偏移和 Hex。Govee H5074 为 7 字节，H5075 为 5 或 6；公司 ID 相同但布局不同。',
        ]),
        P(
            "Hex 为原始字节，不加 0x，不要求空格，如 <font face='FWText'>05</font>、<font face='FWText'>0215</font>。Hex 字节数须与条件长度一致，否则字段永不显示。"
        ),
        P(
            '<b>命名值</b>是“原始值 → 显示为”表。整数可填十进制 65 或十六进制 0x41，文本类型填 UTF-8 / hex 字符串。未列值仍显示原数或缩放数。GoPro、Osmo、Nest Weave、Remote ID 类型自带映射；添加值逐个录入，移除清空表。'
        ),
        P(
            '启用<b>实时条目</b>后，各命名值可设<b>突出</b>并附<b>说明</b>；突出使用更醒目的列表标签，说明作为一句话进入详情和总结。DULT / Find Hub 的分离突出，靠近主人 / 附近低调且各有说明。Remote ID 的紧急突出，同时显示未声明、地面、空中、RID 故障。'
        ),
        P('9.6.5 预览、详情与报告', "h3"),
        bullets([
            '底部<b>预览</b>使用当前正在广播且已匹配本特征的设备，显示源字节及解析行。没匹配设备也能保存；匹配但 hex 空通常选错源或此包无厂商 / 服务数据；解析空常是偏移、长度、条件错误，尤其误将公司 ID 算偏移 0。',
            '<b>详情 → 解码字段</b>对当前广播执行相同解析。多个匹配特征有映射时，每行加特征名前缀。有映射但无结果会提示，例如 Govee 灯常只发名称，原始 hex 仍保留。',
            '实时页用六边形表示有映射，实时条目字段在名称旁显示当前词（§5.4.1）；雷达不画词或六边形。TAK（§5.8）读 latitude / longitude / alt_geo 发布位置，与列表标签独立。',
            '详情的<b>分享为文本 / AI 导出</b>包含解码字段；观测总结在值得关注 BLE 下列“标签：值”。',
            '解码页保存将映射写回内置 / 自定义特征，直接返回会丢弃。<b>移除解码映射</b>经确认清全部，字段清空后保存也存为无。特征导入导出包含映射；恢复默认值重载内置映射并清自定义，应先导出。',
        ]),
        P('9.6.6 内置映射', "h3"),
        P(
            '以下项目自带映射，目录升级会补入原先没有映射的内置项，都可编辑或清除。Fitbit、Find My 等需连接或加密的广播仅做身份模式识别，旧 Fitbit 广播也不包含步数。'
        ),
        table(
            ['特征', '数据源', '详情可显示内容'],
            [
                ["Ruuvi", '厂商 0x0499', '格式 5：温度、湿度、气压、加速度、电量、TX、运动、序号、载荷 MAC；格式 3：湿度、气压、加速度、电量。格式 3 温度是符号幅值，不是普通有符号整数。'],
                ["Remote ID", 'BLE FFFA 与 Wi-Fi FA:0B:BC', '共用映射，含 OpenDroneID 应用码、计数器、消息类型；协议 0-2 的 Basic ID、位置 latitude / longitude / alt_geo / heading / hspeed。方向 0-179 加 flags 位 1 置位时的 180，不是 ×2；速度 ×0.25，flags 位 0 SpeedMult 置位时 ×0.75 + 63.75。含 Self ID、System 飞手 op_lat / op_lon。Wi-Fi 包封装 FFFA。当前存 Location 时实时显示未声明、地面、空中、紧急、RID 故障，紧急突出。TAK 读取坐标及 course/speed，不是尾号，参见 §5.4.1。'],
                ["Blue Maestro", '厂商 0x0133', 'Tempo Disc 电量、记录间隔、存储日志数、温度、湿度。'],
                ["GoPro", '厂商 0xF202', '数据格式、处理器唤醒 / 休眠、Wi-Fi AP、配对、型号、媒体卸载。'],
                ["Osmo / DJI", '厂商 0x08AA', '型号 ID：Osmo Action / Pocket / 360 和部分飞行器。Osmo、DJI 共享解码，身份规则仍区分摄像头与无人机。'],
                ["Govee", '厂商 0xEC88 / 0x0001', '名称命中后解析 H5074 / H5075 / H510x 温度、湿度和电量。Govee 灯可能不符合这些布局，则不解码。'],
                ["Kontakt.io", '服务 FE6A', '位置包：电量、TX、信道、运动状态。'],
                ["Estimote", '厂商 0x015D', '帧类型 Nearable / Telemetry，不展开打包传感器字节。'],
                ["Nest Weave", '服务 FEAF', 'Weave 身份块：厂商 Nest Labs / Yale，枚举命中时显示 Protect / 温控器 / 摄像头 / Guard / Detect、配对、64 位 Weave ID。两字节 FEAF 载荷仅为产品 ID。'],
                ["Tuya", '厂商 0x07D0', '绑定标志与协议版本，UUID 字节仍加密。'],
                ["Tile", '服务 FEED', '8 字节十六进制轮换私有 ID，不是序列号或稳定身份。'],
                ['DULT 追踪器', '服务 FCB2', 'IETF DULT 定位广播：网络 ID 及下一字节最低位的靠近主人 / 分离。模式显示实时标签，分离突出、靠近主人低调。Chipolo / Pebblebee / moto 可双标签。只有 UUID 列表、无服务数据不匹配。参见 §5.4.1。'],
                ["Google Find Hub", '服务 FEAA', '40 帧附近、41 帧分离，实时显示模式。分离突出且可能约一天保持 MAC，附近低调；不是 Eddystone UID/URL/TLM。参见 §5.4.1。'],
                ["Penguin", '厂商 0x09C8', 'XUNTONG 数据：载荷 MAC、TN 开头 ASCII 序列号，如 TN72023022000771。新电池常广播十位数字名称而非 Penguin-。'],
                ['后装 TPMS', '厂商 0x0001', '匹配 TPMS* / FBB0 / 80-83 数据后的气门帽套件：轮位、kPa 胎压、温度、电量、警报；裸 Nokia 0x0001 不命中。'],
                ["SYTPMS", '厂商数据（7 字节 BR）', '自行车 / 滑板车 BR：表压 psi、温度、电池电压、警报 / 转动 / 静止。'],
                ["Tesla tsTPMS", '厂商 0x022B', '唤醒广播解析 psi、°F、mV，休眠包跳过；身份仍按 tsTPMS* 名称。'],
            ],
            [1.35 * inch, 1.35 * inch, 3.8 * inch],
        ),
        Spacer(1, 6),
        callout(
            '解码值仍是模式信息',
            '温度、型号或 Remote ID 位置只是该广播所含内容，不证明序列号、所有者或无人机在头顶。分离、空中、紧急也一样。固件不同、短扫描响应或加密内容都会使映射不适用，原始字节仍在。',
            "note",
        ),
        P('9.6.7 可靠做法', "h3"),
        bullets([
            '先收紧身份规则再解码；若同时命中灯、电视或全部 0x004C，映射常为空或错误。',
            '按详情原始载荷计算偏移，不用仍含公司 ID / UUID / AD 长度的 USB 嗅探原始数据。',
            '优先填写公司 ID；空值取首条，Apple + 厂商等多公司广播可能读错块。',
            '多格式系列应按格式字节或长度设条件，不要无条件叠加两个温度字段，否则可能同时显示或都不显示。',
            '规范大端时选 BE；默认 LE 对 Ruuvi、Blue Maestro、Govee H5075 打包值不正确。',
            '命名值用于枚举 / 标志，不代替比例；0.01 比例不应写成名为 °C 的映射值。',
            '不要期望 GATT。连接后才有的步数、锁状态等，Fieldwatch 无法接收。',
            '创建前先打开 Ruuvi、Remote ID、Govee 等内置字段卡参考，编辑器显示实际映射规范。',
            '要让 TAK 标广播坐标，ID 用 latitude、longitude 并按规范缩放，标签可任意；op_lat / op_lon 是飞手，不是飞机。参见 §5.8.4。',
            '保存后打开实时设备核对；一半字段缺失可能是不同格式或短扫描响应，应添加条件或接受该包较短。',
        ]),
    ]

    # 10 Alerts
    flow += [
        PageBreak(),
        P('10. 提醒与灵敏度', "h1"),
        P('10.1 关注列表', "h2"),
        P(
            '关注目标可为类型 + MAC 或特征 ID。本会话首次出现时提醒一次，只有消失后再回来才再次提醒，持续停留不重复。仅新检测开启时，只有该行实际会出现在实时页才提醒；被隐藏的既有设备及学习窗口内 Wi-Fi 不提醒。'
        ),
        bullets([
            '设备关注：详情书签预填广播名或类型推测；设置的命名设备可改名、备注、开关提醒、删除或清空。特征系列不在该列表，轮换后的旧 BLE 地址保留到手动删除。',
            '特征关注：书签在新匹配出现时提醒。首次 / 恢复默认关注重点关注系列，包括 Axon、WatchGuard Video、Ray-Ban / Meta、Snap、Fieldy、Plaud Note、业余 BLE 串口、Hak5 Pineapple、Flipper Zero、Pwnagotchi、Marauder / Deauther、GhostESP、Bruce、Porkchop、Cradlepoint、AirLink、Compex、Novatel Wireless、Utility Inc，以及 Flock、Penguin、Pigvision、FS Ext Battery、Genetec AutoVu、Rekor、Motorola Vigilant、Verkada、Avigilon、Axis、Hikvision、Dahua、Hanwha Wisenet、Uniview、Rhombus；另含全部内置无人机 DJI、Remote ID、Skydio、Autel、Parrot、HOVERAir。',
            '总开关为设置中的关注提醒，关闭后无提示音、语音、振动、闪烁或跳转。音与语音独立，跳转配任一种均可。系统通知默认关，开启会发静音通知卡，现场可不使用。',
        ]),
        P('10.2 提示音、语音、闪烁与通知', "h2"),
        P(
            "默认提醒仅在应用内。提示音是媒体音量上的约 1 kHz 双短音，默认开启；语音默认开并读分类 + 特征。可先双音后语音、仅音或仅语音，都会闪行一秒并可跳转，测试按当前组合播放。按分类先展开对应层级再闪，跳转尽量保留标题；雷达以两个扩散环和亮心提示，纯语音也会闪。振动为短双脉冲。可选静音系统卡使用 <font face='FWText'>fieldwatch_watch_v3</font> 频道，默认不为每次命中建立通知；独立低优先级 <font face='FWText'>fieldwatch_scan</font> 是扫描状态，不是提醒。"
        ),
        P('10.2.1 关注特征语音', "h3"),
        P(
            '语音为第二种提示，默认开启，只想听短音可在设置关闭。仍受关注提醒总开关约束，关闭总开关后无音、语音、闪烁或跳转。'
        ),
        P(
            '语音开启时可选<b>播报内容</b>，默认<b>分类 + 特征</b>。分类与实时图标一致，如 AirTag / Chipolo / Tile 均播定位标签，Axon 播公共安全，ISP / 路由器播相应类别，适合口袋或驾车了解类型。特征只读具体库名，分类 + 特征两者都读。名称斜线以停顿处理，如 Ray-Ban / Meta 眼镜。'
        ),
        P(
            '<b>命名设备</b>始终播其关注名，即预填广播名 / 推测或自定义名，例如“Peter 的 Mesh 节点”，不受分类 / 特征选择影响；未匹配也读名称，不读未匹配。<b>特征书签</b>仍遵循播报内容，同设备多特征时读被关注系列，不一定首个标签。'
        ),
        P(
            '组合可为双音后约 400 毫秒播语音（默认）、仅音或仅语音。不能看屏幕时用语音，需要安静时仅短音，需要先提示再辨认则两者。测试分类读定位标签，特征读 Apple AirTags，两者则都读。跳转不依赖短音，任一可触发；信号追踪的盖革式点击从不播语音。'
        ),
        P(
            '语音使用本机 TTS，无网络或 Fieldwatch 服务器。正在播报时忽略该波后续命中以免重叠；没安装语言包仍可发短音。请调高媒体音量，两者使用同一音频流。'
        ),
        P('10.3 扫描强度', "h2"),
        table(
            ['模式', '适用情形', '代价'],
            [
                ['高性能', '步行、驾车经过或到场头五分钟，默认开启；完整手机检查见 §4.5。', '耗电发热最高，BLE 低延迟约 70 秒重启，默认 Wi-Fi 约 30 秒。移动中查特征 AP 可加快扫描（§10.3.1）。'],
                ['均衡', '一小时静坐的折中选择。', '接收率适中，默认 Wi-Fi 约 40 秒。'],
                ['省电', '全天放包中或房间内过夜。', '可能漏短 BLE 突发，默认 Wi-Fi 约 55 秒；列表频繁显示消失时延长过期时间。'],
            ],
            [1.5 * inch, 2.7 * inch, 2.3 * inch],
        ),
        Spacer(1, 6),
        P(
            '过期时间在设置可选 15-180 秒，默认 45，独立于扫描强度。屏幕保留取过期与短暂保留较大值，因此保留 60 秒会在末包后显示整分钟。省电配短过期可能把慢广播标消失，宜提高保留；标签场景可用高性能或 90-120 秒过期。'
        ),
        P('10.3.1 加快 Wi-Fi AP 扫描', "h2"),
        P(
            '扫描强度下的独立开关，默认关，不替代 BLE 高性能 / 均衡 / 省电，仅改变请求新 AP 列表的频率。'
        ),
        P(
            '<b>用途：</b>OUI、厂商 IE、IBR* / AirLink* / UniFi* 等特征只作用于扫描批次，不在空档自行搜索。静坐时 AP 会重复，驾车时车载 Cradlepoint、AirLink、路边 UniFi / Cisco 或隐藏 SSID 可能只短暂可见。45 mph 时默认两批相距约 600 米、加快后 160 米；65 mph 为 870 与 230 米（§7.1.1）。更多批次增加听到 BSSID、显示特征 / 重点关注并触发书签的机会，错过扫描窗口就会错过特征。'
        ),
        P(
            '<b>系统前提：</b>Android 11+ 可查询扫描限频。尝试开启及返回设置时应用都会检查；系统仍为默认限频时保持关闭，并提供打开开发者选项的提示，不能代写系统标志。Android 10 无法查询，此开关保持关闭。'
        ),
        P(
            '<b>开启顺序：</b>关于手机连续点版本号启用开发者选项；关闭其中 Wi-Fi 扫描限频；返回 Fieldwatch 开启加快扫描。仍需保持扫描通知，观察时常亮；想保留接收位置则开 GPS。'
        ),
        P(
            '<b>生效时：</b>约每 8 秒调用 startScan，跳过每两分钟四次配额，页头倒计时缩短。厂商仍拒绝时照常等待系统、最长退避 45 秒。系统重新限频后即使应用保存开关仍开，实际也不用快速模式，并可能提示需要开发者选项。车程结束可关，比单纯高性能更耗电发热。'
        ),
        P(
            '<b>边界：</b>仍非连续 Wi-Fi、非信号追踪、无客户端，也不保证捕捉每个车队 AP；人体、其他车辆、5 GHz 范围、改名随机 BSSID 且无 IE 都会漏。匹配不识别机构或具体车辆，作为驾车捕捉已关心特征的工具，仍需目视。'
        ),
        P('10.4 提醒配置建议', "h2"),
        bullets([
            '默认已关注执法记录仪、摄录眼镜、Fieldy / Plaud Note 录音穿戴、渗透测试、公共安全车载 AP 及公共摄像 / ALPR。不需声音可取消；Meta ID 也可能是 Quest，旧 Flock 模块 OUI 可能很吵。',
            '想知道某系列是否在场时关注特征，不要关注二十个 MAC。',
            '已锁定单设备、想知道离开后是否返回时关注设备。',
            'DIRECT- / ESP_ 通用名若无产品特征应保持未匹配，不要造万能特征，否则会与真实产品双标。',
            '首个提醒应目视复核，单条 BLE 可能只是路人。',
            '系统通知卡设计为静音。提高媒体音量并测试当前提示音 / 语音组合；只在需要通知卡时检查 POST_NOTIFICATIONS。',
        ]),
    ]

    # 11 Logging
    flow += [
        PageBreak(),
        P('11. 日志', "h1"),
        P('11.1 写入内容', "h2"),
        P(
            "设置可关闭日志。开启后，观察追加到 <font face='FWText'>files/logs/fieldwatch-NNN.jsonl</font>，JSON lines 每次接收一行。CSV / GPX / KML / WiGLE 仅在报告分享 / 保存时转换，不是另一路实时写入，旧 CSV 轮转文件仍兼容。默认每 1024 KB 轮转，000-011 共 12 个。洪泛时记录新设备及每第 25 次重复，并限制每批行数，避免磁盘锁卡界面。导出合并当前部分、去重复 CSV 表头。GPS 开且有定位时写 lat / lon，表示接收时操作者手机，关闭或未定位则空。新增末列 vendor_ie，最多八个 Wi-Fi 厂商 IE OUI，以竖线分隔；放最后使旧 17 列混合导出时经纬度位置不变，旧行和 BLE 为空。候选分析使用产品 IE，WPA / RSN / P2P / Qualcomm 协议芯片 IE 只记录不聚类。fleets 是<b>写入时</b>特征名，目录变动后应据其他字段重匹配。"
        ),
        P('11.2 CSV 列', "h2"),
        table(
            ['列名', '含义'],
            [
                ["timestamp", 'Unix 纪元毫秒，使用设备时钟。'],
                ["iso", "UTC 时间戳，格式 yyyy-MM-dd'T'HH:mm:ss.SSS'Z'。"],
                ["kind", 'WIFI 或 BLE。'],
                ["mac", '规范化地址，冒号分隔十六进制。'],
                ["name", 'SSID 或 BLE 本地名称，去除逗号 / 换行，未知或隐藏为空。'],
                ["rssi", '最近接收强度，dBm。'],
                ["channel", '由 MHz 推导的 Wi-Fi 信道，BLE 为 0。'],
                ["freq", 'MHz。BLE 记录 2402 作为频段标识，不是精确广播信道。'],
                ["oui", '前三个字节。'],
                ["vendor", '通用 MAC 使用 IEEE MA-L/M/S 名称，否则有数据时用蓝牙公司名称；随机 BLE 通常为空。'],
                ["fleets", '写入时匹配特征名，以 + 连接。为兼容日志列名仍叫 fleets；候选分析会重匹配，目录变化后不要直接信任此列。'],
                ["mfg", '十六进制厂商公司 ID，无则空。'],
                ["uuids", '服务 UUID 以 | 连接。'],
                ["flags", 'RAND 和 / 或 HIDDEN。'],
                ["raw", '厂商数据或原始广播十六进制，截到 80 字符。'],
                ["lat", 'GPS 开且有定位时的操作者纬度，WGS84 十进制度、六位小数；否则空。是接收时手机位置，不是目标。'],
                ["lon", '操作者经度，规则同 lat。'],
                ["vendor_ie", '最后一列，最多八个 Wi-Fi IE OUI，以竖线分隔，如 C8:3A:6B|00:50:F2。BLE、旧 17 列或系统没报告时为空。候选分析聚产品 IE；00:50:F2（WPA）、00:0F:AC（RSN）、50:6F:9A（P2P）、8C:FD:F0（Qualcomm）只记录不作系列 ID。'],
            ],
            [1.3 * inch, 5.2 * inch],
        ),
        Spacer(1, 6),
        P('表头：', "body_left"),
        P("timestamp,iso,kind,mac,name,rssi,channel,freq,oui,vendor,fleets,mfg,uuids,flags,raw,lat,lon,vendor_ie", "mono"),
        P(
            '旧文件没有末列。混合日志导出只写一次 18 列表头，旧行仍 17 字段，因此 vendor_ie 为空，经纬度保持原列。'
        ),
        P('11.3 JSON Lines', "h2"),
        P(
            '每行一个对象，事实与 CSV 相同，适合 jq 或笔记本分析；CSV 更适合表格。JSON 用 rand / hidden 布尔而非 flags，mfg 用整数而非 CSV 十六进制。旧 JSONL 缺 vendor_ie、rand、hidden 时，解析器按空或从 MAC 推断。'
        ),
        table(
            ['字段', '含义'],
            [
                ["ts", 'Unix 纪元毫秒，与 CSV timestamp 相同。'],
                ["iso", 'UTC 时间戳。'],
                ["kind", 'WIFI 或 BLE。'],
                ["mac", '规范化地址。'],
                ["name", 'SSID 或 BLE 本地名称。'],
                ["rssi", '最近 RSSI，dBm。'],
                ["channel", 'Wi-Fi 信道，BLE 为 0。'],
                ["freq", 'MHz，BLE 用 2402 标记频段。'],
                ["oui", '前三个字节。'],
                ["vendor", 'IEEE 或蓝牙公司名称，无则 null。'],
                ["fleets", '写入时特征名，以 + 连接，目录变化后应重匹配。'],
                ["mfg", '整数厂商公司 ID，无则 null，CSV 同 ID 用十六进制。'],
                ["uuids", '逗号分隔的服务 UUID。'],
                ["raw", '厂商或广播十六进制，最多 160 字符。'],
                ["vendor_ie", '最多八个 Wi-Fi IE OUI，以竖线分隔；旧文件和 BLE 为空，含义同 CSV。'],
                ["rand", '仅 JSON，随机地址标志；CSV 使用 flags RAND。'],
                ["hidden", '仅 JSON，隐藏 SSID 标志；CSV 使用 flags HIDDEN。'],
                ["lat", '接收时手机纬度，GPS 关闭或无定位时 JSON null。'],
                ["lon", '手机经度或 null，规则同纬度。'],
            ],
            [1.3 * inch, 5.2 * inch],
        ),
        P('11.4 观测总结与 AI 导出', "h2"),
        callout(
            '实验性观测报告，不是事实认定',
            NOTICE_SHORT +
            '观测总结“疑似尾随”和 AI 分析是内存窗口的假设，不是身份、完整记录或人身安全建议。不要把总结或 AI 聊天当作证据。AI 提示词也以相同声明开头并要求模型重复。',
            "warn",
        ),
        P(
            '报告有两个总结按钮，同一内容两种格式。使用选中观测最多 6,000 台，或最近 15 分钟内存约 400（§11.4.1），不受实时视图 / 筛选影响。默认清单省略未匹配轮换 BLE，计数保留（§5.6）。分享面板打开时扫描继续。内容含周围 SSID、MAC 及可选操作者 GPS，应按现场敏感信息处理。'
        ),
        bullets([
            "<b>观测总结（文本）：</b>通过系统分享 <font face='FWText'>text/plain</font>，可粘贴笔记、聊天或观测日志。",
            "<b>观测总结（PDF）：</b>Android PdfDocument 排版为 letter（612×792 pt），荧光绿 FIELDWATCH / 观测总结页头、编号章节；非空时显示琥珀色疑似随行追踪器 / 尾随、随行零售信标 / 穿戴设备，逐条重点关注框，绿色要点框，N / M 页码及 Off Grid Pete LLC 现场敏感信息页脚。缓存在 <font face='FWText'>cache/debrief/fieldwatch-debrief-YYYYMMDD-HHMMSS.pdf</font>，经 FileProvider <font face='FWText'>app.fieldwatch.files</font> 以 application/pdf 分享，可用 Drive、文件、邮件或 PDF 阅读器打开。",
        ]),
        P('11.4.1 观测总结实际能看到什么', "h3"),
        P(
            '未选命名观测时，总结读取<b>内存实时映射</b>而非回放日志。点击时取仍在内存的设备及操作者 GPS，保留首次或最后接收位于最近 15 分钟者，不受实时筛选 / 视图影响。磁盘 JSON lines 是另一来源，由日志导出和候选分析读取（§11.5）。'
        ),
        P(
            '两个时间限制与容量限制：',
            "body_left",
        ),
        bullets([
            '<b>15 分钟报告窗口：</b>最后听到已超过 16 分钟的设备不会进入本次总结，即使日志仍有包。',
            '<b>内存淘汰：</b>无名称 / 未匹配设备约末包后三分钟移除，已命名 / 匹配可保留 15 分钟。',
            '<b>实时容量：</b>约 400 台、硬上限 900，先删最旧未命名，短暂保留期内不因普通上限删除；仍超硬上限时命名项也可能移除。',
            '<b>命名观测容量：</b>报告中开始的观测最多 6,000，不同于实时 400。满额时优先保留重点关注、广播位置、书签及关注特征，先删最旧无名 BLE，再其他未固定项；低内存不加新未匹配。滚动日志仍是独立会话流水。总结默认不列未匹配轮换 BLE，计数保留（§5.6）。',
        ]),
        P(
            '城市驾车几公里就可能因手机地址轮换、商店 AP 和车辆填满 400，起点咖啡馆或路口随即不在下次总结，无名 BLE 三分钟后已可能消失。这是预期，不是扫描失败或日志自删。'
        ),
        P(
            '沿途持续广播的包中标签、车胎压、自有 AirTag / 手表或被放入的追踪器会不断刷新最近时间；有特征又获得 15 分钟保留，且不先被拥挤淘汰，因此可能连续出现在各次总结。仅路过的路边设备不保留。无需开启随行筛选，总结使用同样 GPS 轨迹自行分析。'
        ),
        P('<b>较长行程的做法</b>', "body_left"),
        bullets([
            '约每 10-15 分钟或每站生成文本 / PDF 总结，并<b>保存分享文件</b>；每份只覆盖当时窗口，不是全程。',
            '不要到家才生成一次，末尾 15 分钟通常只剩最后几公里，非出发街区。',
            '保持日志，日志导出才有一小时流水；总结不能从内存重建它。',
            '无需静坐，移动中总结仍给距离、所在位置及与车同行的设备。',
            '要长于实时窗口，可开始命名观测，最多 6,000，满时无名 BLE 先移除。',
            '高速后无名 BLE 清单较少正常，先看疑似追踪器 / 尾随 / 重点关注；默认清单跳过未匹配 RAND。',
        ]),
        P(
            'AI 导出使用同一快照并加 5 分钟切片，限制相同；长行程要让聊天看到更多，应多次导出。'
        ),
        P(
            '两种总结正文相同：生成时间、窗口、扫描设置、GPS 开关、GPS 开启时沿线距离和直线跨度；接着是概览、<b>所在位置</b>（操作者停留 / 移动，每停留点只列一次坐标，在线地名可用时列街道），有广播经纬度时加<b>飞行器</b>（状态、最后位置、高度、航向、速度、定位点数，地图见 §5.6.1）；有备注时加<b>观测备注</b>（自定义名、MAC、RSSI、备注，弱设备也可列，即使不属最强 AP）。然后是追踪评估，以及非空时的琥珀<b>疑似随行追踪器</b>和<b>疑似尾随</b>定位标签提示。' +
            '若相应分类沿途存在，还列<b>随行零售信标</b>和<b>随行穿戴设备</b>，随后为环境、Wi-Fi、BLE（有映射时附解码，自定义名替广播名）、特征命中、持续出现、重点关注（完整说明，PDF 琥珀框，只是模式非盗刷器检测）、异常、隐私、建议行动及一句要点。GPS 有步行路线时附全宽图，地图开启用 OSM，同处设备共索引，附近飞行轨迹黑点，末位分类图标、飞手人形。<b>异常</b>不重复设备清单，只列前述章节未覆盖线索，如 Fast Pair 配对、极强无名设备、随机 BLE 数偏高；不重列 AirTag / SmartTag / Tile 或重点关注。'
        ),
        P(
            'GPS 开且移动约 45 米后，总结按分类判断同行。追踪概述只说测试是否运行及移动距离，只有<b>沿路持续存在</b>者有独立提示，路过住宅标签省略。<b>疑似随行追踪器</b>含 AirTag / Find My、SmartTag、Tile、Chipolo、Pebblebee 及强口袋 Apple BLE，可能是自有设备，也可能在出发前放在车 / 包 / 身上，须逐 MAC 核实。Apple BLE / Continuity 需峰值 ≥-55、从不低于 -70、至少两 GPS 点、最近三分钟收到。<b>疑似尾随</b>是观测开始后首次出现再同行的定位标签，可能是后来同行的人自带手机 / 钥匙，或途中新增设备；额外要求覆盖约半条路线、至少三分之二样本 ≥-75、最后值不比峰值弱 12 dB。仅绕路听到住宅 Find My 或逐渐衰减者不列。<b>随行零售信标</b>含 iBeacon、Target Atrius、Minew、Estimote、Kontakt.io，常是固定装置，若同行需核对测试标签、工牌或短暂覆盖，不能当 Find My 尾随。<b>随行穿戴</b>含 Garmin、Fitbit、Oura，常是自有或同行者设备，不典型为暗置追踪器。Find My / iPhone 会轮换，每 MAC 仅表示本会话。若有实时值则引用特征库说明：分离保留约一天地址说明，靠近主人常为自有；对比会说明模式变化。GPS 关闭或静坐无法运行，驾车经过仍需该设备三个 GPS 点。此为启发式，非法律结论或身份。无需开启随行或看列表，任意实时视图均可生成这些分析。'
        ),
        P(
            'GPS 开启时，<b>所在位置</b>将路径分为约 40 米簇的停留和移动，各停留列 UTC 时间、持续时长、手机经纬度、可选街道名及该处强设备。静坐为一个停留，换街区为停留 → 移动 → 停留，不在每设备行重复坐标。默认在线地名与地图通过系统服务反查停留中心并加载轨迹瓦片；离线提示后仍列坐标和北向线图，不报错。手机 GPS 不等于杆体或标签位置。'
        ),
        P(
            '报告<b>AI 导出</b>用于补充分析，窗口同总结而非滚动日志。提示词<b>原样包含机内总结</b>，再附 5 / 15 分钟速率、RSSI 区间、随机 BLE 比例、重点关注、备注和类定位标签的判断校验表；不再粘贴第二份 Wi-Fi / BLE 清单，并要求模型<b>不要重写总结</b>或在答复堆 MAC。'
        ),
        P('提示词包含：', "body_left"),
        bullets([
            '与首次启动和总结相同的业余 / 原样声明，并要求模型重复。',
            '任务是分析补充，不是第二份总结；使用五个输出标题，再给一个包含机内要点未提到数值的结论。',
            '机内总结原文，与文本 / PDF 同一观测报告。',
            '仅接收约束：仅 AP、BLE 地址轮换、GPS 属手机、不虚构尾随、不提供安全建议。',
            '工作表：15 / 5 分钟计数、RSSI 区间、RAND 百分比、每分钟新到、持续 / 消失、系列数、GPS 长度 / 跨度、重点关注 ID、备注与类定位标签（不是尾随名单）。',
            '要求输出免责声明、已有结论、数字补充、重点关注与追踪线索、信号追踪 / 二次观测可缩小的不确定性、要点，不给安全建议。',
        ]),
        P(
            '快照与总结相同（§11.4.1）：约 400 台，无名 BLE 三分钟后已可能移除，窗口 15 分钟或所选命名观测。分享文字上限约 90,000 字符，应按敏感内容处理。'
        ),
        P(
            '设备详情有独立<b>AI 导出</b>和<b>分享为文本</b>（§5.5），仅针对打开的设备，导出该页或要求聊天解释 OUI / 公司 / UUID、推测产品。它们不替代整次观测 AI 导出。发到公开聊天前应脱敏，模型仍受实验声明约束，不应给安全判断或识别人名。',
            "body_left",
        ),
        P('11.5 候选特征', "h2"),
        P(
            "候选特征是日志分析，不是观测报告，也不读 15 分钟内存。合并 <font face='FWText'>files/logs/</font> 各轮转文件，按类型 + MAC 去重，用当前 SignatureEngine 重匹配，再聚类共享独特广播 ID 的未匹配设备。界面与创建见 §5.6.4，保存见 §9.2.1；详情系列卡（§5.5）对单设备结合当前和日志做同样 ID 质量判断。"
        ),
        P(
            '每台独立设备读取以下字段，CSV 名称及 JSON 对应见 §11.3：'
        ),
        bullets([
            '<b>kind、mac、name、flags（RAND / HIDDEN）：</b>身份。无其他 ID 的随机地址跳过；guest / xfinity / 单词住宅名称若无其他独特 ID 也跳过。',
            '<b>vendor：</b>IEEE / 公司名。Espressif、MediaTek、AMPAK、Qualcomm、UGSI、Realtek 模块厂商，以及 Google、Apple、Samsung、Microsoft 不作仅 OUI 系列。',
            '<b>oui：</b>稳定 BSSID 前缀。至少三 MAC，或两 MAC 且至少两个非住宅名，避免把一户 AP 的虚拟地址建成系列。',
            '<b>vendor_ie：</b>Wi-Fi IE OUI，在随机 BSSID 上可识别 Roku 类 ID；仅新列发布后写入的数据有，协议 IE 只记不聚。',
            '<b>mfg、raw、uuids：</b>BLE 公司 + 首数据字节和 16 位服务 UUID。Apple 0x004C、Google、Samsung 0x0075、Microsoft 等宽泛公司及 Fast Pair FEF3/FCF1、FCB2、Battery 180F 等通用 UUID 不单独聚类。',
            '<b>fleets：</b>忽略，按手机当前目录重新匹配。',
            '<b>lat、lon、rssi、timestamp：</b>不用于聚类，频次指独立 MAC 数而非包数。',
        ]),
        P(
            '至少两台共享独特 ID 才是系列。相同 AP 同时符合名称与 OUI 等重叠簇合并卡片并附更多规则，最多 20 个系列。创建草稿同时指定无线类型，避免 Wi-Fi 通配符命中 BLE。日志关闭、已清或只有噪声会空；厂商 IE 需新行，名称与稳定 OUI 可分析旧文件。'
        ),
        P('11.6 分享、保存与清空', "h2"),
        P(
            '报告中两个导出卡格式相同、文件不同。<b>观测导出</b>是所选窗口逐类型 + MAC 一行，无需开日志；<b>日志导出</b>是记录开启时每次写入的会话流水，同设备可多行。清日志不删观测，删观测不动日志；候选特征分析日志。'
        ),
        P(
            "设置控制日志开关和轮转大小，磁盘 JSON lines 在分享 / 保存时转换 CSV / JSON lines / GPX / KML / WiGLE，可筛全部 / Wi-Fi / BLE。日志地图格式为手机接收点，观测 GPX/KML 另加手机轨迹。应用不上传，用户自行选目标；分享用系统面板，保存用存储访问框架选内存或 SD。清空删除轮转文件、跳过排队追加并新建文件。导出显示进度，复制日志时暂停实时写入避免卡界面。FileProvider 为 <font face='FWText'>app.fieldwatch.files</font>，不自动同步外部。总结是摘要、观测导出是名单、日志是流水；GPS 开则含操作者经纬度，新 Wi-Fi 行含 vendor_ie，隐私不遮蔽两种导出文件。"
        ),
        P('11.7 阅读历史', "h2"),
        bullets([
            '先按 iso 排序，再按 mac + kind 分组，新组代表新设备或轮换 BLE 地址。',
            '将 rssi 对 iso 绘图观察增强 / 衰减，忽略单样本尖峰。',
            '筛选非空特征列（CSV 为 fleets）可复盘特征命中，不受当时画面筛选影响。',
            'WIFI 名称空且 HIDDEN 是隐藏 AP，使用 mac / oui 而非名称。',
            '两 MAC 同 OUI 且一分钟内出现时，可判断聚类规则是否会将其关联。',
            'lat/lon 属手机，应画自己的路径，不是 AP / 标签坐标。空值表示未开标记或当次无定位。',
            'vendor_ie 为竖线分隔 OUI，旧行和 BLE 为空；按其分组可找 BSSID OUI 漏掉的产品 IE，但跳过 00:50:F2 / 00:0F:AC / 50:6F:9A / 8C:FD:F0。',
            'fleets 是写入时结果，目录改变后用 name / oui / vendor_ie / mfg / uuids 重匹配，或使用候选特征。',
        ]),
        P('11.8 存储', "h2"),
        P(
            '默认 12 个约 1 MB 轮转文件约占 12 MB，另加 config.json。卸载删除日志，重装或恢复前应先导出重要文件；需恢复目录与命名设备则导出特征和设置。时间来自手机，定时观测前应校准。扫描中 GPS / 网络实时定位会写内存详情、随行、总结及新日志 lat/lon，忽略超过 30 秒旧定位；新 Wi-Fi 行还存 vendor_ie。非高精度时驾车轨迹也可能保持 0。位置只用于接收时关联，不是测绘级轨迹，含操作者坐标的日志应谨慎分享。'
        ),
    ]

    # 12 Field playbooks
    flow += [
        PageBreak(),
        P('12. 现场操作方案', "h1"),
        P(
            '这些操作方案用于回答可向无线信号提出的问题。每项都说明使用哪些控件、实时画面应呈现什么，以及匹配结果能支持哪些判断。特征标签只表示公开广播符合某种模式；还应结合 RSSI 趋势、持续出现情况和目视观察确认。筛选与显示仅改变画面，日志仍会记录。无论采用什么视图或筛选，观测总结的跟踪章节都分析内存中的最近 15 分钟。'
        ),
        P(
            '每次运行<b>一个</b>方案，直到能读懂结果。可以叠加“随行 + 仅新发现 + 仅匹配特征”，但空列表也就有了三种解释。第 13 章讨论无线观测习惯（电池、屏幕、人群），完整条款见声明页。“我是否被跟踪？”等方案只是无线观测练习，不能用于判断你是否处于危险中，见 §12.2。'
        ),
        P('12.1 如何使用操作方案', "h2"),
        bullets([
            '<b>先到现场。</b>选择高性能、全部流量、按信号强度排序的列表，并确认扫描通知存在。记下信号最强的五个 AP，了解周围的固定背景信号。如果列表已难以阅读，先打开“显示”精简条目（副标题行设为“无”、关闭附加项），再隐藏设备。',
            '<b>再缩小范围。</b>应用与问题相关的筛选或特征集合。如果列表变空，先撤销最后一项条件，再判断现场是否没有目标。',
            '<b>暂停后检查。</b>从冻结的条目打开详情。“可能的设备类型”、标志位和载荷比匆匆看一眼标签更有用。',
            '<b>保持日志开启</b>，除非公共场所的大量数据使存储负担过重。你可以在实时画面隐藏条目，同时保留文件记录。',
            '<b>记录观测。</b>筛选和实时视图只改变你看到的内容。观测总结和 AI 导出分析最近 15 分钟内存数据（上限约 400 个设备；§11.4.1），包括类似追踪器的设备是否随行。驾车时应多次生成观测总结；日志导出提供完整文件。不同分享方式见 §12.12。',
        ]),
        P('12.2 我是否被跟踪？', "h2"),
        callout(
            '这不是安全测试',
            '此方案无法判断现实中你是否被跟踪。它只报告沿本机 GPS 轨迹持续随行的强信号设备。静默标签、轮换的“查找”地址、漏收广播的手机以及你自己的包内标签都会影响判断。如果认为自己有危险，请离开并求助，不要等待 Fieldwatch。参见声明页。',
            "warn",
        ),
        P(
            '<b>问题。</b>步行或驾车时，是否有强信号设备持续随行，而不只是到门口才遇到的住宅 AP？',
            "body_left",
        ),
        P('<b>准备。</b>', "body_left"),
        numbered([
            '“为探测结果添加 GPS 标记”和“保持屏幕常亮”默认开启。将定位设为高精度。扫描必须运行，实时 GPS 更新才能启动。',
            '步行或驾车，直到筛选页显示约 50 米轨迹。若一直为 0 米，说明手机未提供实时定位。原地不动不会增加轨迹。一次观测结束后，如需重新进行随行检测，请在实时页面点按“重新开始”。',
            '在“筛选”中选择“随行”预设，或打开无线设备区域中的“随行”开关。此开关会清除“仅匹配特征”“仅已关注”“仅命名设备”和类别的“仅显示”，让未匹配设备也能参与随行判断。',
            '可选：在“显示 → 排序”中选择“新设备置底”，使新的随行设备追加到列表末尾，避免列表跳动。',
            '出现并非自有装备的条目时，暂停并打开详情；如需在它再次出现时收到提示音，可关注该设备。',
        ]),
        P('<b>预期画面。</b>只显示在距离和时间上覆盖<i>你</i>大部分轨迹的强信号设备，其大多数带 GPS 标记的样本约为 −75 dBm 或更强。包内或车内标签会匹配，可用来确认筛选工作正常。仅在你到达时出现的住宅 AP 应保持隐藏。高速路上经过的车辆仍会时隐时现，真正随行的设备应持续存在。“仍在此处”的窗口不是固定 50 米圆圈：它随移动速度增大，且 Wi-Fi 因扫描较慢而比 BLE 更长，避免杯架里的标签在两次广播之间消失。步行时仍采用约一栋房屋长度的较小窗口。检查条件和速度表见 §8.5。', "body_left"),
        P('<b>不能说明什么。</b>这不是测向，也不是对方设备的 GPS，而是本机接收时的位置。“查找”／离线查找轮换 MAC 后，无法把每分钟换地址的设备串成同一个跟踪目标。静默、弱信号或只在轨迹一端出现的设备不满足条件。', "body_left"),
        P(
            '<b>记录结果。</b>移动约 45 米后，在“报告”中生成观测总结（文本或 PDF）。跟踪评估先简要说明检测是否实际运行。琥珀色提示只列出持续随行的设备，并按类别区分：<b>随行的疑似追踪器</b>／<b>疑似尾随</b>（寻物标签）、<b>随行的零售场所信标</b>（iBeacon／Target Atrius 购物篮／Minew／Estimote／Kontakt.io，通常是设施；你推行的 Target 购物篮也会随行）、<b>随行的可穿戴设备</b>（Garmin／Fitbit／Oura，通常是自己的装备）。路过住宅的标签会省略，并给出总体距离。范围始终是内存中的最近 15 分钟，无论是否保留随行筛选、隐藏该系列，或切换雷达／时间线／混合／按类别视图。筛选和视图不会缩小观测总结。携带 AirTag 或 iPhone 时，若持续保持约 −55 至 −70 dBm 强信号，应进入“随行的疑似追踪器”。“查找”MAC 会轮换，因此看到的是本次会话地址，不是一小时内固定的 ID。社区环线有额外要求：住宅“查找”设备只有覆盖约一半轨迹、大部分 GPS 标记处达到 −75 dBm，且未较最强信号衰减 12 dB，才会被称为尾随。驾车经过仍至少需要三个 GPS 标记。需要街道名称时可开启在线地名；需要聊天模型阅读提示和清单时可用 AI 导出，并明确要求“应用 §12.2；不要把整次观测都存在的设备一概当成我的；不要列出只路过的设备；不要把零售信标当作‘查找’尾随”。长途驾驶时在下一停靠点再次生成观测总结（§11.4.1）：持续随行的设备仍在，起初几公里的未命名路边设备可能已不在。这不构成法律认定或身份确认。',
            "body_left",
        ),
        callout(
            '先排除自己的装备',
            '若携带 AirTag、SmartTag、Tile 或车内追踪器，“随行”会显示它。先隐藏该系列或将其视为已知条目，再把其他设备判断为尾随。',
            "note",
        ),
        P('12.3 是否有新设备进入现场？', "h2"),
        P(
            '<b>问题。</b>我坐下后出现了哪些原本不在房间里的设备：手机、标签，还是新的 AP？',
            "body_left",
        ),
        P('<b>准备。</b>', "body_left"),
        numbered([
            '留在现场，使用高性能模式，等待首批 Wi-Fi 结果到达（页眉先显示“Wi-Fi 下次扫描 N 秒”，随后 AP 数量增加）。',
            '开启“筛选 → 仅新发现”。实时画面先显示“仅新设备 · 正在学习现有 Wi-Fi”，随后显示“仅新设备 · 已隐藏 N 个”。',
            '房间形成基线后，点按标签栏上方的“标记已见”。先暂停再标记，只会吸收冻结画面中的设备，不包含冻结后到达的设备。',
            '将短暂保留设为 30 或 60 秒，避免广播较慢的设备反复出现、消失。',
            '更换房间并希望把该空间设备视为新设备时，使用“重置已见”。清除日志不会重置已见集合。',
        ]),
        P('<b>预期画面。</b>只显示不在已见集合中的设备。Wi-Fi 学习期间，BLE 仍可作为新设备出现。“标记已见”后，下一个新条目就是下一次新增。只有该条目确实会显示在当前实时列表时，才会触发关注警报。', "body_left"),
        P('<b>不能说明什么。</b>随机化 BLE 地址每次轮换都像新设备。“刚到”的未命名 LE 可能只是换了 MAC 的手机。现有 Wi-Fi 会按设计隐藏到下一次扫描。此筛选不能识别谁走进来了，只说明本次会话尚未纳入已见集合的设备正在广播。', "body_left"),
        P(
            '<b>记录结果。</b>“仅新发现”不会缩小观测总结或 AI 导出的范围，它们忽略实时筛选。可查看观测总结中的持续出现／首次发现信息，或 AI 导出中 5 分钟与 15 分钟首次发现计数。之后需要每条已写入记录时，使用日志导出。',
            "body_left",
        ),
        P('12.4 只查找指定系列', "h2"),
        P(
            '<b>问题。</b>我只关心追踪器、摄像头，或某个自定义特征。',
            "body_left",
        ),
        P('<b>准备。</b>', "body_left"),
        numbered([
            '在“筛选”中选择“仅显示”，再选择寻物标签、摄像头、无人机、监控、门禁、渗透测试等类别。匹配仍在运行，只是实时画面减少条目。需要作为预设使用时，点按“将当前筛选另存为…”。',
            '某系列在本地经常误报时，可在筛选页隐藏它（类别用“隐藏所选”，单个系列用“隐藏所选特征”），或在编辑器中关闭干扰较多的规则，例如 Flock 中的 LiteOn OUI，见 §7.6。',
            '希望有新匹配时发出提示音，可关注该特征。',
            '雷达或混合视图用于观察信号相对强弱，列表便于筛查，详情用于解码。',
        ]),
        P('<b>预期画面。</b>未匹配的消费类设备背景信号消失，剩余条目上的标签表示仍在实时画面中的系列。列表为空，可能是接收范围内没有匹配设备，也可能是在筛选页隐藏了该系列。匹配仍会标注，不会停止运行。', "body_left"),
        P('<b>不能说明什么。</b>“仅匹配特征”不会增强搜索，只会隐藏未匹配设备。内置 Ring、Nest、Hikvision 等条目大多按名称匹配，公寓摄像头和偶然重名的 SSID 也会被标注。现场干扰较多时可隐藏该系列。将摄像头标签视为路边立杆前，请阅读 §7.6.1。', "body_left"),
        P(
            '<b>记录结果。</b>查看观测总结中的特征命中及摄像头／追踪器标记。观测 AI 导出提供系列计数和重点关注 ID，不重复输出一份已标注设备清单。单个设备使用详情 AI 导出。未脱敏前不要粘贴到公开聊天中。',
            "body_left",
        ),
        P('12.5 去除干扰，保留现场概况', "h2"),
        P(
            '<b>问题。</b>我想查看整个周边环境，但排除已经知道只是干扰的系列。',
            "body_left",
        ),
        P('<b>准备。</b>', "body_left"),
        numbered([
            '先选择“全部流量”，保留未匹配设备。',
            '在“筛选 → 隐藏所选”中选择“寻物标签”，会隐藏整个类别。若只想隐藏包中 AirTag 所属特征，使用“隐藏所选特征”并打开对应条目。',
            '实用组合：“仅匹配特征 + 隐藏所选的寻物标签”，保留已命中特征，去掉包内标签干扰，同时仍显示摄像头。',
        ]),
        P('<b>预期画面。</b>保留其余现场设备。隐藏类别会从实时画面移除，直到关闭“隐藏所选”。切换模式会保留类别选择，只有“重置筛选”才会清除。', "body_left"),
        P('<b>不能说明什么。</b>隐藏寻物标签不代表现场没有 AirTag；它们仍会匹配并写入日志。当前实时筛选排除的条目不会触发关注提示音。', "body_left"),
        P(
            '<b>记录结果。</b>隐藏的系列只要仍在实时数据表中，就会出现在观测总结和 AI 导出里。日志的意义就在于：画面可以清静，文件仍保留记录。之后需要查看被隐藏的干扰设备时，用日志导出。',
            "body_left",
        ),
        P('12.6 这是我自己的标签吗？', "h2"),
        P(
            '这是检查随身物品，不是指控。移动约 50 米后开启“随行”。如果唯一类似追踪器的条目就是放在包里或车里的标签，说明筛选正常。关注该 MAC 或隐藏该系列，避免它与真正候选设备争夺注意力。DULT 或 Find Hub 条目先看模式标签。“分离”显示更醒目，并可能维持同一 MAC 约一天。整次观测都随行且显示“靠近主人”的设备往往是自己的标签，见 §5.4.1。',
            "body_left",
        ),
        P(
            '如果你<b>没有</b>携带标签，却仍有类似追踪器的强信号覆盖整个轨迹，请暂停，查看详情、“可能的设备类型”和 RSSI 趋势。需要再次分析<i>该</i>设备时，可使用文本分享或详情 AI 导出。随后生成观测总结（文本或 PDF），区分“随行的疑似追踪器”（自己的，或开始前就被放置的，需要解释其来源）和“疑似尾随”（本次观测开始后才首次接收到）。无论“随行”是否开启、实时画面是否切换视图，这些提示都分析内存中的最近 15 分钟。需要聊天模型结合速率和设备组合检验提示时，可用观测级 AI 导出；其中已嵌入观测总结，应要求模型不要重写。所有结论都是启发式判断，“查找”地址轮换仍无法拼接。',
            "body_left",
        ),
        P('12.7 摄像头／ALPR 观测', "h2"),
        callout(
            '没有标签不代表没有摄像头',
            '静默或优先使用蜂窝网络的立杆设备，往往无法被本机看到。不要依据空白实时画面判断某地是否适合安全地拍摄、集会或驾车经过。仅用于实验性观测，见 §7.6.1 和声明页。',
            "warn",
        ),
        P('<b>准备。</b>选择“监控”预设，或启用关心的 Flock／Raven／摄像头名称，再开启“仅匹配特征”。使用高性能模式，沿街区走动。路边／公共摄像头与 ALPR 条目（Flock、Penguin、Pigvision、FS Ext Battery、Genetec AutoVu、Rekor、Motorola Vigilant、Verkada、Avigilon、Axis、Hikvision、Dahua、Hanwha Wisenet、Uniview、Rhombus）会发出提示音并带有重点关注“!”；卡片说明该系列的用途。标签出现时，先目视查看，再记录亲眼看到的情况，而不是把标签内容当作事实。', "body_left"),
        P(
            '<b>实际限制。</b>较新的立杆设备通常优先使用蜂窝网络，Wi-Fi／BLE 上几乎静默；没有标签不代表没有摄像头。Fieldwatch 听不到 LTE，看不到已关联客户端，也无法混杂捕获。IEEE B4:1E:52 加 Flock-* SSID 可信度较高；LiteOn／Espressif／Raspberry Pi OUI 若无名称或 UUID 佐证，可信度较低。手机 GPS 表示<i>你</i>的位置，不是立杆位置。完整限制见 §7.6.1。',
            "body_left",
        ),
        P(
            '<b>记录结果。</b>先观察，再生成观测总结，PDF 便于归档。特征命中和摄像头标记只是线索，不是立杆身份。AI 导出可列出所有类似摄像头的条目并解码载荷；应告诉模型“遵循 §7.6.1；存在静默立杆；不要把摄像头放在 GPS 标记点上”。不希望粘贴内容包含<i>自己</i>的行进街道时，关闭在线地名。',
            "body_left",
        ),
        P('12.8 追踪一个追踪器', "h2"),
        callout(
            '不保证能够找到',
            '标签广播可能很慢、会轮换地址，也可能超出本机接收能力。没有条目不能证明没有追踪器。“信号追踪”显示相对强度，不是米数或指南针。不要用于判断人身安全，参见声明页。',
            "warn",
        ),
        P(
            '<b>先找到条目。</b>选择“筛选 → 仅 BLE”，并仅显示寻物标签；未匹配设备保持隐藏，“仅匹配特征”会变灰。标签广播较慢，省电模式通常足够。若条目闪烁消失，将短暂保留设为 60 秒、过期时间设为 90–120 秒，使用时间线并关注该系列。自己的标签挤满列表时，可隐藏其特征。AirTag／“查找”地址会轮换，看到的是新 MAC，不是一小时内的固定身份。步行中持续随行的强信号应按 §12.2 处理；无论屏幕显示信号追踪还是寻物标签筛选，观测总结仍记录最近 15 分钟的随行情况。找到<b>一个</b> BLE 候选后，打开详情 → <b>信号追踪</b>；Wi-Fi 没有此按钮。屏幕会保持常亮，始终用同样姿势握持手机，改变握姿后重置本次追踪。',
            "body_left",
        ),
        P(
            '<b>不知道应追踪哪个设备时。</b>筛选仅显示寻物标签，使用按信号强度排序的列表和高性能模式。隐藏已知自有装备（钥匙、包内 AirTag）的特征，否则它们总占据顶部。然后把手机<i>放在</i>可能藏标签的位置，将其作为嗅探探头，而非沿街走动。检查车辆时，依次查看各轮拱、保险杠内、门槛下方、拖车钩、备胎和车厢（中控台、座椅下、遮阳板）。每处停留 10–20 秒，让慢速广播设备有机会发声；标签并非每秒都发送。如果追踪器系列条目升到顶部，或 RSSI 比上一位置大幅提高，就将其作为候选并打开信号追踪。按同一网格重复检查，参考“更近／更远”；仍需方向时再做身体遮挡转身。若显示“已离开”，可能是 MAC 轮换，应回到实时画面，选择新的最强追踪器条目后重新追踪。安静的扫描不能证明车内没有设备：标签可能休眠、超出本机接收范围或未被特征库收录。车身金属会遮挡信号，某个车轮处的峰值也可能来自反射。同一方法也适用于包、外套或婴儿车：依次把手机放到每个口袋／隔间。',
            "body_left",
        ),
        P(
            '<b>逐步靠近。</b>缓慢移动，每次只尝试一个方向。查看“更近／更远／大致相同”和本次最强信号，不要参考实时雷达的角度；该角度来自 MAC 哈希，不代表北向。显示更近时可沿该方向继续；显示更远时停下、转身并换方向。大致相同表示应等待或改变方向，不要把 dBm 换算成英尺。“非常近”（约 −45 dBm 或更强）提示查看附近，通常可能在手中、口袋或同一个包内，但仍不是距离。变弱可能是墙体遮挡，并非方向错误。若从实时画面消失，地址可能已轮换；回到实时画面，选择同一系列的新条目再追踪。',
            "body_left",
        ),
        P(
            '<b>用身体遮挡判断可能方向。</b>手机没有测向能力，但躯干会衰减来自一侧的 BLE，类似把天线靠近身体后旋转寻找峰值。站定，将手机贴在胸口中央，或每次放在同一口袋，让身体遮挡半个方向。缓慢转完整一圈，观察大号 RSSI 和本次最强信号。如果某个方向变强，该方向只是<i>候选</i>方位，往往表示身体对信号路径遮挡最少，大致朝向设备。再转一圈确认，将其视为数十度范围，不是精确罗盘方向。然后重置本次追踪，沿候选方向移动并观察更近／更远。反射和金属会制造虚假峰值，见下文。',
            "body_left",
        ),
        P(
            '<b>建筑结构会误导。</b>真实距离不变时，墙、楼板或门也可使 RSSI 下降 10–20 dB。汽车、柜子、电梯及带铝箔保温层等金属会反射和遮挡信号，身体遮挡法的最强方向可能只是面包车的反射。人体和水吸收信号，混凝土与钢筋使其散射，玻璃通常比砖墙影响小。隔着两层楼也可能显示“更远”，用拳头包住天线相当于再加一道墙。不要把一次峰值当地图定位；继续走动和转向，看看经过下一个开口后“更近”是否仍成立。信号追踪页面详见 §12.13。',
            "body_left",
        ),
        P(
            '<b>记录结果。</b>使用详情中的文本分享或 AI 导出分析该设备。若问题是是否被放置了持续随行的标签，“报告 → 观测总结”仍含最近 15 分钟跟踪评估（§12.2）；信号追踪、寻物标签筛选及雷达／列表切换都不改变该报告。观测级 AI 导出列出“查找”／Fast Pair 标记，日志导出便于之后用表格比较 MAC，但这些地址会轮换。',
            "body_left",
        ),
        P('12.9 跟进 SSID 或 OUI 线索', "h2"),
        P(
            '<b>准备。</b>设置“名称／MAC 包含”或“OUI／厂商包含”，选择 AND，开启两种无线类型。<b>不要</b>开启“仅匹配特征”，否则会隐藏尚未匹配但相关的 AP。使用按信号强度排序的列表。若设备反复出现，可在详情中选择“从设备创建特征”。',
            "body_left",
        ),
        P(
            '多次到访都重复出现的 BSSID 通常是固定设施。重复的随机 BLE MAC 更可能只是同一次会话，并非长期身份。观测总结的 Wi-Fi 清单与 AI 导出的完整 AP 列表是本次观测快照；下次到访时应比较日志导出。',
            "body_left",
        ),
        P('12.10 步行、驻留或驾车', "h2"),
        table(
            ['你的场景…', '建议使用'],
            [
                ['扫描新街区', '全部流量、高性能、按信号强度排序的列表或混合视图。先了解背景信号，再筛选。'],
                ['步行：谁在随行', '按 §12.2 在实时页面开启“随行”；离开该筛选或切换视图后，观测总结仍记录最近 15 分钟跟踪结果。需要 GPS 标记和约 50 米轨迹。步行采用约 75 米的较小“仍在此处”窗口（§8.5）。'],
                ['驾车：谁在随行', '使用同一筛选。“仍在此处”窗口随速度增大，避免车内标签在两次广播之间消失；路边经过的设备仍无法通过轨迹移动条件，见 §8.5、§12.2。'],
                ['在房间驻留：谁刚到', '按 §12.3 使用“仅新发现”。房间形成基线后标记已见，更换房间时重置已见。'],
                ['ATAK 叠加显示（Remote ID／重点关注）', '配置见 §5.8，观测见 §12.15，接收 RID 见 §12.16。开启“设置 → TAK／CoT 推送”，选择重点关注和载荷位置。支持 BLE FFFA 与 Wi-Fi FA:0B:BC。使用同一 Wi-Fi 局域网，关闭隐私模式。'],
                ['长时间观测／停放车辆', '使用均衡或省电模式及时间线。难以阅读时将 RSSI 下限设为 −80，开启日志。依靠关注提醒，无需一直盯屏。'],
                ['驾车后到家', '“随行”仅用于 BLE，住宅 AP 保持隐藏。如果包内标签仍不显示，可能轨迹太短，或 GPS 只在目的地添加了标记。'],
                ['查看轨迹增长', '保持打开“报告 → 轨迹”。进行中的观测从起点延伸至现在；最近 15 分钟是滑动轨迹，尾部会逐渐移除。观测中如有广播飞行器轨迹，也会用白色虚线绘制，最新位置显示类别图标，操作员显示人物图标。黑点为起点，蓝点为你的最新位置。MAC 和特征警报只绘制一次，解码经纬度采用最近广播位置；其他设备在最强接收点显示类别图标。数字代表同一地点有多个设备。单个类别图标没有数字框，点按可查看该设备。约每 3 秒重绘，见 §5.6.1。'],
                ['长途驾车（数公里）', '开始观测可使用 6000 个设备的窗口，满额时优先丢弃未命名 BLE。每 10–15 分钟或停靠时生成观测总结并保存分享内容（§11.4.1）。实时内存仍约为 400 个设备。观测总结默认跳过未匹配的随机地址 BLE，观测导出含完整清单，日志导出则逐次记录接收。可将“报告 → 轨迹”保持在前台查看实时轨迹。'],
                ['列表太快，无法点按', '先暂停，再打开详情，随后恢复。也可将“显示 → 副标题行”设为“无”，让屏幕容纳更多条目，减少暂停需要。'],
                ['按任务调整列表行', '见 §5.3。“显示”决定外观（标题／副标题行、附加项），“筛选”决定显示谁。公共场所可关闭副标题行；复制 MAC 时将标题设为 MAC；观察信道时开启频率。'],
                ['记录观测', '见 §12.12。观测总结提供报告，观测导出提供当前窗口清单，AI 导出提供聊天提示词，日志导出提供会话记录。长途驾驶时每次停靠都生成观测总结（§11.4.1）。'],
                ['靠近一个 BLE／追踪器条目', '参见 §12.8（追踪器）或 §12.13（信号追踪页）。移动时参考更近／更远，身体遮挡转身只能提供候选方位，不提供米数。'],
                ['不知道应追踪哪个标签', '见 §12.8。仅显示寻物标签，隐藏自有装备，在每个可能藏匿位置（车轮、保险杠、车厢）停留手机。选择顶部条目开始信号追踪，重复检查。结果不能证明现场没有设备。'],
                ['“!”／读卡器／渗透测试装备', '见 §12.14。业余 BLE 串口模块以及 Pineapple／Flipper／Pwnagotchi／Marauder／Porkchop 有重点关注标记，但这不是盗刷器检测器。打开详情并目视观察，未检出不代表没有问题。'],
            ],
            [1.8 * inch, 4.7 * inch],
        ),
        P('12.11 列表难以阅读', "h2"),
        P(
            '列表繁忙不等于显示了错误的设备。先减少每行信息，再隐藏设备。“显示”决定每个设备展示多少内容，“筛选”决定哪些设备出现在列表，两者均不影响日志。'
        ),
        bullets([
            '无法点按条目时先暂停，无线扫描仍会继续。',
            '在实时页面打开“显示”（调整图标），将副标题行设为“无”，每行只保留一行标识，屏幕可容纳更多条目；随机地址／已离开标记移至标题。关闭 RSSI 信号条、频率、首次／末次发现；特征标签太多时也可关闭特征名称。公共场所优先使用按信号强度排序的列表，而不是混合视图。',
            '标题默认已是 MAC。如果“Apple, Inc. · …”等类型推测挤占副标题行，将其设为广播名称或无。',
            '设备仍过多时，再使用筛选。提高 RSSI 下限，选择强信号预设（−70 dBm）或把滑块设为 −80。可仅显示匹配特征、隐藏寻物标签类别，或隐藏单个特征系列。',
            '不要叠加所有筛选。列表变空时，撤销最后增加的条件。',
            '仅在不需要文件时关闭日志。拥挤场景容量为 400；超过约 3 分钟的未命名 BLE 可能已从实时画面移除，但只要曾写入，仍保留在日志中。',
        ]),
        P('12.12 观测结束后：报告与 AI 导出', "h2"),
        P(
            '观测总结、观测级 AI 导出、候选特征、日志导出、保存及重置／清除日志位于<b>报告</b>页。GPS 标记、在线地名和日志开关仍在设置页。<b>设备详情</b>页另有两种分享方式（§5.5）：文本分享和仅分析<i>该设备</i>的 AI 导出。观测级总结和 AI 导出来自实时数据表中最近 15 分钟，约 400 个设备，硬上限 900；实时视图和筛选不影响它们。驾驶时内存如何增长和淘汰见 §11.4.1：应多次生成观测总结，持续随行的设备会保留。只要开启定位标记并发生移动，该报告就包含可能被放置的追踪器随行判断。候选特征从轮转日志提取未匹配系列（§5.6.4、§11.5）。分享面板打开时扫描继续。所有分享内容都应视为现场敏感信息。'
        ),
        table(
            ['分享方式', '内容', '适用场景'],
            [
                ['观测总结（文本）', '纯文本观测报告，包含距离、到访位置、观测备注、跟踪评估（最近 15 分钟，忽略实时视图／筛选）、环境、清单、行动建议和要点，支持自定义名称。位于报告页。', '步行结束后判断是否有设备随行，写入笔记、Signal／短信或日志本。内容与 PDF 相同。'],
                ['观测总结（PDF）', '同一观测报告，采用 Letter 纸张排版：FIELDWATCH 页眉、编号章节、到访位置之后的观测备注；非空的“随行的疑似追踪器／疑似尾随”列表以琥珀色提示框呈现，每项重点关注备注也有独立琥珀色框；另有全宽轨迹图（OSM／停留／编号命中）和要点框。跟踪评估不受实时视图或筛选影响。', '交给他人、归档观测或打印，比纯文本更便于阅读。'],
                ['对比（文本／PDF）', '仅按无线类型与 MAC 对比本次观测和第二次已保存观测中的出现情况，支持自定义名称。观测备注位于时间窗口之后；两次都有 GPS 时，PDF 显示叠加轨迹。', '对比两个房间、两天，或最近 15 分钟与命名观测（内存约 400 个，观测 6000 个）。'],
                ['AI 导出（报告）', '观测级分析<i>提示词</i>：原样嵌入机内观测总结，附紧凑工作表，包含 5／15 分钟速率、RSSI 区间、重点关注、观测备注和寻物标签 ID。要求提供补充分析，不重写报告，也不重复清单。', '需要聊天模型查看数字、检验跟踪提示时粘贴使用，不是法律意见书。'],
                ['候选特征', '报告页中的日志挖掘功能，重新匹配轮转日志，列出至少两个设备共享独特广播 ID 的未匹配系列。“创建特征”生成带共同规则、不绑定 MAC 的草稿。保存后返回列表并重新分析，可离线使用。', '开启日志完成观测后，查找值得建立自定义特征的重复名称通配模式／厂商 IE／OUI，并非列出每个未知设备。见 §5.6.4、§9.2.1、§11.5。'],
                ['日志导出', '报告 → 日志导出。格式包括 CSV、JSON lines、GPX、KML、WiGLE；无线类型可选两者／Wi-Fi／BLE。轮转文件为 JSON lines。地图标记表示本机位置，Fieldwatch 不上传数据。', '用于事后文件、表格、Google Earth，或由你自行发起的 WiGLE 上传。'],
                ['观测导出', '报告 → 观测导出，格式选项与日志导出相同。所选观测或最近 15 分钟中的每个唯一设备各占一行。CSV／JSON lines 包含匹配特征及重点关注系列；日志可保持关闭。GPX／KML 包含操作者轨迹。它不是轮转日志。', '将本次行走的设备清单导入表格或 Google Earth，无需带上全天日志。'],
                ['文本分享（详情）', '将当前打开设备的详情页导出为纯文本。', '用于笔记、工单，或单独保留一个 MAC／载荷，无需分享整次观测。'],
                ['AI 导出（详情）', '关于<b>一个</b>设备的提示词：详情转储及注册表／格式解码任务，适用与观测级 AI 导出相同的免责声明。', '用于询问“这是什么 AP／标签／芯片？”不要当作随行检测；随行判断应在移动后查看报告中的观测总结。'],
                ['信号追踪（详情，BLE）', '显示更近／更远指针、围绕“你”的圆环和追踪趋势线。约 −45 dBm 或更强时显示非常近。底部有类似盖革计数器的提示音／振动，可选择用身体遮挡估计方向。建筑结构会遮挡和反射信号。', '用于靠近房间、包或车内的单个 BLE；不提供米数，也不是随行检测，见 §12.13。'],
            ],
            [1.45 * inch, 2.3 * inch, 2.75 * inch],
        ),
        P('<b>如何搭配操作方案</b>', "body_left"),
        bullets([
            '<b>§12.2 是否被跟踪？</b>开启 GPS 标记，移动约 50 米，再生成观测总结。查看“随行的疑似追踪器”和“疑似尾随”；其范围是最近 15 分钟内存数据，不受实时视图或“随行”开关影响。较长步行或驾车途中，应在下一停靠点再次生成（§11.4.1），持续随行设备仍会保留。需要聊天模型结合速率和设备组合检验提示时用 AI 导出，并要求不要重写观测总结、不要把整次观测都在的设备一概视为自己的、不要列出仅路过的设备。',
            '<b>§12.3 房间里来了新设备？</b>查看观测总结的持续出现／首次发现，或 AI 导出中 5 分钟与 15 分钟首次发现计数。“仅新发现”筛选不改变报告。',
            '<b>§12.4／§12.7 系列与摄像头。</b>查看观测总结中的特征命中。观测 AI 导出提供重点关注 ID 和系列计数，详情 AI 导出分析单个设备载荷。摄像头观测的提示词中应保留 §7.6.1。',
            '<b>§12.5 已隐藏的干扰。</b>仍在观测总结、AI 导出和日志里；实时画面清静了，文件记录仍完整。',
            '<b>§12.6 自己的标签？</b>比较观测总结中的“随行的疑似追踪器”（自己的或预先放置的，需要解释来源）与“疑似尾随”。AI 导出包含相同判断。',
            '<b>§12.8 追踪标签。</b>仅显示寻物标签。不知道选哪行时，将手机停留于可能藏匿的位置（车轮、保险杠、车厢），直到某行升至顶部，再开启信号追踪。通过移动和身体遮挡缩小范围。建筑结构会遮挡信号，结果不能证明现场没有设备。',
            '<b>§12.9 SSID／OUI 线索。</b>用观测总结查看本次 Wi-Fi 清单，通过“报告 → 对比观测”按无线类型和 MAC 对比当前窗口与第二次已保存观测。需要文件时仍可用日志导出比较 BSSID。相同未匹配名称通配模式或厂商 IE 反复出现时，查看候选特征。',
            '<b>特征库有遗漏？</b>打开未匹配设备，详情中的“特征系列”提供单设备检查（强候选／可能／仅此设备）。开启日志后，在“报告 → 候选特征”查看整个观测中的重复未匹配名称通配模式、厂商 IE 或稳定 OUI。创建并保存特征后，实时画面应在下次接收时标注。不要用住宅 SSID 或通用芯片模块 OUI 建立宽泛特征。',
            '<b>§12.14 重点关注／渗透测试装备／读卡器提示。</b>查看观测总结的重点关注章节与 PDF 琥珀色提示。详情分享和 AI 导出会引用“重点关注”。应告诉聊天模型：“这是模式匹配，不是盗刷器检测器，也不证明正在发生攻击。”',
        ]),
        P(
            '<b>在线地名与地图</b>默认开启，适用于观测总结、AI 导出和轨迹瓦片。离线时仅提示，不报错，也不提供街道名称。移动距离无需联网。不希望聊天粘贴内容包含地址时，请关闭。',
            "body_left",
        ),
        P(
            '可用表格比较多次到访中的 OUI 和名称。反复出现的 BSSID 通常是固定设施。观测总结中的“疑似尾随”及 AI 根据导出内容生成的任何说法，都只是进一步查看的线索，不是结论。',
            "body_left",
        ),
        P('12.13 信号追踪：靠近一个 BLE 设备', "h2"),
        callout(
            '相对信号强度，不是位置追踪器',
            '信号追踪为单个 BLE 广播设备提供类似无线电测向竞赛的强弱指针，不测量米数、不提供罗盘方位，也不识别人。随机地址可能在追踪中途消失。没有“更近”提示不能证明设备已离开。不要用本页判断人身安全，参见声明页。',
            "warn",
        ),
        P(
            '<b>何时使用。</b>你已经确定<b>一个</b>关心的 BLE 条目，如标签、强信号未命名 LE 或音箱。打开详情 → 信号追踪。Wi-Fi AP 没有此按钮：系统约每 30 秒才批量更新，快速扫描生效时约 8 秒，仍不适合信号追踪。合理范围是房间、包、车辆或同一楼层；隔着停车楼墙体时会误导。',
            "body_left",
        ),
        P('<b>准备。</b>使用高性能模式，全程保持同样握姿、同一只手和相同倾角。本页会保持屏幕常亮。改变握姿或完成身体遮挡转身后重置本次追踪，避免将步行与转身数据比较。日志和 GPS 标记可保持开启；在人群密集处会增加负担，指针延迟时可关闭。', "body_left"),
        figure_wrap(
            "fig-hunt.png",
            '图 5（再次展示）：信号追踪。',
            '<b>移动。</b>缓慢步行，观察“更近／更远／大致相同”（数秒内约 3 dB 变化）、“你”周围的圆环（向内表示更强，向外表示更弱）及本次最强信号。“提示音／振动”位于重置和返回按钮下方，默认关闭；启用后按最近 RSSI 发出盖革式节奏，越强越快，安静或离开时停止。启用提示音却听不到时，提高媒体音量。非常近（约 −45 dBm 或更强）表示应查看此处的口袋、包或手中，不是卷尺测距。显示安静时先停下，可能是墙体而非方向错误。从实时画面消失时，可能是 MAC 轮换或设备离开；返回实时页面，若同一系列出现新条目，再开启追踪。不要把 dBm 换算成英尺。',
        ),
        P(
            '<b>身体遮挡方向（可选）。</b>手机没有 DF 测向功能。躯干是有损屏障，原理类似将鞭状天线靠近身体并旋转寻找峰值。站定，将手机贴胸口中央或始终放同一口袋，缓慢转完整一圈。观察本次最强信号和大号 RSSI，而非实时雷达角度；后者来自 MAC 哈希，不代表北向。峰值方向往往是身体遮挡最少的方向，大致朝向设备，但反射、金属或第二个信号源都可制造假峰。重复一圈，将方向视为数十度范围，而非精确罗盘。随后重置本次追踪，沿该方向移动并观察更近／更远。这不是 UWB 精确查找，也不应把该方位记录为事实。',
            "body_left",
        ),
        P(
            '<b>结构会改变指针。</b>信号追踪读取的是到设备的一条传播路径，并非真空环境。墙、楼板或门可在真实距离不变时使 RSSI 下降 10–20 dB；安静或更远可能只是走到砖石结构后方。金属影响更强：车身、文件柜、电器、带铝箔保温层及电梯会反射和遮挡，转身所得最强方向可能是面包车的反射，不是源头。水和人体吸收信号，人群隔在中间看起来像距离增加。混凝土和钢筋（停车楼、地下室）会散射 2.4 GHz，门口的趋势峰值常是结构中的通道。玻璃比砖墙影响小，两层楼就足以造成“更远”假象。保持握姿；拳头盖住天线相当于另一堵墙。不要把一次峰值当定位点；走动、转身，观察经过下个开口后“更近”是否仍成立。',
            "body_left",
        ),
        P(
            '<b>不可据此断定。</b>不能断定距离、对应人员，不能因追踪变安静就认为安全；载荷不再匹配时，不能断定两次追踪的轮换 MAC 属于同一标签；靠近金属或墙体时，也不能把最强方向当真实方位。',
            "body_left",
        ),
        P(
            '<b>记录结果。</b>在详情中对该设备使用文本分享或 AI 导出。如果问题是是否随行，无论处于信号追踪还是雷达视图，“报告 → 观测总结”仍有最近 15 分钟的跟踪评估（§12.2）。该评估不用于在房间里找包内标签。',
            "body_left",
        ),
        P('12.14 重点关注：读卡器与渗透测试装备', "h2"),
        callout(
            '不是盗刷器检测器，也不是攻击证据',
            '实时页面的“!”表示匹配特征填写了重点关注内容。它是公开广播的模式，不代表人员、被安装的盗刷覆盖装置，也不能认定正在犯罪。同样的业余 BLE 模块也用于打印机、汽车和 DIY。渗透测试固件可改名或静默，未匹配不代表没有问题。请目视观察。Fieldwatch 不建立连接，也不尝试 PIN，参见声明页。',
            "warn",
        ),
        P(
            '<b>问题。</b>这里是否有被特征库标为重点关注的设备，例如读卡器旁的低价 BLE 串口模块，或使用默认名称的渗透测试 AP／Flipper／握手采集器？看到标记后实际应做什么？',
            "body_left",
        ),
        P('<b>准备。</b>', "body_left"),
        numbered([
            '特征库中的业余 BLE 串口、Hak5 Pineapple、Flipper Zero、Pwnagotchi、Marauder／Deauther 和 Porkchop 已填写重点关注。某名称在本地只是干扰时，可在筛选页隐藏。',
            '实时页面选择全部流量和按信号强度排序的列表，或混合视图。“!”是重点关注标记，与编辑器的备注字段不同。',
            '可选：先查看房间概况，若只关心这些系列，再开启“仅匹配特征”。不要一开始就筛掉其他设备，否则会漏看未匹配设备。',
            '点按带“!”的条目，阅读详情中的重点关注。需要 MAC 再次出现时提示，可关注它。仅 BLE 支持信号追踪，可用于判断更近／更远（§12.13）。',
        ]),
        P(
            '<b>预期画面。</b>只有<i>已匹配</i>特征包含重点关注文字时，才显示“!”。详情显示完整提示，观测总结和 AI 导出引用该内容，PDF 对每次命中绘制琥珀色提示。重点关注为空则没有标记。',
            "body_left",
        ),
        table(
            ['系列', 'Fieldwatch 能接收到的内容', '实际限制'],
            [
                ['业余 BLE 串口', 'BLE 名称 HMSoft／HM-10／CC41／AT-09／JDY／BT05／ESP32 BLE。重点关注提示：同类板卡曾用于部分加油机／ATM 覆盖装置。', '不包括经典蓝牙 HC-05／HC-06，Fieldwatch 看不到经典蓝牙。同样模块也用于打印机、汽车和 DIY。读卡器旁有强信号时应目视检查，不构成盗刷器证据；未检出也不能排除，因为可能改名、使用经典蓝牙或蜂窝网络。'],
                ['Hak5 Pineapple', '设置用 SSID：Pineapple_XXXX／Hak5／WiFi Pineapple。', '匹配管理 AP，不按 Alfa OUI 00:C0:CA 匹配。PineAP 克隆看起来像普通咖啡馆 SSID；改名或只运行克隆时会漏检。'],
                ['Flipper Zero', 'OUI 0C:FA:22；BLE 名称 Flipper*。', '较新设备使用该 IEEE OUI。自定义固件可修改名称和 MAC，关闭蓝牙会漏检。匹配不是攻击证据。'],
                ['Pwnagotchi', '经典 BSSID de:ad:be:ef:de:ad；名称 pwnagotchi。', '握手采集器信标。自定义 MAC／名称会漏检。'],
                ['Marauder / Deauther', '默认名称 MarauderAP／Marauder／Deauther。', 'ESP32 Marauder 或 Spacehuhn 风格的默认值。同样板卡也用于 DIY，改名会漏检。'],
                ['Porkchop', 'SSID／名称 PORKCHOP；BACON 伪 AP 厂商 IE 50:52:4B。', 'M5PORKCHOP Cardputer 或 CYD 移植版。不按 Espressif OUI 匹配。BLE 垃圾广播（仿 Apple／Android）不匹配。仅被动运行或没有 AP 时会漏检。'],
            ],
            [1.35 * inch, 2.45 * inch, 2.7 * inch],
        ),
        P(
            '<b>不能说明什么。</b>这不是盗刷器扫描器，也无法检测仅通过 USB 工作的 Hak5、改名固件或静默设备。执法记录仪／眼镜／录音录像可穿戴设备（Axon、WatchGuard Video、Ray-Ban／Meta、Snap Spectacles、Fieldy、Plaud Note）的重点关注也使用同一“!”；这些系列见 §9.5 和附录，不属于本方案。Fieldwatch 从不连接设备。不要把“!”视为身份确认，也不要据此触碰别人的装备。',
            "body_left",
        ),
        P(
            '<b>记录结果。</b>使用详情中的文本分享或 AI 导出分析单个设备，转储以“重点关注”开头。整次观测可生成观测总结，需琥珀色提示时选 PDF；或用 AI 导出并要求模型“遵循 §12.14；重点关注是模式匹配，不是盗刷器检测器，也不是攻击证据”。筛选不会缩小观测总结。未脱敏前不要粘贴到公开聊天。',
            "body_left",
        ),
        P('12.15 在 ATAK 上叠加显示（TAK／CoT）', "h2"),
        callout(
            '向局域网发送坐标',
            '此方案会向你设置的主机与端口监听者发送完整 MAC 和坐标。必须关闭隐私模式，否则 Fieldwatch 不发送。组播仅在当前 Wi-Fi 局域网内传播。这不是安全态势图、无线测向或 Remote ID 拦截器，见 §5.8。',
            "warn",
        ),
        P(
            '<b>问题。</b>能否不开发 Remote ID 插件，也不让 ATAK 学习 Fieldwatch 格式，就把重点关注设备和飞行中的 Remote ID 显示在团队使用的同一张地图上？',
            "body_left",
        ),
        P('<b>准备。</b>', "body_left"),
        numbered([
            '手机与 ATAK（或 WinTAK／iTAK）连接同一 Wi-Fi，确认 AP 未隔离客户端。组播始终收不到时，将主机改为 ATAK 设备的 IPv4。',
            'ATAK 已为 SA 监听 UDP 239.2.3.1:6969，无需 Fieldwatch 插件。此推送使用 UDP，不登录 TAK 服务器。',
            '在 Fieldwatch 设置中关闭隐私模式。需要“此处接收”标记时，开启 GPS 标记并使用高精度定位；Remote ID 广播位置不需要本机 GPS。',
            '开启“设置 → TAK／CoT 推送”。此手机上的 ATAK CIV 选择“本机”，同一 Wi-Fi 中其他 ATAK 选择“局域网组播”。开启重点关注和载荷位置，关闭关注列表和全部特征。确认主机字段下的推送状态显示已发送，而非错误。',
            '实时页面使用全部流量和高性能。如果还关心执法记录仪／眼镜，不要只筛选无人机；推送虽忽略实时筛选，但这些设备仍需完成特征匹配。',
        ]),
        P(
            '<b>预期画面。</b>收到符合条件的广播后几秒内，ATAK 显示标记。重点关注设备（Axon、眼镜、Flipper、Pineapple 等）标在最强接收时<i>你的</i> GPS 位置；靠近时更新，走远时保持。Remote ID 位置标在 BLE FFFA 或带 FA:0B:BC 厂商 IE 的 Wi-Fi AP 信标（Android 11+）中<i>广播</i>的飞行器经纬度，显示黄色无人机。下一条 Basic ID 不会清除位置；一旦收到 UAS ID，该飞行器就保持一个随位置移动的标记。位置消息中的航向和速度写入 ATAK 轨迹，使图标可指向航向。解码出的操作员位置显示为第二个橙色标记。“此处接收”的呼号以“（此处）”结尾。点按标记可查看名称、MAC、RSSI、特征等备注。离开的设备会从 ATAK 移除，不再停留两分钟。',
            "body_left",
        ),
        table(
            ['如果出现…', '则…'],
            [
                ['地图没有内容', '可能开启了隐私模式、总开关关闭、局域网不对，或尚无重点关注／Remote ID 广播。打开实时画面确认有“!”或 Remote ID 标签。组播被过滤时，尝试向 ATAK IP 单播。'],
                ['标记位于我身上，而不是无人机上', '该设备没有广播经纬度，或载荷位置已关闭。“此处接收”功能正在正常工作。Remote ID 需要 BLE FFFA 或 Wi-Fi 厂商 IE FA:0B:BC（Android 11+）中的位置消息。'],
                ['此处接收标记停在信号更强的位置', '符合预期。标记保留最接近、RSSI 更强时的位置，而非最后接收点。约每 10 秒发送保活，刷新相同经纬度。这不是测向。'],
                ['无人机标记距离数公里', '广播位置出现这种情况是正常的。Fieldwatch 没有对它测向，WGS84 坐标由飞行器自行编码。'],
                ['咖啡馆 AP 填满地图', '说明“全部特征”已开启，请关闭。现场默认组合是重点关注加载荷位置。'],
                ['约两分钟后标记消失', '设备已离开接收范围、扫描停止，或 Fieldwatch 发送了离开事件。仍需观测时重新启动扫描。'],
                ['想把包中的一个标签放到地图上', '开启关注列表，关注该 MAC 并打开警报。重点关注可保持开启，不要使用全部特征。'],
                ['自定义传感器在广播中提供经纬度', '解码字段使用 ID latitude 和 longitude，并按规范设置倍率。开启载荷位置，无需额外 TAK 复选框。见 §5.8.4、§9.6。'],
            ],
            [2.0 * inch, 4.5 * inch],
        ),
        P(
            '<b>不能说明什么。</b>不能替代团队 SA；Fieldwatch 不是你的自身位置标记。不支持 Wi-Fi NAN Remote ID 或加密广播，也不提供距离圈。筛选、暂停和显示设置不改变推送；扫描通知中的停止按钮会停止发送。BLE FFFA 静默时，含位置消息的 Wi-Fi 信标仍可标出飞行器。',
            "body_left",
        ),
        P(
            '<b>记录结果。</b>ATAK 提供实时叠加图，Fieldwatch 仍可通过观测总结／日志导出生成观测文件。CoT 备注不是报告。分享地图截图时请记住 MAC 是完整的，因为发布时隐私模式已关闭。',
            "body_left",
        ),
        P('12.16 接收 Remote ID（BLE 与 Wi-Fi）', "h2"),
        callout(
            '广播位置，不是测向',
            'Remote ID 标记来自飞行器编码的位置，可能离你数公里。Fieldwatch 不测距也不测向，见 §5.8.3。',
            "note",
        ),
        P(
            '<b>问题。</b>Fieldwatch 能否通过蓝牙和 Wi-Fi 标注飞行中无人机的数字号牌，以及何时会在 ATAK 上变成移动标记？',
            "body_left",
        ),
        P('<b>准备。</b>', "body_left"),
        numbered([
            'Wi-Fi RID 依赖厂商 IE，需要 Android 11+；Android 10 仍可接收 BLE FFFA。',
            '实时页面使用全部流量和高性能。同次行走也要关注重点关注设备时，不要仅筛选无人机。',
            'TAK 设置：关闭隐私模式，开启载荷位置和重点关注。飞行器广播位置标记无需本机 GPS 标记，见 §12.15。',
            '悬停或慢速飞过比快速掠过更容易接收，系统 Wi-Fi 扫描采用批处理。',
        ]),
        P(
            '<b>预期画面。</b>BLE FFFA 或含 FA:0B:BC 厂商 IE 的 Wi-Fi AP 信标进入接收范围时，实时页面出现 Remote ID 标签。随着消息类型轮换，详情解码字段可显示 UAS ID、自述 ID、位置经纬度／高度、航向以及操作员经纬度。在信号强度列表、混合、时间线或按类别视图中，位置消息还会显示未声明、地面、空中、紧急状态或 RID 故障；紧急状态更醒目。TAK 将位置显示为黄色无人机；Basic ID 固定 uid，使一个标记随飞机移动；System 可增加橙色操作员标记；航向／速度使飞行器图标指向相应方向。Skydio／Autel／Parrot 名称条目仍是设置／遥控无线设备，飞行中的数字号牌对应此 Remote ID 条目。',
            "body_left",
        ),
        table(
            ['如果出现…', '则…'],
            [
                ['BLE 有标签，Wi-Fi 没有', '符合预期。许多飞行器同时使用两者；Fieldwatch 的 Wi-Fi 接收路径是含 FA:0B:BC 的 AP 信标，不是 NAN。'],
                ['Wi-Fi AP 已标为 Remote ID，但暂无经纬度', '等待该信标包中的位置消息。Basic ID 包含 UAS ID，不包含地图位置。'],
                ['Android 10 的 Wi-Fi 没有结果', '符合预期，厂商 IE 需要 Android 11+。BLE FFFA 仍可使用。'],
                ['快速飞过，没有 Wi-Fi 标签', '受到系统扫描节流限制。减速或悬停更易接收，BLE 仍可能捕获 FFFA。'],
                ['ATAK 上出现一群 BLE 点', '尚未收到 UAS ID。第一条 Basic ID 会将 uid 归并到一个标记。'],
                ['标记远在数公里外', '那是飞行器广播的 GPS，不是 Fieldwatch 的定位结果。'],
                ['没有地面／空中／紧急状态标签', '保存的广播不是位置消息，或位置消息位于尚未拆分的 BLE 包内。等待下一条位置广播，Wi-Fi 包仍可能显示状态。'],
            ],
            [2.0 * inch, 4.5 * inch],
        ),
        P(
            '<b>不能说明什么。</b>不是机尾注册号，不是 DJI OcuSync，也不是 Wi-Fi NAN。BLE FFFA 与带 FA:0B:BC 的 Wi-Fi AP 信标均可解码，支持协议版本 0–2；不同打包形式仍可能漏检。',
            "body_left",
        ),
        P(
            '<b>记录结果。</b>单个设备使用详情文本分享，包含解码字段。整次观测使用报告中的观测总结。TAK 是实时叠加图（§12.15），发布需关闭隐私模式。',
            "body_left",
        ),
    ]

    # 13 Field hygiene
    flow += [
        PageBreak(),
        P('13. 现场使用习惯', "h1"),
        P(
            '第 12 章介绍操作方案，本章说明执行这些策略时如何让手机持续采集。'
        ),
        P('13.1 探测质量', "h2"),
        bullets([
            '不要把手机放进近似法拉第屏蔽袋的包中，也不要放在金属仪表台上。',
            '身体遮挡确实存在，身后的 BLE 标签可能弱 10–20 dB。',
            '5 GHz AP 的范围较短；它们消失而 2.4 GHz 仍在，往往是传播条件，并不代表对方关机。',
            'Wi-Fi 数量不再更新时，可能是系统节流或定位中断。API 30+ 的设置页会显示节流提示。',
            '飞行模式下手动重新开启 Wi-Fi 和蓝牙，可减少蜂窝无线干扰，但并非必需，部分厂商系统也可能处理异常。',
        ]),
        P('13.2 电池、屏幕与后台', "h2"),
        P(
            '有两种目标。若在观测或驾车时希望获得系统允许的每次扫描，请按 §4.5 使用高性能、屏幕常亮、后台不受限制，并可选快速 Wi-Fi，同时接受耗电。本节讨论画面稳定后，全天使用或放入口袋时的折中。'
        ),
        bullets([
            '开始时用高性能（§4.5），画面稳定后若需续航可降到均衡。省电适用于过夜或随包携带，但会漏掉短促 BLE 广播。',
            '设置中的<b>保持屏幕常亮</b>默认开启，在 Fieldwatch 位于前台时防止三星熄屏后暂停 BLE。放入口袋时可关闭。',
            '<b>允许后台运行</b>打开 Fieldwatch 的电池页面及对应开关；<b>电池使用不受限制</b>打开同一页面，应选择“不受限制”。部分手机（包括三星）不直接显示该选项，需要点按“允许后台运行”进入再选择。后台运行允许应用不在前台时继续扫描，不受限制可防止厂商为省电而冻结它。Fieldwatch 开关反映这些 Android 授权，不会保持屏幕常亮，也不会解除 Wi-Fi 或 BLE 扫描配额。三星还需在后台使用限制中避免将 Fieldwatch 加入休眠，见 §4.5.3。',
            '<b>夜间模式</b>位于设置 → 外观，提供红色现场显示。',
            '如果全天都需要低延迟 BLE，廉价 USB 移动电源通常比反复调整省电滑块更实用。',
        ]),
        P('13.3 拥挤公共场所', "h2"),
        P(
            '繁忙街道可能产生数万条 BLE 广播和数千个轮换 MAC。若曾出现列表清空、手机卡住，可能是堆达到 256 MB 上限后，三星又暂停扫描器。当前版本限制实时集合、批量处理接收并丢弃溢出广播，因此仍可看到繁忙列表，但不保留每个随机地址。界面负担较重时，优先使用信号强度列表而非混合视图；不需要文件时可关闭日志。'
        ),
        P('13.4 伦理与法律考量', "h2"),
        P(
            'Fieldwatch 只处理设备向范围内所有接收者公开广播的信号，但这不代表任何用途都合法或适当。你有责任遵守当地关于无线截获、跟踪和记录的法律，尤其是：'
        ),
        bullets([
            '不要利用匹配结果骚扰、尾随或曝光他人隐私。',
            '没有佐证时，不要在报告中把 LiteOn OUI 宣称为“Flock 摄像头”。',
            '不要尝试访问、禁用或篡改观测到的基础设施。',
            '日志可能包含邻居手机和电视的 MAC，应将导出文件视为敏感数据。',
            '所在场所限制无线监测时，请离开。',
            '不要在涉及安全判断的场景使用 Fieldwatch。仅供实验使用，参见声明页。',
        ]),
        callout(
            '操作安全',
            'Fieldwatch 不会隐藏手机 Wi-Fi 和蓝牙已开启的事实。除非修改通知渠道设置，锁屏上会显示扫描通知。应用不提供匿名性。',
            "warn",
        ),
    ]

    # 14 Technical specifications / How it works
    flow += [
        PageBreak(),
        P('14. 技术规格与工作原理', "h1"),
        P(
            '本章介绍处理流程，不逐一罗列 Kotlin 文件。一次接收是本机听到 Wi-Fi AP 信标或 BLE 广播；Fieldwatch 在本机完成匹配、绘制实时画面，并可记录观测、生成总结或推送 TAK。没有 Fieldwatch 服务器。'
        ),
        P('14.1 从空中信号到列表条目', "h2"),
        P(
            '从左到右经过六个阶段，然后处理下一条。筛选在实时页面隐藏设备，“显示”（调整）隐藏条目中的字段；匹配、日志和观测总结仍可使用已接收数据。先看图 20，再参阅 §7（接收）、§9（匹配）、§8（筛选）、§5.3（显示）、§10（关注）、§11（日志／观测／总结）和 §5.8（TAK）。'
        ),
        diagram(
            "how-it-works.png",
            "图 20：一次接收如何成为列表条目。源码路径位于 <font face='FWText'>app/src/main/java/app/fieldwatch/</font> 下。",
        ),
        PageBreak(),
        P(
            '以下按顺序介绍六个阶段，章节编号可跳转至对应现场说明。'
        ),
        numbered([
            '<b>无线广播。</b>包括 Wi-Fi AP 信标（SSID、BSSID、信道、厂商 IE）和 BLE 广播（名称、公司 ID、服务 UUID、制造商数据）。仅接入别人网络的笔记本不会显示。Fieldwatch 接收 BLE 无需配对或连接，见 §1.1、§3.1、§7.1–7.2。',
            '<b>ScanService。</b>前台服务通过常驻“Fieldwatch 正在扫描”通知运行。返回主屏幕会继续，划掉应用或点按停止则结束。Wi-Fi 批量扫描，高性能约每 30 秒请求一次，受系统上限约束；期间 BLE 持续接收。见 §4.5、§7.1、§10.3。',
            '<b>特征库匹配。</b>SignatureEngine 根据 OUI、名称通配符、UUID 和制造商数据，对内置包及自建条目评分。匹配后，解码字段将明文 BLE 字节映射为含义，加密广播保留十六进制。见 §7.3–7.4、§9、§9.6。',
            '<b>实时与调整。</b>FilterEngine 决定实时页面出现哪些设备。右上角调整按钮打开显示设置，包括雷达、信号强度列表、时间线、混合、按类别以及排序和字段。实时容量约 400 个设备，见 §4.4、§5.3、§6、§8。',
            '<b>关注列表与信号追踪。</b>关注特征后可播放提示音和／或语音。重点关注系列和无人机默认已关注。信号追踪按 RSSI 引导接近单个 BLE。命名设备是单 MAC 别名，可选警报。见 §5.5、§10、§12.8、§12.13。',
            '<b>日志、观测、TAK。</b>日志在磁盘轮转。观测是全部已接收设备的命名时间窗口；观测总结和 AI 导出使用进行中的观测、选中的已保存观测，或最近 15 分钟。TAK／CoT 默认关闭。隐私模式隐藏屏幕敏感信息并暂停推送，日志仍保留完整 MAC 和 GPS。见 §5.6–5.8、§11。',
        ]),
        P('14.2 并非故障的限制', "h2"),
        P(
            '原生 Android 不向 Fieldwatch 提供 Wi-Fi 客户端、经典蓝牙查询、蜂窝／LTE／C-V2X 或方位。这些缺失来自平台，不是安装损坏。完整列表见第 3 章，API 见第 7 章。快速 Wi-Fi AP 扫描（§7.1.1）是可选方式，需要先在开发者选项关闭系统扫描节流，才能缩短批次间隔。'
        ),
        P(
            '离线优先：配置、特征、关注、日志和观测保存在应用私有目录。“设置 → 从 GitHub 更新内置特征库”仅在你发起时覆盖内置条目，关注数据保留本地。无账号、无遥测、无 Fieldwatch 云端，见 §1.2、§5.7、§9.3。'
        ),
        P('14.3 各部分的源码位置', "h2"),
        table(
            ['阶段', '源码树（app.fieldwatch 下）'],
            [
                ['Wi-Fi／BLE 无线接收', 'radio/WifiRadio.kt, BleRadio.kt'],
                ['前台扫描', 'radio/ScanService.kt, Permissions.kt'],
                ['特征库匹配', 'domain/SignatureEngine.kt, DefaultCatalog.kt'],
                ['实时与调整', 'ui/LiveScreens.kt, FieldwatchAppUi.kt, domain/FilterEngine.kt'],
                ['关注列表／信号追踪', 'alert/Alerter.kt, domain/Hunt.kt, domain/RadioBookmarks.kt'],
                ['日志／观测／TAK', 'data/LogStore.kt, data/SitStore.kt, domain/TakPublish.kt'],
                ['设置／特征库下载', 'ui/screen/SettingsScreen.kt, data/ConfigStore.kt, data/CatalogRemote.kt'],
            ],
            [2.2 * inch, 4.3 * inch],
        ),
        P(
            '这张对应表供对照本手册阅读源码时使用，运行应用不需要了解它。现场遇到问题时，仍应使用第 12 章的操作方案。'
        ),
    ]

    # Appendix
    flow += [
        PageBreak(),
        P('15. 附录', "h1"),
        P('A. 术语表', "h2"),
    ]
    flow.append(table(
        ['术语', '定义'],
        [
            ['AP', 'Wi-Fi 接入点。Fieldwatch 的每个 Wi-Fi 条目都属于此类，包括路由器、热点、网状节点和软 AP，不报告已关联客户端。实时页面中对应副标题行开头的小 Wi-Fi 图标，不是圆圈或双字母标签。详情明确写出“Wi-Fi 接入点”。副标题行设为无时，第二行及图标一起隐藏。见 §1.1、§5.4。'],
            ['LE', '低功耗蓝牙广播设备，包括耳机、手机、标签和未命名 BLE 条目。Fieldwatch 只监听，探测无需配对。实时页面中对应副标题行开头的小蓝牙图标，不是圆圈或双字母标签。详情明确写出“BLE 广播设备”，见 §1.1、§5.4。'],
            ['类别图标', '出现在实时条目的圆圈、筛选类别选项和按类别标题中。表示首个匹配特征的类别，未匹配时为问号，用于快速辨识。无线类型则由副标题行中的 Wi-Fi／蓝牙图标表示，见 §1.1、§5.4、§9.5。'],
            ['BSSID', '扫描结果中的 AP MAC 地址。完整 MAC 前缀规则对应的就是该 BSSID。'],
            ['公司 ID', 'AD 类型 0xFF 中的 16 位 Bluetooth SIG 制造商标识，可离线查询约 4012 个名称。'],
            ['CoD', '蓝牙设备类别。24 位主类别／子类别／服务类别位字段，由广播或系统协议栈提供时解码。'],
            ["BLE", '低功耗蓝牙。其广播是无需连接的数据包。'],
            ['经典蓝牙', 'BR／EDR，包括耳机、文件传输、HC-05／HC-06 串口。Fieldwatch 不执行经典蓝牙查询。双模 BLE 设备可能在标志位或 CoD 中声明经典蓝牙能力，但这不等于经典蓝牙扫描。见 §2.2、§3.5、§7.2。'],
            ['特征', '具有名称的一组匹配规则，可附加聚类标志。'],
            ['解码字段', '特征上的可选明文映射，位于“特征库 → 条目 → 解码字段”。规则命中后，设备详情／分享／AI 导出／观测总结会将制造商或服务数据字节解析为温度、型号、Remote ID 等标签。开启实时条目的字段还会在列表显示一个值（§5.4.1），“醒目”使用更重的标签，“备注”是在详情和总结中显示的句子。TAK／CoT 也读取数字 ID latitude／longitude 生成广播位置标记。Remote ID 对 BLE FFFA 和包装为 FFFA 的 Wi-Fi FA:0B:BC 使用同一映射。它不参与匹配、不配对、不使用 GATT；加密广播保留十六进制。特征标签上的六边形表示存在映射（§5.4）。制造商数据的字节 0 位于公司 ID 之后，服务数据则从首字节开始。建立映射见 §9.6.1–§9.6.5，内置映射见 §9.6.6，TAK ID 见 §5.8.4，Remote ID 见 §5.8.3。'],
            ['解码六边形', '特征存在解码字段映射时，在名称标签内显示同色小六边形。多特征设备只标记有映射的名称。它检查特征库是否有映射，不代表当前数据包已成功解析。关闭“显示 → 特征名称”时隐藏。重点关注“!”、青色观测备注、荧光警报铃和实时值标签均独立。特征列表、按类别中的特征行和详情的已解码字段使用相同图标，见 §5.4、§9.6。'],
            ['实时值', '在实时列表行显示一个解码值，颜色与特征一致。对应解码字段必须开启实时条目，且当前广播确实解析出该值；醒目值使用更重的标签。内置示例包括 DULT／Find Hub 的分离，以及 Remote ID 的紧急状态、地面、空中、未声明和 RID 故障。支持信号强度列表、混合、时间线、按类别，不支持雷达。关闭特征名称仍显示该值，见 §5.4.1。'],
            ['特征系列（详情）', '位于详情中“从设备创建特征”上方的卡片，按与候选特征相同的广播 ID 规则检查此设备：强系列候选、可能系列、仅此设备或已标注。统计日志与当前广播中的不同 MAC。它只提供判断；从设备创建仍会绑定此 MAC。已标注不禁止第二个 UUID／OUI 特征再标注，例如 iBeacon 加商店。候选列表会跳过已标注设备。见 §5.5、§9.2、§9.2.1。'],
            ['命名设备', '设置中的单 MAC 自定义名称列表，可选最多 280 字观测备注及警报，在详情保存名称／备注或点按关注图标创建。可重命名、编辑备注、切换警报、移除单个或清除全部，不包含特征关注。隐私模式隐藏 MAC 末尾，已离开或轮换地址的孤立条目保留到手动删除。“仅命名设备”匹配任何自定义名称，“仅已关注”还要求警报开启。轨迹只绘制开启警报的命名设备。观测总结、对比和 AI 导出列出已接收且有备注的设备。见 §5.5、§5.7、§8.1、§10.1。'],
            ['隐私模式', '设置开关，默认关闭。将屏幕及观测总结／AI 导出／详情分享中的 MAC 后三组隐藏为 AA:BB:CC:**:**:**。最近 GPS 和观测报告坐标显示为已隐藏，省略街道名称。在线地名与地图开启时，“报告 → 轨迹”仍加载地图瓦片。日志、匹配、筛选、追踪计算、随行和已保存特征保留完整数据。暂停 TAK／CoT 推送，避免发送完整 MAC 与坐标。见 §5.7、§5.8。'],
            ['TAK／CoT 推送', '设置开关，默认关闭。通过 UDP 向 ATAK／WinTAK／iTAK 发送 Cursor-on-Target 标记。目标为本机（127.0.0.1:10011）、局域网组播（239.2.3.1:6969）或自定义。仅 UDP，不是 TAK 服务器 TCP 客户端。“此处接收”的重点关注标在操作者最强接收时的 GPS，呼号以“（此处）”结尾；广播经纬度标在飞行器位置。Remote ID BLE FFFA 或 Wi-Fi FA:0B:BC 通过持续保留 UAS ID 维持一个移动标记，解码 op_lat／op_lon 后另加操作员标记，位置消息的航向／速度写入轨迹。离开设备会移除，设置显示上次发送。隐私模式暂停推送。这不是测向、Remote ID 插件或实时画面本身。见 §5.8、§12.15、§12.16。'],
            ['夜间模式', '设置 → 外观，默认关闭。文字、标签、RSSI、信号追踪和重点关注采用黑底红色现场显示，手机亮度不变。见图 9、§5.7。'],
            ['此处接收（TAK）', 'CoT 标记位于截至目前本机接收最强信号时的 GPS。对方设备只是在接收范围内，不一定在标记点上。走远不会拖动标记，呼号以“（此处）”结尾，重点关注使用栗红色。需要 GPS 标记和实时定位。重点关注默认使用此方式，除非载荷含经纬度。这不是测向。'],
            ['广播位置（TAK）', 'CoT 标记来自解码字段 latitude／longitude，可选 alt_geo。内置 Remote ID 在 BLE FFFA 和 Wi-Fi FA:0B:BC 上用同一映射填充，跨 ASTM 消息类型保留。UAS ID 用作 TAK uid，使飞行器只有一个移动标记，不留下多个 MAC 点。op_lat／op_lon 生成第二个操作员标记，航向／速度写入轨迹。本机 GPS 标记可关闭，见 §5.8.3。'],
            ["Remote ID", 'ASTM F3411／OpenDroneID 数字号牌，属于内置无人机类别。支持 BLE UUID FFFA，以及 Wi-Fi 厂商 IE FA:0B:BC 类型 0x0D，使用同一解码映射。支持协议 0–2 的 Location／Basic ID／System／Self ID。位置消息在列表显示未声明、地面、空中、紧急状态或 RID 故障，紧急状态更醒目。TAK 载荷位置在广播坐标标注飞行器，并在有数据时写入航向／速度。观测可保留一段较短广播轨迹，报告中的轨迹和观测报告都绘制它（§5.4.1、§5.6.1）。Wi-Fi IE 需要 Android 11+，仍不支持 NAN。不是机尾注册号，也不是测向。见 §5.8.3、§9.6.6、§12.16。'],
            ['载荷位置', 'TAK 发送内容选项，开启推送时默认开启。选择已保留广播经纬度的设备。内置 Remote ID 没有重点关注标记，因此必须开启此项。BLE FFFA 和 Wi-Fi FA:0B:BC 均符合条件。'],
            ['报告', '底部标签页，包含观测（可选命名窗口）、轨迹、观测总结（文本／PDF）、观测导出、对比观测、AI 导出、候选特征、日志导出（格式与无线类型）、重置／清除日志。所选观测决定轨迹、总结、观测导出和对比中的本次观测。GPS、地名和日志开关仍在设置，见 §5.6。'],
            ['命名观测', '从“报告 → 开始观测”启动的可选观测窗口。轨迹、观测总结、对比中的本次观测、观测导出和 AI 导出使用该开始／结束时间，而非内存最近 15 分钟。上限为 6000 个唯一设备；满额时保留重点关注、载荷位置、已关注设备及特征，优先丢弃未命名 BLE。约每 10 秒向应用存储写入检查点。同时只能进行一次，保留 10 次已结束观测。实时列表仍约为 400 个设备。这不是测向，见 §5.6。'],
            ['轨迹', '报告页卡片，以北向朝上绘制本机在所选观测或最近 15 分钟的轨迹。保持报告页在前台，可观看进行中的观测增长或滑动的 15 分钟轨迹，约每 3 秒重绘。黑点为起点，蓝点为你的最新位置。MAC 和特征警报只绘制一次；解码经纬度使用最近广播位置，其他设备在最强 RSSI 处显示类别图标。数字表示同一点有多个设备，单个图标没有数字框，点按可查看该设备。只有重点关注而未关注该特征时不会绘制。列表在 MAC 旁显示 Wi-Fi／BLE 图标，MAC 警报行显示观测备注。粗绿线表示停留，并标时间刻度。进行中末端标为现在，保存后标为终点。进行中或已保存观测中，距本机轨迹 2 公里内的飞行器广播轨迹以白色虚线显示；Letter 报告图用黑点绘制相同轨迹，末位为类别图标，操作员为人物图标。点按末位图标可查看设备，数字表示该点还有其他设备；只有一个定位点时仅显示图标、不连线。更远且有 UAS ID 的飞行器会获得独立地图，最多显示三架。“最近 15 分钟”只绘制本机。开启在线地名与地图且联网时加载 OSM 瓦片；离线只画轨迹，隐私模式不隐藏瓦片。观测总结和对比图使用相同 MAC／特征警报，解码位置仍取最近广播定位。飞行器在图例中使用无人机类别图标，并附实时状态、UAS ID、最后位置、运动和操作员位置。图中重点关注为红色，MAC 警报为蓝色，其他特征警报为绿色。见 §5.6.1。'],
            ['观测导出', '报告页观测报告下方的卡片，格式选项与日志导出相同，但文件不同：所选观测或最近 15 分钟的每个唯一设备各占一行。CSV／JSON lines 含匹配特征和重点关注系列；日志可关闭。GPX／KML 将操作者路径作为轨迹导出。不是轮转日志，隐私模式不遮蔽文件。见 §5.6.2。'],
            ['日志导出', '报告页卡片，用于分享／保存轮转会话文件。磁盘上为 JSON lines，导出时可生成 CSV／GPX／KML／WiGLE。日志开启期间每次接收占一行，需要开启写入磁盘。清除日志不删除观测，见 §5.6.3、§11.6。'],
            ['观测备注', '命名设备上的可选 280 字字段，与自定义名称使用相同 KIND+MAC。详情中为青色区域，实时页面在重点关注“!”旁显示青色备注标签。观测总结在到访位置之后列出，对比在时间窗口之后列出。轨迹仅在该设备已关注时列出备注，AI 导出列出已接收且有备注的设备。它不是特征库备注，也不是金色重点关注。BLE 隐私地址隐藏编辑铅笔。设置备份包含备注，见 §5.5、§5.6。'],
            ['候选特征', '报告页操作，先用当前特征库重新匹配轮转日志，再列出至少两个设备共享独特广播 ID 的未匹配系列。跳过随机地址和类似家庭网络的名称。“创建特征”打开带共同规则、不绑定 MAC 的编辑草稿；保存后返回列表并重新运行。可离线使用，见 §5.6.4、§9.2.1、§11.5。'],
            ['vendor_ie（日志）', '新 Wi-Fi 行的最后一个 CSV 列／JSON 字段，最多八个厂商 IE OUI，以竖线分隔。BLE 和旧版 17 列记录为空。候选特征使用产品 IE；WPA／RSN／P2P／Qualcomm 芯片 IE 仍记录，但不用于聚类。见 §11.2、§11.5。'],
            ['已报警（列表）', '本次会话触发关注警报后，实时列表、混合、时间线和按类别条目显示荧光通知标记，持续到离开 Fieldwatch。它不同于重点关注“!”和一秒闪烁。“最近警报”按同一事件排序。雷达中这些设备在脉冲后保留荧光圆环，见 §5.3、§5.4、§6.1。'],
            ['备注（特征）', '特征编辑器中的字段，匹配设备的详情以低调备注卡片显示，并包含在分享／AI 导出中。内置文字说明系列是什么、通常做什么，而不是匹配配方（公司 ID、UUID）。它不是重点关注：没有实时“!”，不使用琥珀色，也不进入观测总结。多特征设备分别列出各系列，见 §5.5、§9.3。'],
            ['重点关注', '特征的可选字段，独立于备注。非空时，匹配设备在实时页获得“!”，详情显示琥珀色重点关注卡，观测总结／AI 导出增加对应内容，PDF 使用琥珀色提示框。留空则无标记。“!”是独立标签，不是解码六边形、青色观测备注或荧光警报铃。内置填充的系列包括业余 BLE 串口、Axon、WatchGuard Video、Digital Ally、Reveal Media、Wolfcom、Ray-Ban／Meta 眼镜、Snap Spectacles、Brilliant Frame、Even G1、Fieldy、Plaud Note、Limitless、Bee、Omi、Friend、Hak5 Pineapple、Flipper Zero、Pwnagotchi、Marauder／Deauther、GhostESP、Bruce、Porkchop、Cradlepoint、AirLink、Compex、Novatel Wireless、Utility Inc、Panasonic i-PRO／Arbitrator，以及路边／公共摄像头和 ALPR：Flock、Penguin、Pigvision、FS Ext Battery、Genetec AutoVu、Rekor、Motorola Vigilant、Verkada、Avigilon、Axis、Hikvision、Dahua、Hanwha Wisenet、Uniview、Rhombus、Hayden AI、Miovision、Tattile、LVT LiveView。这些条目也默认已关注。许多摄像头／ALPR 仅按名称匹配，蜂窝设备可能静默。模式匹配不是身份确认，也不是安全结论，见 §5.5、§9.3、§9.5、§12.14。'],
            ['业余 BLE 串口', '默认开启的特征，匹配低价 UART 模块的 BLE 广播名称，如 HMSoft、JDY、CC41、AT-09、BT05、ESP32 BLE，不包括经典蓝牙 HC-05／HC-06。重点关注说明同类板卡曾用于部分加油机／ATM 覆盖装置；读卡器旁信号很强时应目视查看，但不构成证据。本地这些名称只是干扰时可关闭条目。'],
            ['Axon', '默认开启的特征，结合 IEEE OUI 00:25:DF、Axon Body／Fleet／Dock 名称、UUID 及 BLE 服务数据中的 BWCDEVICE。重点关注涉及执法记录仪、车载设备、底座或 TASER。属于公共安全类别，执法领域常用但并非专用，不能指认具体警员。静默 LTE 设备不会出现。'],
            ['WatchGuard Video', '默认开启的特征，使用 IEEE OUI 00:1D:96，对应 WatchGuard Video 而非防火墙公司。重点关注为执法记录仪／车载设备，现属 Motorola。属于公共安全类别，执法领域常用但并非专用。'],
            ['Ray-Ban／Meta 眼镜', '默认开启的特征，使用 BLE 公司 ID 0x01AB／0x058E／0x0D53 和 Ray-Ban 名称，含重点关注。Quest 和其他 Meta 可穿戴设备也可能匹配相同 ID。'],
            ['Snap Spectacles', '默认开启的特征，使用 BLE 公司 ID 0x03C2 和 Spectacles 名称，含重点关注，不证明正在录制。'],
            ['Hak5 Pineapple', '默认开启的特征，匹配设置用 SSID Pineapple_XXXX。重点关注针对管理 AP，不是每个被克隆的咖啡馆 SSID。'],
            ['Flipper Zero', '默认开启的特征，匹配 OUI 0C:FA:22 和 BLE 名称 Flipper*，含重点关注。自定义固件可隐藏它。'],
            ['Pwnagotchi', '默认开启的特征，匹配经典 BSSID de:ad:be:ef:de:ad，含重点关注。'],
            ['Marauder / Deauther', '默认开启的特征，匹配 MarauderAP／Deauther 默认名称，含重点关注。DIY 板卡也会匹配。'],
            ['Porkchop', '默认开启的特征，匹配 SSID／名称 PORKCHOP 和 BACON 伪 AP 厂商 IE 50:52:4B，含重点关注。对应 Cardputer／CYD 固件，不是所有 ESP32。'],
            ['随行', '筛选仍在接收、轨迹大致为 −75 dBm 或更强、且 GPS 记录沿你路径延伸的 BLE。排除 Wi-Fi AP，因为强 AP 上的接收时 GPS 看起来也像随行。“仍在此处”不是固定半径：允许距离取 50 米与“近期速度 × 15 秒”的较大值，再加 25 米 GPS 容差。步行保持约一栋房屋长度，高速路上保留几个广播间隔，避免车内标签在包间消失。路过 BLE 仍无法通过轨迹移动条件。需要实时定位标记，不能只用过期的上次位置，并需约 45 米轨迹。包内／车内标签可匹配，另一部 iPhone 通常因 BLE MAC 轮换而不行。开关启动 BLE 随行检测，清除仅匹配特征／仅显示／仅命名设备／仅已关注，保留隐藏所选；预设则替换整套筛选。实时页面“重新开始”清除本机及设备轨迹。无论此筛选是否关闭、实时页面是否为列表，观测总结仍对最近 15 分钟做相同随行评估。见 §8.5。'],
            ['重新开始', '开启随行时显示在实时页面的按钮。清除操作者 GPS 路径和设备 GPS 轨迹，保留列表与日志，路径计数回到 0 米。'],
            ['实时画面', '底部第一个标签，手机上标为实时。可用雷达、列表、时间线、混合或按类别展示设备。筛选决定谁出现，调整中的显示设置决定视图和条目外观。并非“实时与录制”模式切换；观测总结、日志和 TAK 推送各自独立。见 §4.4、§5.1–5.3。'],
            ['按类别', '显示设置中的实时视图，以大纲呈现筛选集合：类别按名称 A–Z → 特征 A–Z → 设备 → 详情，未匹配最后。默认显示全部，保留空类别；收起空类别隐藏零计数，这些选项随列表滚动。类别标题使用与实时条目相同的图标，未匹配为问号。计数是设备数，不是包数。设备行遵循显示设置中的信号条、标签、频率、首次／末次发现。多特征设备出现在各自匹配类别中。关注命中会展开类别和特征，让条目闪烁；设备位置足够靠近时，自动跳转仍保留这些标题在屏幕内。这不是报告，见 §6.5。'],
            ['显示（实时页面）', '由实时页右上角滑块图标打开，调整本次任务的列表外观：视图、排序、短暂保留、标题行、副标题行、信号条、特征名称、频率、首次／末次发现。视图可选雷达、信号强度列表、时间线、混合或按类别。每行圆圈是类别图标，无线类型由副标题行的 Wi-Fi／蓝牙图标表示。筛选隐藏设备，显示隐藏字段。它不在设置页，见 §4.4、§5.3、§6.5。'],
            ['排序（显示）', '列表、混合和时间线的排列方式：信号最强、30 秒平均信号最强（默认）、最近接收、最近警报、最近出现、新设备置底、名称 A–Z（按标题行）、匹配特征优先。不会隐藏设备，雷达仍按 RSSI 决定半径。见 §5.3。'],
            ['预设（筛选）', '位于筛选页顶部，点按后替换整套筛选，不改变显示。内置少量预设：全部流量、仅 Wi-Fi、仅 BLE、强信号、随行、仅已关注，另加你保存的预设。类别仅显示（摄像头、无人机、寻物标签等）位于下方，可用“将当前筛选另存为…”保存。仅显示预设隐含仅匹配特征，该开关会变灰。长按任意预设可删除；删除的内置预设保持移除，直到恢复默认特征库与预设。重置筛选清除此页，不是撤销。见 §8.4。'],
            ['特征类别', '每个特征的分组：寻物标签、零售信标、标牌、可穿戴设备、监控、无人机、渗透测试、公共安全、车辆、眼镜、音频、摄像头、温控器、门禁、健康、家庭物联网、ISP／路由器、网状网络、手机／电脑、其他。公共安全包括 Axon／WatchGuard Video 及 Cradlepoint、AirLink、Compex、Novatel、Utility Inc 等公共安全车辆 AP，执法领域常用但并不专用，政府、市政和企业车队也可能使用。健康包括诊所／家庭医疗 BLE，如 Honeywell Xenon HC 扫描器、Omron 血压计、Withings 体重秤、Dexcom。摄像头指消费／运动相机，不是监控立杆，也不是 Axon。门禁包括 August／Schlage、ASSA ABLOY／SALTO／dormakaba／Paxton 门锁与读卡器，不是摄像头。眼镜是 Meta／Snap，音频是 AirPods／Sony／Bose／JBL／Sonos。颜色用于实时标签，类别用于筛选。自定义条目默认其他，旧版随身佩戴类别已合并入可穿戴设备。旧“门锁”现显示为门禁，但存储值仍是 LOCK。见 §8.3、§9.5。'],
            ['特征包', '从“设置 → 导出特征库”生成的 JSON 文件，名称为 fieldwatch-signatures-YYYYMMDD.json，包含内置条目与修改，不包含日志、GPS、筛选或关注列表。导入跳过相同 ID 或匹配规则，将额外规则合并至内置条目，名称冲突时改为“名称（已导入）”。恢复默认值仍会清除自定义内容。设置包是另一种文件，见 §5.7、§9.3。'],
            ['设置包', '从“设置 → 导出设置”生成的 JSON 文件，名称为 fieldwatch-settings-YYYYMMDD.json。包含设置开关、当前筛选、预设、命名设备和已关注特征，不包含特征库、日志或 GPS。导入替换这些设置字段，保留特征库，不覆盖首次运行免责声明。用于恢复出厂设置或更换手机后的备份恢复，见 §5.7。'],
            ['仅显示／隐藏所选', '筛选页的特征类别模式。仅显示保留匹配所选类别的设备，隐藏未匹配项，隐含仅匹配特征且该开关变灰。隐藏所选移除这些类别，但保留未匹配项。仅影响实时画面，匹配、日志和观测总结仍处理它们。仅显示未选任何类别时，实时画面不变。见 §8.1–8.4。'],
            ['标题行', '显示设置中每个列表、混合或时间线条目的第一行，可选广播名称、名称 + 类型、MAC（默认）。即使是 MAC 也保持粗体。名称 A–Z 按此行排序，所以默认按 MAC 排列。雷达标签忽略该设置。'],
            ['副标题行', '显示设置中的第二行，先显示小 Wi-Fi 图标（接入点）或蓝牙图标（BLE 广播设备），再显示广播名称、名称 + 类型（默认）或 MAC，以及随机／配对／已离开标记。配对表示本次会话见到 Fast Pair 配对模式。设为无会隐藏第二行以容纳更多条目，状态碎片移至标题行，无线类型图标不会移过去。未命名 BLE 在此仅写未命名，图标已表明 LE。厂商不在此行。'],
            ['短暂保留', '显示设置中设备在最后一包之后保留多久，可选关闭、10、30 或 60 秒。保留期间最后 RSSI、排序和雷达圆环冻结，不衰减。实际保留时长取此值与过期时间的较长者。'],
            ['已离开／过期', '最后数据包早于过期时间和短暂保留的较长值。系统保留的 Wi-Fi 或 BLE 扫描重启不算。条目在保留期内仍列出，雷达仅在标为已离开后变暗。'],
            ['保持屏幕常亮', '设置开关，默认开启。在 Fieldwatch 可见时保持显示，放入口袋时可关闭。它不同于后台不受限制，最大采集观测见 §4.5。'],
            ['最大采集（§4.5）', '按原生 Android 允许的最高频率接收：开启系统定位／Wi-Fi／蓝牙，授予 Fieldwatch 全部权限（精确位置、附近 Wi-Fi、蓝牙扫描与连接、通知），将电池设为不受限制并禁止应用休眠，观察时保持屏幕常亮，使用高性能，可选加快 Wi-Fi AP 扫描。代价是耗电和发热，不解除监听模式、客户端或经典蓝牙限制。'],
            ['加快 Wi-Fi AP 扫描', '设置开关，默认关闭。将 AP 批次间隔从约 30／40／55 秒缩短至约 8 秒。Fieldwatch 在 Android 11+ 读取系统 Wi-Fi 扫描节流状态，开发者选项中的扫描节流关闭前不会启用。目的在于带 OUI／出厂 SSID 特征的 AP 处于范围内时增加接收机会，驾车时尤其有用。不提供信号追踪、客户端或连续 RF 捕获，会增加耗电和发热。见 §7.1.1、§10.3.1。'],
            ['制造商数据', 'BLE AD 类型 0xFF：16 位公司 ID 加厂商字节。'],
            ['仅匹配特征', '隐藏没有匹配特征的设备。类别仅显示或仅显示所选特征正在缩小范围时，该开关变灰。见 §8.1–8.3。'],
            ['仅已关注', '隐藏既未匹配已关注特征、也不是警报开启的命名设备的条目，始终按 AND 应用。隐藏所选仍生效，例如仅已关注加隐藏监控会排除已关注摄像头。只设名称未开警报的设备使用仅命名设备查看。开启时实时画面显示仅已关注提示条；随行会清除此条件。见 §8.1。'],
            ['仅命名设备', '隐藏没有自定义名称的设备，警报可关闭。不同于仅匹配特征或仅已关注。随机／隐私 MAC 仍只绑定当前地址，见 §5.5、§8.1。'],
            ['隐藏 Fast Pair 账号密钥广播', '隐藏仅匹配 Fast Pair 且载荷是较长账号密钥筛选器的设备，保留 3 字节配对模式型号 ID。配对模式仍显示 Fast Pair 配对标签及副标题行配对标记，多特征设备仍保留。隐藏所选 Fast Pair 会同时隐藏两种模式。始终按 AND 应用，见 §8.1、§9.5。'],
            ['仅显示所选特征', '筛选页可折叠列表，按类别 A–Z 分组，与特征库相同。实时画面只保留匹配所选特征的设备。空列表不增加包含条件，与隐藏所选使用独立选择。见 §8.1–8.3。'],
            ['隐藏所选特征', '针对单个系列的筛选开关。开启后匹配设备从实时画面移除，关闭时仍保存选择，空列表不隐藏任何设备。整个寻物标签或 ISP 类别都是干扰时，优先使用类别隐藏所选。'],
            ['暂停（实时页面）', '冻结实时画面，无线扫描与日志继续。筛选和设置仍可更新，恢复实时画面时应用新筛选。从暂停条目打开的是当时快照，即使设备后来已离开。再次点按此时标为实时的标签即可恢复。暂停期间标记已见使用冻结列表。'],
            ['标记已见', '仅开启仅新发现时，在实时页面标签栏上方显示。将当前画面中的设备加入已见集合，暂停时使用冻结列表。'],
            ['重置已见', '仅开启仅新发现时，在实时页面标签栏上方显示。将已见集合清零，使这些设备可重新作为新设备出现，不清除日志。'],
            ['观测总结（文本）', '报告页分享的纯文本现场观测总结，以免责声明开头，说明业余／按现状提供、推测非身份、遵守当地法律。使用所选观测（最多 6000 个唯一设备）或最近 15 分钟内存数据（约 400 个）。列表默认省略未匹配的轮换地址 BLE，但计数仍包含；保留重点关注、命名特征、已关注设备和载荷位置标记。可在观测报告卡片开启显示未匹配的轮换地址 BLE，观测导出则包含全部设备。忽略实时视图与筛选，包含到访位置、观测备注、跟踪、清单及要点。驾车时应多次生成，见 §5.6、§11.4.1。'],
            ['观测总结（PDF）', '与文本观测总结相同的 Letter 尺寸 PDF，时间窗口、未匹配随机 BLE 隐藏规则和计数都相同。包含免责声明、FIELDWATCH 页眉、编号章节、全宽轨迹图、琥珀色随行／重点关注提示及要点。长途应多次生成（§11.4.1），分享 MIME 为 application/pdf。'],
            ['观测对比', '报告页观测报告下的卡片，将本次观测（进行中、所选或最近 15 分钟）与第二次已保存观测对比。仅按无线类型加 MAC 比较出现情况：仅本次、仅第二次或两次都有。提供文本、PDF 和 AI 导出，观测备注位于时间窗口之后。不表示设备定位，见 §5.6。'],
            ['在线地名与地图', '设置开关，默认开启。联网时通过系统地理编码器，将观测总结和 AI 导出的 GPS 标记反向解析为地名。报告轨迹在路径下加载 OpenStreetMap 瓦片，填满并裁剪绘图区，保留路线周边地图。离线或无瓦片时，总结只用坐标，轨迹保持北向朝上，不弹错误。隐私模式不隐藏地图；关闭此项会同时去掉街道与地图。'],
            ['新设备在底部', '显示 → 排序。按首次发现排列，最早在顶部，新设备追加，离开设备移除。除非你向上滚动，列表会跟随底部。'],
            ['未命名 LE', '没有广播名称且无有用解码时，BLE 广播名称／名称 + 类型使用此占位。副标题行已有蓝牙图标，正文只写未命名，避免重复 LE；标题行选择广播名称时仍写未命名 LE。未修改时标题行是 MAC。'],
            ['AI 导出', '共有三个按钮。报告中的观测导出嵌入机内总结并附紧凑速率、重点关注和观测备注，要求补充分析而非重复清单。报告对比提供交集与各自独有的重点关注、命名设备、观测备注。设备详情分析单个设备，包含详情转储和注册表解码。都供粘贴到聊天中，均以实验性免责声明开头，都是推测而非身份确认，应按敏感内容处理。'],
            ['特征颜色（内置）', '内置条目按类别共用调色板：渗透测试红色，摄像头／ALPR／UniFi Protect／DJI 琥珀色，手机／“查找”紫色，可穿戴追踪设备青色，网状网络绿色，眼镜和音频橙色，公共安全与车辆蓝绿色，家庭物联网／ISP Wi-Fi（含 UniFi AP）／零售标牌／未知银色。未匹配设备按 RSSI 着色：≥−55 绿色、−55 至 −70 琥珀色、−70 至 −85 橙色、更弱红色。可修改任意条目，见 §9.5。'],
            ['UniFi AP', '仅 Wi-Fi 的 ISP／路由器特征，匹配出厂 SSID UniFi*／UAP-*／UBNT*，以及 BSSID 或厂商 IE 中的 Ubiquiti IEEE OUI。虚拟 BSSID 可能不匹配 MAC OUI，但仍可命中 Ubiquiti 厂商 IE。另一个独立 UniFi 条目在两种无线类型上仅按名称匹配。UniFi Protect 摄像头仍属于监控，见 §9.5、附录 B。'],
            ['为探测结果添加 GPS 标记', '设置开关，默认开启。扫描时获取实时 GPS／网络位置，为每次接收添加标记，供详情、随行、观测总结、日志经纬度和此处接收 TAK 标记使用。忽略超过 30 秒的上次已知位置。表示操作者接收时的手机位置，不是对方设备。Remote ID 广播位置 TAK 标记不需要此项。请使用高精度定位，否则轨迹可能为 0。见 §5.7、§5.8。'],
            ['以文本分享', '设备详情按钮，导出当前设备的标识、信号、解码和会话信息，不是整次观测报告，也不是轮转日志。'],
            ['语音（关注列表）', '设置中的已关注特征语音提示默认开启。特征关注可选择播报类别、特征或类别 + 特征，默认两者。命名设备改为播报关注名称，包括自定义名称。语音与提示音独立，不用于信号追踪，重叠播报会跳过，使用本机 TTS。“测试警报”使用所选组合，只有语音时也可自动跳转。见 §5.7、§10.2.1。'],
            ['信号追踪', '设备详情中的 BLE 专用全屏功能，根据平滑 RSSI 显示更近／更远。“你”周围圆环在更近时收缩，更远时扩张。约 −45 dBm 或更强显示非常近，提示查看周围但不代表米数。忽略 127。显示本次最强信号与趋势线。底部提示音／振动默认关闭，RSSI 越强越快，安静或离开时停止；不同于关注提示音，且不播报语音。可用身体遮挡转身粗略估计方向（§12.13）。墙、金属、人群和楼板可在距离不变时改变 RSSI。这不是测距或测向。Wi-Fi 因系统节流而不支持，即使快速扫描仍为批次，不能用于此功能。'],
            ['lat／lon（日志）', 'GPS 标记开启且有定位时，新日志行中的 CSV 列和 JSON 字段。表示本机接收时的位置，不是对方设备；否则为空或 null。CSV 中位于 vendor_ie 之前，以便旧文件仍可解析。'],
            ['到访位置', '观测总结／AI 导出章节，将操作者路径分为约 40 米范围的停留与转移。每次停留只列一次经纬度，可附街道名称和在那里接收到的强信号设备，不在每条清单上重复坐标。'],
            ['Fast Pair', 'Google 点按配对，服务 UUID 0xFE2C。内置特征默认开启，覆盖 Android 手机和许多耳塞。配对模式使用 3 字节型号 ID，实时标签显示 Fast Pair 配对；较长载荷为账号密钥筛选器。隐藏 Fast Pair 账号密钥广播只排除此类单特征设备；隐藏所选 Fast Pair 会排除两种模式。见 §8.1、§9.5。'],
            ['iBeacon', 'Apple 制造商布局 0x02／0x15：UUID + major + minor + 校准发射功率。'],
            ['Appearance', 'BLE GAP 字段，表示设备自述类型，如耳机、鼠标、手表，用于详情的“可能的设备类型”推测。'],
            ['仅新发现', '筛选开关。开启时，实时页面标签栏上方显示标记已见／重置已见。已见集合仅在首次开启及下一次 Wi-Fi 扫描，或点按标记已见时增长；重置已见将其清零。新设备接收期间保持显示，最后一包后至少保留短暂保留时长。实时提示为“仅新设备 · 已隐藏 N 个”。'],
            ['观测', '一次观察无线设备的会话，可以是房间、步行或驾车。轨迹、观测总结、观测导出和对比中的本次观测使用所选观测，或内存最近 15 分钟。日志导出提供轮转会话文件。见 §5.6、§11.4。'],
            ['处理流程', '一次接收成为条目的过程：无线广播 → ScanService → 特征库匹配 → 实时与调整 → 关注列表／信号追踪 → 日志、观测、TAK。见图 20、第 14 章。'],
            ['接收时刻', 'Fieldwatch 收到数据包的瞬间。探测记录上的 GPS 是本机在该时刻的位置，不是对方设备的位置。'],
            ['标签（特征）', '实时条目上彩色的特征名称，代表模式命中，不代表身份。“显示 → 特征名称”可隐藏标签，但不移除设备。'],
            ['OUI', '组织唯一标识符，即 MAC 前 24 位（三字节），分配给厂商。同一模块厂商会出现在许多产品中。'],
            ['随机化 MAC', '本地管理的单播地址，U/L 位为 1，常见于手机和部分标签。'],
            ['RSSI', '接收信号强度指示，单位 dBm。值越大、越接近 0，信号越强。'],
            ['迷你趋势图', '混合视图和详情中的 RSSI 图，按数据包顺序排列，最新在右，使用固定 −30 至 −100 dBm 网格；不是时间轴，也不会自动缩放。'],
            ['趋势标记', 'RSSI 旁的 &gt;&gt; &gt; = &lt; &lt;&lt;，表示最近数据包变强或变弱。'],
            ['服务 UUID', 'BLE 服务标识符。16 位别名可扩展为蓝牙基础 UUID。'],
            ['SSID', 'Wi-Fi 网络名称，可以隐藏，此时扫描结果为空。'],
            ['混杂／监听模式', '让 Wi-Fi 芯片接收某信道上的所有帧。原生 Android 应用无法启用。Fieldwatch 仅使用 startScan() 获取 AP 信标，并接收 BLE 广播。'],
            ['蜂窝优先／静默设备', '较新的摄像头／ALPR 立杆使用 LTE／5G 回传，仅在安装维护时开启 Wi-Fi／BLE。大部分时间无法被 Fieldwatch 看到属于预期情况。'],
            ['规则启用', '特征编辑器中每条规则的开关。关闭后保留规则，但不参与匹配。'],
        ],
        [1.6 * inch, 4.9 * inch],
    ))
    flow += [
        Spacer(1, 10),
        P('B. 默认预载特征', "h2"),
        P(
            '除另有说明外，下列特征均匹配任意规则。可信度说明用于现场判断，不构成法律认定。精确 OUI 列表可在应用编辑器查看。每个内置特征规则命中时始终标注。系列干扰较多时在筛选页隐藏，类别使用隐藏所选，单条使用隐藏所选特征。标签按类别着色（§9.5）。下表所示执法记录仪、摄像眼镜、录音录像可穿戴设备、渗透测试、公共安全车辆 AP、路边／公共摄像头与 ALPR 均预置重点关注和关注状态；所有内置无人机类别条目（DJI、Remote ID、Skydio、Autel、Parrot、HOVERAir）也默认关注。消费摄像头、ISP 网关和办公鼠标在接收到出厂名称或 OUI 时会标注。表格按特征名称 A–Z 排列。'
        ),
    ]
    stock_sigs = [
            ['Flock Safety 摄像头', 'OUI B4:1E:52；名称 Flock、FLCK、CONDOR、FALCON、SPARROW；通配模式 Flock-*、Flock-??????。已填写重点关注，默认已关注。', '路边 ALPR／摄像立杆。B4:1E:52 或 Flock-* SSID 的可信度较高。当前立杆往往在 Wi-Fi 和 BLE 上静默，新匹配会发出提示音。'],
            ['LiteOn 摄像设备无线模块', 'LiteOn／相关模块 OUI，已移除 UGSI E0:4F:43，之前也已移除 Espressif A4:CF:12 和 3C:71:BF；厂商 IE 00:80:19／00:0A:EB。属于摄像头类别，无重点关注，也不默认关注。', '摄像板卡前缀。门铃和其他 OEM 无线设备也使用这些芯片。Flock 名称或 B4:1E:52 对应 Flock Safety 摄像头。'],
            ['Raven / ShotSpotter', '名称 RAVEN、ShotSpotter、SoundThinking；UUID 3100–3500；OUI D4:11:D6。', 'UUID 范围是更强的数字特征。0x09C8 对应 Penguin。'],
            ['Apple AirTags', '名称 AirTag／Find My；制造商数据 0x004C／12；UUID FD44。', '离线查找。iPhone 也发送 0x12；同一设备出现 Continuity（Apple 设备）时会抑制此标签，除非名称为 AirTag 或 UUID 为 FD44。不是 Continuity 0x10，也不是 AirPods 0x07。'],
            ['Apple 设备', 'Apple 0x004C 类型 0x10／0x0F／0x0B／0x05／0x0C–0x0E／0x08／0x0A；名称 iPhone、iPad、MacBook。', '手机／平板／Mac 的 Continuity。同一设备上的 OF 0x12 不会再显示第二个 AirTag 标签。街上大量 iPhone 会频繁命中。'],
            ['Apple 音频', '0x004C／07 邻近配对；0x004C／09 AirPlay；名称 AirPods、Beats。', 'AirPods／Beats／AirPlay，不是标签，也不是 Nearby Info 手机。'],
            ['Microsoft 设备', '公司 ID 0x0006；名称 Surface、Xbox。', 'Windows 电脑的 Swift Pair／附近共享。'],
            ['Tesla', '公司 0x022B；UUID FE96／FE97；名称 Tesla／Cybertruck；BLE 通配模式 S????????????????C（VIN SHA1 手机钥匙）；Apple iBeacon UUID 74278BDA-…；Wi-Fi TeslaGW*／tesla-vehicle／TeslaWallConnector*／Cybertruck*。', '手机钥匙广播是 S + 16 位十六进制 + C。Tesla 也使用 iBeacon 布局让 iOS 找到车辆，因此 Fieldwatch 标注 Tesla，而非 iBeacon。属于车辆类别。'],
            ['Ford', '公司 0x0723；BLE 名称 Ford／Lincoln。', '广播该 ID 时可识别手机钥匙／信息娱乐系统，不是经销商 SSID。'],
            ['Honda', '公司 0x0915；BLE 名称 Honda／Acura。', '不是 Sony Honda Mobility 0x0EDE。'],
            ['Hyundai', '公司 0x0826；BLE 名称 Hyundai／Genesis。', '在广播该公司 ID 时匹配。'],
            ['Toyota', '公司 0x0977；BLE 名称 Toyota／Lexus；Wi-Fi TOYOTA*／LEXUS*。', '广播该公司 ID 或出厂 SSID 时匹配。'],
            ['Nissan', '公司 0x0BA6；BLE 名称 Nissan／Infiniti。', '在广播该公司 ID 时匹配。'],
            ['Subaru', '公司 0x0A10；BLE 名称 Subaru。', '不是 Starlink 卫星互联网。'],
            ['BMW', '公司 0x05EB；BLE 名称 BMW；Wi-Fi BMW_*。', '不匹配“BMW of …”等经销商名称。'],
            ['Volkswagen', '公司 0x011F；UUID FE30／FE31；名称 Volkswagen／VW；Wi-Fi My VW*。', 'Skoda／SEAT／Porsche 使用各自独立 ID。'],
            ['Porsche', '公司 0x0120；BLE 名称 Porsche；Wi-Fi Porsche_WLAN*。', '不是 Volkswagen 0x011F。'],
            ['Jaguar Land Rover', '公司 0x020B；名称 Jaguar／Land Rover／Range Rover。', '在广播该公司 ID 时匹配。'],
            ['BYD', '公司 0x0C34；BLE 名称 BYD。', '这是模式匹配，不代表具体型号。'],
            ["Tesla tsTPMS", 'BLE 名称 tsTPMS*。', 'Tesla BLE 胎压传感器。此条目不按公司 0x022B 或 UUID 0x1122 匹配。唤醒广播可解码压力、温度、电池，属于车辆类别。'],
            ['Google', '公司 0x00E0；名称 Pixel／Chromecast。', 'Pixel／Chromecast。Fast Pair UUID FE2C 属于独立 Fast Pair 条目。'],
            ['Fast Pair', 'BLE UUID 0xFE2C', 'Android 手机及许多耳塞／音箱。配对模式为 3 字节型号 ID，实时显示 Fast Pair 配对及配对标记；较长载荷是账号密钥筛选器，常为公共场所干扰。隐藏 Fast Pair 账号密钥广播仅排除该类单特征设备，隐藏所选 Fast Pair 排除两者。不代表人员，也不是所有未命名 LE。属于手机／电脑类别。'],
            ['Sony', '公司 0x012D；名称 Sony／WH-1000／WF-1000。', '耳机、电视、相机，不是 Sony Ericsson 0x0056。'],
            ['Bose', '公司 0x009E；UUID FE21／FEBE；名称 Bose。', '耳机／音箱。FEBE 是常见的 LE 音箱／QC 广播。'],
            ['Garmin', '公司 0x0087；UUID FE1F；名称 Garmin。', '手表／inReach。'],
            ['Pokemon GO Plus', '名称 Pokemon GO Plus*；UUID 138C35B6（Plus +）和 21c50462-…（初代）。', 'Nintendo 夹式设备，不是公司 0x0553 或 OUI 60:1A:C7，后两者对应 Joy-Con／Switch。属于可穿戴类别。'],
            ['Fieldy', 'BLE 名称 Fieldy*，已填写重点关注，默认已关注。', 'Field Labs AI 笔记吊坠。不是 Arduino／ESP32 示例 UUID 4FAFC201-…，也不是公司 0xFEFE。不证明正在录制，新匹配会发出提示音。'],
            ['Plaud Note', 'BLE 名称 Plaud Note*，已填写重点关注，默认已关注。', 'Plaud Note／NotePin AI 录音设备。不证明正在录制，新匹配会发出提示音。'],
            ['Amazon', '公司 0x0171；名称 Echo／Amazon／Fire TV。', 'Echo／Fire。'],
            ['Fitbit', '公司 0x018E；UUID FD62／FD63；名称 Fitbit。', '可穿戴设备。仅识别系列，广播不携带步数；现代数据转储属于 GATT 或加密内容，没有解码字段映射。'],
            ['Oura', '公司 0x02B2；名称 Oura。', '戒指。'],
            ['Logitech', '公司 0x01DA；UUID FE61；Logitech／Logi。', '鼠标／键盘，常见办公背景信号。'],
            ['JBL / Harman', '公司 0x0057；JBL／Harman。', '音频。'],
            ['Sonos', '公司 0x05A7；UUID FE07；名称 Sonos。', '音箱（S41／S57 LE）。'],
            ["GoPro", 'UUID FEA5／FEA6；GoPro*。', '运动相机，属于摄像头类别，不是眼镜。解码公司 0xF202 的结构版本、唤醒、Wi-Fi AP、配对、型号、媒体导出等字段（§9.6）。'],
            ['Osmo', '0x08AA 型号 ID 0x0006–0x0022；OsmoAction*／OsmoPocket*／Osmo360*／OsmoNano*／XtraEdgePro*。', 'DJI Osmo Action／Pocket／360／Nano 相机，不是 Osmo Mobile 云台，也不是 DJI 飞行器，后者仍归 DJI。属于摄像头类别，可解码 0x08AA 型号 ID（§9.6）。'],
            ['Insta360', '公司 0x10D7；Insta360*／X3 *／X4 *／X5 *／Ace Pro*／GO 3*／ONE X*／ONE RS*。', 'Arashi Vision 运动／全景相机，属于摄像头类别，不是监控。'],
            ['DJI', '公司 0x08AA；BLE 和 Wi-Fi 上的 DJI*。', '无人机／遥控／设置 AP。Osmo 相机使用独立 Osmo 条目，OcuSync 不是 AP。飞行中的 ASTM Remote ID 使用 Remote ID 条目。属于无人机类别，可解码 0x08AA 型号 ID（§9.6），默认已关注。'],
            ["Remote ID", 'BLE UUID FFFA 与 Wi-Fi 厂商 IE FA:0B:BC（ASTM F3411／FAA Remote ID）。', '两种无线类型上的飞行中数字号牌，覆盖 DJI、Skydio、Autel、Parrot、HOVERAir 及 Dronetag／Aerobits／BlueMark 模块。使用同一解码映射：协议 0–2 的 Basic ID、位置（lat／lon／alt_geo／heading／speed）、Self ID、System（op_lat／op_lon 为操作员）。位置消息在列表显示未声明、地面、空中、紧急状态或 RID 故障，紧急状态更醒目。Wi-Fi 包包装为 FFFA。TAK 使用载荷位置及轨迹航向／速度。新观测可在报告轨迹和观测报告中绘制广播轨迹。仍不支持 NAN；AP 信标需要 Android 11+。不是 FIDO FFF9 或 Thread FFFB，也不是机尾注册号。属于无人机类别，默认已关注。见 §5.4.1、§5.8.3、§9.6、§12.16。'],
            ['Skydio', '名称 Skydio*。', '美国公共安全／企业无人机。飞行中 RID 使用 Remote ID 条目（BLE FFFA 或 Wi-Fi FA:0B:BC），仍不支持 NAN。属于无人机类别，默认已关注。'],
            ['Autel', '名称 Autel*。', 'Autel Robotics 无人机，不匹配 EVO* 或 SSID default-ssid。属于无人机类别，默认已关注。'],
            ['Parrot', '名称 ANAFI*／Bebop*。', 'Parrot 无人机，不按汽车用途的公司 0x0043 匹配，也不使用 Disco*。属于无人机类别，默认已关注。'],
            ['HOVERAir', 'Wi-Fi Hover*／HoverX1_*；名称 HOVERAir*。', 'Zero Zero Robotics 飞行相机，属于无人机类别，默认已关注。'],
            ['Starlink', 'Wi-Fi SSID STARLINK*／Starlink*；SpaceX OUI 00:26:12。', 'BSSID 常随机化，通常通过名称命中。'],
            ['Meraki', 'Wi-Fi SSID Meraki* 加 Cisco Meraki IEEE OUI。', '不使用 Cisco Systems OUI。SSID 改名后仍可按 BSSID 命中。同一信标中的 Cisco 厂商 IE 00:00:0C 仍只标为 Meraki。属于 ISP／路由器类别。'],
            ['Cisco', 'Wi-Fi Cisco*、tsunami；Cisco Systems 和 Cisco SPVTG IEEE OUI。', '不是按 Cisco 子字符串匹配，避免 Francisco。仅 AP 信标。Meraki／Cisco-Linksys 有各自 OUI 列表。属于 ISP／路由器类别。'],
            ['Aruba', 'Wi-Fi Aruba*／SetMeUp*／InstantOn* 加 Hewlett Packard Enterprise IEEE OUI。', 'HPE Aruba Instant／Instant On。不匹配单独的 instant 单词，也不是 HP Inc. 打印机。属于 ISP／路由器类别。'],
            ['Ruckus', 'Wi-Fi Ruckus*／Configure.Me* 加 Ruckus Wireless IEEE OUI。', 'SSID 改名后仍可按 BSSID 命中，属于 ISP／路由器类别。'],
            ['Fortinet', 'Wi-Fi Fortinet*／FortiAP*／FAP-config* 加 Fortinet IEEE OUI。', 'SSID 改名后仍可按 BSSID 命中，属于 ISP／路由器类别。'],
            ['MikroTik', 'Wi-Fi MikroTik* 加 Routerboard.com IEEE OUI。', 'SSID 改名后仍可按 BSSID 命中。'],
            ['EnGenius', 'Wi-Fi EnGenius*／EnMGMT* 加 EnGenius IEEE OUI。', '云管理 AP，未认领时使用 EnMGMT*。'],
            ['Zyxel', 'Wi-Fi Zyxel* 加 Zyxel IEEE OUI。', 'SSID 改名后仍可按 BSSID 命中。'],
            ['Peplink', 'Wi-Fi Peplink*／Pepwave* 加 Peplink IEEE OUI。', '旅行／分支机构路由器，不匹配 MAX-*。'],
            ['OpenWrt', 'Wi-Fi OpenWrt*。', 'OpenWrt 出厂 SSID，没有 OpenWrt IEEE OUI。'],
            ['Arris', 'Wi-Fi Arris*／SURFboard* 加 Arris 与 CommScope IEEE OUI。', '有线网关。Ruckus 保留自己的 OUI 列表。配置后的 ISP 自定义名称可能漏检。'],
            ['Mist', 'Mist Systems IEEE OUI。', 'Juniper Mist 园区 AP。云管理 SSID 使用场所名称，属于 ISP／路由器类别。'],
            ['T-Mobile', 'Wi-Fi TMOBILE-*／T-Mobile*。', '家庭互联网／热点，常由 HUMAX／Arcadyan／Askey 代工。'],
            ['HUMAX', 'HUMAX IEEE OUI。', '5G／有线网关，常用于 T-Mobile Home Internet。'],
            ['Sagemcom', 'Sagemcom Broadband IEEE OUI。', 'ISP 网关，包括 Comcast 等。'],
            ['Arcadyan', 'Arcadyan IEEE OUI。', 'ISP 网关／网状网络，Verizon／T-Mobile 代工设备。'],
            ['Askey', 'Askey Computer IEEE OUI。', 'ISP／5G 网关，T-Mobile 代工设备。'],
            ['Calix', 'Calix IEEE OUI。', '光纤网关，如 GigaSpire 系列。'],
            ['Nokia', 'Nokia Solutions and Networks IEEE OUI。', '网关／小基站，不是 Nokia 手机。'],
            ['AirTies', 'AirTies IEEE OUI。', 'ISP 网状网络扩展器。'],
            ['Tenda', 'Wi-Fi Tenda* 加 Tenda IEEE OUI。', '消费级 AP／路由器。'],
            ['Sercomm', 'Sercomm IEEE OUI。', 'ISP 有线／光纤代工网关。'],
            ['Luxul', 'Luxul IEEE OUI。', '中小企业 AP。'],
            ['Sophos', 'Sophos IEEE OUI。', '防火墙／AP，属于 ISP／路由器类别。'],
            ['AUMOVIO', 'AUMOVIO IEEE OUI。', '原 Continental 车辆 Wi-Fi，属于车辆类别。'],
            ['CenturyLink', 'Wi-Fi CenturyLink*。', '网关出厂 SSID。'],
            ['GM 热点', 'Wi-Fi myCadillac*／myGMC*／myBuick*／CADILLAC*／BUICK*／CHEVROLET*。', 'GM 车载热点。myChevrolet* 仍归 Chevrolet 热点条目。'],
            ['Audi MMI', 'Wi-Fi Audi_MMI_*。', 'Audi 车载热点。'],
            ['Extreme', 'Extreme Networks IEEE OUI。', '园区 AP，云管理 SSID 使用场所名称，属于 ISP／路由器类别。'],
            ['Adtran', 'Wi-Fi Adtran* 加 Adtran IEEE OUI。', '光纤网关，常见 CenturyLink／Lumen／Quantum Fiber 代工设备。'],
            ['Cambium', 'Wi-Fi Cambium*／cnPilot*／IgniteNet* 加 Cambium 和 IgniteNet IEEE OUI。', 'WISP／cnPilot AP，Quantum Fiber 出厂名称也可能命中。'],
            ['TRENDnet', 'Wi-Fi TRENDnet* 加 TRENDnet IEEE OUI。', '消费级 AP，SSID 改名后仍可按 BSSID 命中。'],
            ['Cudy', 'Wi-Fi Cudy* 加 Cudy IEEE OUI。', '旅行／家庭路由器，出厂名称 Cudy-XXXX。'],
            ['SnapAV', 'Wi-Fi Control4*／Wattbox* 加 SnapAV IEEE OUI。', 'Control4／Wattbox 家庭影音 AP，属于家庭物联网类别。'],
            ['Vantiva', 'Wi-Fi Technicolor*／THOMSON*／Vantiva* 加 Vantiva 和 Technicolor IEEE OUI。', '原 Technicolor ISP 网关，配置后的 ISP 自定义名称可能漏检。'],
            ['Hitron', 'Wi-Fi Hitron* 加 Hitron IEEE OUI。', '有线网关，常见 Xfinity 代工设备。'],
            ['Actiontec', 'Wi-Fi Actiontec* 加 Actiontec IEEE OUI。', 'FiOS／Frontier 网关，Verizon 名称仍归 Verizon。'],
            ['Buffalo', 'Wi-Fi Buffalo*／AirStation* 加 BUFFALO.INC IEEE OUI。', 'AirStation／路由器，SSID 改名后仍可按 BSSID 命中。'],
            ['Grandstream', 'Wi-Fi Grandstream*／GWN* 加 Grandstream IEEE OUI。', 'GWN AP，通配模式匹配前缀，不匹配名称中间的 GWN 单词。'],
            ['Edgecore', 'Edgecore IEEE OUI。', '园区／开放 Wi-Fi AP，云管理 SSID 使用场所名称，属于 ISP／路由器类别。'],
            ['WatchGuard AP', 'WatchGuard Technologies IEEE OUI 00:01:21／00:90:7F。', '防火墙／AP，不是 WatchGuard Video 00:1D:96，属于 ISP／路由器类别。'],
            ['Mojo', 'Mojo Networks IEEE OUI。', '现为 Arista Cognitive Wi-Fi，不使用 Mojo* SSID 通配模式，属于 ISP／路由器类别。'],
            ['Winegard', 'Wi-Fi Winegard* 加 Winegard IEEE OUI 00:17:1A。', '房车／船用 Wi-Fi，属于车辆类别。'],
            ['Inseego', 'Wi-Fi Inseego* 加 Inseego Wireless IEEE OUI。', '5G／MiFi 热点，不单独匹配 MiFi*。'],
            ['Franklin', 'Wi-Fi RG3100* 加 Franklin Technology Inc. IEEE OUI 50:FB:FF。', '5G／LTE 家庭互联网网关，常由运营商提供。不是 Franklin Electric，也不按 Qualcomm 芯片 IE 匹配。属于 ISP／路由器类别。'],
            ['Synology', 'Wi-Fi Synology* 加 Synology IEEE OUI。', 'NAS／路由器 AP。'],
            ['NETGEAR', 'Wi-Fi NETGEAR*／Orbi* 加 NETGEAR IEEE OUI。', 'SSID 改名后仍可按 BSSID 命中。'],
            ['TP-Link', 'Wi-Fi TP-Link*／TP-LINK*／Deco* 加 TP-Link IEEE OUI。', '不匹配 Tapo 名称，但使用 TP-Link OUI 的 Tapo 摄像头也可能命中此条目。'],
            ['ASUS', 'Wi-Fi ASUS* 加 ASUSTeK IEEE OUI。', 'SSID 改名后仍可按 BSSID 命中，笔记本热点也可能命中。'],
            ['Linksys', 'Wi-Fi Linksys*／Velop* 加 Linksys IEEE OUI。', '部分 Velop 使用 Belkin OUI。'],
            ['Eero', 'Wi-Fi eero* 加 eero inc. IEEE OUI。', '不是 Amazon Technologies（Echo）。'],
            ['Google Wifi', 'Google Wifi / Nest Wifi', '不是 Pixel BLE、Nest-* 摄像头，也不按 Google Inc IEEE OUI 匹配。'],
            ['Huawei', 'Wi-Fi HUAWEI*／Huawei* 加 Huawei IEEE OUI。', 'CPE 与手机共享这些 OUI。使用公共 OUI 的手机热点也会命中，随机化热点需要出厂 SSID。不是 Honor，属于 ISP／路由器类别。'],
            ['Plume', 'Wi-Fi Plume*／SuperPod* 加 Plume Design IEEE OUI 60:B4:F7。', 'SuperPod／HomePass 网状网络。家庭自定义 SSID 仍可按该 OUI 命中，ISP 品牌节点则常改用 Arris／Sercomm／Hitron。属于 ISP／路由器类别。'],
            ['手机热点', 'Wi-Fi AndroidAP*／Galaxy-*／Galaxy *／Pixel-*／Pixel *。', '出厂个人热点 SSID，BSSID 通常随机化。iPhone 仍归 Apple 设备。通用 DIRECT-* 不匹配，除非同时命中 Raven、Roku、Epson 等产品系列。自定义名称不匹配，属于手机／电脑类别。'],
            ['D-Link', 'Wi-Fi D-Link*／DIR-* 加 D-Link IEEE OUI。', 'SSID 改名后仍可按 BSSID 命中。'],
            ['Belkin', 'Wi-Fi Belkin* 加 Belkin IEEE OUI。', '部分 Linksys Velop 会归入此项。'],
            ["Xfinity", 'xfinitywifi / XFSETUP* / Xfinity*，以及 Comcast IEEE OUI', '多数设备由 Arris / Hitron 代工。'],
            ["Spectrum", "SpectrumSetup* / MySpectrumWiFi* / Spectrum Mobile / Spectrum Free Trial", 'Charter 网关和移动热点。不使用 Charter IEEE OUI。'],
            ["AT&amp;T", 'attwifi / ATT-WIFI* / ATT-GUEST* / ATT???????，以及 AT&amp;T 和 2Wire IEEE OUI', 'Pace 风格的出厂名称。许多设备由 Arris 代工。'],
            ["Verizon", 'Verizon-* / Fios-* / MyVerizon*，以及 Verizon IEEE OUI', '不包括 Verizon Connect / Telematics。许多 FiOS 设备由 Actiontec 代工。'],
            ["GL.iNet", 'GL-iNet* / GL-MT* / GL-AR* / GL-AXT*，以及 GL Technologies IEEE OUI 94:83:C4', '便携路由器。不匹配单独的 GL-*。许多主板仍使用芯片模块前缀。'],
            ["Ruijie", 'Wi-Fi @Reyee* / Reyee* / Ruijie*，以及 Ruijie Networks IEEE OUI', 'Reyee 园区 / 中小企业接入点。SSID 改名后仍可依据 BSSID 匹配。归入运营商 / 路由器类别。'],
            ["DWnet", 'DWnet Technologies IEEE OUI', '消费级 / 中小企业接入点。云管理 SSID 由用户命名。归入运营商 / 路由器类别。'],
            ["WAVLINK", 'Wi-Fi WAVLINK*，以及 Winstars IEEE OUI 80:3F:5D', '消费级接入点。归入运营商 / 路由器类别。'],
            ["Samsung SmartTags", '名称 SmartTag / Smart Tag / Galaxy SmartTag；UUID FD5A；厂商 ID 0x0075', 'FD5A 是常见的 SmartTag 服务。'],
            ["Tile Trackers", '名称 Tile；UUID FEED、FEDD；厂商 ID 0x00C7', '旧款 Tile 通过名称广播更容易发现。解码字段：FEED 中 8 字节的轮换私有 ID（不是序列号）。见 §9.6。'],
            ["Google Find Hub", 'BLE 服务 FEAA，数据前缀 40（附近）或 41（分离）', 'Google Find Hub 寻物标签。不匹配通用 Eddystone UID/URL/TLM。列表显示“附近”或“分离”；分离标签更醒目，并可能维持同一 MAC 约一天。归入寻物标签类别。解码：模式和 20 字节 EID。Chipolo / Pebblebee / moto tag 名称条目可能同时匹配。见 §5.4.1。'],
            ['DULT 追踪器', 'BLE 服务数据 FCB2（任意载荷）。归入寻物标签类别。无重点关注提示。', 'IETF“检测不受欢迎的位置追踪器”（DULT）定位广播。列表显示“靠近主人”或“分离”；分离标签更醒目，并可能维持同一 MAC 约一天。解码：网络 ID 和状态位。仅出现在 UUID 列表中的 FCB2 不会匹配。Chipolo / Pebblebee / moto tag 名称可能同时匹配。见 §5.4.1。'],
            ['iBeacon', 'Apple 0x004C，类型 0x02，长度 0x15；名称 *iBeacon*', '这是协议而非厂商。如果无线设备已有产品特征标签（Sony 电视、Tesla 手机钥匙），则移除此项。Minew / Estimote / Kontakt / Target Atrius basket 仍可同时显示。不是 Nearby Info 0x10 / AirTags 0x12 / AirPods 0x07，也不是 Eddystone FEAA。'],
            ["Target Atrius basket", 'Apple iBeacon UUID 5993A94C-7D97-4DF7-9ABF-E493BFD5D000；服务 0xB1BB', 'Target 购物篮 / Atrius 标签。在两家商店观察到数百个未命名设备，各有独立主编号 / 次编号，TX 为 0xC3。这些设备并非使用 Acuity 公司 ID 0x0346。可与 iBeacon 同时匹配，归入零售信标类别。'],
            ["Minew", 'IEEE OUI AC:23:3F；名称 Minew*', '深圳 Minew 信标 / 传感器。现场 AC:23:3F 设备常同时发送 iBeacon 或 Eddystone。'],
            ["Estimote", 'BLE 公司 ID 0x015D；名称 Estimote*', '定位信标 / 贴片。解码字段：帧类型（Nearable / 遥测）。不展开打包的传感器数据。见 §9.6。'],
            ["Kontakt.io", 'BLE 公司 ID 0x01FD；名称 Kontakt*', 'Kontakt 微定位信标。解码字段：UUID FE6A 的位置数据包（电量 / 发射功率 / 信道 / 移动状态）。见 §9.6。'],
            ["Penguin", '名称 / 通配 Penguin*；厂商 ID 0x09C8（XUNTONG）。含重点关注说明，默认已关注。', 'Flock 系列外置电池。0x09C8 是常用识别依据；Penguin* 名称来自旧版固件。解码：厂商数据中的 TN 序列号。新匹配时蜂鸣提醒。'],
            ["Pigvision", '名称 / 通配 Pigvision*。含重点关注说明，默认已关注。', 'Flock 系列 / 路边摄像头名称。仅按名称匹配。新匹配时蜂鸣提醒。'],
            ["FS Ext Battery", '名称 FS Ext Battery；通配 FS_*、FS Ext*；保留电池组 OUI 04:0D:84、1C:34:F1、38:5B:44、94:34:69、B4:E3:F9、F0:82:C0（已移除 Silabs 90:35:EA / 58:8E:81 / EC:1B:BD）。含重点关注说明，默认已关注，归入监控设备类别。', '通常是 Flock 系列摄像头电池组。名称匹配可信度中等。当前杆装设备通常不发出 Wi-Fi 或 BLE 广播。新匹配时蜂鸣提醒。'],
            ['Raven / ShotSpotter', '名称 RAVEN / ShotSpotter / SoundThinking；UUID 3100–3500；OUI D4:11:D6', 'Flock Raven 或 ShotSpotter 类枪声声学传感器。DIRECT-rR-Raven-* 等 Wi-Fi Direct SSID 通过 Raven 名称匹配，不使用通用 DIRECT- 前缀。0x09C8 归入 Penguin。归入监控设备类别。'],
            ["Digital Ally", 'IEEE 00:23:BD；名称 FirstVu / Digital Ally / EVO-HD / VuLink', '随身或车载摄像头。重点关注。静默的 LTE 设备不发出可接收广播。'],
            ["Limitless Pendant", 'BLE 服务 632de001-604c-446b-a80f-7963e950f3fb；名称 Limitless', '可穿戴对话录音设备。重点关注。'],
            ["Bee Pendant", 'BLE 服务 03d5d5c4-a86c-11ee-9d89-8f2089a49e7e；Bee Pioneer', 'Amazon Bee Pioneer 录音设备。重点关注。'],
            ["Omi", '名称 Omi / OpenGlass；BLE 23ba7924。不使用 Arduino 19B10000。', '挂件或 OpenGlass 摄像眼镜。重点关注。'],
            ["Friend Pendant", 'BLE 服务 1a3fd0e7-b1f3-ac9e-2e49-b647b2c4f8da；Friend Pendant', '可聆听对话的可穿戴项链。重点关注。'],
            ["Chipolo", '名称 / 通配 Chipolo*', 'Find Hub /“查找”/ DULT 寻物标签。仅按名称匹配。'],
            ["Pebblebee / moto tag", "Pebblebee*, moto tag / Moto Tag", 'Find Hub / DULT 定位标签。仅按名称匹配。'],
            ["Verkada", '名称 / 通配 Verkada*。含重点关注说明，默认已关注。', '用于建筑物和部分公共场所的云摄像头 / 车牌识别设备。仅按名称匹配。新匹配时蜂鸣提醒。'],
            ["Motorola Vigilant", 'Vigilant、Vigilant Solutions、Motorola Vigilant。含重点关注说明，默认已关注。', '机构和停车场使用的车牌识别设备。仅在广播名称时匹配。新匹配时蜂鸣提醒。'],
            ["eufy Security", "eufy / EufyCam / eufy*", 'Anker 摄像头和标签。'],
            ["Wyze", "Wyze / WyzeCam / Wyze*", '消费级摄像头。归入摄像头类别，而非监控设备类别。'],
            ["Ring", "Ring-*, Ring Doorbell / Camera / Setup", '避免仅凭 Ring 子字符串匹配。'],
            ["Arlo", 'Arlo / Arlo* / ARLO_VMB_*；Arlo Technology IEEE OUI', '摄像头和 VMB 基站接入点。SSID 改名后仍可依据 BSSID 匹配。'],
            ["Nest", "Nestcam, Nest Cam, Nest-Hello, Nest-*", '避免仅凭 Nest 单词匹配。属于摄像头，而非 Nest Thermostat BLE 条目。'],
            ["Nest Thermostat", 'BLE 公司 ID 0x01B5（Nest Labs）；名称 Nest Thermostat*', '不使用 Google 0x00E0。E / 第 3 代的 Nest 温度传感器可能匹配 0x01B5。壁装设备完成设置后通常仅使用 Wi-Fi。'],
            ["Nest Weave", 'BLE UUID 0xFEAF / 0xFEB0（Nest Labs 的 Weave-over-BLE）', '现场 N02QP 是第 2 代 Protect（Topaz2，Weave 产品 0x0009）。其他 Weave 摄像头 / 恒温器 / 传感器也使用相同 UUID。不是 Matter 0xFFF6。解码字段：FEAF 标识块（厂商 / 产品 / 配对 / 设备 ID）。见 §9.6。'],
            ["ecobee", 'BLE 公司 ID 0x07D6；名称 ecobee*', 'Premium BLE（设置 / Spotify）。房间传感器可能匹配同一 ID。'],
            ["Sensi", 'BLE 名称 Sensi*', 'Emerson / Copeland 的设置 BLE。不使用 Emerson 0x04DF。'],
            ["Honeywell Home", "BLE Honeywell Home* / Lyric Thermostat / Lyric T* / Amazon Smart Thermostat*", 'Resideo 制造。不使用 Honeywell 0x0526 或 Resideo 0x0B01（过于宽泛）。T9/T10 传感器使用 900 MHz。'],
            ["Honeywell Xenon HC", "BLE Xenon_*HC* / Xenon_CCB-U00-H* / 1962h* / 1952h* / 1902h*", '医疗条码扫描器 / 充电通信底座。不包括仓储 CCB-U00-G，也不是 Honeywell Home。归入健康设备类别。'],
            ["Omron", 'BLE 公司 ID 0x020E；名称 OMRON* / HEM-* / BLESmart_*', 'Omron Healthcare 血压计和体重秤。不包括工业 OMRON 0x02D5。归入健康设备类别。'],
            ["Withings", "BLE Withings* / WBS0* / BPM Connect", '体重秤和 BPM Connect。不包括 Nokia 手机或运营商网关。归入健康设备类别。'],
            ["Dexcom", "BLE Dexcom*", 'G6 / G7 血糖传感器。这里只是模式匹配，不能确定具体患者。归入健康设备类别。'],
            ["Haiku Fan", 'BLE UUID E0FC1000-1FB1-4168-96DF-B3F057A86E01；名称 Haiku Fan / Mammoth Fan', 'Big Ass Fans，使用自定义 128 位服务。'],
            ["Tuya", 'BLE 公司 ID 0x07D0；UUID FD50；名称 TUYA*', '插座 / 灯具 / 摄像头 / 传感器。不匹配两字母 TY。解码字段：绑定标志和协议版本（UUID 字节已加密）。见 §9.6。'],
            ["ASSA ABLOY", 'BLE 0x012E / HID 0x0124 / Yale 0x0BDE；UUID FCBF；Seos UUID 00009800-…；名称 Seos / Yale*', '门禁设备类别，包括门锁、读卡器、Seos 凭证。使用 HID Mobile Access 的手机可能匹配 Seos。不使用 Apple FCB2。'],
            ["August", 'BLE 公司 ID 0x01D1；UUID FE24；名称 August*', 'August Home 门锁。现场名称 L40A33A。不使用 ASSA 0x012E。'],
            ["Schlage", 'BLE Allegion 0x013B；UUID FCF4；名称 SCHLAGE*', 'Encode 及其他 Allegion BLE 设备。'],
            ["Nuki", '自定义 UUID a92ee000–a92ee300 / a92ae200；名称 Nuki*', 'Keyturner / Ultra / Opener。不使用 SIG 公司 ID。'],
            ["SALTO", 'BLE 公司 ID 0x0199；名称 SALTO*', '门禁设备类别。商用门锁或读卡器。'],
            ["dormakaba", 'BLE 公司 ID 0x0C64；名称 dormakaba* / Saflok* / Oracode*', '门禁设备类别。酒店 / 商用门锁。'],
            ["Lockly", 'BLE 名称 LOCKLY*', '仅按名称匹配。不使用 Nordic 0x0059。'],
            ["Kevo", 'BLE Unikey 0x015E；名称 Unikey* / Kevo*', "Kwikset Kevo."],
            ["Master Lock", 'BLE 公司 ID 0x014B；名称 Master Lock*', '蓝牙挂锁。不匹配单独的 Master 子字符串。'],
            ["igloohome", 'BLE 公司 ID 0x05BA；名称 igloohome*', '钥匙盒 / 门锁。不匹配单独的 igloo。'],
            ["Tedee", 'BLE 公司 ID 0x0725；名称 Tedee*', '改装式门锁。'],
            ["Paxton", 'BLE 公司 ID 0x0196；名称 Paxton* / Net2*', '门禁设备类别。Net2 门禁读卡器或控制面板。'],
            ["Kwikset", 'BLE 名称 Kwikset*', '不使用 Spectrum Brands 0x0356。Kevo 归入 Unikey 条目。'],
            ["myQ", 'BLE 公司 ID 0x0878（Chamberlain）；UUID 26D91A37-…；名称 MyQ-*', '车库门中枢。'],
            ["Hatch", 'BLE 公司 ID 0x0434；OUI C8:FA:9C；名称 Hatch Rest* / Restore* / Mini*', 'Hatch Baby 助眠音响。不使用 180A/180F。归入智能家居类别。'],
            ["Orbit B-hyve", '名称 bhyve* / B-hyve*；OUI 44:67:55；UUID FE32', 'Orbit 水管定时器。不仅凭 Pro-Mark 公司 ID 0x047F 匹配。归入智能家居类别。'],
            ["Samsung appliance", "Wi-Fi [fridge]* / [oven]* / [range]* / [cooktop]* / [refrigerator]*", 'Family Hub / 炉灶设置热点，不是 SmartTag。归入智能家居类别。'],
            ["EcoWater", 'Wi-Fi 名称 H2O- 加 12 个字符', '软水机设置热点（通常是去掉冒号的 MAC）。不匹配单独的 H2O。归入智能家居类别。'],
            ["Retail LED sign", "BLE UUID 56D63956-93E7-11EE-B9D1-0242AC120002", 'LED 信息显示屏。广播名称是显示文字（FOOD、STORY BAORD），并非产品名。不使用 Earda OUI F0:96:02。归入信息标牌类别。'],
            ["Electronic shelf label", 'BLE UUID 0x1857（SIG 电子货架标签服务）', '蓝牙 5.4 PAwR 电子货架标签。多数 Hanshow / SES-imagotag 标签使用专有无线协议，不会匹配。归入信息标牌类别。'],
            ["Chevrolet hotspot", "Wi-Fi myChevrolet*", 'GM 车载热点。使用出厂 SSID，BSSID 经常随机化。'],
            ["Rivian", 'BLE 公司 ID 0x0941；名称 Rivian*', '手机钥匙 / 露营音箱 / 传感器。'],
            ["Govee", 'BLE 名称 Govee* / GBK_* / ihoment_* / GV5108* / GVH5*', '灯具和传感器（H5075 / H510x 温湿度计）。仅依据名称识别。匹配后解码字段：0xEC88 H5074/H5075 及 0x0001 H510x 的温度 / 湿度 / 电量。灯具可能不符合这些数据格式。见 §9.6。'],
            ["HP", 'BLE 公司 ID 0x0065；UUID FE78；ENVY*；Wi-Fi HP-Print*', '打印机，常见的办公 / 家庭背景信号。'],
            ["Epson", 'Wi-Fi / BLE 名称 *EPSON-ET-* / *EPSON-WF-*', 'EcoTank 和 WorkForce。不使用 Seiko Epson 0x0040。归入智能家居类别。'],
            ["LG webOS TV", 'BLE 名称 [LG] webOS* / webOS TV*；UUID FEB9', '客厅电视。不使用 LG 公司 ID 0x00C4。未命名 FEB9 可能是其他 LG 无线设备。归入智能家居类别。'],
            ["Roku", 'Wi-Fi Roku IEEE OUI（BSSID 或厂商 IE C8:3A:6B）；DIRECT-roku* / Roku-*', '流媒体棒 / Roku 电视。隐藏的 Wi-Fi Direct 遥控热点即使 BSSID 随机化，也可依据厂商 IE 匹配。不使用 WPS 00:50:F2 或 P2P 50:6F:9A。归入智能家居类别。'],
            ["Nespresso", 'BLE 公司 ID 0x0225；Vertuo/Venus/Barista/Mini UUID；名称 Vertuo* / Venus_*', '咖啡机。不匹配单独的 Venus。归入智能家居类别。'],
            ["RadiaCode", 'BLE UUID E63215E5-7003-49D8-96B0-B024798FB901；名称 RadiaCode*', '辐射检测仪（101/102/103/Zero）。现场 0x77AC 并非 SIG 分配值。归入智能家居类别。'],
            ["Shokz", 'BLE 名称 OpenRun / LE-OpenRun / OpenFit / Shokz', '骨传导耳机。不使用电池服务 0x180F 或 Qualcomm FD92。归入音频设备类别。'],
            ["Mercedes MBUX", "Wi-Fi MBUX*", '车载热点，使用出厂 SSID。'],
            ["Motive", "Wi-Fi Motive * / Motive_* / Motive Hotspot* / KeepTruckin*", 'KeepTruckin 电子行车记录设备 / 车队热点。不按 Motive 子字符串匹配（如 Locomotive）。归入车辆类别。'],
            ["PeopleNet", 'Wi-Fi PNet*，以及 PeopleNet IEEE OUI 98:5D:46', '车队电子行车记录设备 / 卡车热点。不是 Motive。归入车辆类别。'],
            ["Uconnect", "Wi-Fi Uconnect*", 'Stellantis 车载热点。归入车辆类别。'],
            ["CarPlay", 'Wi-Fi CarPlay* / 名称包含 CarPlay', 'Alpine / 车机的车载热点。归入车辆类别，而非运营商类别。'],
            ["CARLINK", 'Wi-Fi CARLINK-??????（6 位十六进制）；Panasonic Automotive OUI CC:57:63；Zhuolian 68:8F:C9', 'CarPlay / Android Auto 适配器或车机热点。同组设备常见 Alps Alpine E0:2D:F0，但不将其作为单独 OUI 规则（也用于 Toyota / Lexus 车机）。厂商 IE 00:A0:40（旧 Apple）未收录。归入车辆类别，而非运营商类别。'],
            ["Cradlepoint", 'Wi-Fi IBR* / IBR600* / IBR1100* / IBR1700* / R 系列 / Cradlepoint*，以及 CradlePoint IEEE OUI 00:30:44 / 00:E0:1C。含重点关注说明，默认已关注。', 'Ericsson Cradlepoint 车载路由器。常见于美国警务车队，也用于政府、市政及其他企业车队。隐藏或改名的 SSID 仍可依据 BSSID 匹配。这里只是模式匹配，不能确定具体机构。新匹配时蜂鸣提醒。归入公共安全类别，执法机构会使用，但并非其专用设备。'],
            ["AirLink", 'Wi-Fi AirLink*，以及 Sierra Wireless / AirLink Communications IEEE OUI。含重点关注说明，默认已关注。', 'Sierra Wireless AirLink 车载网关。常见于美国警务车队，也用于政府、市政及其他企业车队。隐藏或改名的 SSID 仍可依据 BSSID 匹配。不使用 AirLink WiFi Networking 00:23:D3。这里只是模式匹配，不能确定具体机构。新匹配时蜂鸣提醒。归入公共安全类别，执法机构会使用，但并非其专用设备。'],
            ["Compex", 'Wi-Fi 114K-*，以及 Compex IEEE OUI 04:F0:21 / 00:80:48 / 00:40:29。含重点关注说明，默认已关注。', '部分公共安全车辆接入点。其他 Compex 无线设备也使用相同 OUI；政府、市政及其他企业车队也可能使用同类设备。这里只是模式匹配，不能确定具体机构。新匹配时蜂鸣提醒。归入公共安全类别，执法机构会使用，但并非其专用设备。'],
            ["Novatel Wireless", 'Inseego IEEE OUI 28:80:A2。含重点关注说明，默认已关注。', '原 Novatel Wireless，曾在公共安全车载热点观察中出现。相同前缀也可能匹配 Inseego。政府、市政及其他企业车队也可能使用同类设备。这里只是模式匹配，不能确定具体机构。新匹配时蜂鸣提醒。归入公共安全类别，执法机构会使用，但并非其专用设备。'],
            ["Utility Inc", 'Utility, Inc IEEE OUI 00:09:BC / 00:16:ED。含重点关注说明，默认已关注。', '曾在公共安全车载热点观察中出现。政府、市政及其他企业车队也可能使用同类设备。这里只是模式匹配，不能确定具体机构。新匹配时蜂鸣提醒。归入公共安全类别，执法机构会使用，但并非其专用设备。'],
            ["Samsara", 'BLE 公司 ID 0x0B6B；名称 Samsara*', '车队电子行车记录设备 / 拖车 / 网关。归入车辆类别。'],
            ["Goodyear TPMS", 'BLE 公司 ID 0x0B99', '智能轮胎 / SightLine 类 BLE。不是原装 315/433 MHz 气门嘴传感器。MAC 随机化，厂商依据公司 ID 确定。归入车辆类别。'],
            ["Schrader TPMS", 'BLE 公司 ID 0x0601', 'AirCheck BLE / 拖车 / 房车，不是 Nokia 0x0001 仿制品。归入车辆类别。'],
            ["Pacific TPMS", 'BLE 公司 ID 0x0E32', 'Pacific Industrial 原装胎压监测。归入车辆类别。'],
            ["Huf", 'BLE 公司 ID 0x070A', 'Huf Hülsbeck 胎压监测和车辆门禁设备，不一定是气门嘴。归入车辆类别。'],
            ["FOBO TPMS", 'BLE 公司 ID 0x0127（Salutica）；UUID 00EE；名称 FOBO*', '摩托车 / 汽车后装 BLE 胎压监测。归入车辆类别。'],
            ['后装 TPMS', 'BLE 名称 TPMS*；UUID FBB0；厂商 0x0001 的数据 80/81/82/83', '廉价气门帽 BLE 胎压监测（TPMS1 / FBB0 系列）。不单凭 Nokia 0x0001 匹配。解码字段：轮位、压力（kPa）、温度、电量、报警。归入车辆类别。见 §9.6。'],
            ["SYTPMS", 'BLE 名称精确匹配 BR；UUID 0x27A5', 'SYTPMS / BR 自行车或滑板车 BLE 胎压监测。解码字段：表压（psi）、温度、电量、移动状态。归入车辆类别。见 §9.6。'],
            ["TireCheck", 'BLE 公司 ID 0x0BA2；名称 TireCheck*', 'TireCheck BLE 轮胎传感器。归入车辆类别。'],
            ["TPMS service", 'BLE UUID 0x1860（SIG 胎压监测服务）', '任何广播 Bluetooth SIG 胎压监测系统服务的传感器。归入车辆类别。'],
            ["Ruuvi", 'BLE 公司 ID 0x0499；名称 Ruuvi*', '广播温度 / 湿度 / 气压 / 运动数据的标签。归入智能家居类别。解码字段：数据格式 5（RAWv2）和格式 3 的湿度 / 气压 / 加速度 / 电量。格式 3 温度采用符号数值编码，并非普通整数。见 §9.6。'],
            ["Blue Maestro", 'BLE 公司 ID 0x0133', 'Tempo Disc 温湿度记录仪。归入智能家居类别。解码字段：电量、间隔、日志条数、温度、湿度。见 §9.6。'],
            ["SensorPush", 'BLE UUID EF090000-…090AA9 / …090AB0；名称 SensorPush*', 'HT / HTP 温湿度设备，使用自定义 128 位服务。归入智能家居类别。'],
            ["Tapo", "Tapo / Tapo*", 'TP-Link 摄像头。'],
            ["Reolink", "Reolink / Reolink*", '消费级摄像头。'],
            ["Hikvision", 'Hikvision / HIKVISION / Hikvision*。含重点关注说明，默认已关注。', '商业闭路电视及部分公共摄像杆。仅按名称匹配，新匹配时蜂鸣提醒。'],
            ["Dahua", 'Dahua / DAHUA / Dahua*。含重点关注说明，默认已关注。', '商业闭路电视及部分公共摄像杆。仅按名称匹配，新匹配时蜂鸣提醒。'],
            ["Meshtastic", "Meshtastic / Meshtastic_*; UUID 6ba1b218…", 'LoRa Mesh 节点。名称和服务 UUID 提供较强依据。'],
            ["Helium", "Helium / Helium*", 'LoRaWAN / Helium 热点名称。'],
            ["Genetec AutoVu", 'Genetec、AutoVu。含重点关注说明，默认已关注。', '市政 / 停车场车牌自动识别。仅按名称匹配，新匹配时蜂鸣提醒。'],
            ["BlueTOAD Spectra", 'IEEE OUI 00:14:7B（Iteris）；名称 BlueTOAD* / Vantage Velocity / Spectra CV / TrafficCast / VantageARGUS / BlueARGUS。无重点关注提示，默认不关注。', 'Iteris 路边蓝牙行程时间采集设备（Vantage Velocity，现为 Spectra / Spectra CV）。采样经过的手机和车载蓝牙，通过两点匹配估算速度。静默 / 仅接以太网的机柜和 5.9 GHz C-V2X 不会出现。Iteris OUI 也可能匹配其他 Iteris 路侧设备。这里只是模式匹配，不能确认具体机柜。'],
            ["BlipTrack", 'IEEE OUI 00:0E:A5（BLIP Systems）；名称 BlipTrack* / BLIP Systems。无重点关注提示，默认不关注。', '路边蓝牙 / Wi-Fi 行程时间传感器，功能与 BlueTOAD 类似。静默 / 仅接以太网的机柜可能不广播。这里只是模式匹配，不能确认具体机柜。'],
            ["Hanwha Wisenet", 'IEEE OUI 00:09:18（Samsung Techwin）；名称 Wisenet* / *_WISENET / Hanwha*。含重点关注说明，默认已关注。', 'Hanwha Vision / Wisenet 摄像头，用于商业闭路电视及部分公共摄像杆。设置 SSID 是较强的匹配依据。新匹配时蜂鸣提醒。'],
            ["Uniview", '浙江宇视 IEEE OUI 14:BA:88 / 48:EA:63 / 6C:F1:7E / 88:26:3F / C4:79:05；名称 Uniview* / UNV-* / Uniarch*。含重点关注说明，默认已关注。', 'Uniview / UNV 摄像头，用于商业闭路电视及部分公共摄像杆。新匹配时蜂鸣提醒。'],
            ["Rhombus", 'IEEE OUI CC:47:BD；名称 Rhombus*。含重点关注说明，默认已关注。', 'Rhombus 云摄像头，通常仅在未注册或离线时发送 BLE 广播。新匹配时蜂鸣提醒。'],
            ["MeshCore", 'BLE 名称 MeshCore / MeshCore_*。无重点关注提示。', 'MeshCore LoRa 配套设备。不使用 Nordic UART UUID 6E400001（众多 ESP32 串口板均使用）。'],
            ["goTenna", 'BLE UUID 1276aaee-df5e-11e6-bf01-fe55135034f3；名称 goTenna*。无重点关注提示。', 'goTenna Mesh 或 Pro 配套设备。无法接收其 UHF Mesh 网络。Pro 面向机构销售。这里只是模式匹配，不能确定具体操作者。'],
            ["SenseCAP", 'Wi-Fi SenseCAP / SenseCAP_*。无重点关注提示。', 'Seeed SenseCAP LoRaWAN / Helium 网关设置热点。接入以太网后通常静默。使用 Helium 名称的设备也可能匹配 Helium。'],
            ["RAK WisGate", 'Wi-Fi RAK7* / RAK7268* / WisGate*。无重点关注提示。', 'RAKwireless WisGate LoRaWAN 网关设置热点。接入以太网后通常静默。'],
            ["GhostESP", 'Wi-Fi GhostNet / GhostNet*。含重点关注说明，默认已关注。', 'GhostESP ESP32 审计固件的默认热点。相同主板也用于 DIY，不能证明正在攻击。新匹配时蜂鸣提醒。'],
            ["Bruce", 'Wi-Fi BruceNet / BruceNet*。含重点关注说明，默认已关注。', 'Bruce ESP32 渗透测试固件的默认热点。恶意门户 SSID 看起来与普通 Wi-Fi 相同，不会匹配。不能证明正在攻击。新匹配时蜂鸣提醒。'],
            ["Rekor", 'Rekor / Rekor*。含重点关注说明，默认已关注。', '公路 / 交通运输车牌自动识别。仅按名称匹配，新匹配时蜂鸣提醒。'],
            ['Axon', 'OUI 00:25:DF（Axon Enterprise）；名称 Axon Body / Fleet / Dock / Axon*；UUID FE6B/FE6C/FC81；TASER International 公司 ID 0x034D；服务数据包含 BWCDEVICE（任意 UUID，也匹配字节倒序）。含重点关注说明，默认已关注。', '公共安全类别，执法机构会使用但并非专用（政府、市政和其他企业车队也可能使用同类设备）。包括随身、车载、底座或 TASER。Body 3/4 常使用公共 OUI 发送 BLE 广播。BWCDEVICE 位于服务载荷而非本地名称中。不能确定具体人员。不使用 Axon Networks 00:58:28。ZTE Axon 手机可能因名称匹配。新匹配时蜂鸣提醒。'],
            ['WatchGuard Video', 'OUI 00:1D:96；名称 WatchGuard / VISTA WiFi / VISTA XLT。含重点关注说明，默认已关注。', '公共安全类别，执法机构会使用但并非专用（政府、市政和其他企业车队也可能使用同类设备）。WatchGuard Video（现属于 Motorola）随身 / 车载摄像头。不使用 WatchGuard 防火墙 OUI 00:01:21。巡逻设备可能保持静默。新匹配时蜂鸣提醒。'],
            ['Ray-Ban／Meta 眼镜', 'BLE 公司 ID 0x01AB、0x058E、0x0D53；UUID FEB7/FEB8；名称 Ray-Ban / Meta View / Oakley Meta。含重点关注说明，默认已关注。', '通常为 Ray-Ban Meta。相同 ID 也用于 Quest 和其他 Meta 可穿戴设备。不能证明正在录制。新匹配时蜂鸣提醒。'],
            ['Snap Spectacles', 'BLE 公司 ID 0x03C2；UUID FE45；Spectacles 名称。含重点关注说明，默认已关注。', 'Snap Spectacles 或其他 Snap BLE 设备。不能证明正在录制。新匹配时蜂鸣提醒。'],
            ["Vuzix", 'BLE 公司 ID 0x060C；名称 Vuzix*。含重点关注说明，新安装时默认已关注。', 'Vuzix 智能眼镜。不能证明正在录制。已关注时，新匹配会蜂鸣提醒。'],
            ["Avigilon", 'Avigilon / Avigilon*。含重点关注说明，默认已关注。', '市政摄像杆和商业场所的 Motorola 摄像头 / 车牌识别设备。仅按名称匹配，新匹配时蜂鸣提醒。'],
            ["Axis", 'AXIS-* / Axis Camera。含重点关注说明，默认已关注。', '市政 / 公共闭路电视摄像杆。仅按名称匹配，新匹配时蜂鸣提醒。'],
            ["UniFi", 'UniFi、Ubiquiti、UAP-*（Wi-Fi 或 BLE）', '仅按名称匹配。如需按 BSSID 匹配，请使用 UniFi AP。归入运营商 / 路由器类别。'],
            ['UniFi AP', 'Wi-Fi UniFi* / UAP-* / UBNT*，以及 Ubiquiti IEEE OUI（BSSID 或厂商 IE）', '园区 / 城市 / 家庭接入点。归入运营商 / 路由器类别，而非监控设备类别。虚拟 BSSID 可能无法匹配 MAC OUI，但 Ubiquiti 厂商 IE 仍可匹配。'],
            ["UniFi Protect", 'BLE 名称 UVC G3/G4/G6 Instant', '处于 BLE 设置模式的 Protect Instant 摄像头。不使用接入点 BSSID OUI，也不使用自定义 16 位 252A/2529。归入监控设备类别。'],
            ['业余 BLE 串口', 'BLE 名称 HMSoft / HM-10 / CC41 / AT-09 / JDY-08/10/16/31 / BT05 / MLT-BT05 / ESP32（仅 BLE）。含重点关注说明，默认已关注。', '廉价 UART 模块。相同主板用于 DIY，也曾用于部分加油机 / ATM 非法附加装置。不是盗刷检测器，不包括经典蓝牙 HC-05/HC-06。新匹配时蜂鸣提醒。如果这些名称属于当地背景信号，可在筛选中隐藏。'],
            ['Hak5 Pineapple', '名称 Pineapple_XXXX / Hak5 / WiFi Pineapple。含重点关注说明，默认已关注。', '设置 / 管理热点。不使用 Alfa OUI 00:C0:CA。PineAP 仿冒热点看起来与普通 SSID 相同。新匹配时蜂鸣提醒。'],
            ['Flipper Zero', 'OUI 0C:FA:22；BLE 名称 Flipper*。含重点关注说明，默认已关注。', 'Flipper Devices IEEE 地址段（2024）。自定义固件可改名。不能证明正在攻击。新匹配时蜂鸣提醒。'],
            ['Pwnagotchi', 'MAC DE:AD:BE:EF:DE:AD；名称 pwnagotchi。含重点关注说明，默认已关注。', '握手采集器信标。新匹配时蜂鸣提醒。'],
            ['Marauder / Deauther', '名称 MarauderAP / Marauder / Deauther。含重点关注说明，默认已关注。', 'ESP32 Marauder 或 Spacehuhn 类默认名称。相同主板也用于 DIY。新匹配时蜂鸣提醒。'],
            ['Porkchop', '名称 PORKCHOP / M5PORKCHOP；厂商 IE 50:52:4B。含重点关注说明，默认已关注。', 'M5PORKCHOP Cardputer 或 CYD 移植版。CYD 远程热点名称为 PORKCHOP。BACON 伪造热点使用 50:52:4B 标识。不使用 Espressif OUI，不匹配 BLE 垃圾广播。新匹配时蜂鸣提醒。'],
        ]
    stock_sigs.sort(key=lambda row: row[0].replace("&amp;", "&").lower())
    flow.append(table(
        ['特征', '主要规则', '可信度说明'],
        stock_sigs,
        [1.45 * inch, 2.7 * inch, 2.35 * inch],
    ))
    flock_ouis = [
        "70:C9:4E", "3C:91:80", "D8:F3:BC", "80:30:49", "B8:35:32", "14:5A:FC", "74:4C:A1",
        "08:3A:88", "9C:2F:9D", "C0:35:32", "94:08:53", "E4:AA:EA", "F4:6A:DD", "F8:A2:D6",
        "24:B2:B9", "00:F4:8D", "D0:39:57", "E8:D0:FC", "B8:1E:A4", "70:08:94",
        "58:00:E3", "5C:93:A2", "64:6E:69", "48:27:EA", "82:6B:F2",
    ]
    oui_cols = 4
    oui_w = 6.5 * inch / oui_cols
    oui_head = [Paragraph(
        '<b>LiteOn 摄像头无线模块 OUI 列表</b>（不属于重点关注；B4:1E:52 仍归入 Flock Safety Cameras）',
        S["cell_b"],
    )] + [""] * (oui_cols - 1)
    oui_body = [
        [Paragraph(flock_ouis[i + j] if i + j < len(flock_ouis) else "", S["cell"]) for j in range(oui_cols)]
        for i in range(0, len(flock_ouis), oui_cols)
    ]
    oui_table = Table(
        [oui_head] + oui_body,
        colWidths=[oui_w] * oui_cols,
        rowHeights=[20] + [16] * len(oui_body),
        splitByRow=0,
    )
    oui_table.setStyle(TableStyle([
        ("SPAN", (0, 0), (-1, 0)),
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), ACCENT_DK),
        ("GRID", (0, 0), (-1, -1), 0.35, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PANEL]),
        ("FONTNAME", (0, 1), (-1, -1), "FWText"),
    ]))
    flow += [
        Spacer(1, 10),
        oui_table,
        P('C. 故障排查', "h2"),
        P(
            '如果实时界面与前述章节不符，请从这里开始排查。即使列表经过筛选或暂时安静，日志与报告仍会运行。模式匹配不能确认设备身份。'
        ),
    ]
    flow.append(table(
        ['现象', '可能原因', '处理方法'],
        [
            ['每次启动都显示权限提示', '必需的运行时权限被拒绝，或被系统重置。', '授予位置（精确）、附近的 Wi-Fi、蓝牙扫描/连接及通知权限。开启系统定位。完整清单见 §4.5.2。'],
            ['想尽可能多地接收信号 / 手机发热', '高性能、保持屏幕常亮和加快 Wi-Fi 扫描会持续使用无线电和屏幕。', '长时间观测时属于正常现象。按 §4.5 检查设置。接入电源或使用充电宝。结束后切回均衡模式并关闭加快 Wi-Fi 扫描。列表为空仍不等于“安全”。'],
            ['Wi-Fi 列表为空，但 BLE 正常', '尚未到系统扫描窗口、扫描被限流、Wi-Fi 关闭，或定位关闭。', '开启 Wi-Fi 和定位。查看顶部状态：Wi-Fi 下次扫描剩余秒数，或正在等待系统。上次收到的接入点应继续保留；高性能模式约每 30 秒收到一批。若开启加快 Wi-Fi 接入点扫描，并在开发者选项中关闭 Wi-Fi 扫描节流，则约为 8 秒。'],
            ['BLE 原本正常，随后列表为空', '三星系统暂停了扫描器。', '查看顶部是否显示 BLE 正在重启，或 BLE 已暂停、正在重启。查看时保持屏幕常亮。离开应用时允许后台运行，并将电池使用设为不受限制。只有持续无响应时才切换扫描强度。'],
            ['人群中界面卡住，随后两个列表都为空', '广场中大量轮换 BLE 地址耗尽了内存。', '实时设备集上限约为 400 个。不需要日志文件时可关闭记录。密集人群中优先使用信号强度列表，而非混合视图。'],
            ['雷达看似为空，但列表有设备', '离开的设备在雷达中变暗，或被实时界面筛选条件隐藏。', '暗点表示设备已超过过期时间或短暂保留时间。检查是否开启了仅显示特征匹配，而现场没有匹配项。'],
            ['所有设备都显示“已离开”', '过期时间短于广播间隔，或扫描服务被终止。', '将过期时间提高到 90–120 秒，或提高扫描强度。确认扫描通知仍存在，并将应用加入电池优化例外。'],
            ['锁屏后服务停止，或 BLE 停止', '厂商电池管理策略，和/或三星息屏 BLE 策略所致。', '在设置中开启查看时保持屏幕常亮，并允许后台运行、将电池使用设为不受限制。如需持续扫描，请将 Fieldwatch 保留在最近任务中，不要划掉。'],
            ['关闭应用后仍在扫描 / 蜂鸣', '扫描服务仍在运行。', '从最近任务中划掉 Fieldwatch，或点击扫描通知中的停止。按主屏幕键会保留扫描。'],
            ['无法删除特征', '删除按钮位于编辑页，而非列表页。', '打开该特征，点击底部的删除特征并确认。误删内置项后可恢复默认设置。'],
            ['特征中没有解码字段一栏', '该项仅适用于 Wi-Fi（隐藏 SSID / 厂商 IE / 无线类型为 Wi-Fi），或当前打开的是实时界面而非编辑器。', '打开一个 BLE 特征，如 Ruuvi、Remote ID 或 Govee。解码字段位于添加规则下方。见 §9.6。'],
            ['详情中缺少解码字段', '该特征没有解码映射，广播已加密或长度不足，或未满足条件限制。', '打开特征 → 解码字段。详情中的说明表示存在映射，但此数据包不适用。常见错误是把公司 ID 计入偏移量 0。加密的 Fitbit / Find My 广播仍显示十六进制。见 §9.6.1 / §9.6.5。'],
            ['详情显示 127 dBm / 信号极强', '127 是蓝牙“RSSI 不可用”的标记，并非发射功率。部分蓝牙协议栈会在回调中返回该值。', '1.1.11 起，当前值、最小/最大值、趋势线、信号追踪和分享均排除 127。真实 BLE 接收值通常远低于 0 dBm。见 §5、§5.5。'],
            ['十六进制数据看似正确，但预览为空', '偏移量包含了公司 ID、字节序错误，或条件限制的十六进制值与数据包不符。', '在详情的原始载荷中按字节对计数，第一对为 0。若规范采用大端序，尝试 BE。核对条件长度与十六进制长度。打开内置 Ruuvi 特征，参考其字段卡片。见 §9.6.3–§9.6.4。'],
            ['详情中没有自定义名称编辑入口', 'BLE 地址为随机 / 隐私地址（IEEE 本地位或 Android Random 类型）。', 'BLE 出现此情况属于预期行为，因为名称不能随地址轮换延续。Wi-Fi 始终显示编辑图标，包括采用本地管理地址的车辆 / Mesh BSSID。已保存的名称仍会显示，关注功能也仍可监测此 MAC。'],
            ['想添加摄像头 / 无人机 / 监控设备筛选标签', '这些类别的观测配置不属于内置预设。', '进入筛选 → 仅显示，选择类别标签，再选择将当前设置另存为。恢复默认特征与预设会恢复精简的内置预设，并清除自定义标签。'],
            ['暂停时筛选标签看起来没有反应', '暂停仅冻结实时界面。', '这是预期行为。筛选与设置仍接受操作。在实时标签页再次点击实时后，冻结的列表才会更新。'],
            ['删除预设后，实时界面看起来没有变化', '删除仅移除配置快照，不会清除当前生效的筛选条件。', '这是预期行为。应用另一个预设，或点击重置筛选，才能改变实时界面显示的内容。'],
            ['找不到雷达 / 列表 / 按类别 / 切换视图入口', '显示面板未打开，或正在设置 / 筛选页查找。', '实时界面 → 点击调节（右上角滑杆图标）。视图是第一个下拉项。再次点击调节或点击变暗的列表即可关闭。见 §4.4、§5.3、图 3。'],
            ['找不到标题行 / 副标题行 / RSSI 下方的频率', '显示面板未打开，或正在设置页查找。', '实时界面 → 点击调节（右上角滑杆图标）。标题行和副标题行下拉项位于短暂保留下方。频率是一个开关；信道与 MHz 显示在 RSSI 下方，而非身份信息行。见图 3。'],
            ['列表仍显示“Apple, Inc. · AirTag…”', '显示 → 副标题行设为名称 + 类型，采用与详情相同的类型推测。', 'IEEE 厂商信息位于详情页。如不想显示类型推测，将副标题行设为广播名称或无。'],
            ['实时界面某一行显示“!”', '匹配的特征填写了重点关注说明。内置项包括 Hobby BLE serial、Axon、WatchGuard Video、Ray-Ban / Meta glasses、Snap Spectacles、Fieldy、Plaud Note、Hak5 Pineapple、Flipper Zero、Pwnagotchi、Marauder / Deauther、GhostESP、Bruce、Porkchop、Cradlepoint、AirLink、Compex、Novatel Wireless、Utility Inc、Flock、Penguin、Pigvision、FS Ext Battery、Genetec AutoVu、Rekor、Motorola Vigilant、Verkada、Avigilon、Axis、Hikvision、Dahua、Hanwha Wisenet、Uniview 和 Rhombus。', '打开详情并阅读重点关注说明。模式匹配不能确认身份。Meta 公司 ID 也可能匹配 Quest。Fieldy / Plaud Note 是可穿戴录音设备，不能据此断定有人正在录制你。摄像头 / ALPR 条目表示路侧或公共监控 / 车牌读取设备，不能指认某根杆上的设备。如只是当地常见干扰，可在筛选中隐藏该系列。此图标不同于解码六边形，也不同于荧光色的已提醒铃铛。'],
            ['实时界面某一行显示铃铛', '该设备已在本次会话中触发关注提醒（蜂鸣 / 语音 / 闪烁）。', '这是预期行为。图标会保留到退出 Fieldwatch。重点关注使用红色“!”。最新提醒排序也以这次事件为准；雷达的提示动画结束后，该点仍保留荧光色圆环。'],
            ['特征标签有六边形，但详情没有解码字段', '六边形表示特征具有解码映射，不表示当前广播成功解析。Govee 灯具与温湿度计共享 Govee 名称，灯具通常只发送名称。', '打开详情：若出现说明，表示映射不适用于此数据包。温湿度计包括 H5074/H5075（0xEC88）和 H510x（0x0001）。关闭显示 → 特征名称会同时隐藏六边形。移除不适用的映射：特征库 → 对应条目 → 解码字段 → 移除解码映射。见 §5.4、§9.6。'],
            ['手机 / 电脑类别里满是 Fast Pair', '大多是已配对设备的账户密钥广播，例如关联账户的耳机或手机，并不表示有人正在配对。', '筛选 → 隐藏 Fast Pair 账户密钥广播。配对模式仍会显示，标签为 Fast Pair 配对中。如需全部隐藏，使用隐藏所选 Fast Pair。未广播 Fast Pair 的口袋中 Android 手机仍可能是未匹配设备；Apple Device 则常见于密集的 Continuity 广播。见 §9.5。'],
            ['手机 / 电脑类别中从未看到 Android', 'Apple Continuity 通常持续广播，而大多数 Android 手机不发送稳定的“我是一部手机”载荷。', '这是预期行为。Fast Pair 是常见的 Android 相关标签，设备经常没有名称。Google 特征仅覆盖 Pixel / Chromecast。手机热点仅在手机以出厂 SSID 作为接入点时匹配。口袋中安静的 Android 手机通常显示为未匹配 BLE。见 §9.5。'],
            ['列表文字太密 / 想减少每行内容', '额外显示项已开启，或副标题行仍为 MAC。', '见 §5.3 / §12.11：将副标题行设为无，关闭信号条、频率和首次/末次时间。这不会隐藏设备。如果显示的设备集合仍不合适，再调整筛选。'],
            ['找不到标为已见 / 重置已见', '这些按钮只在开启仅新检测时出现。', '开启筛选 → 仅新检测。标为已见与重置已见会出现在实时界面底部标签栏上方。'],
            ['找不到重新开始', '它位于实时界面，而非筛选页。', '开启筛选 → 随行。重新开始位于底部标签栏上方。它会清除 GPS 轨迹，不会清空实时列表。'],
            ['关注列表从不触发提醒', '提醒已关闭、蜂鸣和语音都关闭，或匹配项被仅新检测 / 其他筛选条件隐藏。', '开启关注提醒，再开启蜂鸣、语音或两者。确认已关注该系列，且对应行能在实时界面显示。点击测试提醒，并提高媒体音量。跳转可配合任一提示方式使用。系统通知为可选项，默认关闭。'],
            ['关注列表会蜂鸣，但不说话', '已关闭关注特征语音、媒体音量过低，或手机没有可用的中文文字转语音语音包。', '设置 → 关注特征语音（默认开启）。提高媒体音量。点击测试提醒；类别 + 特征模式会读出“寻物标签，Apple AirTags”，若同时开启蜂鸣，则先响提示音。信号追踪不会播报语音。'],
            ['寻物标签 / 监控设备类别中没有内容', '仅显示该类别，但周围没有正在广播的匹配设备。', '实时界面为空表示接收范围内没有该类别设备；可用包里的 AirTag 检查寻物标签。对其他类别使用隐藏这些，不会禁用此类别的标签。'],
            ['仅显示模式下，仅特征匹配开关不起作用', '仅显示已经隐藏了未匹配设备。', '仅显示选择了类别或具体特征时，该开关会变暗。关闭仅显示后才能使用仅特征匹配；若需保留未匹配设备，可改用隐藏这些。'],
            ['仅显示寻物标签后，随行列表为空', '类别的仅显示、仅特征匹配、仅命名设备或仅已关注仍在生效。寻物标签会轮换 MAC，经常无法满足随行判据，同时未匹配设备又被隐藏。', '点击随行预设，或开启随行开关。两种方式都会清除仅显示、仅特征匹配、仅命名设备和仅已关注。若此前隐藏了包里的标签，隐藏这些会保留。仍需先积累约 50 米轨迹。'],
            ['仅已关注列表为空', '没有已关注特征匹配，且没有命名设备开启提醒；或匹配项又被隐藏这些排除了。', '在特征库中关注一个系列，或对命名设备开启提醒（详情中的关注图标）。仅命名、不提醒的设备只进入仅命名设备。隐藏这些仍会排除已关注的摄像头。关闭该开关可查看其他设备。'],
            ['隐藏 AirTag 后，它们又出现了', '类别的隐藏这些或隐藏所选已关闭。只有对应模式开启时才会隐藏。', '重新开启隐藏这些（寻物标签）或隐藏所选。只有重置筛选才会清除所选项。'],
            ['暂停后，详情显示已离开范围', '从正在更新的列表打开详情后，该设备已超时。', '先暂停，再点击该行。详情会使用冻结的快照。'],
            ['雷达只显示一个特征标签', '雷达使用首个匹配项标记该点。', '这是预期行为。列表 / 混合 / 时间线最多显示三个，详情列出全部匹配项。'],
            ['新特征给半个咖啡馆的设备都加上了标签', '规则太宽泛，例如常见芯片的 OUI，或在任一匹配模式中加入 RADIO_KIND。', '在筛选中隐藏它，或删除自定义条目。将规则收紧到 MAC、名称、UUID 或厂商数据。'],
            ['从设备创建的特征匹配所有 BLE', '特征在任一匹配模式中包含了无线类型规则。', '删除该特征。重新打开详情 → 从设备创建特征，只保留 MAC、名称或 UUID 规则。不要单独添加无线类型。'],
            ['导出分享面板为空 / 分享失败', '尚无日志，或接收应用不支持 content URI。', '等待记录几条观测。分享到文件或 Drive，避免使用拒绝 text/plain 的应用。'],
            ['观测总结为空 / 内容很少', '最近 15 分钟的实时设备较少、未命名 BLE 已被移出内存（约 3 分钟），或行车过程中已达到约 400 个设备的上限，较早路段的设备被淘汰。', '先扫描几分钟。文本和 PDF 使用同一份内存快照，并非磁盘日志。旅途中每隔 10–15 分钟或停车时生成一次观测总结（§11.4.1）；随行设备会保留在每份文件中。需要完整一小时记录时，使用日志导出。'],
            ['找不到日志导出 / 观测导出 / 观测总结 / 候选特征', '这些按钮位于报告标签页。', '底部栏 → 报告。观测导出位于观测报告下，候选特征位于特征库分区下。GPS、地名和日志开关仍在设置中。'],
            ['找不到观测总结 / AI 导出', '这些按钮位于报告标签页。', '底部栏 → 报告。设置中仍有 GPS 标记、在线地名和日志开关。单台设备的 AI 导出位于设备详情页，而非报告页。'],
            ['候选特征为空', '日志未开启、记录时间太短，或剩余设备使用随机地址、类似家用设备，或只有一次性 MAC。', '在设置中开启日志，观测一段时间后再次点击候选特征。一个系列至少需要两台不同设备共享独特标识。单个强信号未匹配 MAC 应使用从设备创建特征，而非系列候选。'],
            ['没有厂商 IE 系列（如 Roku 类隐藏接入点）', '旧日志没有 vendor_ie 列。', '升级后写入新的 Wi-Fi 数据包之前，这是预期行为。旧日志仍可提取名称通配模式和稳定 OUI。如需在手机外分析 IE，请导出一次新的观测日志。'],
            ['保存候选后，它仍留在列表中', '草稿未匹配那些设备（规则过严，或规则已被修改），或保存尚未完成。', '打开特征库，确认条目存在。从候选草稿保存后会返回列表并重新分析；若新规则命中，该系列应消失。取消不会改变列表。'],
            ['详情页 AI 导出与报告页 AI 导出的区别', '两者使用不同的提示词。', '详情页针对单台设备，回答“它是什么”；报告页包含应用内观测总结与工作数据，要求生成统计补充，而非重写总结。不要把单台设备的解码当作跟随判定。'],
            ['信号追踪中的重置 / 返回详情难以点击', '提示文字变长，把按钮挤出了屏幕。', '重置、返回和蜂鸣 / 振动位于信号追踪页底部。提示与说明区域保持固定高度，避免 dBm 数值跳动。'],
            ['明明朝设备走，信号追踪却显示更远', '途中有墙壁、车辆、人群或楼层遮挡，或握持手机的方式发生变化。', '打开门或绕过金属障碍，观察是否恢复更近。转身造成身体遮挡后，重置本次追踪。不要将 dBm 换算为英尺距离。见 §12.13。'],
            ['信号追踪变为安静 / 已离开', '约 8 秒未收到广播，或 BLE 地址轮换后已离开实时列表。', '先等待。若显示已离开，返回实时界面；如果仍是同一系列，选择新的条目。随机 MAC 不会自动合并。'],
            ['到访位置有坐标，但没有街道名', '在线地名已关闭，或虽已开启但没有网络 / 地理编码服务。', '这是预期行为。停留地点仍会打印经纬度。距离计算不需要联网。如不想尝试查询，可关闭在线地名。'],
            ['最近定位或观测总结显示“已隐藏”，而非经纬度', '隐私模式已开启。', '这是预期行为。设置 → 隐私模式会隐藏屏幕与观测报告中的 GPS 坐标，也会省略街道名。日志仍包含经纬度。TAK / CoT 推送会暂停。需要地图标记或叠加层时，关闭隐私模式。'],
            ['整个界面变红 / 想恢复绿色标签', '夜间模式已开启。', '设置 → 外观 → 关闭夜间模式。恢复默认设置也会关闭夜间模式。见图 9。'],
            ['ATAK 地图一直为空', 'TAK 推送关闭、隐私模式开启、目标地址错误，或没有符合条件且带位置的设备。', '设置 → 开启 TAK / CoT 推送，关闭隐私模式。开启重点关注和载荷位置。若 ATAK CIV 在同一手机上，目标选择本机；其他 ATAK 设备选择局域网组播。确认推送状态显示已发送。在此接收到的位置还需要 GPS 标记与实时定位。见 §5.8、§12.15。'],
            ['实时界面有 Remote ID，但 ATAK 没有', '载荷位置标签关闭、尚未收到位置消息，或坐标为 0,0 / 无效。', '发送内容 → 开启载荷位置。等待 BLE FFFA 或 Wi-Fi FA:0B:BC（Android 11+）上的 ASTM 位置消息（类型 1，协议 0–2）。基本 ID 不含经纬度，但先前收到的位置会在本次会话中保留。0,0 会被拒绝。见 §5.8.3、§12.16。'],
            ['检测到 Wi-Fi 无人机，却没有 Remote ID 标签', '使用 Android 10、只广播 NAN RID，或无人机快速飞过。', '厂商 IE 需要 Android 11+，仍无法接收 NAN。尝试悬停或缓慢飞过。BLE FFFA 在 Android 10 上仍可用。见 §5.8.3、§12.16。'],
            ['TAK 标记位于我这里，而非另一台设备的位置', '这是接收位置：该系列未广播经纬度。', '对重点关注设备（Axon、眼镜、Flipper 等）而言，这是预期行为。Remote ID 位置才是广播的位置。关闭 GPS 标记只会停止发送接收位置。'],
            ['走开后，TAK 接收位置标记没有跟着移动', '接收位置保留信号最强时的位置。', '这是预期行为。走近设备才可能更新该位置。保活消息维持原经纬度，这不是无线测向。见 §5.8.8。'],
            ['观测总结仍覆盖最近 15 分钟', '没有正在进行或被选中的命名观测。', '这是预期行为。报告 → 开始观测。观测进行期间，或在设备列表中选中已保存观测后，观测总结会使用对应时间窗口。见 §5.6。'],
            ['ATAK 上满是咖啡馆接入点', '全部特征已开启。', '关闭全部特征。默认现场配置为重点关注 + 载荷位置。'],
            ['TAK 标记消失了', '设备离开推送范围、扫描停止，或隐私模式暂停了推送。', '这是预期行为。设备离开时，Fieldwatch 会发送离开事件（stale=now）。隐私模式暂停不会发送离开事件；ATAK 约 120 秒后将其判为过期。若没有持续保留的 UAS ID，轮换后的 BLE MAC 会成为新的 uid。'],
            ['Remote ID 在 ATAK 上形成一片散点', 'UID 使用了会不断轮换的 BLE MAC。', '1.0.3 起以持续保留的 UAS ID 标识航空器，应由单个标记随位置移动。首次收到基本 ID 数据包前仍以 MAC 标识，之后会切换一次。'],
            ['开车时报告中的轨迹没有增长', '报告页不在前台、GPS 标记关闭，或选中了已保存观测。', '保持报告页打开。该页显示时，轨迹约每 3 秒重绘。最近 15 分钟或正在进行的观测会实时更新，前端标为现在；已保存观测是静态快照，标为终点。开启 GPS 检测标记与高精度定位，并保持扫描运行。见 §5.6.1。'],
            ['开车时 GPS 轨迹始终为 0 米 / 随行一直提示继续移动', '手机没有提供实时定位。', '开启 GPS 检测标记和高精度定位，保持扫描运行。等待轨迹计数不再为 0，再步行或驾车。'],
            ['车内第二部 iPhone 没有出现在随行中', 'iOS 会轮换 BLE 地址，Fieldwatch 因而将其视为没有 GPS 轨迹的新设备。', '这是预期行为。可用 MAC 稳定的标签（如包内的 AirTag / Tile）检查功能是否正常。多次出现的手机地址不会合并成一个跟随设备。'],
            ['回家后随行列表中出现住宅接入点', 'Wi-Fi 接入点已被此筛选排除。', '这是预期的排除行为。驾车经过的强信号接入点会在你的接收轨迹上留下记录，看起来像随行，因此接入点始终不满足条件。包里和车内的 BLE 标签应继续显示。'],
            ['高速公路上随行设备时隐时现', '擦肩而过的 BLE 只重叠几秒，无法通过轨迹移动判据。车内标签不应闪现：“仍在附近”的容许时间随速度增加，55 英里/小时时约对应手机行进 400 米，因此几秒静默不会被判为离开。见 §8.5。', '保持 GPS 检测标记开启。路过的手机仍会出现后离开，这是筛选正常工作的表现。路边接入点不会显示。车内标签应保留；若没有，在积累约 50 米轨迹后点击重新开始，并确认标签仍在广播。'],
            ['LE 颜色 / “这看起来像什么”反复出现和消失', 'BLE 广播会轮换载荷，例如先发送 iBeacon，再发送 Nearby。', 'Fieldwatch 会按公司与类型为每台设备保留厂商记录，因此载荷轮换时，已命中的标签应继续保留。'],
            ['其他应用无法打开观测总结 PDF', '接收应用未获得读取权限，或拒绝 application/pdf。', '分享到文件、Drive 或 PDF 阅读器。'],
            ['恢复默认设置清除了自定义特征', '恢复操作会用内置特征库重写 config.json。', '这是预期行为。如需备份，请先在设置中导出特征，再恢复默认设置。重新导入该 JSON 可恢复自定义项；内置 ID 会合并附加规则，而非创建副本。命名设备与设置开关通过导出设置备份。'],
            ['导入特征时提示不是 Fieldwatch 特征包', '所选文件是日志、照片、设置包或 config.json，而非导出的特征库包。', '使用设置 → 导出特征。文件包含 format 值 fieldwatch-signatures。设置包使用 fieldwatch-settings，应通过导入设置加载。日志操作位于报告页。'],
            ['导入设置时提示所选文件是特征包', '选择了 fieldwatch-signatures JSON。', '使用导入特征加载特征库。设置备份使用导出设置 / 导入设置，格式为 fieldwatch-settings。'],
            ['导入设置没有恢复自定义特征', '设置包不包含特征库。', '这是预期行为。新增或修改的特征通过导入特征恢复。开关、预设和命名设备通过导入设置恢复。'],
            ['导入后没有新增内容', '包中每一项都与手机上已有 ID 或规则相同。', '再次导入同一包，或两部手机使用相同内置特征库时，这是预期行为。只会加入新的自定义项，以及内置项上的附加规则。'],
            ['计数不再变化', '进程仍在运行，但扫描失败，或当前筛选内容已过期。', '检查扫描通知。若已消失，重新启动应用。重置筛选；开关飞行模式，间隔 5 秒，以重启无线电。'],
        ],
        [1.7 * inch, 2.2 * inch, 2.6 * inch],
    ))
    flow += [
        Spacer(1, 12),
        P('D. 文档信息', "h2"),
        table(
            ['字段', '值'],
            [
                ['产品', "Fieldwatch"],
                ['作者', "Off Grid Pete LLC"],
                ['版权', "Copyright (c) 2026 Off Grid Pete LLC. All rights reserved."],
                ["Instagram", "@OffGridPete"],
                ["X", "@OGridPete"],
                ['文档', '用户手册与技术文档'],
                ['应用 ID', "app.fieldwatch"],
                ['软件版本', '1.1.17-zh-CN（versionCode 27），基于 2026 年 10 月 1 日的 1.1.17 现场版本汉化'],
                ['文档版本', "1.1.17"],
                ['文档日期', '2026 年 10 月 1 日'],
                ['许可证', 'MIT 许可证（见 LICENSE）；第三方声明见 NOTICE'],
                ['平台', 'Android 10 及以上（minSdk 29），targetSdk 35'],
                ['密级', '非密。填入现场日志后可能包含敏感行动信息。'],
            ],
            [2.0 * inch, 4.5 * inch],
        ),
        Spacer(1, 10),
        P('E. 关于本文档', "h2"),
        P(
            '本手册说明 Fieldwatch 的实际发布功能。文档版本与日期见文档信息。软件采用 MIT 许可证（LICENSE；声明页也有列出）。第三方声明见 NOTICE。'
        ),
        Spacer(1, 10),
        P(
            'Fieldwatch 由 Off Grid Pete LLC 开发（Instagram @OffGridPete，X @OGridPete）。版权所有 (c) 2026 Off Grid Pete LLC。保留所有权利。设置页显示版权与这些账号。模式匹配不能确认身份。仅接收式观测并不授予访问原本无权使用的系统的权限。',
            "caption",
        ),
    ]
    return wrap_body_around_figures(prevent_orphan_headings(flow))


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = FieldwatchDoc(
        OUT,
        pagesize=letter,
        title='Fieldwatch — 用户手册与技术文档',
        author="Fieldwatch",
        subject='面向 Android 的被动无线信号观察工具',
        creator='Fieldwatch 文档构建',
    )
    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover")
    body_frame = Frame(
        0.75 * inch, 0.6 * inch, 7.0 * inch, 9.55 * inch, id="body",
        showBoundary=0,
    )
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=cover_frame, onPage=draw_cover),
        PageTemplate(id="body", frames=body_frame, onPage=draw_body),
    ])
    doc.multiBuild(story())
    os.makedirs(os.path.dirname(DIST_OUT), exist_ok=True)
    shutil.copy2(OUT, DIST_OUT)
    print('已写入', OUT)
    print('已复制', DIST_OUT)


if __name__ == "__main__":
    main()
