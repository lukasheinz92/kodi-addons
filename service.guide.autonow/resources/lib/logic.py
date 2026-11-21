"""Pure decision logic of Guide Auto-Now (no Kodi imports, unit-testable)."""

# Kodi window IDs (xbmcgui.getCurrentWindowId())
WINDOW_TV_GUIDE = 10702
WINDOW_RADIO_GUIDE = 10707

INTERVAL_MIN = 1
INTERVAL_MAX = 1440
INTERVAL_DEFAULT = 10


def parse_interval(raw):
    """Setting value (string or int) -> minutes, clamped to 1..1440; invalid -> default."""
    try:
        minutes = int(str(raw).strip())
    except (TypeError, ValueError):
        return INTERVAL_DEFAULT
    return max(INTERVAL_MIN, min(INTERVAL_MAX, minutes))


def guide_windows(include_radio):
    return (WINDOW_TV_GUIDE, WINDOW_RADIO_GUIDE) if include_radio else (WINDOW_TV_GUIDE,)


def is_stale(now, idle_since, last_refresh, interval_s):
    """The guide is stale when neither the user nor we touched it for interval_s seconds."""
    return now - max(idle_since, last_refresh) >= interval_s


def should_refresh(window_id, windows, playing, now, idle_since, last_refresh, interval_s):
    return (window_id in windows
            and not playing
            and is_stale(now, idle_since, last_refresh, interval_s))
