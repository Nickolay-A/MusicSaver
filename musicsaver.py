"""Модуль для сохранения музыки из YouTube"""
import os
import re
import yt_dlp

from yt_dlp.utils import DownloadError


def save_music(url: str) -> None:
    """Функция для схранения аудидорожки из видео на YouTube
    на вход принимает ссылку на виедо
    Имя выходного файла будет состоять из имени исходного видео
    скобки в названии видео (где чаще всего указвают инфу о видео) обрезаются"""
    if not os.path.exists('data'):
        os.makedirs('data')

    url = re.sub(r"[&].*", "", url)

    ydl = yt_dlp.YoutubeDL({
                            'format': 'bestaudio/best',
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192'
                            }]}
                        )
    try:
        info = ydl.extract_info(url, download=False)
    except DownloadError:
        print('Файл по данной ссылке не доступен')
        return None

    audio_title = re.sub(r'\([^)]*\)', '', info['title']).strip('. ')

    ydl = yt_dlp.YoutubeDL({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join('data', audio_title),
                }
            )

    with ydl:
        ydl.download([url])

    return None


if __name__ == '__main__':
    with open('urls.txt', 'r', encoding='utf-8') as file:
        urls = file.readlines()

    REGEX = \
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]{11})'

    for url_ in urls:
        match = re.search(REGEX, url_)
        if match:
            save_music(url=url_)
        else:
            print('Ссылка на явлется ссылкой на YouTube-видео.')
