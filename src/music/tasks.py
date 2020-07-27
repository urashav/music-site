import re
import sys
import requests
from celery.exceptions import MaxRetriesExceededError
from config.celery import app
from music.models import Playlist, Keywords
from .services.store_track import store_track
from .services.store_playlist import store_playlist
from django.db.models import Q

"""
Таски для Celery
"""

CLIENT_ID = "a3dd183a357fcff9a6943c0d65664087"
STREAM_URL = f"https://api.soundcloud.com/i1/tracks/{0}/streams?client_id={CLIENT_ID}"

"""
https://cf-media.sndcdn.com/TKL2d40kIJqK.128.mp3?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiKjovL2NmLW1lZGlhLnNuZGNkbi5jb20vVEtMMmQ0MGtJSnFLLjEyOC5tcDMiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE1OTI0NjM4NzF9fX1dfQ__&Signature=CWn-AXx~KrRyfSA~bB4M~ISFpZLVgX9~RnhZlo3T2clm6MEf7TfxYjm6gZIP4mqUPEdEystKenKkwdbOYc-QctISipKAJbWIsUKb8KFKcUuEd0RnJ65VK0~ofUZN6oTCLtGfEiDuS5M8WQSjLHHgYbvxSBUJdj8o6znIXjjKZsSQbbcbSoierafVvUbymo2~6ZNjypqi--0WWxoGIP~S8N6sM898Xm3I41JdgkoKhLryHIjbHWX9PLmEaOSi9c9Mlh7KNCI~qInJCCt9AJnmsDxbSNEP76WKSaw2917cAK2EldEcqc8-s9SX-maXGi3ELjjlJljanL3U1D5ScmMPDw__&Key-Pair-Id=APKAI6TU7MMXM5DG6EPQ

https://api-v2.soundcloud.com/search/playlists_without_albums?q=russian&sc_a_id=a674aaeac948cbaf191091fd2becb346700c71b3&variant_ids=1933&facet=genre&user_id=205566-30266-370477-883383&client_id=qRWH2RsvPGYONh3ogLQUj1zRUE6CTmDq&limit=10&offset=10000&linked_partitioning=1&app_version=1593700229&app_locale=en
"""


@app.task(bind=True, default_retry_delay=10 * 60, max_retries=3)
def get_playlists_from_keywords(self):
    for keyword in Keywords.objects.filter(Q(status='new') | Q(status='in_process'))[:1]:
        api_url = f"https://api-v2.soundcloud.com/search/playlists_without_albums?q={keyword.keyword}&sc_a_id=a674aaeac948cbaf191091fd2becb346700c71b3&variant_ids=1933&facet=genre&user_id=205566-30266-370477-883383&client_id=qRWH2RsvPGYONh3ogLQUj1zRUE6CTmDq&limit={keyword.limit}&offset={keyword.offset}&linked_partitioning=1&app_version=1593700229&app_locale=en"
        json_playlist = requests.get(api_url).json()

        keyword.total_results = json_playlist.get('total_results')
        keyword.save()

        if not json_playlist['collection'] and json_playlist['total_results'] > keyword.offset + keyword.limit:
            keyword.status = 'error'
            keyword.save()
            return False
        elif not json_playlist['collection'] and json_playlist['total_results'] <= keyword.offset + keyword.limit:
            keyword.status = 'done'
            keyword.save()
            return True
        elif store_playlist(json_playlist):
            keyword.offset = keyword.offset + keyword.limit
            keyword.status = 'in_process'
            keyword.save()
            return True


@app.task(bind=True, default_retry_delay=10 * 60, max_retries=3)
def get_playlist_original_id(self):
    """
        Запускаем таски
        :param playlist_id:
        :return:
        """
    for playlist in Playlist.objects.filter(status='new')[:1]:
        chain = fetch_page.s(playlist.id) | store_page_info.s(playlist.id)
        chain()


@app.task(bind=True, default_retry_delay=10 * 60, max_retries=3)
def fetch_page(self, playlist_id):
    """
    Получаем номер плейлиста

    :param self:
    :param playlist_id:
    :return:
    """
    playlist = Playlist.objects.get(pk=playlist_id)
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
