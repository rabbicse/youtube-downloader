# -*- coding: utf-8 -*-
import os
import time
from http.cookiejar import LWPCookieJar
from urllib import request, error

from youtube_downloader.utils import regex_utils
from youtube_downloader.utils.printer import Printer
from ..utils.tail_call import tail_call_optimized

__author__ = 'rabbi'

HEADERS = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'),
           ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
           ('Connection', 'keep-alive')]


class FileDownloader(object):
    def __init__(self, url, file_name):
        self.__url = url
        self.__file_name = file_name

    @tail_call_optimized
    def download_file(self, retry=0):
        dl_file = None
        try:
            current_size = 0
            opener = self.__create_opener(headers=HEADERS)
            try:
                if os.path.exists(self.__file_name):
                    start = os.path.getsize(self.__file_name)
                    current_size = start
                    opener.addheaders.append(('Range', 'bytes=%s-' % start))
            except Exception as x:
                print(x)

            resp = opener.open(self.__url, timeout=60)
            print(resp.info())
            content_length = resp.info()['Content-Length']
            content_length = regex_utils.search_pattern_single('^(\d+)', content_length)
            total_size = float(current_size) + float(content_length)
            total_size_mb = round(total_size / (1024 * 1024), 2)

            if current_size == total_size:
                print('Already exists...')
                return

            directory = os.path.dirname(self.__file_name)
            if not os.path.exists(directory):
                os.makedirs(directory)

            dl_file = open(self.__file_name, 'ab')

            # res = opener.open(url, timeout=60)
            chunk_size = 256 * 1024
            while True:
                start = time.time()
                data = resp.read(chunk_size)
                total = time.time() - start
                # data = resp.read(CHUNK_SIZE)
                if not data:
                    break
                current_size += len(data)
                dl_file.write(data)
                dl_file.flush()

                downloaded = round(float(current_size * 100) / total_size, 2)
                download_speed = ((len(data) / 1024.0) / total)
                # print('============> ' + str(downloaded) + '% of ' + str(
                #     total_size_mb) + ' Mega Bytes. ' + 'Download Speed: %.2f KBPS' % download_speed)
                log = '============> ' + str(downloaded) + '% of ' + str(
                    total_size_mb) + ' Mega Bytes. ' + 'Download Speed: %.2f KBPS' % download_speed
                Printer(log)
            if current_size >= total_size:
                return True
        except error.HTTPError as e:
            print(e.code)
        except error.ContentTooShortError as e:
            print(e.reason)
        except error.URLError as e:
            print(e.reason)
        except Exception as x:
            print(x)
            if retry < 20:
                time.sleep(5)
                return self.download_file(retry + 1)
        finally:
            if dl_file:
                dl_file.close()
        return False

    @staticmethod
    def __create_opener(headers=None, handler=None):
        """
        Create opener for fetching data.
        headers = [] Ex. User-agent etc like, [('User-Agent', HEADERS), ....]
        handler = object Ex. Handler like cookie_jar, auth handler etc.
        return opener
        """
        try:
            opener = request.build_opener(request.HTTPRedirectHandler(),
                                          request.HTTPHandler(debuglevel=0),
                                          request.HTTPSHandler(debuglevel=0))
            if headers is not None:
                opener.addheaders.extend(headers)
            if handler is not None:
                opener.add_handler(handler)

            request.install_opener(opener)
            return opener
        except Exception as x:
            raise x

    @staticmethod
    def __create_cookie_jar_handler():
        """
        Create cookie jar handler. used when keep cookie at login.
        """
        cookie_jar = LWPCookieJar()
        return request.HTTPCookieProcessor(cookie_jar)
