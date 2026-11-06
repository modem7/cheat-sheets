# VSCode shortcuts (macOS)
Default key bindings for Visual Studio Code on macOS. On Windows and Linux replace `⌘` with `Ctrl` and `⌥` with `Alt`. See [VSCode (Visual Studio Code)](../tools/vscode.md) for settings and extensions, and [MacOS keyboard shortcuts](macos-shortcuts.md) for system keys.

- [macOS keyboard shortcuts PDF](https://code.visualstudio.com/shortcuts/keyboard-shortcuts-macos.pdf)
- [Key bindings for Visual Studio Code](https://code.visualstudio.com/docs/getstarted/keybindings)
- Open the shortcut editor with `⌘ + K` then `⌘ + S`. Your overrides live in `keybindings.json`.

## General
| shortcut  | description                |
| :-------- | :------------------------- |
| ⌘ + ⇧ + P | Command palette            |
| ⌘ + P     | Quick open a file          |
| ⌘ + ,     | Settings                   |
| ⌘ + ⇧ + O | Go to symbol in file       |
| ⌃ + G     | Go to line                 |
| F12       | Go to definition           |
| ⌘ + /     | Toggle line comment        |

## Side Menu
| shortcut  | description                         |
| :-------- | :---------------------------------- |
| ⌘ + B     | Show or hide the side bar           |
| ⌘ + ⇧ + E | Explorer                            |
| ⌘ + ⇧ + F | Search across files                 |
| ⌘ + F     | Find in the current file            |
| ⌘ + ⌥ + F | Replace in the current file         |
| ⌃ + ⇧ + G | Source control (Git)                |
| ⌘ + ⇧ + D | Run and debug                       |
| ⌘ + ⇧ + X | Extensions                          |
| ⌘ + J     | Toggle the bottom panel             |

## Multi-Cursor Editing
| shortcut  | description                                       |
| :-------- | :------------------------------------------------ |
| ⌘ + ⌥ + ↓ | add a cursor below (`↑` for above)                |
| ⌥ + Click | add a cursor at the mouse click                   |
| ⌘ + D     | select the next occurrence of the current word    |
| ⌘ + ⇧ + L | select all occurrences of the current selection   |

## Split Editor
| shortcut | description                         |
| :------- | :---------------------------------- |
| ⌘ + \    | split the editor                    |
| ⌘ + 1    | focus the 1st editor group          |
| ⌘ + 2    | focus the 2nd editor group          |
| ⌃ + `    | toggle the integrated terminal      |
| ⌃ + tab  | switch between open tabs            |
| ⌘ + `    | switch between VS Code windows      |
| ⌘ + ⇧ + E | focus the Explorer                 |

## IntelliSense
| shortcut  | description                    |
| :-------- | :----------------------------- |
| ⌃ + Space | trigger suggestions            |
| ⌘ + ⇧ + Space | trigger parameter hints    |
| ⌘ + .     | quick fix and code actions     |

## Line Actions
| shortcut  | description                     |
| :-------- | :------------------------------ |
| ⇧ + ⌥ + ↓ | copy the line below             |
| ⇧ + ⌥ + ↑ | copy the line above             |
| ⌥ + ↓     | move the line down              |
| ⌥ + ↑     | move the line up                |
| ⌘ + ⇧ + K | delete the line                 |
| ⌘ + Enter | insert a line below             |
| ⌘ + ⇧ + Enter | insert a line above         |

## Rename Refactoring
| shortcut                           | description                          |
| :--------------------------------- | :----------------------------------- |
| F2 (Fn + F2)                       | Rename symbol in the current project |
| Right-click, Rename Symbol         | Rename symbol in the current project |

## Formatting
| shortcut      | description            |
| :------------ | :--------------------- |
| ⇧ + ⌥ + F     | format entire document |
| ⌘ + K, ⌘ + F  | format selected text   |

## Transform Selected Text
The commands exist (Command palette: *Transform to Uppercase*, *Transform to Lowercase*, *Transform to Snake Case*, *Transform to Title Case*) but have **no default key binding** in current versions. Bind your own in `keybindings.json` if you use them often.

## Code Folding
| shortcut      | description     |
| :------------ | :-------------- |
| ⌘ + ⌥ + [     | fold            |
| ⌘ + ⌥ + ]     | unfold          |
| ⌘ + K, ⌘ + 0  | fold all        |
| ⌘ + K, ⌘ + J  | unfold all      |
| ⌘ + K, ⌘ + 1  | fold level 1    |
| ⌘ + K, ⌘ + 2  | fold level 2    |
| ⌘ + K, ⌘ + 5  | fold level 5    |

## Errors and Warnings
| shortcut  | description                   |
| :-------- | :---------------------------- |
| F8        | next error or warning         |
| ⇧ + F8    | previous error or warning     |
| ⌘ + ⇧ + M | open the Problems panel       |

## Not Verified
Shortcuts are the long-standing macOS defaults, not re-checked against the newest release. Open the shortcut editor to confirm.
