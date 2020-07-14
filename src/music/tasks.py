import re
import sys
import requests
from celery.exceptions import MaxRetriesExceededError
from config.celery import app
from music.models import Playlist
from .services.store_track import store_track
"""
Таски для Celery
"""


CLIENT_ID = "a3dd183a357fcff9a6943c0d65664087"
STREAM_URL = f"https://api.soundcloud.com/i1/tracks/{0}/streams?client_id={CLIENT_ID}"

"""
https://cf-media.sndcdn.com/TKL2d40kIJqK.128.mp3?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiKjovL2NmLW1lZGlhLnNuZGNkbi5jb20vVEtMMmQ0MGtJSnFLLjEyOC5tcDMiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE1OTI0NjM4NzF9fX1dfQ__&Signature=CWn-AXx~KrRyfSA~bB4M~ISFpZLVgX9~RnhZlo3T2clm6MEf7TfxYjm6gZIP4mqUPEdEystKenKkwdbOYc-QctISipKAJbWIsUKb8KFKcUuEd0RnJ65VK0~ofUZN6oTCLtGfEiDuS5M8WQSjLHHgYbvxSBUJdj8o6znIXjjKZsSQbbcbSoierafVvUbymo2~6ZNjypqi--0WWxoGIP~S8N6sM898Xm3I41JdgkoKhLryHIjbHWX9PLmEaOSi9c9Mlh7KNCI~qInJCCt9AJnmsDxbSNEP76WKSaw2917cAK2EldEcqc8-s9SX-maXGi3ELjjlJljanL3U1D5ScmMPDw__&Key-Pair-Id=APKAI6TU7MMXM5DG6EPQ
"""

def get_playlist_original_id(playlist_id):
    """
    Запускаем таски
    :param playlist_id:
    :return:
    """
    chain = fetch_page.s(playlist_id) | store_page_info.s(playlist_id)
    chain()


@app.task(bind=True, default_retry_delay=10 * 60, max_retries=3)
def fetch_page(self, playlist_id):
    """
    Получаем номер плейлиста

    :param self:
    :param playlist_id:
    :return:
    """
    playlist = Playlist.objects.get(id=playlist_id)
    try:
        page = requests.get(playlist.full_url)
    except requests.exceptions.ConnectionError as e:
        playlist.status = 'in_process'
        playlist.save()
        try:
            self.retry()
        except MaxRetriesExceededError:
            playlist.status = 'error'
            playlist.save()
    else:
        if page.status_code != 200:
            playlist.status = 'in_process'
            playlist.save()
            try:
                self.retry()
            except MaxRetriesExceededError:
                playlist.status = page.status_code
                playlist.save()
        elif page.status_code == 200:
            original_id = re.search(r'soundcloud://playlists:(.+?)"', page.text)
            return original_id.group(1)

    raise Exception('Ошибка очереди!')


@app.task(ignore_result=True)
def store_page_info(original_id, playlist_id):
    """
    Пишем номер полейлиста в базу
    :param original_id:
    :param playlist_id:
    :return:
    """
    playlist = Playlist.objects.get(id=playlist_id)
    playlist.original_id = original_id
    playlist.status = 'ready'
    playlist.save()


@app.task
def get_tracks_from_api_playlist():
    for playlist in Playlist.objects.filter(status='ready')[:1]:
        if playlist:
            playlist.status = 'in_process'
            playlist.save()

            playlist_url = f"https://api.soundcloud.com/playlists/{playlist.original_id}?representation=full&client_id={CLIENT_ID}"
            # TODO: try:
            json_playlist = requests.get(playlist_url).json()

            if store_track(json_playlist, playlist):
                playlist.status = 'done'
                playlist.save()
