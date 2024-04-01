"""модуль для проверки целостности и переименования существующих файлов
существующие файлы помещаются в папку data"""
import os
import logging

from tqdm import tqdm
from musicsaver import compare_audio_duration, rename_song


def main() -> None:
    """функция для проверки целостности и переименования существующих файлов
    существующие файлы помещаются в папку data
    'main-function' """
    folder_path = 'data'
    music_files = [
        os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.mp3')
    ]

    for index, file_path  in tqdm(enumerate(music_files, 1)):
        logging.info(f'Обрабатываю файл номер {index}')
        flag = None
        try:
            flag = compare_audio_duration(file_path)
        except Exception:  # pylint: disable=broad-except
            logging.error('Целостность файла нарушена\n')
        if flag:
            rename_song(file_path)


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
