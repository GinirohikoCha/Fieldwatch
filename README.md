# Fieldwatch

Fieldwatch 是我为自己制作的一款工具，用来查看手机能够接收到的 Wi-Fi 接入点和低功耗蓝牙（BLE）广播，帮助了解周围正在使用哪些设备。它采用被动监听方式，不需要外接适配器、账号或后台服务器。我希望它能在现场离线使用。

我的目标是提供现代、易用的界面，让信息显示方式足够灵活，可以按任务调整视图；提供筛选引擎以减少无关信息；提供可扩展的特征库，尽可能识别无线信号来源并随时添加新特征；同时能够生成观测报告。

经过一段时间的实际使用和迭代，这款工具对我很有帮助，因此决定分享出来。

这是一个业余项目，是我在闲暇时做的兴趣作品。Fieldwatch 没有后台服务器，也没有广告，所有内容都保存在手机上。源码和侧载文件均在本仓库中；`dist/` 包含 APK、安装说明和用户手册。

本工作副本的版本为 `1.1.17-zh-CN`，已将应用界面、报告、AI 提示词和使用文档翻译为简体中文。`dist/Fieldwatch.apk` 是由本工作副本源码构建的中文版本，使用本地 Android Debug 证书；不能直接覆盖上游签名版本，请先备份再卸载旧版。APK 与签名校验值见[安装说明](dist/instruction.txt)。上游 GitHub 下载文件属于上游发布版本，可能不包含这些中文改动。

截至 1.2.14，这款工具曾使用 Spectre 名称。后来我了解到已有其他应用使用该名称，因此将它改名为 Fieldwatch，避免混淆。现场工具的定位不变，应用 ID 改为 `app.fieldwatch`，源码采用 MIT 许可证。安装 Fieldwatch 不会替换手机上的 Spectre，它们是两个独立应用。

