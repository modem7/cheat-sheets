# ffmpeg
`ffmpeg` converts, trims, scales and re-encodes audio and video; `ffprobe` inspects media files. Syntax is `ffmpeg [input options] -i INPUT [output options] OUTPUT`, and options apply to the next file named after them. Pair it with [yt-dlp](yt-dlp.md) for downloading media.

Documentation: [ffmpeg docs](https://ffmpeg.org/ffmpeg.html), [H.264 guide](https://trac.ffmpeg.org/wiki/Encode/H.264), [H.265 guide](https://trac.ffmpeg.org/wiki/Encode/H.265)

## Install
COMMAND | DESCRIPTION
---|---
`sudo apt install ffmpeg` | Ubuntu / Debian
`brew install ffmpeg` | macOS ([Homebrew](../macos/homebrew.md))
`winget install Gyan.FFmpeg` | Windows ([winget](../windows/winget.md))
`ffmpeg -version` | Show version and build flags
`ffmpeg -encoders \| grep -i x26` | List available encoders (also `-decoders`, `-formats`, `-hwaccels`)

## Everyday Conversions
COMMAND | DESCRIPTION
---|---
`ffmpeg -i in.mkv out.mp4` | Convert; ffmpeg picks codecs from the extension (re-encodes)
`ffmpeg -i in.mkv -c copy out.mp4` | Change container only, no re-encode (fast, lossless)
`ffmpeg -i in.mp4 -c:v copy -c:a aac -b:a 192k out.mp4` | Copy video, re-encode audio
`ffmpeg -i in.mov -vf scale=1280:-2 out.mp4` | Scale to 1280 wide, keep aspect (`-2` keeps height even)
`ffmpeg -i in.mp4 -vf scale=-2:720 out.mp4` | Scale to 720p tall
`ffmpeg -i in.mp4 -r 30 out.mp4` | Change frame rate
`ffmpeg -i in.mp4 -vf "transpose=1" out.mp4` | Rotate 90 degrees clockwise
`ffmpeg -i in.mp4 -an out.mp4` | Drop the audio track
`ffmpeg -y -i in.mkv out.mp4` | Overwrite the output without asking (`-n` never overwrites)
`ffmpeg -hide_banner -loglevel error -i in.mkv out.mp4` | Quiet output for scripts
`ffmpeg -i in.mkv -map 0 -c copy out.mkv` | Keep every stream (video, all audio, subtitles)
`ffmpeg -i in.mkv -map 0:v -map 0:a:1 -c copy out.mkv` | Pick streams: video plus the second audio track

## Trim and Cut
COMMAND | DESCRIPTION
---|---
`ffmpeg -ss 00:01:30 -to 00:02:45 -i in.mp4 -c copy out.mp4` | Cut a clip without re-encoding (snaps to keyframes)
`ffmpeg -ss 00:01:30 -i in.mp4 -t 30 out.mp4` | 30 seconds from 1:30, re-encoded, frame accurate
`ffmpeg -i in.mp4 -ss 90 -t 30 -c copy out.mp4` | Same as above using seconds
`ffmpeg -sseof -10 -i in.mp4 -c copy out.mp4` | Last 10 seconds

`-ss` before `-i` seeks quickly; with `-c copy` the cut lands on the nearest earlier keyframe, so re-encode when you need exact frames.

## Audio
COMMAND | DESCRIPTION
---|---
`ffmpeg -i in.mp4 -vn -c:a copy out.m4a` | Extract audio without re-encoding (check the codec first)
`ffmpeg -i in.mp4 -vn -c:a libmp3lame -q:a 2 out.mp3` | Extract to VBR MP3 (`-q:a 0` best to `9` smallest)
`ffmpeg -i in.wav -c:a flac out.flac` | Lossless FLAC
`ffmpeg -i in.mp3 -c:a libopus -b:a 96k out.opus` | Opus at 96 kbit/s
`ffmpeg -i in.mp4 -af loudnorm out.mp4` | Normalise loudness (EBU R128, single pass)
`ffmpeg -i in.mp4 -af volume=1.5 out.mp4` | Raise volume by 50%
`ffmpeg -i video.mp4 -i audio.m4a -map 0:v -map 1:a -c copy -shortest out.mp4` | Replace or add an audio track

## Encoding: x264, x265, AV1
Lower CRF means higher quality and a bigger file. Slower presets compress better at the same quality.

CODEC | EXAMPLE | NOTES
---|---|---
H.264 | `ffmpeg -i in.mkv -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 160k out.mp4` | CRF 18 to 28, default 23; widest compatibility
H.265 | `ffmpeg -i in.mkv -c:v libx265 -crf 24 -preset medium -tag:v hvc1 -c:a copy out.mp4` | CRF 28 is about x264 CRF 23; `-tag:v hvc1` helps Apple players
AV1 (SVT) | `ffmpeg -i in.mkv -c:v libsvtav1 -crf 32 -preset 6 -c:a libopus out.mkv` | CRF 0 to 63, preset 0 (slow) to 13 (fast)
AV1 (libaom) | `ffmpeg -i in.mkv -c:v libaom-av1 -crf 30 -b:v 0 -cpu-used 4 out.mkv` | Slow; `-b:v 0` enables constant quality
VP9 | `ffmpeg -i in.mkv -c:v libvpx-vp9 -crf 31 -b:v 0 out.webm` | Web friendly
Web stream | `ffmpeg -i in.mkv -c:v libx264 -crf 22 -pix_fmt yuv420p -movflags +faststart out.mp4` | `faststart` moves metadata up front for playback while downloading

Available encoders depend on how your ffmpeg was built; check with `ffmpeg -encoders`.

## Hardware Acceleration
Hardware encoders are much faster but give larger files than x264/x265 at the same quality. Use `-cq`/`-global_quality`/`-qp` rather than `-crf`.

HARDWARE | EXAMPLE
---|---
NVIDIA NVENC | `ffmpeg -hwaccel cuda -i in.mkv -c:v hevc_nvenc -preset p5 -cq 28 -c:a copy out.mkv`
Intel QSV | `ffmpeg -hwaccel qsv -i in.mkv -c:v h264_qsv -global_quality 23 out.mp4`
VA-API (Intel/AMD, Linux) | `ffmpeg -vaapi_device /dev/dri/renderD128 -i in.mkv -vf 'format=nv12,hwupload' -c:v h264_vaapi -qp 23 out.mp4`
AMD AMF (Windows) | `ffmpeg -i in.mkv -c:v h264_amf -quality balanced out.mp4`
Apple VideoToolbox | `ffmpeg -i in.mkv -c:v hevc_videotoolbox -q:v 60 out.mp4`

Codec names follow `h264_`, `hevc_` or `av1_` plus the API. List support with `ffmpeg -hwaccels` and `ffmpeg -encoders | grep -E 'nvenc|qsv|vaapi'`. For containers, pass `/dev/dri` through (see [Docker-Compose](../docker/docker-compose.md)).

## Concatenate
Same codecs and parameters in every file: use the concat demuxer.
```bash
printf "file '%s'\n" part1.mp4 part2.mp4 part3.mp4 > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4
```
Different codecs or sizes: use the concat filter (re-encodes).
```bash
ffmpeg -i a.mp4 -i b.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" out.mp4
```

## GIF and Images
COMMAND | DESCRIPTION
---|---
`ffmpeg -i in.mp4 -vf "fps=12,scale=480:-1:flags=lanczos" out.gif` | Quick GIF (poor palette)
`ffmpeg -i in.mp4 -vf "fps=12,scale=480:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" out.gif` | GIF with a generated palette (better quality)
`ffmpeg -ss 5 -i in.mp4 -frames:v 1 shot.png` | One screenshot at 5 seconds
`ffmpeg -i in.mp4 -vf fps=1 frame_%04d.png` | One frame per second to PNGs
`ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p out.mp4` | Images to video
`ffmpeg -i in.mp4 -vf "thumbnail,scale=320:-1" -frames:v 1 thumb.jpg` | Pick a representative frame

## Subtitles
COMMAND | DESCRIPTION
---|---
`ffmpeg -i in.mkv -map 0:s:0 subs.srt` | Extract the first subtitle track to SRT
`ffmpeg -i in.mp4 -i subs.srt -c copy -c:s mov_text out.mp4` | Add soft subtitles to MP4
`ffmpeg -i in.mp4 -i subs.srt -c copy -c:s srt out.mkv` | Add soft subtitles to MKV
`ffmpeg -i in.mp4 -vf "subtitles=subs.srt" out.mp4` | Burn subtitles into the picture (re-encodes)
`ffmpeg -i in.mkv -vf "subtitles=in.mkv:si=1" out.mp4` | Burn in the second embedded subtitle track
`ffmpeg -i in.mp4 -i subs.srt -map 0 -map 1 -c copy -metadata:s:s:0 language=eng out.mkv` | Tag the subtitle language

Image-based subtitles (PGS, VobSub) cannot be converted to SRT without OCR.

## ffprobe
COMMAND | DESCRIPTION
---|---
`ffprobe in.mp4` | Human-readable summary of streams
`ffprobe -v error -show_format -show_streams in.mp4` | Full detail
`ffprobe -v error -print_format json -show_format -show_streams in.mp4` | JSON output, pipe to [jq](jq.md)
`ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -of csv=p=0 in.mp4` | Video codec, size and frame rate
`ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 in.mp4` | Duration in seconds
`ffprobe -v error -select_streams a -show_entries stream=index,codec_name:stream_tags=language -of csv=p=0 in.mkv` | Audio tracks and languages

## Batch Examples
```bash
# Convert every MKV in a folder to MP4 (H.264/AAC)
for f in *.mkv; do ffmpeg -n -i "$f" -c:v libx264 -crf 22 -c:a aac "${f%.mkv}.mp4"; done
```
```powershell
# PowerShell equivalent
Get-ChildItem *.mkv | ForEach-Object { ffmpeg -n -i $_.FullName -c:v libx264 -crf 22 -c:a aac "$($_.BaseName).mp4" }
```
In a `while read` loop add `-nostdin` to ffmpeg, otherwise it swallows the loop's standard input.

## Not Verified
Commands were written from the official documentation and not executed. Hardware encoder flags depend on drivers and the ffmpeg build.
