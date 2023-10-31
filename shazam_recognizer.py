"""Вызываемый модуль для получения информации о песне"""
import asyncio
from shazamio import Shazam


async def recognize_song(file_path: str) -> tuple[str]|None:
    """Получает информацию о песне с помощью библиотеки shazamio"""
    shazam = Shazam()
    result = await shazam.recognize_song(file_path)
    track = result.get('track', None)
    return (track['sections'][0]['metadata'][0]['text'],
            track['title'],
            track['subtitle']) if track else None

def main(file_path):
    """main-function"""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(recognize_song(file_path))
    if result:
        album, song_title, artist_name = result
    loop.close()
    print(album, song_title, artist_name, sep='\n')


if __name__ == '__main__':
    main(r'data\Петропавловск - RADIO TAPOK.mp3')
