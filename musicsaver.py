"""Модуль для сохранения музыки из YouTube"""
import os
import re
import time
import yt_dlp

from yt_dlp.utils import DownloadError
from pydub import AudioSegment
from mutagen.mp3 import MP3


def compare_audio_duration(file_path: str) -> bool:
    """Служебная функция для проверки целостности mp3 файла
    если файл не удалось открыть - возникает исключение
    если файл не проигрывается полностью (разность в заявленной 
    и фактической продолжительности больше 1 сек) - вернет False
    """
    audio = MP3(file_path)
    declared_duration = audio.info.length
    audio_data = AudioSegment.from_file(file_path, format="mp3")
    actual_duration = len(audio_data) / 1000

    if abs(declared_duration - actual_duration) < 1:
        return True
    else:
        return False

def retry_on_error(max_retries=3):
    """
    функция-декоратор для повторного использования вложенной функции
    если вложенная функция вернула False или воникло исклчение - она будет вызвана еще раз
    количество раз по умолчанию указано 3
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0

            while retries < max_retries:
                try:
                    result = func(*args, **kwargs)
                    if result:
                        break
                except Exception as error: # pylint: disable=broad-except
                    print(f'Попытка {retries + 1} завершилась ошибкой: {error}')
                    retries += 1
                    time.sleep(1)

            if retries >= max_retries:
                print('Сохранить целый файл не удалось')

            return result
        return wrapper
    return decorator

@retry_on_error()
def save_music(url: str) -> bool:
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

    return compare_audio_duration(os.path.join('data', f'{audio_title}.mp3'))


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
