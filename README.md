Introduction
===================
This is a sample dummy provider for Pulsar.

**PLEASE NOTE THAT THIS IS SUBJECT TO CHANGE QUITE HEAVILY**

When Pulsar wants to find a stream for a media, it will call all the providers installed on the locally running XBMC instance.

To be recognized as a Pulsar provider, the addon's name has to start with `script.pulsar.`.

Pulsar will round up all the matching addons and call them using `XBMC.RunAddon()`.


Payload
=======
Pulsar will call your addon with a Base64 encoded JSON payload as first argument (`sys.argv[1]`).

Here's a sample payload:

```
{
	"method": "search_episode"
	"callback_url": "http://localhost:9001/callbacks/3404454616782090989"
	"args": [...]
}
```

Searching
---------
The `method` key can be one of three strings, on which the `args` value depends:

- `search`
- `search_movie`
- `search_episode`

Depending on the method, the `args` key will contains different arguments:

- `search(query string)`
- `search_episode(imdb_id, tvdb_id, name, season, episode)`
- `search_movie(imdb_id, name, year)`


The callback URL
----------------
The way for Pulsar to know about the provider results is via a callback URL that the provider has to call before a certain timeout (5s right now).

The callback URL expects a JSON body with the result payload.


The results payload
-------------------
The result payload is an array of found torrents objects.

The torrent object has the following schema:

```
{
	"name": string
	"uri": string
	"info_hash": string
	"trackers": [string, ...]
	"size": int
	"seeds": int
	"peers": int
}
```

Because Pulsar needs to know about uniqueness (via `info_hash`), availability (via `seeds` and `peers`) and quality (via `name` parsing), the torrent object has to be properly filled.

If `uri` is a magnet link, that's the only thing needed. Pulsar will figure all out by itself.

If not, you'll need to fill certain keys, so either:

- `name`, `info_hash` and `trackers`. Pulsar will connect to the trackers and figure out availability
- `name`, `info_hash`, `seeds` and `peers`


Once the list is complete, just send it to the callback URL.

Also, there is no use to send more than a page worth of links to Pulsar, as they are supposed to be relevant anyway.
