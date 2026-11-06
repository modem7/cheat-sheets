# yt-dlp
`yt-dlp` is a feature-rich command-line downloader for video and audio from YouTube and a large list of other sites (a maintained fork of youtube-dl). It needs [[ffmpeg]] to merge separate video and audio streams, convert audio and embed metadata. Only download content you have the right to.

Documentation: [yt-dlp README](https://github.com/yt-dlp/yt-dlp#readme), [supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## Install and Update
COMMAND | DESCRIPTION
---|---
`pipx install yt-dlp` | Install with pipx (or `uv tool install yt-dlp`)
`brew install yt-dlp` | macOS / Linux ([[homebrew]])
`winget install yt-dlp.yt-dlp` | Windows ([[winget]])
`yt-dlp -U` | Self-update (release binary installs only)
`pipx upgrade yt-dlp` | Update a pipx install
`yt-dlp --version` | Show version

Sites change often. If a download breaks, update first. The apt package is usually old; prefer pipx or the release binary.

## Basic Downloads
COMMAND | DESCRIPTION
---|---
`yt-dlp <URL>` | Download best quality
`yt-dlp -o "%(title)s.%(ext)s" <URL>` | Set the output file name
`yt-dlp -P ~/Videos <URL>` | Set the output directory
`yt-dlp -a urls.txt` | Download every URL listed in a file
`yt-dlp --no-playlist <URL>` | Only the video when the URL also points at a playlist
`yt-dlp -S "res:1080" <URL>` | Best quality up to 1080p
`yt-dlp --limit-rate 2M <URL>` | Cap download speed
`yt-dlp -N 4 <URL>` | Download fragments in parallel (4 connections)
`yt-dlp --write-subs --sub-langs en --embed-subs <URL>` | Fetch English subtitles and embed them
`yt-dlp --embed-metadata --embed-thumbnail <URL>` | Embed tags and cover image
`yt-dlp --sponsorblock-remove sponsor <URL>` | Cut SponsorBlock "sponsor" segments (needs ffmpeg)

## Formats
COMMAND | DESCRIPTION
---|---
`yt-dlp -F <URL>` | List available formats and their IDs
`yt-dlp -f 137+140 <URL>` | Specific video ID plus audio ID, merged
`yt-dlp -f "bv*+ba/b" <URL>` | Best video plus best audio, else best single file (the default)
`yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" <URL>` | Cap at 1080p
`yt-dlp -f "b[ext=mp4]" <URL>` | Best pre-merged MP4
`yt-dlp -S "vcodec:h264,res,acodec:m4a" <URL>` | Sort preference: H.264, resolution, then AAC audio
`yt-dlp --merge-output-format mkv <URL>` | Container for merged output (mp4, mkv, webm)
`yt-dlp --recode-video mp4 <URL>` | Re-encode to another container after download

`-S` (format sort) is usually easier than writing `-f` filters. Quote filters so the shell does not treat `[`, `<` or `&` specially.

## Audio Extraction
COMMAND | DESCRIPTION
---|---
`yt-dlp -x <URL>` | Extract audio in the best available format
`yt-dlp -x --audio-format mp3 --audio-quality 0 <URL>` | Convert to MP3, best VBR quality
`yt-dlp -x --audio-format flac <URL>` | Other targets: `m4a`, `opus`, `wav`, `aac`, `vorbis`
`yt-dlp -f ba -x --audio-format m4a --embed-thumbnail --embed-metadata <URL>` | Tagged audio file with cover art
`yt-dlp -x --split-chapters <URL>` | One audio file per chapter

## Playlists and Channels
COMMAND | DESCRIPTION
---|---
`yt-dlp <PLAYLIST_URL>` | Download the whole playlist
`yt-dlp -I 1:5 <PLAYLIST_URL>` | Items 1 to 5 (`-I 3,7,9` for specific ones, `-I -3:` for the last three)
`yt-dlp --playlist-reverse <PLAYLIST_URL>` | Oldest first
`yt-dlp --dateafter 20250101 <CHANNEL_URL>` | Only videos uploaded on or after a date (`--datebefore` too)
`yt-dlp --max-downloads 10 <CHANNEL_URL>` | Stop after 10 downloads
`yt-dlp --flat-playlist --print url <PLAYLIST_URL>` | List video URLs without downloading
`yt-dlp --flat-playlist -J <PLAYLIST_URL> \| jq '.entries[].title'` | Playlist metadata as JSON ([[jq]])
`yt-dlp --match-filters "duration>60 & !is_live" <URL>` | Skip short videos and livestreams
`yt-dlp -o "%(playlist)s/%(playlist_index)03d - %(title)s.%(ext)s" <PLAYLIST_URL>` | Folder per playlist, numbered files
`yt-dlp --ignore-errors <PLAYLIST_URL>` | Carry on past unavailable videos (`-i`)

## Output Templates
Templates use Python-style fields: `%(FIELD)s`, with formatting such as `%(playlist_index)03d`. Show every available field for a video with `yt-dlp -j <URL>`.

FIELD | MEANING
---|---
`%(title)s` | Video title
`%(id)s` | Video ID
`%(ext)s` | File extension
`%(uploader)s` / `%(channel)s` | Uploader or channel name
`%(upload_date)s` | `YYYYMMDD`
`%(upload_date>%Y-%m-%d)s` | Reformatted date
`%(playlist_title)s`, `%(playlist_index)s` | Playlist name and position
`%(height)sp` | Resolution such as `1080p`
`%(title).80B` | Title truncated to 80 characters

Useful patterns:
```bash
yt-dlp -o "%(uploader)s/%(upload_date>%Y-%m-%d)s - %(title)s [%(id)s].%(ext)s" <URL>
yt-dlp --restrict-filenames -o "%(title)s.%(ext)s" <URL>     # ASCII-only, no spaces
yt-dlp --windows-filenames <URL>                              # Safe on Windows and SMB shares
```
Use `-o` with `-P` (paths): `-P ~/Videos -P "temp:~/tmp"` puts in-progress files in a temp folder.

## Cookies and Login
Needed for age-restricted, members-only or private videos, and to avoid bot checks on some networks.

COMMAND | DESCRIPTION
---|---
`yt-dlp --cookies-from-browser firefox <URL>` | Read cookies from an installed browser (`chrome`, `edge`, `brave`, `safari`, ...)
`yt-dlp --cookies-from-browser chrome:Profile\ 1 <URL>` | A specific browser profile
`yt-dlp --cookies cookies.txt <URL>` | Use a Netscape-format cookies file
`yt-dlp -u <USER> -p <PASSWORD> <URL>` | Site login (supported on few sites; avoid putting passwords in shell history)
`yt-dlp --netrc <URL>` | Read credentials from `~/.netrc`

Treat cookie files as secrets: they grant access to your account. Keep them out of git and `chmod 600` them.

## Archive File
The download archive records the IDs of everything already fetched, so re-running a command only grabs new items.
```bash
yt-dlp --download-archive archive.txt <PLAYLIST_OR_CHANNEL_URL>
```
Each line is `<EXTRACTOR> <ID>`. Delete a line to download that video again. Combine with `--break-on-existing` to stop at the first video already in the archive (fast for "latest uploads" runs).

## Config File
Put one option per line in a config file. Lines starting with `#` are comments.

SYSTEM | USER CONFIG LOCATION
---|---
Linux / macOS | `~/.config/yt-dlp/config`
Windows | `%APPDATA%\yt-dlp\config`
Any | `yt-dlp.conf` next to the binary or in the current directory; or `--config-locations <PATH>`

Example:
```
# ~/.config/yt-dlp/config
-P ~/Videos/yt
-o "%(uploader)s/%(upload_date>%Y-%m-%d)s - %(title)s [%(id)s].%(ext)s"
-S "res:1080,vcodec:h264,acodec:m4a"
--merge-output-format mkv
--embed-metadata
--embed-thumbnail
--download-archive ~/Videos/yt/archive.txt
--no-mtime
```
Ignore config files for one run with `--ignore-config`. Check which options are active with `yt-dlp -v` (the first lines show loaded configs).

## Scheduled Downloads
```bash
# crontab -e: check a channel nightly, archive prevents duplicates
30 2 * * * /usr/local/bin/yt-dlp --download-archive /data/archive.txt -P /data/videos "<CHANNEL_URL>" >> /var/log/yt-dlp.log 2>&1
```
Docker users can run the same job in a container; see [[docker]].

## Troubleshooting
SYMPTOM | FIX
---|---
`HTTP Error 403` or "Sign in to confirm you're not a bot" | Update yt-dlp, then retry with `--cookies-from-browser`
No audio or video merged | Install ffmpeg and make sure it is on `PATH`
`Requested format is not available` | Run `-F` and pick from the list, or use `-S` instead of `-f`
Slow downloads | Add `-N 4`; some sites throttle regardless
Debug output for a bug report | `yt-dlp -v <URL>`

## Not Verified
Commands were written from the project README and not executed. Site behaviour and bot detection change frequently.
