#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
# in my experience, pytube3 works and is active. pytube does not work.
import pytube
if pytube.__title__ != 'pytube3':
    sys.exit("Please install pytube3! You are using {title} v{version}."
        .format(title=pytube.__title__, version=pytube.__version__))

from pytube import YouTube

import logging
logger = logging.getLogger(__name__)

def ppytube_download(url):
    try:
        from pytube import extract
        extract.video_id(url)
    except Exception as e:
        sys.exit("Unsupported URL -- {}\n{}".format(url, e))

    try:
        #object creation using YouTube which was imported in the beginning 
        yt = YouTube(url, defer_prefetch_init=True)
        yt.prefetch()
        yt.descramble()
    except Exception as e:
        sys.exit("YouTube Init Error -- {}\n{}".format(url, e))

    if len(yt.streams.all()) == 0:
        sys.exit("No streams")

    try:
        print('{}'.format(yt.title))
        stream = yt.streams.first()
        if yt.streams.count() > 1:
            from pprint import pprint
            pprint(yt.streams.all())
            itag = input("Select itag (default:{}): ".format(stream.itag))
            if itag:
                stream = [st for st in yt.streams.all() if st.itag is int(itag)][0]
    except Exception as e:
        sys.exit("No stream specified\n{}".format(e))

    try:
        print('From {}'.format(stream.url))
        stream.download()
    except Exception as e:
        sys.exit("Download Failed! -- {}\n{}".format(url, e))

    print('Download Completed!')


SHORTDESC="""download a video from youtube url using by pytube."""

if __name__ == "__main__":
    logger.debug(sys.argv)
    if len(sys.argv) <= 1:
        sys.argv.append(input("Please input YouTube URL: "))

    for url in sys.argv[1:]:
        print("URL: {}".format(url))
        ppytube_download(url)