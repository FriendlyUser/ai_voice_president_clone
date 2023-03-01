# Copied from https://huggingface.co/spaces/FriendlyUser/YoutubeDownloaderSubber/blob/main/app.py
import ffmpeg
from yt_dlp import YoutubeDL
import argparse
import json
from subprocess import PIPE, run

audio_folder = "audio"
youtube_livestream_codes = [
    91,
    92,
    93,
    94,
    95,
    96,
    300,
    301,
]
youtube_mp4_codes = [
    298,
    18,
    22,
    140,
    133,
    134
]

def second_to_timecode(x: float) -> str:
    hour, x = divmod(x, 3600)
    minute, x = divmod(x, 60)
    second, x = divmod(x, 1)
    millisecond = int(x * 1000.)

    return '%.2d:%.2d:%.2d,%.3d' % (hour, minute, second, millisecond)

# format float in 00:00:30 format
def format_timecode(x: float) -> str:
    hour, x = divmod(x, 3600)
    minute, x = divmod(x, 60)
    second, x = divmod(x, 1)
    millisecond = int(x * 1000.)

    return '%.2d:%.2d:%.2d' % (hour, minute, second)


def get_video_metadata(video_url: str = "https://www.youtube.com/watch?v=21X5lGlDOfg&ab_channel=NASA")-> dict:
    with YoutubeDL({'outtmpl': '%(id)s.%(ext)s'}) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get('title', None)
        uploader_id = info_dict.get('uploader_id', None)
        print(f"[youtube] {video_title}: {uploader_id}")
    return info_dict


def parse_metadata(metadata) -> str:
    """
    Parse metadata and send to discord.
    After a video is done recording, 
    it will have both the livestream format and the mp4 format.
    """
    # send metadata to discord
    formats = metadata.get("formats", [])
    # filter for ext = mp4
    mp4_formats = [f for f in formats if f.get("ext", "") == "mp4"]
    try:
        format_ids = [int(f.get("format_id", 0)) for f in mp4_formats]
        video_entries = sorted(set(format_ids).intersection(youtube_mp4_codes))

        if len(video_entries) > 0:
            # use video format id over livestream id if available
            selected_id = video_entries[0]
    except Exception as e:
        print(e)
        selected_id = mp4_formats[0].get("format_id")


    return selected_id

def get_video(url: str, config: dict):
    """
    Get video from start time.
    """
    # result = subprocess.run()
    # could delay start time by a few seconds to just sync up and capture the full video length
    # but would need to time how long it takes to fetch the video using youtube-dl and other adjustments and start a bit before
    filename = config.get("filename", "livestream01.mp4")
    end = config.get("end", "00:15:00")
    overlay_file = ffmpeg.input(filename)
    (
        ffmpeg
        .input(url, t=end)
        .output(filename)
        .run()
    )

def get_file_from_yurl(data: dict):
    url = data.get("url", "https://www.youtube.com/watch?v=f0UB06v7yLY&ab_channel=CNN")
    metadata = get_video_metadata(url)
    print(metadata)
    selected_id = parse_metadata(metadata)
    formats = metadata.get("formats", [])
    selected_format = [f for f in formats if f.get("format_id", "") == str(selected_id)][0]
    format_url = selected_format.get("url", "")
    filename = data.get("name", "trump") + ".mp4"
    get_video(format_url, {"filename": f"{filename}"})
    return filename

# make clips from videos


def main(args):
    filename = get_file_from_yurl(args)
    # perform clipping with ffmpeg
    # ffmpeg -i input.mp4 -ss 00:00:30 -to 00:00:40 -c copy output.mp4

    # iterate across clips
    clips = args.get("clips", [])
    for index, clip in enumerate(clips):
        start = clip.get("start", 0)
        end = clip.get("end", 10)
        name = clip.get("name", "clip")
        (
            ffmpeg
            .input(filename)
            .filter("trim", start=format_timecode(start), end=format_timecode(end))
            .output(f"{name}_{index}.mp4")
            .run()
        )

if __name__ == "__main__":
    # argparser to get url
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", type=str, help="Youtube URL", default="cfg/trump.json")
    args = parser.parse_args()
    # read file from args.cfg
    with open (args.cfg, "r") as f:
        cfg = json.load(f)
    main(cfg)
