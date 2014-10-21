Introduction
===================
This is a sample dummy provider for Pulsar.

**PLEASE NOTE THAT THIS IS SUBJECT TO CHANGE QUITE HEAVILY**

When Pulsar wants to find a stream for a media, it will call all the providers installed on the locally running XBMC instance.

To be recognized as a Pulsar provider, the addon's name has to start with `script.pulsar.`.

Pulsar will round up all the matching addons and call them using `XBMC.RunAddon()`.

Testing providers
=================

You can test your provider by calling Pulsar on these endpoints

```
http://localhost:10001/provider/<PROVIDER_ID>/movie/<IMDB_ID>
http://localhost:10001/provider/<PROVIDER_ID>/show/<TVDB_ID>/season/<SEASON>/episode/<EPISODE>
```

It will print the search payload and the return results, as interpreted by Pulsar.


Provider SDK
============

Pulsar ships with a provider SDK that unifies some of tasks commonly found in providers. For lack of PyDoc, we'll document this here for now.

To use this SDK, you must declare Pulsar as a dependency for your provider and import the module

```
<import addon="plugin.video.pulsar" version="0.2"/>
```

Then in your provider module:

```python
from pulsar import provider
```


The `provider` module
---------------------

```python
provider.ADDON
provider.ADDON_ID
provider.ADDON_NAME
```
The SDK gives you access to the `xbmcaddon.Addon` by default using these symbols.

---
```python
provider.register(search, search_movie, search_episode)
```
Registers your search methods to Pulsar. They can be either methods, or `None`.

- `search (func or None)` the generic search function
- `search_movie (func or None)` the search function for movies
- `search_episode (func or None)` the search function for episodes

---
```python
provider.HEAD(url, params={}, headers={}, data=None, with_cookies=False)
provider.GET(url, params={}, headers={}, data=None, with_cookies=False)
provider.POST(url, params={}, headers={}, data=None, with_cookies=False)
provider.PUT(url, params={}, headers={}, data=None, with_cookies=False)
provider.DELETE(url, params={}, headers={}, data=None, with_cookies=False)
```
Performs a HTTP `HEAD`/`GET`/`POST`/`PUT`/`DELETE` request. Note that these functions already provide `gzip` decoding and `User-Agent` spoofing.

- `url (string)` the url to send the request to
- `params (dict)` the url query parameters that would go after `?`
- `headers (dict)` custom headers to send with the request
- `data (string)` adds a body payload (and turns the request to a `POST` by default)
- `with_cookies (bool)` if you want to enable cookies support, set this to `True`, cookies can later be accessed with `provider.COOKIE_JAR`

Returns a standard `urllib2.Reponse` with 2 added methods:

- `json()` parses the body as json, returns `dict`
- `xml()` parses the body as XML, returns `xml.etree.ElementTree.Element`

---
```python
provider.extract_magnets(data)
```
Extracts magnet links from a `string`, using regular expression.

Returns a `list` of torrent `dict`.

---
```python
provider.parse_rss(root)
```
Parses a RSS DOM.

- `root (xml.etree.ElementTree.Element)` root node to the RSS stream

Returns a `list` of torrent `dict`.

---
```python
urllib.quote(string[, safe])
urllib.quote_plus(string[, safe])
urllib.urlencode(query[, doseq])
```
These are [the standard `urllib` methods](https://docs.python.org/2/library/urllib.html#urllib.quote) provided here for conveniency (and maybe later lazy loading).

---
```python
provider.notify(message='', header=None, time=5000, image='')
```
Sends a XBMC notification.

- `message (string)` the message to display
- `header (string, optional)` the message title, it will default to your addon name
- `time (int, optional)` how long to display the notification in milliseconds
- `image (string, optional)` the associated icon to display

---
```python
provider.append_headers(uri, headers)
```
Appends headers after a `uri` for Pulsar to use when downloading non magnets, if needed.

- `uri (string)` the uri
- `headers (dict)` custom headers

Returns a `string` containing the modified `uri`.

Logging
-------

The provider SDK provides logging capabilities. Just use the `provide.log` which is a standard python `logging.Logger` object.

Note that if `message` is not a `string`, it will be sent to `repr()`.

```python
provider.log.debug(message)
provider.log.info(message)
provider.log.warning(message)
provider.log.error(message)
provider.log.critical(message)
```


Result objects
==============

Pulsar expects provider to return a `list` of `dict`s with the following keys:

```json
{
	"name": string
	"uri": string
	"info_hash": string
	"trackers": [string, ...]
	"size": int
	"seeds": int
	"peers": int
	"resolution": int
	"video_codec": int
	"audio_codec": int
	"rip_type": int
	"scene_rating": int
	"language": string (ISO 639-1)
}
```

Pulsar needs to now about uniqueness. This is why Pulsar needs to know about the `info_hash`. Pulsar has several options to know it:

- you provide it yourself by setting `info_hash`
- you set `uri` to a magnet link
- Pulsar will download the `.torrent` file and figure it out itself

Keep in mind the 3rd options is potentially costly if there are lots of results (although it is not counted in the provider timeout). This step is called *resolving*.

If your file needs custom headers to be resolved, you can add headers (cookies etc...) to the URI *a-la* XBMC, like so:

```
http://foo.bar/myfile.torrent|User-Agent=I can have spaces|Cookies=ABCD;
```

Or even better, use `provider.append_headers`:

```python
myfile["uri"] = provider.append_headers(myfile["uri"], {
	"User-Agent": "I can have spaces",
	"Cookies": "ABCD;",
})
```

Finally, there is no use to send more than a page worth of links to Pulsar, as they are supposed to be relevant anyway.



About quality and availability
------------------------------

When deciding which stream to choose, Pulsar tries to be smart and make a balance between quality and availability. For that reason it is crucial that you properly set the quality settings in your object if you have them (`resolution`, `video_codec`, `audio_codec`, `rip_type` and `scene_rating`). See `provider.py` for the possible values.

If you don't set them, Pulsar will try to guess them from the `name`.


Query payload
=============

Pulsar tries to give you the most it can for your provider to make an informed decision when giving back streams.

About backward compatibility
----------------------------

If possible, if changes are made to the payloads, we will add keys, not remove them, to ensure backward compatibility. This might not be possible, but that's the goal anyway.

About title normalisation
-------------------------

All the titles sent in payloads are normalized (accents, special characters, punctuation are removed, lowercase...).

Movie payload
-------------

Here is a sample movie payload

```python
{
    "imdb_id": "tt1254207",
    "title": "big buck bunny",
    "year": 2008,
    "titles": {
        "es": "el gran conejo",
        "nl": "peach open movie project",
        "ru": "большои кролик",
        "us": "big buck bunny short 2008"
    }
}
```

Note that an IMDB id is the best way to search for a movie. If you can't use that, a title + year is a good differentiator, too.

Pulsar will also give you international titles for the movie you're searching. Note that these are *countries* and **not** languages (ISO 3166-1).


Episode payload
---------------

Here is a sample episode payload

```python
{
    "imdb_id": "tt0092400",
    "tvdb_id": "76385",
    "title": "married with children",
    "season": 1,
    "episode": 1,
    "titles": null
}
```

Conclusion
==========

Hopefully you have everything you need to know to write good providers. Don't hesitate to ping @pulsarhq on Twitter.
