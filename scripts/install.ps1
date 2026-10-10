#Requires -Version 5.1
<#
    BABBDI 简体中文汉化 — 一键安装脚本
    ------------------------------------------------------------------
    设计原则：
      1. 只向游戏目录"新增"文件，绝不修改/删除任何游戏原文件
         （所以随时可以一键还原成英文原版，也不会影响 Steam 校验）
      2. 自带全部组件（BepInEx / XUnity.AutoTranslator / 汉化词典 / 中文字体插件），
         全程不需要联网，国内网络环境也能一次装好
      3. 自动探测 Steam 游戏目录，探测不到就弹出文件夹选择框让用户手动选

    参数：
      -Yes   非交互模式：自动确认所有提示（便于批量或无人值守使用）
    ------------------------------------------------------------------
    作者：lordestar
#>
param([switch]$Yes)

$ErrorActionPreference = 'Stop'
try { $Host.UI.RawUI.WindowTitle = 'BABBDI 简体中文汉化 - 安装' } catch {}

function Write-Head($t) { Write-Host ''; Write-Host "  $t" -ForegroundColor Cyan; Write-Host '' }
function Ok($m)   { Write-Host "  [完成] $m" -ForegroundColor Green }
function Info($m) { Write-Host "  [信息] $m" -ForegroundColor Gray }
function Warn($m) { Write-Host "  [注意] $m" -ForegroundColor Yellow }
function Bad($m)  { Write-Host "  [失败] $m" -ForegroundColor Red }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root      = Split-Path -Parent $ScriptDir
$Payload   = Join-Path $Root 'payload'

# =====================================================================
#  工具函数
# =====================================================================