如果发现应用或文档存在错误、设计不合理，或者有功能建议，请[在本仓库提交 Issue](https://github.com/OffGridPete/Fieldwatch/issues)。希望它对你也有帮助，欢迎分享使用反馈。

**只想安装？** 请查看本地分发目录中的 [Fieldwatch.apk](dist/Fieldwatch.apk)、[安装说明](dist/instruction.txt)和[用户手册](dist/Fieldwatch_User_Manual.pdf)。[更新日志](CHANGELOG.md)记录各版本的变化。APK 文件名应保持为 `Fieldwatch.apk`。GitHub 如果提示文件过大、无法预览，请使用下载按钮。

## 安全与免责声明

这是一个业余项目，按 MIT 许可证以现状提供。使用前请了解：

- 使用风险由您自行承担。您须对如何使用 Fieldwatch 负责。在法律允许的最大范围内，Off Grid Pete LLC 不对使用本应用所产生的间接、附带、特殊、后果性或惩罚性损害承担责任。
- 不保证一定能发现、命名或报告追踪器、摄像头、标签、接入点或任何其他设备。无线设备若关闭、仅使用蜂窝网络、休眠、采用随机地址、处于静默状态，或超出手机操作系统提供的信息范围，就不会出现。各手机的无线硬件、固件、扫描配额和厂商电池策略不同，软件无法消除这些限制。
- 模式匹配、GPS 同行分析（“随行” / “可能尾随”）、观测总结文字及 AI 导出结果都只是推测，不代表身份或法律结论，也不是完整的射频捕获。您须独自承担使用本应用和本文档，以及遵守当地法律的责任。使用本软件或手册即表示接受这些条款及 MIT 许可证。
- 开启位置标记后，位置数据表示接收信号时本手机的位置，不是其他无线设备的位置。Fieldwatch 没有服务器，标记会保留在手机中，直到您主动分享。即使隐私模式遮蔽了屏幕和观测报告，日志仍保存完整坐标。观测总结、分享日志、AI 导出（观测或单个设备）及设备详情的文字分享，可能使轨迹离开手机。在线地名使用系统地理编码服务（通常为厂商或 Google 网络），并非 Fieldwatch 云端。如何存储、分享或发布这些文件由您自行负责。

## 安装到手机

安装文件位于 [`dist/`](dist/)，不在仓库根目录：

- [Fieldwatch.apk](dist/Fieldwatch.apk)
- [instruction.txt](dist/instruction.txt)
- [Fieldwatch_User_Manual.pdf](dist/Fieldwatch_User_Manual.pdf)

上游发布文件可在[上游 dist 目录](https://github.com/OffGridPete/Fieldwatch/tree/main/dist)找到；它们与本地中文构建可能不同。请按安装说明核对对应文件和签名信息。

不要重命名 APK。用“文件”或“我的文件”打开 `Fieldwatch.apk`；如果 Android 询问，请允许从该应用安装。

| 文件 | 用途 |
|---|---|
| `dist/Fieldwatch.apk` | 侧载 APK |
| `dist/fieldwatch-signatures.json` | 供 1.1.11 通过 GitHub 更新的默认特征库（版本 77） |
| `dist/fieldwatch-signatures-v2.json` | 供 1.1.12 及以上版本通过 GitHub 更新的默认特征库 |
| `dist/instruction.txt` | 权限与首次启动说明 |
| `dist/Fieldwatch_User_Manual.pdf` | 用户手册 |
| [`CHANGELOG.md`](CHANGELOG.md) | 各版本更新内容 |
| `LICENSE` | MIT 许可证原文 |
| `NOTICE` | 第三方归属声明 |

需要 Android 10 或更新版本。允许从打开 APK 的应用安装。Play Protect 可能提示该应用并非来自 Play 商店，这是侧载应用可能遇到的提示。完整步骤见 `instruction.txt`。

```bash
adb install -r dist/Fieldwatch.apk
```

### 从上游 1.0.4 或更早版本升级：发布者证书变化，需要一次重新安装

Android 为每个应用记录签名证书，用来判断更新是否来自同一发布者。上游 Fieldwatch 的 1.0.4 及更早版本使用构建工具附带的通用 Android 开发证书；上游 1.0.5 起改用 Off Grid Pete LLC 发布证书。这样 APK 带有可供扫描器核查的发布者信息。上游证书指纹见 `instruction.txt`。自行构建的中文 APK 可能使用不同证书，应以实际构建信息为准。

手机会把新证书视为不同发布者，因此上游 1.0.5 无法直接覆盖安装到 1.0.4 或更早版本之上。需要先卸载旧版，再安装新 APK；之后使用相同证书签名的上游版本可以正常覆盖更新，上游 1.1.17 不要求再次卸载。若本地中文构建的签名与已安装版本不同，Android 同样不允许直接覆盖。

卸载会删除手机上的应用数据。如果您添加过特征、修改过设置、命名过无线设备或保存过筛选预设，请先在“设置”中执行**导出特征库**和**导出设置**，将两个文件保存到卸载后仍能访问的位置。它们不包含日志或 GPS。然后卸载旧版（长按 Fieldwatch 图标，或运行 `adb uninstall app.fieldwatch`），安装对应新 APK，打开应用并接受免责声明，再使用**导入特征库**和**导入设置**恢复。如果从未自定义过，可以跳过导出。

## Fieldwatch 的能力边界

- 无法捕获 Wi-Fi 客户端、仅发送探测请求的终端，也不支持 802.11 监听模式。
- 不执行经典蓝牙查询（HC-05 / HC-06 不会出现）。
- 不监听蜂窝网络。
- 不进行无线测向。

## 版权与许可证

版权所有 (c) 2026 Off Grid Pete LLC。

Fieldwatch 源码采用 [MIT 许可证](LICENSE)。AndroidX、Kotlin 及相关库仍采用 Apache-2.0。`radiodb.bin` 中的 IEEE 和 Bluetooth SIG 分配编号表适用各组织的条款。详见 [NOTICE](NOTICE)。
