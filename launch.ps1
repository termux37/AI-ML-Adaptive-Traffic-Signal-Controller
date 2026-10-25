# AI & ML Based Adaptive Traffic Control System - PowerShell Master Launcher
param (
    [switch]$SkipTests,
    [switch]$TestOnly,
    [switch]$Gui,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  AI & ML Based Adaptive Traffic Control System :: Master Launcher" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan

$ArgsList = @()
if ($SkipTests) { $ArgsList += "--skip-tests" }
if ($TestOnly)  { $ArgsList += "--test-only" }
if ($Gui)       { $ArgsList += "--gui" }
if ($NoBrowser) { $ArgsList += "--no-browser" }

python launch.py $ArgsList
