"""Вызываемый модуль для получения информации о песне"""
import asyncio
from shazamio import Shazam


async def recognize_song(file_path: str) -> tuple[str]|None:
    """Получает информацию о песне с помощью библиотеки shazamio"""
    shazam = Shazam()
    result = await shazam.recognize_song(file_path)
    track = result.get('track', None)
    if track:
        title = track.get('title', 'UnknownTitle')
        subtitle = track.get('subtitle', 'UnknownSubtitle')
        sections = track.get('sections', [{},])
        if sections:
            metadata = sections[0].get('metadata', [{},])
            if metadata:
                album = metadata[0].get('text', 'UnknownAlbum')
            else:
                album = 'UnknownAlbum'
        else:
            album = 'UnknownAlbum'
    return (album, title, subtitle) if track else None

def main(file_path):
    """main-function"""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(recognize_song(file_path))
    if result:
        album, song_title, artist_name = result
    loop.close()
    print(album, song_title, artist_name, sep='\n')


if __name__ == '__main__':
    main(r'data\Мясной бор - RADIO TAPOK.mp3')
