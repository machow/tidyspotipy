import tidyspotify
import yaml
import pytest
import tempfile
import os

from tidyspotify import get_artist_audio_features, default_login


ENV_KEYS = {
        'SPOTIPY_CLIENT_ID': 'client_id', 
        'SPOTIPY_CLIENT_SECRET': 'client_secret'
        }

@pytest.fixture(scope = "function")
def reset():
    prev_path = tidyspotify.CONFIG_PATH
    tidyspotify.default_client = None

    with tempfile.NamedTemporaryFile() as tf:
        tidyspotify.CONFIG_PATH = tf.name
        yield

    tidyspotify.CONFIG_PATH = prev_path


@pytest.fixture(scope = "function")
def env_creds():

    pop = lambda k: os.environ.pop(k) if k in os.environ else None
    prev_envs = {k: pop(k) for k in ENV_KEYS}

    yield prev_envs

    for k, v in prev_envs.items():
        os.environ[k] = v


def test_env_specified(env_creds):
    assert not any(os.environ.get(k) for k in env_creds)
    assert all(env_creds.values())

def test_login_with_env(reset):
    default_login()
    tidyspotify.default_client.search(q = "The Beatles", type = "artist")

def test_login_with_file(reset, env_creds):
    config = {ENV_KEYS[k]: v for k, v in env_creds.items()}
    with open(tidyspotify.CONFIG_PATH, 'w') as f:
        yaml.dump(config, f)
    default_login()

def test_query_columns(reset):
    data = get_artist_audio_features("Big Data")

