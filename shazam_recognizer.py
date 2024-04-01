"""Вызываемый модуль для получения информации о песне"""
import os
import pprint
import asyncio

from shazamio import Shazam


async def recognize_song(file_path: str) -> dict:
    """Получает информацию о песне с помощью библиотеки shazamio"""
    shazam = Shazam()
    result = await shazam.recognize_song(file_path)
    track = result.get('track', None)
    album_info = dict()
    if track:
        sections = track.get('sections', [])
        metadata = sections[0].get('metadata', [])
        for item in metadata:
            if item['title'] == 'Album':
                album_info['album'] = item.get('text', '')

            if item['title'] == 'Released':
                album_info['year'] = item.get('text', '')

        metapages = sections[0].get('metapages',[])
        album_info['song'] = metapages[1].get('caption', '')
        album_info['artist'] = metapages[0].get('caption', '')

        genres = track.get('genres',{}).get('primary','')
        album_info['genre'] = genres

        return album_info

def main(file_path):
    """main-function"""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(recognize_song(file_path))
    pprint.pprint(result)


if __name__ == '__main__':
    for file in os.listdir(r'.\data'):
        main(os.path.join(r'.\data', file))
