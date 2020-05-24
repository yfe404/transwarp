from __future__ import unicode_literals

import os
import json
import logging
import urllib.parse
import youtube_dl
from retrying import retry
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


options = Options()
# options.headless = True
driver = webdriver.Firefox(options=options)


class ContentNotFound(Exception):
    pass


@retry(stop_max_delay=30000)  ## 30 seconds
def find_song_url(query):
    """
    Use Selenium to go to YouTube Music and search for a song
    
    :param query: The query describing the song to look for (exemple artist and title)
    :return: The URL of the song on YouTube Music to be sent to youtube-dl
    """
    url = "https://music.youtube.com/search?" + urllib.parse.urlencode({"q": query})

    driver.get(url)
    buttons = None

    while buttons is None or len(buttons) == 0:
        buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "ytmusic-chip-cloud-chip-renderer")
            )
        )

    filter_by_songs = None
    for button in buttons:
        if "Songs" in button.text:
            filter_by_songs = button
    if filter_by_songs is None:
        raise ContentNotFound()

    filter_by_songs.click()

    css_selector = "ytmusic-responsive-list-item-renderer.style-scope:nth-child(1) > div:nth-child(2) > ytmusic-item-thumbnail-overlay-renderer:nth-child(5) > div:nth-child(2) > ytmusic-play-button-renderer:nth-child(1) > div:nth-child(1) > yt-icon:nth-child(1)"

    res = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )

    res.click()

    song_url = driver.current_url

    if "watch" not in song_url:
        raise ContentNotFound()

    return song_url


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

        class MyLogger(object):
            def debug(self, msg):
                pass

            def warning(self, msg):
                pass

            def error(self, msg):
                print(msg)

        def my_hook(d):
            if d["status"] == "finished":
                print("Done downloading, now converting ...")

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "logger": MyLogger(),
            "progress_hooks": [my_hook],
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([song_url])

        except Exception as e:
            print(e)  # @todo log error
