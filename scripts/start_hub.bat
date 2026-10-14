@echo off
:: Double-click this to launch the protected master hub
:: Runs PowerShell as Admin with exit guard

powershell -NoExit -ExecutionPolicy Bypass -Command ^
  "Start-Process powershell -Verb RunAs -ArgumentList '-NoExit -ExecutionPolicy Bypass -File \"%~dp0hub_protected.ps1\"'"
