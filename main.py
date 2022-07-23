import os
import shutil
from pytube.contrib.playlist import Playlist
from pytube import YouTube
from pytube.cli import on_progress
import music_tag
import requests
from mutagen.mp4 import MP4, MP4Cover


def get_songs():
    with open("songs.txt", 'r') as file:
        lines = [line.strip() for line in file]
        return lines


def get_video_thumbnail(pic_url, song_title):
    with open(f'pics/{song_title[:-4]}.jpeg', 'wb') as handle:
        response = requests.get(pic_url, stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)


def set_artwork(title):
    video = MP4(f"music/{title}")
    with open(f"pics/{title[:-4]}.jpeg", "rb") as f:
        video["covr"] = [
            MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)
        ]

    video.save()


def rename_file_metadata(title):
    f = music_tag.load_file(f"music/{title}")
    try:
        artist, title = title.split("-")
    except ValueError:
        f['album'], f['albumartist'], f['artist'] = title[:-4], "Various artists", "Various artists"
    else:
        f['album'], f['albumartist'], f['artist'] = artist, artist, artist

    f.save()


def write_downloaded_songs(temp_list):
    with open('songs.txt', 'a') as file:
        for url in temp_list:
            file.write(f'{url}\n')


def move_file_to_itunes():
    music_dir_path = r"C:\Users\louis\Documents\dev\python\youtube_downloader\music"

    if len(os.listdir(music_dir_path)) == 0:
        return

    for count, filename in enumerate(os.listdir(music_dir_path)):
        original = r"C:\Users\louis\Documents\dev\python\youtube_downloader\music\{}".format(filename)
        target = r"C:\Users\louis\Music\iTunes\iTunes Media\Ajouter automatiquement à iTunes\{}".format(filename)

        shutil.move(original, target)
        print(f"Moving song n°{count + 1}")


def main():
    playlist = Playlist("https://www.youtube.com/playlist?list=PLR9die60_z5X38SvshrGRJMIYIHr0C8Hh")
    downloaded_songs = get_songs()
    videos_to_download = [video_url for video_url in playlist.video_urls if video_url not in downloaded_songs]
    temp_to_write = []

    print("Total new songs to download: ", len(videos_to_download))

    if videos_to_download:
        for count, video_url in enumerate(videos_to_download):
            try:
                yt = YouTube(video_url, on_progress_callback=on_progress)
                yt_complete_title = yt.title.replace("\"", '').replace("|", '').replace("\\", '').replace("/", '') + ".m4a"
                stream = yt.streams.get_highest_resolution()
                print(f"Downloading song n°{count + 1} of {len(videos_to_download)} - {yt.title}")
                stream.download(output_path="music/", filename=yt_complete_title)
                get_video_thumbnail(yt.thumbnail_url, yt_complete_title)
                set_artwork(yt_complete_title)
                rename_file_metadata(yt_complete_title)
                temp_to_write.append(video_url)
                move_file_to_itunes()
            except:
                print(f"there was a problem with song number {count + 1} ")
    if not videos_to_download:
        print("There is no new video in this youtube playlist since last time")

    write_downloaded_songs(temp_to_write)


if __name__ == '__main__':
    main()