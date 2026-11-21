# kodi-addons

Kodi add-ons by lukasheinz92, published as a Kodi repository on GitHub Pages:
<https://lukasheinz92.github.io/kodi-addons/>

| Add-on | What it does |
|---|---|
| [`service.guide.autonow`](service.guide.autonow) – Guide Auto-Now | Re-opens the TV guide on the current time after it was left open and idle (e.g. TV switched off overnight). Only when nothing is playing. Idle time configurable, 1–1440 minutes (default 10). |

## Install (Kodi 19+)

1. **Settings → System → Add-ons → Unknown sources** → on.
2. **Settings → File manager → Add source** → `https://lukasheinz92.github.io/kodi-addons/` → name it `kodi-addons`.
3. **Add-ons → Install from zip file → kodi-addons → `repository.lukasheinz92-x.y.z.zip`**.
4. **Add-ons → Install from repository → lukasheinz92 Add-ons → Services → Guide Auto-Now → Install**.

Installed add-ons then update automatically (Settings → System → Add-ons → Updates).

## Guide Auto-Now

Kodi leaves the guide grid where it was, so after a night with the TV off it still shows yesterday. The service
checks every 30 s and re-opens the guide (via Home → guide, which positions it on "now") when:

- the TV guide (optionally also the radio guide) is the active window,
- nothing is playing,
- there was no input and no refresh for the configured number of minutes.

While a screensaver is active nothing happens (re-opening a window could wake it and, with CEC, the TV); instead the
guide is refreshed right when the screensaver is deactivated, if it became stale in the meantime.

Settings: *Enabled*, *Refresh after idle time (minutes)* (1–1440, default 10), *Also refresh the radio guide*.

## Development

```
service.guide.autonow/      add-on (folder name == add-on id)
repository.lukasheinz92/    Kodi repository add-on pointing at GitHub Pages
tools/build.py              builds _site/: zips, addons.xml(.md5), index.html listings
tests/                      unit tests (python -m unittest discover -s tests)
.github/workflows/          tests + build + deploy to GitHub Pages on push to main
```

- New add-on: add a top-level folder named after its id with an `addon.xml`; the build picks it up.
- Release: **bump `version` in the add-on's `addon.xml`** and push to `main`. Kodi only updates when the version
  increases.
