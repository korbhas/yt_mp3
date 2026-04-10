#!/usr/bin/env python3
"""yt-mp3: Convert YouTube videos to MP3 from the command line."""

import argparse
import json
import sys
import os

import yt_dlp

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".yt-mp3.json")


def _load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_config(cfg: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f)


def get_info(url: str) -> dict:
    """Fetch video metadata without downloading."""
    opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        duration = info.get("duration", 0)
        m, s = divmod(duration, 60)
        return {
            "title": info.get("title", "Unknown"),
            "author": info.get("uploader", "Unknown"),
            "duration": f"{m}:{s:02d}",
            "duration_seconds": duration,
        }


def download(url: str, output_dir: str, quality: str, max_duration: int | None):
    """Download and convert a YouTube video to MP3."""
    # Fetch info first
    info = get_info(url)
    print(f"  Title:    {info['title']}")
    print(f"  Author:   {info['author']}")
    print(f"  Duration: {info['duration']}")

    if max_duration and info["duration_seconds"] > max_duration:
        print(f"\nSkipped: video is longer than {max_duration}s limit")
        sys.exit(1)

    _save_config({"last_output": output_dir})
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

    opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }
        ],
        "quiet": False,
        "no_warnings": True,
        "progress_hooks": [_progress_hook],
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    print("\nDone!")


def _progress_hook(d):
    if d["status"] == "downloading":
        pct = d.get("_percent_str", "?%").strip()
        speed = d.get("_speed_str", "?").strip()
        eta = d.get("_eta_str", "?").strip()
        sys.stdout.write(f"\r  Downloading: {pct} at {speed} ETA {eta}   ")
        sys.stdout.flush()
    elif d["status"] == "finished":
        print(f"\n  Converting to MP3...")


def info(url: str):
    """Show video info without downloading."""
    data = get_info(url)
    print(f"  Title:    {data['title']}")
    print(f"  Author:   {data['author']}")
    print(f"  Duration: {data['duration']}")


def main():
    parser = argparse.ArgumentParser(
        prog="yt-mp3",
        description="Convert YouTube videos to MP3",
    )
    sub = parser.add_subparsers(dest="command")

    # yt-mp3 download <url>
    p_dl = sub.add_parser("download", aliases=["dl"], help="Download as MP3")
    p_dl.add_argument("url", help="YouTube URL")
    default_output = _load_config().get("last_output", ".")
    p_dl.add_argument("-o", "--output", default=default_output, help=f"Output directory (default: {default_output})")
    p_dl.add_argument("-q", "--quality", default="192", help="MP3 bitrate (default: 192)")
    p_dl.add_argument("--max-duration", type=int, default=None, help="Max video length in seconds")

    # yt-mp3 info <url>
    p_info = sub.add_parser("info", help="Show video info")
    p_info.add_argument("url", help="YouTube URL")

    args = parser.parse_args()

    if args.command in ("download", "dl"):
        download(args.url, args.output, args.quality, args.max_duration)
    elif args.command == "info":
        info(args.url)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
