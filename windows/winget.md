# winget
The Windows Package Manager (`winget`) is Microsoft's built-in command-line installer for Windows 10 (1809+) and 11. It is delivered with the App Installer package. Run it from PowerShell ([PowerShell Cheat-Sheet](powershell.md)) or [Windows Terminal](windows-terminal.md). Use it for per-user and Store-style software; see [Chocolatey](chocolatey.md) for the older machine-level manager.

Documentation: [winget docs](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

## Search and Install
COMMAND | DESCRIPTION
---|---
`winget search <TERM>` | Search all sources
`winget search --id <ID> --exact` | Look up an exact package ID
`winget show <ID>` | Package details, installer type and versions
`winget show <ID> --versions` | Available versions
`winget install <ID>` | Install by ID (for example `Git.Git`)
`winget install -e --id <ID>` | Exact match on ID, avoids picking the wrong package
`winget install <ID> --version <VER>` | Specific version
`winget install <ID> --scope machine` | Install for all users (needs elevation; `--scope user` for this user)
`winget install <ID> --silent` | No installer UI (`-h` or `--silent`)
`winget install <ID> --location "D:\Apps\<NAME>"` | Custom install folder (if the installer supports it)
`winget install <ID> --override "<ARGS>"` | Replace the installer arguments entirely
`winget install <ID> --accept-package-agreements --accept-source-agreements` | Non-interactive runs and scripts
`winget install --source msstore <NAME>` | Install from the Microsoft Store source
`winget install --manifest .\app.yaml` | Install from a local manifest

## List, Upgrade, Uninstall
COMMAND | DESCRIPTION
---|---
`winget list` | Installed software that winget can see (also non-winget installs)
`winget list <NAME>` | Filter the installed list
`winget upgrade` | Show available upgrades
`winget upgrade <ID>` | Upgrade one package
`winget upgrade --all` | Upgrade everything
`winget upgrade --all --include-unknown` | Also try packages with an unknown installed version
`winget upgrade --all --silent --accept-package-agreements` | Unattended upgrade
`winget pin add --id <ID>` | Hold a package at its current version (`--version "1.2.*"` to pin a range)
`winget pin list` / `winget pin remove --id <ID>` | List or remove pins
`winget uninstall <ID>` | Remove a package
`winget uninstall <ID> --purge` | Also delete package data (portable packages)

## Export and Import
Rebuild a machine from a JSON list of packages.
```powershell
winget export -o .\apps.json --include-versions
winget import -i .\apps.json --accept-package-agreements --accept-source-agreements --ignore-unavailable
```
COMMAND | DESCRIPTION
---|---
`winget export -o <FILE>` | Write installed packages to a file
`winget export -o <FILE> --include-versions` | Record exact versions
`winget import -i <FILE>` | Install everything in the file
`winget import -i <FILE> --ignore-versions` | Install latest instead of recorded versions
`winget import -i <FILE> --ignore-unavailable` | Skip packages no longer found

Keep the JSON in git and re-run it after a Windows reinstall. Only packages found in a configured source are exported.

## Configuration (DSC)
Newer winget versions can apply a declarative configuration file (YAML, based on Desired State Configuration) to set up a whole dev machine.

COMMAND | DESCRIPTION
---|---
`winget configure -f <FILE.dsc.yaml>` | Apply a configuration
`winget configure show -f <FILE.dsc.yaml>` | Preview without applying
`winget configure --accept-configuration-agreements -f <FILE>` | Non-interactive

## Sources
COMMAND | DESCRIPTION
---|---
`winget source list` | Show configured sources (`winget` community repo and `msstore`)
`winget source update` | Refresh source indexes
`winget source add --name <NAME> --arg <URL> --type Microsoft.Rest` | Add a private REST source (needs admin)
`winget source remove --name <NAME>` | Remove a source
`winget source reset --force` | Reset to defaults (needs admin)
`winget install --source winget <ID>` | Pin one install to a source

## Settings
```powershell
winget settings            # opens settings.json in your editor
winget settings export     # print current settings
```
The file lives under `%LOCALAPPDATA%\Packages\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe\LocalState\settings.json`. Example:
```json
{
  "$schema": "https://aka.ms/winget-settings.schema.json",
  "installBehavior": {
    "preferences": { "scope": "user" }
  },
  "visual": { "progressBar": "rainbow" },
  "source": { "autoUpdateIntervalInMinutes": 240 }
}
```
Other commands: `winget --info` (version, paths, links), `winget features` (experimental features), `winget validate <MANIFEST>`, `winget hash <FILE>` (SHA-256 for a manifest).

## winget vs Chocolatey
TOPIC | winget | [Chocolatey](chocolatey.md)
---|---|---
Ships with Windows | Yes (App Installer) | No, separate install
Elevation | Per package; many install per user | Usually needs elevated shell
Repository | Community manifests (open GitHub repo) plus Microsoft Store | Community repo with moderation; many packages wrap installers
Cost | Free | Free; paid tiers add private repos, GUI and more
Detects non-managed apps | `winget list` matches installed apps to known IDs | Only tracks packages it installed
Upgrade all | `winget upgrade --all` | `choco upgrade all`
Export / import | `winget export` / `import` JSON | `packages.config`
Pinning | `winget pin` | `choco pin`
Scripting maturity | Newer, fewer private-feed options | Long history, strong enterprise tooling

They coexist. Pick one as the primary and avoid installing the same app from both.

## Scripting Tips
```powershell
# Check winget exists, then install a list unattended
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw "winget not found" }
$apps = 'Git.Git','Microsoft.VisualStudioCode','7zip.7zip','Microsoft.PowerShell'
foreach ($id in $apps) {
    winget install -e --id $id --silent --accept-package-agreements --accept-source-agreements
}
```
- Use IDs, not names, in scripts (names are ambiguous).
- Check `$LASTEXITCODE` after a call; many failures return non-zero without a PowerShell error.
- winget cannot run as `SYSTEM` easily (service accounts, some Intune deployments); use the `Microsoft.WinGet.Client` PowerShell module (`Install-Module Microsoft.WinGet.Client`, then `Find-WinGetPackage`, `Install-WinGetPackage`) for those cases.
- `winget upgrade` shows "Unknown" version for apps that do not report one; use `--include-unknown`.

## Troubleshooting
SYMPTOM | FIX
---|---
`winget` not recognised | Install or update **App Installer** from the Microsoft Store; open a new terminal
Source errors or certificate failures | `winget source reset --force` (admin), then `winget source update`
Installer hash mismatch | The vendor changed the file; wait for the manifest update or report it. Avoid `--ignore-security-hash` unless you trust the download
Package missing from `winget list` | The app did not register in Add/Remove Programs
Needs a restart | Some installers defer to reboot; check the exit code and the installer log (`--log <FILE>`)
Verbose logs | `winget install <ID> --verbose-logs`, then `winget --info` for the log folder

## Not Verified
Commands were written from the Microsoft documentation and not executed. Some options (`configure`, `--purge`, pinning ranges) depend on the installed winget version: check with `winget --info` and `winget <COMMAND> --help`.
