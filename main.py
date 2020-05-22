import os
import json
import subprocess
import logging
import urllib.parse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


options = Options()
# options.headless = True
driver = webdriver.Firefox(options=options)


with open("./example_song_list.txt", "r") as f:
    songs = []
    for line in f.readlines():
        title, artist = line.strip().split("|")
        songs.append((title, artist))

    for song in songs:
        query = f"{song[0]} {song[1]}"
        print(query)

        url = "https://music.youtube.com/search?" + urllib.parse.urlencode({"q": query})

        content_loaded = False  # indicates if the url had been updated to show the correct url to pass to youtube-dl (aka the one containing the video id)

        while content_loaded != True:
            driver.get(url)
            buttons = None

            while buttons is None or len(buttons) == 0:
                sleep(1)
                buttons = driver.find_elements_by_class_name(
                    "ytmusic-chip-cloud-chip-renderer"
                )
                print("======================")

            sleep(3)
            filter_by_songs = None
            for button in buttons:
                if "Songs" in button.text:
                    filter_by_songs = button
                    content_loaded = True
            if filter_by_songs is None:
                content_loaded = False

            filter_by_songs.click()
            sleep(2)

            css_selector = "ytmusic-responsive-list-item-renderer.style-scope:nth-child(1) > div:nth-child(2) > ytmusic-item-thumbnail-overlay-renderer:nth-child(5) > div:nth-child(2) > ytmusic-play-button-renderer:nth-child(1) > div:nth-child(1) > yt-icon:nth-child(1)"

            res = driver.find_element_by_css_selector(css_selector)

            res.click()

            song_url = driver.current_url

            if "watch" not in song_url:
                content_loaded = False
            print(f"========================{song_url}======================")

        pos = song_url.find("&list")
        if pos != -1:
            song_url = song_url[:pos]

        try:
            subprocess.run(
                [
                    "youtube-dl",
                    "-f",
                    "bestaudio",
                    "--extract-audio",
                    "--audio-format",
                    "mp3",
                    "--audio-quality",
                    "0",
                    song_url,
                ],
                check=True,
            )
        except:
            pass  # @todo log error
