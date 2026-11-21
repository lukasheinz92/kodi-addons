# kodi-addons

Public GitHub repo `lukasheinz92/kodi-addons` (personal account; push via `git@github.com-lukasheinz92:`).
Monorepo of Kodi add-ons + the Kodi repository add-on `repository.lukasheinz92`, published by the GitHub Actions
workflow to GitHub Pages (`https://lukasheinz92.github.io/kodi-addons/`, Pages source = GitHub Actions).

- Each top-level folder with an `addon.xml` is an add-on; folder name must equal the add-on id (build enforces it).
- To release a change: bump `version` in that add-on's `addon.xml` (and `<news>`), push to `main`. Kodi updates
  only on a higher version.
- Test: `python -m unittest discover -s tests`; build locally: `python tools/build.py <outdir>`.
- Keep Kodi-independent logic in `resources/lib/logic.py` so it is unit-testable without Kodi.
- Main consumer: pi-media (LibreELEC 12 / Kodi 21, `ssh root@192.168.144.111`, see `rpi/pi-media`). Kodi log there:
  `/storage/.kodi/temp/kodi.log` (grep the add-on id).
- Gotcha (2026-11-21): Kodi on pi-media got into a state where direct HTTPS reads returned 0 bytes instantly (no
  request, nothing in the log even at trace level) → "Could not connect to repository" / `CRepository: failed read
  '…addons.xml.md5'`, while `curl` on the Pi and Kodi via `http://` (301 → https) worked. `systemctl restart kodi`
  fixed it. Quick check from Kodi's VFS: a `RunScript` with `xbmcvfs.File(url).readBytes()`.
