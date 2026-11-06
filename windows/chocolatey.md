# Chocolatey
Chocolatey is a machine-level, command-line package manager and installer for Windows software. Run it from an **elevated** PowerShell ([[powershell]]). For per-user installs also consider `winget`.

Project Homepage: [Chocolatey Homepage](https://chocolatey.org)

---
## Installation

1. Check the Execution Policy

Run `Get-ExecutionPolicy`. If it returns `Restricted`, then run `Set-ExecutionPolicy AllSigned` or `Set-ExecutionPolicy Bypass -Scope Process`.

2. Install Chocolatey

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
Review the script first at https://community.chocolatey.org/install.ps1 before piping it to `iex`.

3. Check if you install chocolatey

```powershell
choco -?
```

---
## Install software package

```powershell
choco install <package>
```

## Commands
COMMAND | DESCRIPTION
---|---
`choco search <TERM>` | Search the community repository
`choco install <PKG> -y` | Install without prompts
`choco install <PKG> --version=<VER>` | Install a specific version
`choco install <PKG1> <PKG2> -y` | Install several packages
`choco list --local-only` | Installed packages (use `choco list -l` on v1)
`choco outdated` | Packages with updates
`choco upgrade <PKG> -y` | Upgrade one package
`choco upgrade all -y` | Upgrade everything
`choco uninstall <PKG> -y` | Remove a package
`choco pin add -n=<PKG>` | Hold a package at its version
`choco info <PKG>` | Package details
`choco source list` | Configured sources
`choco feature enable -n=allowGlobalConfirmation` | Always answer yes

## Install from a File
`packages.config`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="git" />
  <package id="vscode" />
  <package id="7zip" />
  <package id="powershell-core" />
</packages>
```
```powershell
choco install packages.config -y
```
