"""Модуль для сохранения музыки из YouTube"""
import os
import re
import time
import asyncio
import yt_dlp

from yt_dlp.utils import DownloadError
from pydub import AudioSegment
from mutagen.mp3 import MP3
from shazam_recognizer import recognize_song


def compare_audio_duration(file_path: str) -> bool|str:
    """служебная функция для проверки целостности mp3 файла
    если файл не удалось открыть - возникает исключение
    если файл не проигрывается полностью (разность в заявленной 
    и фактической продолжительности больше 1 сек) - вернет False
    иначе вернет имя файла
    """
    audio = MP3(file_path)
    declared_duration = audio.info.length
    audio_data = AudioSegment.from_file(file_path, format="mp3")
    actual_duration = len(audio_data) / 1000

    if abs(declared_duration - actual_duration) < 1:
        return file_path
    else:
        return False

def sanitize_filename(filename: str) -> str:
    """функция для очистки имени файла"""
    sanitized_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized_filename = sanitized_filename.strip()
    return sanitized_filename

def retry_on_error(max_retries=3):
    """функция-декоратор для повторного использования вложенной функции
    если вложенная функция вернула False или возникло исключение - она будет вызвана еще раз
    количество раз по умолчанию равно 3
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0

            while retries < max_retries:
                try:
                    result = func(*args, **kwargs)
                    if result:
                        break
                except Exception as error:  # pylint: disable=broad-except
                    print(f'Попытка {retries + 1} завершилась ошибкой: {error}')
                    retries += 1
                    time.sleep(1)

            if retries >= max_retries:
                print('Сохранить целый файл не удалось')
                return None

            return result
        return wrapper
    return decorator

@retry_on_error()
def save_music(url: str) -> bool|str:
    """функция для сохранения аудиодорожки из видео на YouTube
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
    audio_title = sanitize_filename(audio_title)

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

    return compare_audio_duration(os.path.join('data', f'{audio_title}.mp3'))

def rename_song(file_path: str) -> None:
    """Функция, которая присваивает аудиофайлу название и имя исполнителя
    перемещает песню в папку named_songs если для песни найдены эти данные,
    иначе оставляет в прежней папке"""
    if not os.path.exists('named_songs'):
        os.makedirs('named_songs')

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(recognize_song(file_path))

    if result:
        album, song_title, artist_name = result
        audio = AudioSegment.from_file(file_path, format='mp3')
        new_name = f'{song_title} - {artist_name}.mp3'
        new_name = sanitize_filename(new_name)
        audio.export(os.path.join('named_songs', new_name),
                    format='mp3',
                    tags={'title': song_title,
                          'artist': artist_name,
                          'album': album})
        os.remove(file_path)

def logging(url: str) -> None:
    """функция для логирования. В случае, если какую-то из ссылок не
    удалось полностью обработать, она будет записана в файл log.txt"""
    with open('log.txt', 'a', encoding='utf-8') as file:
        file.write(url)

def main():
    """main-function"""
    with open('urls.txt', 'r', encoding='utf-8') as file:
        urls = file.readlines()

    regex = \
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]{11})'

    for index, url in enumerate(urls, 1):
        print(f'Обрабатываю ссылку номер {index} из {len(urls)}')
        match = re.search(regex, url)
        if match:
            file_path = save_music(url=url)
            if file_path:
                rename_song(file_path)
            else:
                logging(url)
        else:
            print('Ссылка на явлется ссылкой на YouTube-видео.')
            logging(url)


if __name__ == '__main__':
    main()
