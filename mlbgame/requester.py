"""Class for loading data from MLBAM. It knows when the last time it requested
a URL so can be more efficient when asking for updates.

This is also nicer to the MLBAM site than constantly re-hitting it.

Note however that I am not sure how this works when multi-threading or
multi-processing, so I'm not sure if its the best way to handle things."""

from urllib.request import urlopen, Request, HTTPError
from collections import deque


class Page(object):
    """Used for scraping a specific URL page."""

    def __init__(self, url, verbose=False):
        """The state of the page is defined by
            url: The url of the page.
            content: The last known content of the site.
            last_request: The time the page was last requested.
        """
        self.url = url
        self.content = None
        self.last_request = None
        self.verbose = verbose

    def _request_site(self, request):
        """Tries to open a request and return the data."""
        response = urlopen(request)
        assert response.getcode() == 200

        # Set the state from the response.
        self.content = response.read()
        self.last_request = response.getheader('Date')

        return self.content

    def scrape(self):
        """Scrape the site, using the cached result if nothing changed."""
        request = Request(self.url)

        if self.content is None:
            # Site has never been scraped before so we have no last scraped
            # time and we need a 200 (i.e. everything ok) response.
            self._request_site(request)

        else:
            # Site has previously been scraped so we let the server know we
            # don't need the webpage unless its been changed.
            request.add_header("If-Modified-Since", self.last_request)

            try:
                self._request_site(request)
            except HTTPError as e:
                if e.code == 304:
                    # This is fine, the site hasn't been updated since last
                    # request.
                    if self.verbose:
                        print("Site not updated since last call.")
                else:
                    raise HTTPError(e)

        return self.content


class Requester(object):
    """Holds a number of Page scrapers for repeated requests. Can set a maximum
    number to hold so that after reaching this limit they start getting popped
    off the queue."""

    def __init__(self, max_size):
        """Need the maximum number of Page instances it can hold before popping
        off the queue."""
        # The self.urls object keeps track of when urls were added, the
        # self.pages dictionary holds their corresponding Page instance.
        self.urls = deque(maxlen=max_size)
        self.pages = {}

    def urlopen_read(self, url):
        """Mimic the urllib urlopen method when called with read."""
        if url not in self.pages:
            if len(self.urls) < self.urls.maxlen:
                # Have space for more URLs.
                self.urls.append(url)
                self.pages[url] = Page(url, verbose=False)
            else:
                # Must remove the oldest URL.
                oldest_url = self.urls.popleft()
                del self.pages[oldest_url]

                self.urls.append(url)
                self.pages[url] = Page(url, verbose=False)

        assert len(self.urls) == len(self.pages)

        return self.pages[url].scrape()
