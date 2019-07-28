import unittest
import time

from mlbgame.requester import Page, Requester


def time_content(method):
    """Calls a method and returns its output along with the time it
    took to run."""
    now = time.time()
    out = method()
    time_taken = time.time() - now

    return out, time_taken


class TestRequester(unittest.TestCase):
    """Unfortunately due to stochastic issues in scraping web pages, sometimes
    speeds can vary not as a result of caching. This can cause tests to
    occasionally fail."""

    urls = {
        'mlbam': 'http://gd2.mlb.com/components/game/mlb/year_2017/month_07/day_08/gid_2017_07_08_miamlb_sfnmlb_1/game_events.xml',
        'clock': 'https://www.timeanddate.com/worldclock/'
    }

    def __test_cached(self, method, time_taken, content, repeats):
        """Test whether a page is cached by checking its speed when retrieving
        urls versus the time it originally took."""
        time_taken_cumulative = 0
        for _ in range(repeats):
            content2, time_taken2 = time_content(method)
            #print(f"{time_taken} vs {time_taken2}")

            assert content == content2
            time_taken_cumulative += time_taken2

        # Depends on internet connection but likely to be at least 1.5 times
        # quicker when cached.
        self.assertLess(time_taken_cumulative/repeats,  time_taken/2)

    def __test_not_cached(self, method, time_taken, content, repeats):
        """Test whether a page is not cached by checking its speed when
        retrieving urls versus the time it originally took."""
        time_taken_cumulative = 0
        for _ in range(repeats):
            content2, time_taken2 = time_content(method)
            #print(f"{time_taken} vs {time_taken2}")

            assert content != content2
            time_taken_cumulative += time_taken2

        # Depends on internet connection but likely to be at least 2 times
        # quicker when cached on average.
        self.assertGreater(time_taken_cumulative/repeats,  time_taken/2)

    def test_page(self):
        """Test the Page class doesn't reload data that doesn't change."""
        # Can turn on verbose output for testing.
        verbose = False

        # First check an old MLBAM match doesn't change.
        page = Page(self.urls['mlbam'], verbose)

        # Load the page a few times (scraping time fast after the first).
        content, time_taken = time_content(page.scrape)
        self.__test_cached(page.scrape, time_taken, content, 6)

        # Now check a constantly updating site does change.
        page = Page(self.urls['clock'], verbose)

        # Load the page a few times (scraping time fast after the first).
        content, time_taken = time_content(page.scrape)
        self.__test_not_cached(page.scrape, time_taken, content, 6)

    def test_requester(self):
        """Make sure requester caches urls and correctly responds when it runs
        out of space."""
        # Make an instance that can hold a maximum of 2 urls.
        requester = Requester(2)

        # Test caching for our non-updating page.
        openurl = lambda: requester.urlopen_read(self.urls['mlbam'])
        content, time_taken = time_content(openurl)

        self.__test_cached(openurl, time_taken, content, 6)

        # Test caching for our updating page.
        openurl = lambda: requester.urlopen_read(self.urls['clock'])
        content, time_taken = time_content(openurl)

        self.__test_not_cached(openurl, time_taken, content, 6)

        # Add a new site and test that the MLBAM site is no longer cached.
        requester.urlopen_read('http://www.google.com')
        assert self.urls['mlbam'] not in requester.urls
        assert self.urls['mlbam'] not in requester.pages

