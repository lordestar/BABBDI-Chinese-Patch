# 第三方组件许可说明

本项目 `payload/` 目录中随包分发了一些第三方组件，以便玩家**无需联网**即可一键安装。
这些组件遵循各自的许可证，本文件列出它们及其许可条款。

> 本项目的汉化词典、字体插件与安装脚本使用 MIT 许可证（见 [LICENSE](LICENSE)）。
> 游戏 **BABBDI** 的文本与一切相关权利归开发商 Lemaitre Bros 所有，
> 本项目不包含任何游戏本体文件。

---

## 1. BepInEx 5.4.23.5

- 项目地址：https://github.com/BepInEx/BepInEx
- 许可证：**GNU Lesser General Public License v2.1**
- 完整许可文本：[`third_party/BepInEx-LGPL-2.1.txt`](third_party/BepInEx-LGPL-2.1.txt)
- 分发文件：
  - `winhttp.dll`、`doorstop_config.ini`、`.doorstop_version`（Unity Doorstop 4.5.0）
  - `BepInEx/core/BepInEx.dll`、`BepInEx.Preloader.dll`、`BepInEx.Harmony.dll`
  - `BepInEx/core/0Harmony.dll`、`0Harmony20.dll`、`HarmonyXInterop.dll`（HarmonyX，MIT）
  - `BepInEx/core/Mono.Cecil*.dll`（MIT）
  - `BepInEx/core/MonoMod.RuntimeDetour.dll`、`MonoMod.Utils.dll`（MIT）
  - `BepInEx/core/XUnity.Common.dll`（XUnity 项目，MIT）

BepInEx 采用 LGPL-2.1 授权，允许以库的形式随其他作品一起分发，前提是：
保留版权声明与许可证、并使得接收者能够替换该库的版本。
本项目正是以未修改的原始二进制形式分发 BepInEx，并完整附上其许可证文本。

## 2. XUnity.AutoTranslator 5.6.2

- 项目地址：https://github.com/bbepis/XUnity.AutoTranslator
- 许可证：**MIT License**（Copyright (c) 2018 Bepis）
- 完整许可文本：[`third_party/XUnity-MIT.txt`](third_party/XUnity-MIT.txt)
- 分发文件：
  - `BepInEx/plugins/XUnity.AutoTranslator/`（含 `ExIni.dll`、`Translators/`、`Translators/FullNET/`）
  - `BepInEx/plugins/XUnity.ResourceRedirector/`

> 本项目**不使用**其中任何在线翻译接口：配置中 `Endpoint=` 为空，翻译完全来自本地词典文件。

## 3. 其他随包 DLL

| 组件 | 许可证 | 来源 |
|---|---|---|
| Newtonsoft.Json | MIT | James Newton-King |
| Mono.Cecil / Mono.Cecil.Mdb / Mono.Cecil.Pdb / Mono.Cecil.Rocks | MIT | Jb Evain |
| MonoMod.RuntimeDetour / MonoMod.Utils | MIT | 0x0ade (MonoMod) |
| HarmonyX (0Harmony) | MIT | BepInEx Team |
| ExIni | MIT | Bepis |
| ICSharpCode.SharpZipLib | MIT | ICSharpCode |

上述组件均以未修改的原始二进制形式、随 BepInEx / XUnity.AutoTranslator 官方发行包一并分发。

---

## 4. 关于 Unity 引擎文件

本项目**不包含**任何 Unity 引擎文件。BepInEx 在运行时使用的是玩家本机游戏自带的
`BepInEx` 所依赖的 Unity 程序集（位于游戏的 `Babbdi_Data/Managed/` 目录）。

## 5. 玩家自行修改与再分发

你可以自由修改本项目的译文、字体与脚本，并按 MIT 许可证再分发。
再分发时请一并保留本文件与 `third_party/` 下的许可证文本。
