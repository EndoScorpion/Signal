---
name: "show-full-file-paths"
description: "Whenever a file is created, saved, exported or delivered, always state its complete path and file name in the reply."
---

# Always show the complete file path

The user needs the full path of every file that gets created, so they can find, install or back it up.

## Rule
Every time a file is created, overwritten, exported, moved or delivered (scripts, userscripts, HTML builds, .txt or .json backups, CSV exports, handoffs), end the reply with a short line for each file:

`File: <complete path>/<file name>  (where: <cloud workspace | user's computer folder | downloads>)`

- Give the full path, not just the file name. Use the real path the tool reported, such as the outputs folder path for cloud files or the connected-folder path for files written to the user's computer.
- If the file lives only in the cloud workspace, say so plainly and add where the user can open it (the chat file list), and that a downloaded copy usually lands in the Windows Downloads folder.
- If the file was written into a connected folder on the user's computer, give that folder path and file name.
- Published artifacts: give the artifact link when asked, plus the local source file path used to publish.
- Keep file names descriptive with a build number and timestamp, and keep at most 3 backups of the same version.
- List several files in one compact block, one per line.
- Do this even when the user did not ask in that message.