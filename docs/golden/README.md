# Golden screenshots

Golden screenshots should be captured manually on a Windows machine with PySide6
available. Save the baseline images for the Qt HUD in this folder and keep names
stable for future diffs.

Suggested captures:
- `hud_idle.png` — no warning, baseline layout.
- `hud_warning_warn.png` — warning block with `warn` level.
- `hud_warning_danger.png` — warning block with `danger` level and long text.
- `hud_macro.png` — macro block with multiple lines to validate auto-height.
