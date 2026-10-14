---
name: "bell-alarm-floating-panels"
description: "Use when building or editing the Signal Live Companion: notification bell + counter, alarm-clock reminders, and movable, non-overlapping floating panels/popups."
---

# Bell, alarm clock and floating panels (Signal Live Companion)

Rules the user set; apply to every page, module and the top view panel.

## Notification bell
- A bell button (UTF-8 bell or ASCII) with a numeric counter at the top of EVERY page, module and the view panel. Class `slcBell`, counter span `.bn` (always null-check `.bn` before writing).
- Notify on: test finished, export done, progress, logs, feed quality, lost feed/data/connection, risk of losing csv/txt/strategies/logs. API: `slcNotify(kind,text)`, `slcNotifyLog(k,t)`.
- Counter turns red on error; clicking opens a movable list.

## Alarm clock (next to every bell)
- Floating reminder popup: snooze, mute, dismiss. Reminds the user to check, export, verify, test, and edit/review price/chart signals. State in localStorage `slc_alarm`.

## Floating panels / popups
- Nothing may overlap another window without being easily movable. Every popup, panel, frame, message is draggable from inside the frame (5 px threshold, not on buttons/inputs) AND from its border: edge midpoints move, corners resize (Shift/Ctrl/Alt+edge resizes).
- Popups (e.g. unfinished-test warning) stack with an offset, are non-blocking, max 4, newest on top; click brings to front.
- User position/size always overrides autofit; remembered in `slc_userpos` / `slc_usersize`.
- A Tidy button arranges all floating panels without overlap.
- Test with Playwright: real mouse drag moves the element; no pageerror.

## House rules
- Always show the full path of any created file; label pages with build/version; keep max 3 backups per version.