function Copy-Tree {
    param([string]$Source, [string]$Destination)
    if (-not (Test-DirSafe $Destination)) {
        New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    }
    $files = Get-ChildItem $Source -Recurse -File -Force
    foreach ($f in $files) {
        $rel    = $f.FullName.Substring($Source.Length).TrimStart('\')
        $target = Join-Safe $Destination $rel
        $tdir   = Split-Path $target -Parent
        if (-not (Test-DirSafe $tdir)) { New-Item -ItemType Directory -Force -Path $tdir | Out-Null }
        Copy-Item $f.FullName $target -Force
    }
}

# --- 安全路径工具 ---------------------------------------------------
# 注意：Steam 的 libraryfolders.vdf 里可能记录了当前并未挂载的磁盘
# （例如已经拔掉的外接硬盘 E:\SteamLibrary）。Join-Path 与 Test-Path 遇到
# 不存在的盘符会报错，在 $ErrorActionPreference='Stop' 下会直接中断脚本，
# 因此这里统一改用不会抛异常的 .NET API。
function Join-Safe {
    param([string]$Base, [string]$Child)
    if ([string]::IsNullOrWhiteSpace($Base)) { return $null }
    return ($Base.TrimEnd('\') + '\' + $Child.TrimStart('\'))
}

function Test-FileSafe {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    try { return [System.IO.File]::Exists($Path) } catch { return $false }
}

function Test-DirSafe {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    try { return [System.IO.Directory]::Exists($Path) } catch { return $false }
}

function Test-GameDir {
    param([string]$Dir)
    return (Test-FileSafe (Join-Safe $Dir 'Babbdi.exe'))
}

function Get-SteamLibraryFolders {
    $result = New-Object System.Collections.Generic.List[string]

    $steam = $null
    foreach ($key in @('HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam', 'HKLM:\SOFTWARE\Valve\Steam')) {
        try {
            $p = Get-ItemProperty -Path $key -ErrorAction Stop
            foreach ($name in @('SteamPath', 'InstallPath')) {
                $v = $p.$name
                if ($v) { $steam = $v; break }
            }
        } catch {}
        if ($steam) { break }
    }

    if ($steam) {
        $steam = $steam -replace '/', '\'
        $result.Add($steam)

        $vdf = Join-Safe $steam 'steamapps\libraryfolders.vdf'
        if (Test-FileSafe $vdf) {
            try {
                $content = Get-Content $vdf -Raw -Encoding UTF8
                foreach ($m in [regex]::Matches($content, '"path"\s+"([^"]+)"')) {
                    $lib = $m.Groups[1].Value -replace '\\\\', '\'
                    if ($lib) { $result.Add($lib) }
                }
            } catch {}
        }
    }
    return $result
}

function Find-GameDir {
    $candidates = New-Object System.Collections.Generic.List[string]

    # 1) Steam 注册表 + 所有 Steam 库文件夹
    foreach ($lib in (Get-SteamLibraryFolders)) {
        $candidates.Add((Join-Safe $lib 'steamapps\common\BABBDI'))
    }

    # 2) 常见路径兜底（多硬盘、自定义库位置）
    $drives = @()
    try { $drives = (Get-PSDrive -PSProvider FileSystem -ErrorAction Stop) | ForEach-Object { $_.Name } } catch {}
    foreach ($d in $drives) {
        foreach ($sub in @('Steam\steamapps\common\BABBDI',
                           'SteamLibrary\steamapps\common\BABBDI',
                           'Games\Steam\steamapps\common\BABBDI',
                           'Program Files (x86)\Steam\steamapps\common\BABBDI',
                           'Program Files\Steam\steamapps\common\BABBDI')) {
            $candidates.Add("${d}:\$sub")
        }
    }

    foreach ($c in $candidates) {
        if (Test-GameDir $c) {
            try { return [System.IO.Path]::GetFullPath($c) } catch { return $c }
        }
    }
    return $null
}

function Select-GameDirByDialog {
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue
    $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
    $dlg.Description = '请选择 BABBDI 游戏目录（该目录里应当有 Babbdi.exe）'
    $dlg.ShowNewFolderButton = $false
    if ($dlg.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        return $dlg.SelectedPath
    }
    return $null
}

# =====================================================================
#  0. 欢迎
# =====================================================================
Write-Head 'BABBDI 简体中文汉化 — 一键安装'
Write-Host '  本汉化不修改任何游戏原文件，随时可以一键还原成英文。'
Write-Host '  全过程不需要联网。'

if (-not (Test-Path $Payload)) {
    Bad "安装包不完整：找不到 payload 目录（$Payload）"
    Write-Host '  请确认你是把整个压缩包解压后再运行，而不是直接在压缩包里双击。' -ForegroundColor Yellow
    exit 1
}

# =====================================================================
#  1. 定位游戏目录
# =====================================================================
Write-Head '第 1 步 / 4：查找 BABBDI 游戏目录'

$gameDir = Find-GameDir

if ($gameDir) {
    Ok "自动找到：$gameDir"
} else {
    Warn '没有自动找到游戏目录。'
    Write-Host '  接下来会弹出文件夹选择框，请选中 BABBDI 的安装目录。'
    Write-Host '  提示：Steam 里右键游戏 → 管理 → 浏览本地文件，就能看到该目录。' -ForegroundColor Gray
    Start-Sleep -Seconds 1
    $gameDir = Select-GameDirByDialog
}

# 人工输入兜底
$tries = 0
while (-not (Test-GameDir $gameDir)) {
    $tries++
    if ($tries -gt 5) {
        Bad '多次未能选到正确的游戏目录，安装中止。'
        Write-Host '  正确的目录里必须直接能看到 Babbdi.exe。' -ForegroundColor Yellow
        exit 1
    }

    Write-Host ''
    Write-Host '  请手动粘贴 BABBDI 游戏目录的完整路径，然后回车。' -ForegroundColor Yellow
    Write-Host '  例如：D:\Steam\steamapps\common\BABBDI' -ForegroundColor Gray
    $userInput = Read-Host '  游戏目录'
    if ([string]::IsNullOrWhiteSpace($userInput)) { continue }
    $gameDir = $userInput.Trim().Trim('"')
}

$gameDir = (Get-Item $gameDir).FullName
Ok "游戏目录已确认：$gameDir"
# =====================================================================
#  2. 检查游戏是否正在运行
# =====================================================================
Write-Head '第 2 步 / 4：检查游戏状态'

$running = Get-Process -Name 'Babbdi' -ErrorAction SilentlyContinue
if ($running) {
    Warn '检测到 BABBDI 正在运行，安装需要先关闭它。'
    $ans = 'Y'
    if (-not $Yes) { $ans = Read-Host '  是否现在自动关闭游戏？(Y/N)' }
    if ($ans -match '^[Yy]') {
        try {
            $running | Stop-Process -Force -ErrorAction Stop
            Start-Sleep -Seconds 2
            Ok '游戏已关闭。'
        } catch {
            Bad "关闭游戏失败：$($_.Exception.Message)"
            Write-Host '  请手动关闭游戏后重新运行本安装程序。' -ForegroundColor Yellow
            exit 1
        }
    } else {
        Bad '游戏仍在运行，安装中止。请关闭游戏后重新运行。'
        exit 1
    }
} else {
    Ok '游戏当前未运行，可以安全写入文件。'
}

# =====================================================================
#  3. 复制汉化文件
# =====================================================================
Write-Head '第 3 步 / 4：安装汉化文件'

try {
    Copy-Tree -Source $Payload -Destination $gameDir
    Ok 'BepInEx 加载框架'
    Ok 'XUnity.AutoTranslator 文本替换插件'
    Ok '中文汉化词典（187 条人工译文）'
    Ok '中文字体支持插件'
} catch {
    Bad "写入文件失败：$($_.Exception.Message)"
    Write-Host '  常见原因：游戏目录权限不足，或游戏仍在运行。' -ForegroundColor Yellow
    Write-Host '  可以尝试右键本安装程序 → 以管理员身份运行。' -ForegroundColor Yellow
    exit 1
}

# 安装结果自检
Write-Host ''
Info '正在自检安装结果…'
$checks = @(
    @{ n = 'BepInEx 注入器';  p = 'winhttp.dll';                                          must = $true },
    @{ n = 'BepInEx 核心';    p = 'BepInEx\core\BepInEx.dll';                             must = $true },
    @{ n = 'XUnity 插件';     p = 'BepInEx\plugins\XUnity.AutoTranslator\XUnity.AutoTranslator.Plugin.Core.dll'; must = $true },
    @{ n = '中文字体插件';    p = 'BepInEx\plugins\BabbdiChineseFont\BabbdiChineseFont.dll'; must = $true },
    @{ n = '字体字符集';      p = 'BepInEx\plugins\BabbdiChineseFont\charset.txt';        must = $true },
    @{ n = '汉化词典';        p = 'BepInEx\Translation\zh-CN\Text\BABBDI_zh-CN.txt';      must = $true }
)
$allOk = $true
foreach ($c in $checks) {
    $full = Join-Path $gameDir $c.p
    if (Test-Path $full) {
        Write-Host "         √ $($c.n)" -ForegroundColor DarkGray
    } else {
        Write-Host "         × $($c.n) 缺失" -ForegroundColor Red
        $allOk = $false
    }
}
if (-not $allOk) {
    Bad '自检未通过，汉化可能无法正常工作。'
    Write-Host "  请把 $gameDir\BepInEx\LogOutput.log 的内容发给作者。" -ForegroundColor Yellow
    exit 1
}
Ok '自检全部通过。'

# =====================================================================
#  4. 完成
# =====================================================================
Write-Head '第 4 步 / 4：全部完成！'
Write-Host '  现在直接从 Steam 启动 BABBDI 就是中文的了。' -ForegroundColor Green
Write-Host '  （首次启动会多花几秒初始化插件，属于正常现象）' -ForegroundColor Gray
Write-Host ''
Write-Host '  小贴士：' -ForegroundColor Cyan
Write-Host '    · 想改某句译文：编辑 BepInEx\Translation\zh-CN\Text\BABBDI_zh-CN.txt,' -ForegroundColor Gray
Write-Host '      在游戏里按 ALT+R 就能立刻生效，不用重启。' -ForegroundColor Gray
Write-Host '    · 想换字体：编辑 BepInEx\config\babbdi.chinesefont.cfg 里的 FontFile。' -ForegroundColor Gray
Write-Host '    · 想还原英文：运行同目录下的「一键还原英文.bat」。' -ForegroundColor Gray
Write-Host ''
