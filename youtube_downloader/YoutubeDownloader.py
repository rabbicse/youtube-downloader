import os
import re
import platform
import subprocess
from youtube_downloader.downloader.file_downloader import FileDownloader

from youtube_downloader.downloader.spider import Spider
from youtube_downloader.utils import parser_utils

__author__ = 'rabbi'


class YoutubeDownloader(Spider):
    def __init__(self, url, directory):
        Spider.__init__(self)
        self.__url = url
        self.__dir = directory

    def start_download(self):
        try:
            print("Youtube Video URL: " + self.__url)
            media_list, cc_list = self.__extract_meta()
            if not media_list:
                return
            print('Please select itag from the following list:')
            for media in iter(media_list):
                print(media.itag, media.quality, media.media_type,
                      '%d x %s' % (media.size.width, media.size.height) if media.size else '')
            user_input = input('Please enter itag: ')

            if not user_input:
                selected_video = media_list[0]
            else:
                selected_video = next(y for y in iter(media_list) if y.itag == user_input)

            print(selected_video.url)

            # get title & generate file name
            video_title = self.__extract_title(self.__url)
            output_file_name = self.__extract_filename(video_title)
            print(output_file_name + '.mp4')

            # check directory
            if not os.path.exists(self.__dir):
                os.makedirs(self.__dir)

            # todo download cc
            if cc_list:
                print('All cc list:')
                for cc in cc_list:
                    print(cc.lan, cc.url)
                    cc_output_file = self.__dir + output_file_name + '_' + cc.lan + '_cc.srt'
                    xml_data = self.fetch_data(cc.url)
                    if not xml_data:
                        continue
                    parser_utils.convert_xml_to_srt_file(xml_data, cc_output_file)

            # todo download
            video_output_file = self.__dir + output_file_name + '_video.mp4'
            video_downloader = FileDownloader(selected_video.url, video_output_file)
            video_downloader.download_file()

            # todo download audio
            audio_output_file = self.__dir + output_file_name + '_audio.mp4a'
            selected_audio = next(y for y in iter(media_list) if y.media_type == 'audio/mp4')
            audio_downloader = FileDownloader(selected_audio.url, audio_output_file)
            audio_downloader.download_file()

            # todo merge
            merged_av_file = self.__dir + output_file_name + '.mkv'
            if self.__merge_av(merged_av_file, video_output_file, audio_output_file):
                print('download completed....')
                # os.remove(video_output_file)
                # os.remove(audio_output_file)
        except Exception as x:
            print(x)

    def __extract_meta(self):
        media_list = []
        cc_list = []
        try:
            data = self.fetch_data(self.__url)
            if not data:
                return
            adaptive_fmt_match = re.search(r'(?i)"adaptive_fmts":\s*?"([^"]*?)"', data, re.MULTILINE)
            if not adaptive_fmt_match:
                return
            cc_match = re.search(r'(?i)"caption_tracks":\s*?"([^"]*?)"', data, re.MULTILINE)
            if cc_match:
                cc_info_list = cc_match.group(1)
                cc_info_list = parser_utils.unquote_url(cc_info_list)
                cc_info_list = cc_info_list.split(',')
                for cc_info in cc_info_list:
                    cc = self.__parse_cc(cc_info)
                    if not any(c.lan == cc.lan for c in cc_list):
                        cc_list.append(cc)
            adaptive_fmt_all = adaptive_fmt_match.group(1)
            adaptive_fmt_all = parser_utils.unquote_url(adaptive_fmt_all)
            adaptive_fmts = adaptive_fmt_all.split(',')
            for adaptive_fmt in adaptive_fmts:
                # print(adaptive_fmt)
                meta_data = self.__parse_info(adaptive_fmt)
                media_list.append(meta_data)
        except Exception as x:
            print(x)
        return media_list, cc_list

    def __extract_title(self, url):
        try:
            """
                https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v=9bZkp7q19f0&format=xml
            """
            xml_url = 'https://www.youtube.com/oembed?url=' + str(url) + '&format=xml'
            data = self.fetch_data(xml_url)
            if not data:
                return ''
            match = re.search(r'(?i)<title>([^<]*)</title>', data)
            return match.group(1) if match else ''
        except Exception as x:
            print(x)

    @staticmethod
    def __parse_cc(cc_info):
        cc_info = re.split(r'\\u0026', cc_info)
        if cc_info and len(cc_info) > 0:
            cc = Subtitle()
            for c in cc_info:
                if 'u=' in c:
                    cc.url = c.replace('u=', '').strip()
                elif 'lc=' in c:
                    cc.lan = c.replace('lc=', '').strip()
            return cc

    @staticmethod
    def __merge_av(output_file, *args):
        try:
            ffmpeg_cmd = 'ffmpeg'
            if str(platform.system()).startswith('Windows'):
                ffmpeg_cmd = 'ffmpeg.exe'
            cmd = '%s -i "%s" -i "%s" -acodec copy -vcodec copy "%s"' % (ffmpeg_cmd, args[0], args[1], output_file)
            subprocess.call(cmd, shell=True)
            return True
        except Exception as x:
            print(x)
        return False

    @staticmethod
    def __extract_filename(text):
        file_name = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        file_name = re.sub(r'[_]+', '_', file_name)
        # file_name = re.sub(r'"', '', text)
        # file_name = re.sub(r'\'', '', file_name)
        # file_name = re.sub(r',', '', file_name)
        # file_name = re.sub(r'\|', '', file_name)
        # file_name = re.sub(r'\s+', '_', file_name)
        # file_name = re.sub(r'/', '_', file_name)
        # file_name = re.sub(r'\\\\', '_', file_name)
        # file_name = re.sub(r'[_\-\.]+', '_', file_name)
        return file_name
        # dlPath = './' + fname + '.mp4' if filename is None else filename

    @staticmethod
    def __parse_info(adaptive_info):
        adaptive_info = re.split(r'\\u0026', adaptive_info)
        if adaptive_info and len(adaptive_info) > 0:
            media = Media()
            for u in adaptive_info:
                if 'url=' in u:
                    media.url = u.replace('url=', '').strip()
                elif 'quality_label=' in u:
                    media.quality = u.replace('quality_label=', '').strip()
                elif re.match(r'^type=.*?$', u.strip()):
                    media.media_type = u.replace('type=', '').split(';')[0].strip()
                elif 'size=' in u:
                    media.size = Size(u.replace('size=', '').strip())
                elif re.match(r'^itag=\d+$', u.strip()):
                    media.itag = u.replace('itag=', '').strip()
            return media


class Media(object):
    def __init__(self, url=None, itag=None, quality=None, media_type=None, size=None):
        self.__url = url
        self.__itag = itag
        self.__quality = quality
        self.__media_type = media_type
        self.__size = size

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def itag(self):
        return self.__itag

    @itag.setter
    def itag(self, value):
        self.__itag = value

    @property
    def quality(self):
        return self.__quality

    @quality.setter
    def quality(self, value):
        self.__quality = value

    @property
    def media_type(self):
        return self.__media_type

    @media_type.setter
    def media_type(self, value):
        self.__media_type = value

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, value):
        self.__size = value


class Subtitle(object):
    def __init__(self, url=None, lan=None):
        self.__url = url
        self.__lan = lan

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def lan(self):
        return self.__lan

    @lan.setter
    def lan(self, value):
        self.__lan = value


class Size(object):
    def __init__(self, size):
        width_height = size.split('x') if size else None
        if width_height and len(width_height) > 1:
            self.__width = int(width_height[0])
            self.__height = int(width_height[1])
        else:
            self.__width, self.__height = 0, 0

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def __int__(self):
        return self.__width * self.__height
