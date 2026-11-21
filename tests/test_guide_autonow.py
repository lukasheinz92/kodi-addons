import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "service.guide.autonow"))

from resources.lib import logic  # noqa: E402

TV, RADIO = logic.WINDOW_TV_GUIDE, logic.WINDOW_RADIO_GUIDE
HOME = 10000
MIN = 60


class ParseInterval(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(logic.parse_interval("10"), 10)
        self.assertEqual(logic.parse_interval(1), 1)
        self.assertEqual(logic.parse_interval(" 1440 "), 1440)

    def test_clamped(self):
        self.assertEqual(logic.parse_interval("0"), 1)
        self.assertEqual(logic.parse_interval("-5"), 1)
        self.assertEqual(logic.parse_interval("5000"), 1440)

    def test_invalid_uses_default(self):
        for raw in ("", "abc", None, "1.5"):
            self.assertEqual(logic.parse_interval(raw), 10)


class ShouldRefresh(unittest.TestCase):
    def check(self, window=TV, playing=False, idle_min=11, refreshed_min_ago=60, interval_min=10,
              radio=True):
        now = 100000.0
        return logic.should_refresh(window, logic.guide_windows(radio), playing, now,
                                    now - idle_min * MIN, now - refreshed_min_ago * MIN,
                                    interval_min * MIN)

    def test_guide_idle_long_enough(self):
        self.assertTrue(self.check())

    def test_exactly_interval(self):
        self.assertTrue(self.check(idle_min=10, refreshed_min_ago=10))

    def test_not_idle_long_enough(self):
        self.assertFalse(self.check(idle_min=9))

    def test_recently_refreshed(self):
        self.assertFalse(self.check(idle_min=600, refreshed_min_ago=5))

    def test_refreshes_again_after_interval_while_still_idle(self):
        self.assertTrue(self.check(idle_min=600, refreshed_min_ago=10))

    def test_other_window(self):
        self.assertFalse(self.check(window=HOME))

    def test_playing(self):
        self.assertFalse(self.check(playing=True))

    def test_radio_guide(self):
        self.assertTrue(self.check(window=RADIO))
        self.assertFalse(self.check(window=RADIO, radio=False))

    def test_long_interval(self):
        self.assertFalse(self.check(idle_min=1439, refreshed_min_ago=2000, interval_min=1440))
        self.assertTrue(self.check(idle_min=1440, refreshed_min_ago=2000, interval_min=1440))


if __name__ == "__main__":
    unittest.main()
