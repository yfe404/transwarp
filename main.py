from __future__ import unicode_literals

import os
import json
import logging
import requests
import urllib.parse
import youtube_dl
import json
from retrying import retry

from config import youtube_config

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)



def find_song_url(query):
    """
    Use Selenium to go to YouTube Music and search for a song

    :param query: The query describing the song to look for (exemple artist and title)
    :return: The URL of the song on YouTube Music to be sent to youtube-dl
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Language': 'en-US,en;q=0.5',
        'Origin': 'null',
        'Connection': 'keep-alive',
        'Cookie': 'categories=general; language=en-US; locale=en; autocomplete=; image_proxy=; method=POST; safesearch=0; theme=oscar; results_on_new_tab=0; doi_resolver=oadoi.org; oscar-style=logicodev; disabled_engines="btdigg__music\054mixcloud__music\054soundcloud__music\054invidious__music\054seedpeer__music\054deezer__music\054genius__music\054torrentz__music\054piratebay__music"; enabled_engines=; disabled_plugins=; enabled_plugins=; tokens=',
        'Upgrade-Insecure-Requests': '1'

    }

    data = f"category_general=1&{urllib.parse.urlencode({'q': query})}&pageno=1&time_range=None&language=en-US&format=json"

    url = "http://searx.titan/"
    r = requests.get(url, data, headers=headers)
    return r.json()["results"][0]["url"]

with open("./example_song_list.txt", "r") as f:
    songs = []
    for line in f.readlines():
        title, artist = line.strip().split("|")
        songs.append((title, artist))

    for song in songs:
        query = f"{song[0]} {song[1]}"

        song_url = find_song_url(query)
        pos = song_url.find("&list")
        if pos != -1:
            song_url = song_url[:pos]

        try:
            ydl_opts = youtube_config.get_youtube_config()
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([song_url])

        except Exception as e:
            print(e)  # @todo log error
