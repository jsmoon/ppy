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

def ppytube_download(url: str, mime_type: str):
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

    if len(yt.streams) == 0:
        sys.exit("No streams")

    try:
        print('{}'.format(yt.title))
        streams = [st for st in yt.streams if st.mime_type.startswith(mime_type)]
        stream = streams[0]
        if len(streams) > 1:
            from pprint import pprint
            for st in streams:
                pprint(st)
            itag = input("Select itag (default:{}): ".format(stream.itag))
            if itag:
                stream = [st for st in streams if st.itag is int(itag)][0]
    except Exception as e:
        sys.exit("No stream specified\n{}".format(e))

    try:
        print('From {}'.format(stream.url))
        stream.download()
    except Exception as e:
        sys.exit("Download Failed! -- {}\n{}".format(url, e))

    print('Download Completed!')


SHORTDESC="""download a video from youtube url using by pytube3."""

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    # parse mime_type filter option
    mime_group = parser.add_mutually_exclusive_group()
    mime_group.add_argument("--audio", help="choose audio only", action="store_true")
    mime_group.add_argument("--video", help="choose video only", action="store_true")
    mime_group.add_argument("--mime", help="filter mime_type (video/mp4, audio/mp4, ...)")

    logger.debug(sys.argv)
    args, argv = parser.parse_known_args(sys.argv[1:])
    mime = 'audio' if args.audio else 'video' if args.video else args.mime if args.mime else ''

    if len(argv) < 1:
        argv.append(input("Please input YouTube URL: "))

    for url in argv:
        print("URL: {}".format(url))
        ppytube_download(url, mime)