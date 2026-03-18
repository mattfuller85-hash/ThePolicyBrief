---
description: Close all VS Code editor tabs and open task_plan.md
---

This workflow uses AppleScript to simulate the "Cmd+K, W" keyboard shortcut in Visual Studio Code to close all currently open tabs, and then explicitly opens the `task_plan.md` file.

1. Close all tabs inside Visual Studio Code.
// turbo
```bash
osascript -e 'tell application "Visual Studio Code" to activate' -e 'tell application "System Events" to keystroke "k" using command down' -e 'delay 0.2' -e 'tell application "System Events" to keystroke "w"'
```

2. Open `task_plan.md` to start with a completely clean slate.
// turbo
```bash
code "/Users/matt/Documents/AntiGravity/ThePolicyBrief/task_plan.md"
```
