@echo off
chcp 936 >nul
title BABBDI 简体中文汉化 - 还原英文
echo.
echo   ================================================
echo     BABBDI 简体中文汉化  一键还原英文原版
echo   ================================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\uninstall.ps1"
echo.
echo   ================================================
pause