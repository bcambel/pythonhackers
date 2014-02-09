import logging
import requests
from requests import Timeout
from urlparse import urlparse


html_ctype = 'text/html'
xml_ctype = 'text/xml'
xml_ctype2 = 'application/xml'

rss_ctype = 'application/rss+xml'
atom_ctype = 'application/atom+xml'
rdf_ctype = 'application/rdf+xml'

feed_types = [xml_ctype, rss_ctype, atom_ctype, rdf_ctype, xml_ctype2]


class HttpFetcher():
    def __init__(self):
        self.session = requests.session()
        self.session.config['keep_alive'] = True

    #	@profile
    def download(self, url):
        r = self.session.get(url)

        return r.text

    def download_json(self, url):
        r = self.session.get(url)

        return r.json

    def head(self, url, extended=True):
        try:
            r = self.session.head(url, allow_redirects=True)
            print r.headers
            print r.url

            if extended:
                return HttpResult(r.url, r.headers, r.status_code, True)
            else:
                return r.url
        except Timeout as tout:
            logging.error(tout.message, tout)
            return None
        except Exception:
            logging.error("Finding Actual URL General Exception:", exc_info=True)
            return None


class HttpResult:
    def __init__(self, url='', headers=None, status=None, success=False):
        self.url = url
        self.headers = headers
        self.status_code = status
        self.success = success
        self.__content_type = None
        self.__set_content_type()

    def __set_content_type(self):
        """
        Parse http headers to find out content type
        :return: Nothing
        """
        if self.headers is None:
            return

        content_type = self.headers.get("content-type", None)

        if content_type is None:
            return
        if ";" in content_type:
            content_type_parts = content_type.split(";")

            if len(content_type_parts) == 2:
                self.__content_type = content_type_parts[0]
        else:
            self.__content_type = content_type

    @property
    def content_type(self):
        """
        Return the content-type from header info
        :return: String content-type from header if exists otherwise None
        """
        return self.__content_type

    @property
    def is_html(self):
        """
        Check if the content-type is text/html
        :return: True/False
        """
        return self.__content_type == html_ctype

    @property
    def is_rss(self):
        """
        Check if the HttpResult is a Feed type ( text/xml, application/rss+xml, application/atom+xml )
        :return: True/False
        """
        return self.__content_type in feed_types

    def __reduce__(self):
        return {
            "url": self.url,
            "headers": self.headers,
            "status_code": self.status_code,
            "success": self.success,
            "content_type": self.content_type,
            "is_html": self.is_html,
            "is_rss": self.is_rss
        }


http_fetcher = HttpFetcher()


def is_same_domain(url1, url2):
    """
    Returns true if the two urls should be treated as if they're from the same
    domain (trusted).
    """
    url1 = urlparse(url1)
    url2 = urlparse(url2)
    return url1.netloc == url2.netloc