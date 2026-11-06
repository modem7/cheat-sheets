# VSCode (Visual Studio Code)
Free, extensible code editor from Microsoft.

Documentation: [VS Code Docs](https://code.visualstudio.com/docs)

macOS shortcuts: [[vscode-macos-shortcuts]]

## Shortcuts (Windows / Linux)
SHORTCUT | ACTION
---|---
`Ctrl+Shift+P` / `F1` | Command Palette
`Ctrl+P` | Quick open file
`Ctrl+Shift+N` | New window
`Ctrl+,` | Settings
`Ctrl+B` | Toggle sidebar
`Ctrl+\`` | Toggle terminal
`Ctrl+Shift+E` / `F` / `G` / `X` | Explorer / Search / Source control / Extensions
`Ctrl+Shift+F` | Search across files
`Ctrl+F` / `Ctrl+H` | Find / Replace
`Ctrl+G` | Go to line
`Ctrl+Shift+O` | Go to symbol in file
`F12` / `Alt+F12` | Go to definition / Peek definition
`Shift+F12` | Find all references
`F2` | Rename symbol
`Ctrl+.` | Quick fix
`Alt+Up` / `Alt+Down` | Move line
`Shift+Alt+Up` / `Shift+Alt+Down` | Copy line
`Ctrl+Shift+K` | Delete line
`Ctrl+/` | Toggle line comment
`Shift+Alt+A` | Toggle block comment
`Ctrl+D` | Select next occurrence
`Ctrl+Shift+L` | Select all occurrences
`Alt+Click` | Add a cursor
`Ctrl+Alt+Up` / `Down` | Add a cursor above / below
`Shift+Alt+F` | Format document
`Ctrl+K Z` | Zen mode
`Ctrl+K Ctrl+S` | Keyboard shortcuts

## Command Line
COMMAND | DESCRIPTION
---|---
`code .` | Open the current folder
`code -r <FILE>` | Reuse the existing window
`code --diff <A> <B>` | Compare two files
`code --goto <FILE>:<LINE>` | Open at a line
`code --list-extensions` | List installed extensions
`code --install-extension <PUBLISHER.NAME>` | Install an extension
`code --uninstall-extension <PUBLISHER.NAME>` | Remove an extension
`code --list-extensions \| xargs -L1 echo code --install-extension` | Generate commands to reinstall extensions elsewhere
`code --profile <NAME> .` | Open with a profile

## Useful settings.json
```json
{
  "editor.formatOnSave": true,
  "editor.minimap.enabled": false,
  "editor.rulers": [80, 120],
  "editor.bracketPairColorization.enabled": true,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.autoSave": "onFocusChange",
  "terminal.integrated.scrollback": 10000,
  "workbench.startupEditor": "none"
}
```

## Handy Extensions
EXTENSION | USE
---|---
`ms-vscode-remote.remote-ssh` | Edit on remote hosts over SSH
`ms-vscode-remote.remote-containers` | Develop inside containers
`ms-azuretools.vscode-docker` | Docker and Compose support
`redhat.vscode-yaml` | YAML schema validation
`ms-kubernetes-tools.vscode-kubernetes-tools` | Kubernetes
`hashicorp.terraform` | Terraform
`redhat.ansible` | Ansible
`timonwong.shellcheck` | Shell script linting
`eamodio.gitlens` | Git blame and history
`yzhang.markdown-all-in-one` | Markdown editing
`EditorConfig.EditorConfig` | Respect `.editorconfig`
