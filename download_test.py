import re
import urllib.request
from youtube_downloader.downloader import generic_file_downloader
from youtube_downloader.downloader.spider import Spider
from youtube_downloader.utils import regex_utils


class NaturalBdDownloader(Spider):
    def __init__(self, url):
        headers = [('Host', 'www.naturalbd.com'), ('Upgrade-Insecure-Requests', '1')]
        Spider.__init__(self)
        self.__url = url

    def start_download(self):
        # HEADERS = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'),
        #            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
        #            ('Connection', 'keep-alive'),
        #            ('Host', 'yesmovies.to'),
        #            ('Referer', 'http://www.naturalbd.com/'),
        #            ('origin', 'http://www.naturalbd.com')]
        # d = self.fetch_data('https://yesmovies.to/ajax/user_get_state.html')

        # login_url = 'http://www.naturalbd.com/login'
        # d =self.fetch_data(login_url, parameters={'password': 'ubuntu36', 'returnpath': '/', 'username': 'rabbicse'})
        # print(d)
        # print(self.__url)
        # data = self.fetch_data(self.__url)
        # print(data)
        req = urllib.request.Request(self.__url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})
        data = urllib.request.urlopen(req).read().decode('utf-8')
        if not data:
            return
        link_match = re.search(r'(?i)<a href="([^"]*?)" title="download from Premium Server"', data, re.MULTILINE)
        if link_match:
            link = link_match.group(1)
            print(link)
            HEADERS = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'),
                       ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                       ('Connection', 'keep-alive'),
                       ('Host', link.split('/')[-3]),
                       ('Referer', self.__url)]
            print(HEADERS)
            dl = generic_file_downloader.GenFileDownloader(link, './' + str(link.split('/')[-1]).strip(), HEADERS)
            dl.download_file()


# file_path = 'http://anime.naturalbd.com:81/r/Rise.of.the.Guardians.2012.BluRay.1080p.x264.NBD.mp4'
# HEADERS = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'),
#            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
#            ('Connection', 'keep-alive'),
#            ('Host', 'anime.naturalbd.com:81'),
#            ('Referer', 'http://www.naturalbd.com/movie/rise-of-the-guardians')]
# dl = generic_file_downloader.GenFileDownloader(file_path, file_path.split('/')[-1], HEADERS)
# dl.download_file()


nbd = NaturalBdDownloader('http://www.naturalbd.com/movie/top-cat-begins')
nbd.start_download()
