# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
from pytube import YouTube

# from pytube.__main__
import json
import logging

from pytube import Caption
from pytube import CaptionQuery
from pytube import extract
from pytube import mixins
from pytube import request
from pytube import Stream
from pytube import StreamQuery
from pytube.compat import install_proxy
from pytube.compat import parse_qsl
from pytube.exceptions import VideoUnavailable
from pytube.helpers import apply_mixin

logger = logging.getLogger(__name__)

# [ppytube] override some YouTube methods to fixup something
class myYouTube(YouTube):
    def prefetch(self):
        self.watch_html = request.get(url=self.watch_url)
        if '<img class="icon meh" src="/yts/img' not in self.watch_html:
            raise VideoUnavailable('This video is unavailable.')
        self.embed_html = request.get(url=self.embed_url)
        self.age_restricted = extract.is_age_restricted(self.watch_html)
        self.vid_info_url = extract.video_info_url(
            video_id=self.video_id,
            watch_url=self.watch_url,
            watch_html=self.watch_html,
            embed_html=self.embed_html,
            age_restricted=self.age_restricted,
        ).replace('&el=$el', '')   # [ppytube] to avoid parameter error
        self.get_vid_info = request.get(self.vid_info_url)
        if not self.age_restricted:
            self.js_url = extract.js_url(self.watch_html, self.age_restricted)
            self.js = request.get(self.js_url)

    def init(self):
        logger.info('init started')

        self.vid_info = {k: v for k, v in parse_qsl(self.get_vid_info)}
        if self.age_restricted:
            self.player_config_args = self.vid_info
        else:
            self.player_config_args = extract.get_ytplayer_config(
                self.watch_html,
            )['args']

            # Fix for KeyError: 'title' issue #434
            if 'title' not in self.player_config_args:
                i_start = (
                    self.watch_html
                    .lower()
                    .index('<title>') + len('<title>')
                )
                i_end = self.watch_html.lower().index('</title>')
                title = self.watch_html[i_start:i_end].strip()
                index = title.lower().rfind(' - youtube')
                title = title[:index] if index > 0 else title
                self.player_config_args['title'] = title

        self.vid_descr = extract.get_vid_descr(self.watch_html)

        # [ppytube] fixup to use player_response streamingData
        streaming_data = json.loads(self.player_config_args['player_response']).get('streamingData')
        # https://github.com/nficano/pytube/issues/165
        stream_maps = ['url_encoded_fmt_stream_map']
        if 'adaptive_fmts' in self.player_config_args or 'adaptiveFormats' in streaming_data:
            stream_maps.append('adaptive_fmts')
        alt_fmts = { 'url_encoded_fmt_stream_map': 'formats', 'adaptive_fmts': 'adaptiveFormats' }

        # unscramble the progressive and adaptive stream manifests.
        for fmt in stream_maps:
            if not self.age_restricted and fmt in self.vid_info:
                mixins.apply_descrambler(self.vid_info, fmt)

            if fmt in self.player_config_args:
                mixins.apply_descrambler(self.player_config_args, fmt)
            # [ppytube] fixup to pass with 'url_encoded_fmt_stream_map' and 'adaptive_fmts'
            elif fmt not in self.player_config_args and alt_fmts[fmt] in streaming_data:
                self.player_config_args[fmt] = streaming_data[alt_fmts[fmt]]
                self.fixup_stream_signature(fmt)
            else:
                continue

            try:
                mixins.apply_signature(self.player_config_args, fmt, self.js)
            except TypeError:
                self.js_url = extract.js_url(
                    self.embed_html, self.age_restricted,
                )
                self.js = request.get(self.js_url)
                mixins.apply_signature(self.player_config_args, fmt, self.js)

            # build instances of :class:`Stream <Stream>`
            self.initialize_stream_objects(fmt)

        # load the player_response object (contains subtitle information)
        apply_mixin(self.player_config_args, 'player_response', json.loads)

        self.initialize_caption_objects()
        logger.info('init finished successfully')

    def fixup_stream_signature(self, fmt):
        stream_manifest = self.player_config_args[fmt]
        for stream in stream_manifest:
            # [ppytube] fixup to download by streamingData
            if 'url' not in stream and 'cipher' in stream:
                mixins.apply_descrambler(stream, 'cipher')
                stream['url'] = stream['cipher'][0]['url']
                stream['s'] = stream['cipher'][0]['s']


def ppytube_download(link, save_path=None):
    try:
        #object creation using YouTube which was imported in the beginning 
        yt = myYouTube(link, defer_prefetch_init=True)
        yt.prefetch()
        yt.init()
    except:
        sys.exit("Connection Error")

    if len(yt.streams.all()) == 0:
        sys.exit("No streams")

    try:
        print('{}'.format(yt.title))
        yt.streams.first().download()
    except:
        sys.exit("Download Failed!")

    print('Download Completed!')


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        link = input("Please input YouTube URL: ")
    else:
        link = sys.argv[1]

    ppytube_download(link)