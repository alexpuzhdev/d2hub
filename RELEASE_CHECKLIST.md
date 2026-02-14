# Release checklist

## Visual smoke (Qt HUD)
- [ ] Launch HUD with `python -m dota_hud`.
- [ ] Verify palette/gradient matches Dota+.
- [ ] Confirm warning block highlight animates locally (danger/warn).
- [ ] Confirm NOW/NEXT/MACRO blocks animate and keep their background.
- [ ] Verify auto-height expands for long warning text.
- [ ] Capture golden screenshots (store under `docs/golden/`).

## Config sanity
- [ ] `configs/timings.yaml` loads without errors.
- [ ] `modules` files (`configs/modules/*.yaml`) merge correctly.
- [ ] `configs/macro.yaml` loads with `macro_config`.

## GSI
- [ ] Start Dota match and confirm timer sync.
- [ ] Pause game -> HUD shows `PAUSED (DOTA)`.
- [ ] Stop GSI updates -> HUD shows `GSI STALE` then `GSI OFFLINE`.

## Tests
- [ ] `pytest -q`
