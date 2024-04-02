"""Модуль для сохранения музыки из YouTube"""
import os
import re
import time
import logging
import asyncio
import yt_dlp

from tqdm import tqdm
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
                    retries += 1
                    result = func(*args, **kwargs)
                    if result:
                        return result
                except Exception as error:  # pylint: disable=broad-except
                    logging.warning(f'Попытка {retries} завершилась ошибкой: {error}')
                    time.sleep(10)

            if retries >= max_retries:
                logging.error('Сохранить целый файл не удалось\n')
                return None
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

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'logger': logging.getLogger(),
    }

    logging.getLogger("yt_dlp").setLevel(logging.WARNING)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        logging.info("Сведения о файле получены")

        audio_title = re.sub(r'\([^)]*\)', '', info['title']).strip('. ')
        audio_title = sanitize_filename(audio_title)
        logging.info("Имя исходного файла преобразовано")

        ydl_opts['postprocessors'][0]['preferredquality'] = '320'
        ydl_opts['outtmpl'] = os.path.join('data', audio_title)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        logging.info("Файл загружен")

    return os.path.join('data', f'{audio_title}.mp3')

@retry_on_error()
def rename_song(file_path: str) -> bool:
    """Функция, которая присваивает аудиофайлу название и имя исполнителя
    перемещает песню в папку named_songs если для песни найдены эти данные,
    иначе оставляет в прежней папке"""
    logging.info("Начинаю распознавать файл")
    if not os.path.exists('named_songs'):
        os.makedirs('named_songs')

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(recognize_song(file_path))

    if result:

        album = result.get('album', 'UnknownAlbum')
        artist = result.get('artist', 'UnknownArtist')
        title = result.get('song', 'UnknownTitle')
        genre = result.get('genre', 'UnknownGenre')
        year = result.get('year', 'UnknownYear')

        audio = AudioSegment.from_file(file_path, format='mp3')
        new_name = f'{title} - {artist}.mp3'
        new_name = sanitize_filename(new_name)
        logging.info("Имя файла перед сохранением преобразовано")
        audio.export(
            os.path.join('named_songs', new_name),
            format='mp3',
            tags={
                'title' : title,
                'artist': artist,
                'album' : album,
                'genre' : genre,
                'date'  : year,
                })
        os.remove(file_path)
        logging.info("Файл распознан и перемещен\n")
    else:
        logging.warning("Файл НЕ распознан и НЕ перемещен\n")
    return True

def main():
    """main-function"""
    with open('urls.txt', 'r', encoding='utf-8') as file:
        urls = file.readlines()

    regex = \
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]{11})'

    for index, url in tqdm(enumerate(urls, 1)):
        logging.info(f'Обрабатываю ссылку номер {index}')
        match = re.search(regex, url)
        if match:
            file_path = save_music(url=url)
            file_path = compare_audio_duration(file_path)
            if file_path:
                rename_song(file_path)
            else:
                pass
        else:
            logging.error(f"Ссылка номер {index} не является валидной\n")


logging.basicConfig(
    level=logging.INFO,
    filename="py_log.log",
    filemode="w",
    encoding="utf-8",
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if __name__ == '__main__':
    main()
