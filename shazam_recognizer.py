"""Вызываемый модуль для получения информации о песне"""
import asyncio
from shazamio import Shazam


async def recognize_song(file_path: str) -> tuple[str]|None:
    """Получает информацию о песне с помощью библиотеки shazamio"""
    shazam = Shazam()
    result = await shazam.recognize_song(file_path)
    track = result.get('track', None)
    return (track['title'], track['subtitle']) if track else None

def main(file_path):
    """main-function"""
    loop = asyncio.get_event_loop()
    song_title, artist_name = loop.run_until_complete(recognize_song(file_path))
    print(song_title, artist_name, sep='\n')


if __name__ == '__main__':
    main(r'data\Павел Пламенев - Ночь перед боем.mp3')
