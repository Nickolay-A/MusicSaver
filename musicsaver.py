"""Модуль для сохранения музыки из YouTube"""
import os
import re
import yt_dlp


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

    info = ydl.extract_info(url, download=False)
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

    for url_ in urls:
        save_music(url=url_)
