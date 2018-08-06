__version__ = '0.0.1'

# TODO:
#    - automatic credential fetching. Renew stale creds.
#    - change all to_exclude parameters to to_keep, so is explicit / can use in docs.
#    - general handling of a name query versus URI (e.g. via a decorator)
#    - need to remove albums artists are only contributers to, or add field?

import pandas as pd
from functools import partial
from itertools import chain


# Utils ---------------------------------------------------------------------------------

def is_uri(s):
    return True


def exclude_fields(to_exclude, d):
    return {k: v for k, v in d.items() if k not in to_exclude}


def keep_fields(to_keep, d):
    return {k: v for k, v in d.items() if k in to_keep}


def row_filter(fields, exclude = True):
    f = exclude_fields if exclude else keep_fields
    return partial(f, frozenset(fields))


def prefix_merge(left, right, prefix, *args, **kwargs):
    """Merge two dataframes, but prefix rather than suffix shared cols"""
    shared = set(left.columns).intersection(set(right.columns))
    new_left  = left.rename(columns = {x: prefix[0] + x for x in shared})
    new_right = right.rename(columns = {x: prefix[1] + x for x in shared})
    return new_left.merge(new_right, *args, **kwargs)


# Client --------------------------------------------------------------------------------
# note: this currently takes the hacky approach of having all functions use the 
#       client (sp) defined here

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# API Main Entrypoint -------------------------------------------------------------------

def get_artist_audio_features(q):
    query = sp.search(q = q, type = "artist")
    items = query['artists']['items']
    artist = items[0] if items else None

    # get artist albums
    albums = get_artist_albums(artist['id'])

    # get album popularity
    album_popularity = get_album_popularity(albums.id)

    # get album tracks
    tracks = get_album_tracks(albums.id)

    # get track audio features
    features = get_track_features(tracks.id)

    # get track popularity
    popularity = get_track_popularity(tracks.id)

    album_data = albums.merge(album_popularity, 'left', 'id')

    track_data = tracks \
            .drop(columns = ['type']) \
            .merge(popularity, 'left', 'id') \
            .merge(features.drop(columns = ['uri', 'type', 'duration_ms']), 'left', 'id')


    return prefix_merge(album_data, track_data, ['album_', 'track_'], how = 'left', on = 'album_id')


# API Functions -------------------------------------------------------------------------

def get_artist_albums(
        artist_id, 
        to_exclude = ('available_markets', 'artists', 'external_urls', 'href', 
                      'images', 'type', 'uri', 'release_date_precision', 'album_group', 'total_tracks'),
        to_df = True
        ):
    """Return albums belonging to an artist.
    
    Arguments:
        artist_id: artist uri or an artist name to search
        to_exclude: fields to exclude from each row of data
        to_df: return a DataFrame rather than a list

    """
    # artist_name artist_uri   album_uri   album_name     album_img        album_type is_collaboration

    if not is_uri(artist_id):
        query = sp.search(q = artist_id, type = "artist")
        items = query['artists']['items']
        if not items:
            raise Exception("No artist matching search: %s" %artist_id)
        artist_id = items[0]['id']
    
    # TODO: pass args?
    albums = sp.artist_albums(artist_id)
    row_filter(['id'])
    items = albums['items']
    for entry in items:
        artist = entry['artists'][0]
        entry['artist_name'] = artist['name']
        entry['artist_uri'] = artist['uri']

    data = list(map(row_filter(to_exclude), items))
    return pd.DataFrame(data) if to_df else data


def get_album_popularity(album_ids, to_df = True):
    query = sp.albums(album_ids)
    
    data = list(map(row_filter(['id','popularity'], exclude = False), query['albums']))

    return pd.DataFrame(data) if to_df else data
    

def get_album_tracks(
        album_ids,
        to_exclude = ('artists', 'available_markets', 'external_urls', 'is_local', 'disc_number'),
        to_df = True
        ):
    
    items = chain.from_iterable(map(_get_album_tracks, album_ids))
    
    rows = list(map(row_filter(to_exclude), items))
    
    return pd.DataFrame(rows) if to_df else rows


def _get_album_tracks(album_id):
    items = sp.album_tracks(album_id)['items']
    for item in items:
        item['album_id'] = album_id
        yield item


def get_track_features(track_ids, to_df = True):
    tracks = []
    for ii in range(0, len(track_ids), 99):
        tracks.extend(sp.audio_features(track_ids[ii:ii+99]))
    
    return pd.DataFrame(tracks) if to_df else tracks


def get_track_popularity(track_ids, to_df = True):
    filter_entries = row_filter(['id', 'popularity'], exclude = False)
    
    tracks = []
    for ii in range(0, len(track_ids), 50):
        crnt_tracks = sp.tracks(track_ids[ii:ii+50]).get('tracks', [])
        tracks.extend(map(filter_entries, crnt_tracks))
    
    return pd.DataFrame(tracks) if to_df else tracks
