@echo off
chcp 936 >nul
title BABBDI 简体中文汉化 - 一键安装
echo.
echo   ================================================
echo     BABBDI 简体中文汉化  一键安装
echo   ================================================
echo.
echo   本汉化不修改任何游戏原文件，随时可一键还原英文。
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1"
echo.
echo   ================================================
pause