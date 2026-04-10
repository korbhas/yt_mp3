# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-file Python CLI tool (`yt_mp3.py`) that downloads YouTube videos and converts them to MP3 using yt-dlp and FFmpeg.

## Prerequisites

- Python 3.10+ (uses `int | None` union syntax)
- FFmpeg must be installed and on PATH (required by yt-dlp for audio conversion)

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Download a video as MP3
python yt_mp3.py download <url> [-o OUTPUT_DIR] [-q BITRATE] [--max-duration SECONDS]
python yt_mp3.py dl <url>  # alias

# Show video info without downloading
python yt_mp3.py info <url>
```

## Architecture

Single module with three main functions:
- `get_info()` — fetches metadata via yt-dlp without downloading
- `download()` — downloads audio and converts to MP3 via FFmpeg postprocessor
- `info()` — prints metadata to stdout

CLI is built with `argparse` using subcommands (`download`/`dl`, `info`). Entry point is `main()` at the bottom of the file.
