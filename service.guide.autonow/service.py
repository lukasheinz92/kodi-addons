"""Guide Auto-Now: re-open the TV guide on the current time after it sat idle.

Kodi keeps the guide grid wherever it was when you stopped using it, so after switching the TV off
in the evening and on the next day the guide still shows yesterday. This service re-opens the guide
(which positions it on "now") when:
  * the TV (or radio) guide is the active window,
  * nothing is playing, and
  * there was no input (and no refresh) for the configured number of minutes.

While a screensaver is active nothing is done (re-opening a window could wake it, and with CEC the TV);
instead the guide is refreshed right when the screensaver is deactivated, if it became stale meanwhile.
"""
import time

import xbmc
import xbmcaddon
import xbmcgui

from resources.lib import logic

ADDON_ID = "service.guide.autonow"
POLL_SECONDS = 30
WINDOW_HOME = 10000


def log(msg, level=xbmc.LOGINFO):
    xbmc.log("[%s] %s" % (ADDON_ID, msg), level)


class Settings(object):
    def __init__(self):
        self.load()

    def load(self):
        addon = xbmcaddon.Addon(ADDON_ID)  # a new instance re-reads the settings
        self.enabled = addon.getSetting("enabled") != "false"
        self.interval_s = logic.parse_interval(addon.getSetting("interval")) * 60
        self.windows = logic.guide_windows(addon.getSetting("radio") != "false")
        log("settings: enabled=%s interval=%d min windows=%s"
            % (self.enabled, self.interval_s // 60, self.windows))


class Service(xbmc.Monitor):
    def __init__(self):
        super(Service, self).__init__()
        self.settings = Settings()
        self.player = xbmc.Player()
        self.last_refresh = time.time()
        self.screensaver_idle_since = None

    # --- Kodi callbacks -------------------------------------------------------------------------
    def onSettingsChanged(self):
        self.settings.load()

    def onScreensaverActivated(self):
        self.screensaver_idle_since = time.time() - xbmc.getGlobalIdleTime()

    def onScreensaverDeactivated(self):
        idle_since, self.screensaver_idle_since = self.screensaver_idle_since, None
        if idle_since is not None:
            self.check(idle_since, "screensaver deactivated")

    # --- logic ----------------------------------------------------------------------------------
    def check(self, idle_since, reason):
        if not self.settings.enabled:
            return
        window_id = xbmcgui.getCurrentWindowId()
        if logic.should_refresh(window_id, self.settings.windows, self.player.isPlaying(),
                                time.time(), idle_since, self.last_refresh, self.settings.interval_s):
            self.refresh(window_id, reason)

    def refresh(self, window_id, reason):
        log("re-opening guide window %d (%s)" % (window_id, reason))
        xbmc.executebuiltin("ActivateWindow(%d)" % WINDOW_HOME, True)
        if self.waitForAbort(0.5):
            return
        xbmc.executebuiltin("ActivateWindow(%d)" % window_id, True)
        self.last_refresh = time.time()

    def run(self):
        log("started")
        while not self.waitForAbort(POLL_SECONDS):
            if xbmc.getCondVisibility("System.ScreenSaverActive"):
                continue
            self.check(time.time() - xbmc.getGlobalIdleTime(), "idle")
        log("stopped")


if __name__ == "__main__":
    Service().run()
