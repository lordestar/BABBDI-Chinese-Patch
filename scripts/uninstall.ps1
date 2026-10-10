#Requires -Version 5.1
<#
    BABBDI 简体中文汉化 — 一键还原（卸载）
    ------------------------------------------------------------------
    本脚本只删除汉化"新增"的文件，不会碰任何游戏原文件。
    卸载后游戏即回到英文原版，且与 Steam 的"验证游戏文件完整性"完全兼容。

    参数：
      -Yes   非交互模式：自动确认所有提示（便于批量或无人值守使用）
    ------------------------------------------------------------------
    作者：lordestar
#>
param([switch]$Yes)

$ErrorActionPreference = 'Stop'
try { $Host.UI.RawUI.WindowTitle = 'BABBDI 简体中文汉化 - 还原英文' } catch {}

function Write-Head($t) { Write-Host ''; Write-Host "  $t" -ForegroundColor Cyan; Write-Host '' }
function Ok($m)   { Write-Host "  [完成] $m" -ForegroundColor Green }
function Info($m) { Write-Host "  [信息] $m" -ForegroundColor Gray }
function Warn($m) { Write-Host "  [注意] $m" -ForegroundColor Yellow }
function Bad($m)  { Write-Host "  [失败] $m" -ForegroundColor Red }

# =====================================================================
#  游戏目录探测（与安装脚本同一套逻辑）
# =====================================================================

# --- 安全路径工具 ---------------------------------------------------
# Steam 的 libraryfolders.vdf 里可能记录了当前并未挂载的磁盘（例如已拔掉的
# 外接硬盘 E:\SteamLibrary）。Join-Path / Test-Path 遇到不存在的盘符会报错，
# 在 $ErrorActionPreference='Stop' 下会中断脚本，故改用不会抛异常的 .NET API。
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
    foreach ($lib in (Get-SteamLibraryFolders)) {
        $candidates.Add((Join-Safe $lib 'steamapps\common\BABBDI'))
    }
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
    if ($dlg.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { return $dlg.SelectedPath }
    return $null
}

# =====================================================================
Write-Head 'BABBDI 简体中文汉化 — 还原英文原版'

$gameDir = Find-GameDir
if ($gameDir) {
    Ok "自动找到游戏目录：$gameDir"
} else {
    Warn '没有自动找到游戏目录，将弹出文件夹选择框。'
    Start-Sleep -Seconds 1
    $gameDir = Select-GameDirByDialog
}

$tries = 0
while (-not (Test-GameDir $gameDir)) {
    $tries++
    if ($tries -gt 5) { Bad '未能选到正确的游戏目录，已中止。'; exit 1 }
    Write-Host ''
    Write-Host '  请手动粘贴 BABBDI 游戏目录的完整路径后回车：' -ForegroundColor Yellow
    $input = Read-Host '  游戏目录'
    if ([string]::IsNullOrWhiteSpace($input)) { continue }
    $gameDir = $input.Trim().Trim('"')
}
$gameDir = (Get-Item $gameDir).FullName

# 检查游戏是否在运行
$running = Get-Process -Name 'Babbdi' -ErrorAction SilentlyContinue
if ($running) {
    Warn 'BABBDI 正在运行，还原前需要先关闭它。'
    $ans = 'Y'
    if (-not $Yes) { $ans = Read-Host '  是否现在自动关闭游戏？(Y/N)' }
    if ($ans -match '^[Yy]') {
        $running | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Ok '游戏已关闭。'
    } else {
        Bad '游戏仍在运行，已中止。'
        exit 1
    }
}

# 待删除项
$targets = @('winhttp.dll', 'doorstop_config.ini', '.doorstop_version', 'BepInEx')

Write-Head '将要删除以下汉化文件：'
$found = @()
foreach ($t in $targets) {
    $p = Join-Path $gameDir $t
    if (Test-Path $p) {
        $found += $p
        Write-Host "    - $t" -ForegroundColor Gray
    }
}

if ($found.Count -eq 0) {
    Warn '没有发现任何汉化文件，游戏可能本来就是英文原版。'
    exit 0
}

Write-Host ''
Write-Host '  注意：你在 BepInEx\Translation 里自己改过的译文也会一起被删除。' -ForegroundColor Yellow
$confirm = 'Y'
if (-not $Yes) { $confirm = Read-Host '  确认要还原成英文原版吗？(Y/N)' }
if ($confirm -notmatch '^[Yy]') {
    Warn '已取消，未做任何修改。'
    exit 0
}

Write-Host ''
foreach ($p in $found) {
    try {
        Remove-Item $p -Recurse -Force -ErrorAction Stop
        Ok "已删除 $(Split-Path $p -Leaf)"
    } catch {
        Bad "删除失败：$p"
        Write-Host "      $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host '      请关闭游戏后重试，或以管理员身份运行。' -ForegroundColor Yellow
    }
}

Write-Host ''
if (-not (Test-Path (Join-Path $gameDir 'BepInEx'))) {
    Ok '还原完成，游戏已回到英文原版。'
    Write-Host '  （因为从未修改过游戏原文件，不会有任何残留问题）' -ForegroundColor Gray
} else {
    Warn '部分文件未能删除，请手动删除游戏目录下的 BepInEx 文件夹。'
}
Write-Host ''
