tidyspotipy
===========

[![Build Status](https://travis-ci.org/machow/tidyspotify.svg?branch=master)](https://travis-ci.org/machow/tidyspotify)

Installing
----------

```
pip install tidyspotify
```

Examples
-------

```
import os
os.environ['SPOTIPY_CLIENT_ID'] = <<YOUR_ID_HERE>>
os.environ['SPOTIPY_CLIENT_SECRET'] = <<YOUR_SECRET_HERE>>

from tidyspotify import get_artist_audio_features

get_artist_audio_features('The Beatles')
```

Note: you currently need to set the client id and secret as environment variables **before** importing tidyspotify.
