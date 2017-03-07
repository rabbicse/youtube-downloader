import sys

from youtube_downloader.YoutubeDownloader import YoutubeDownloader

__author__ = 'rabbi'

if __name__ == '__main__':
    # url = 'https://www.youtube.com/watch?v=Od-6uzcLGqw'
    url = sys.argv[1]
    # url = sys.argv[1]
    # print(url)
    downloader = YoutubeDownloader(url)
    downloader.start_download()
