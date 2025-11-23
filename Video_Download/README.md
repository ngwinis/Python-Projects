# VIDEO DOWNLOADER BY PYTHON

## Getting Started
This project helps you download any video with an URL:
- Link download
- Youtube video

## Installation
First, change directory to the `/script` folder.

To use this tool, you need to install some pip packages:

```
pip install -r requirements.txt
```

In Linux, install ffmpeg with this command:

```
sudo apt update
sudo apt install ffmpeg
```

## Usage
Run this command in the directory `/script`:

```
python video_download.py
```

- First, the banner appears, it looks like this:

    ```
     =======================================================
    ||                                                     ||
    ||               Download video by Python              ||
    ||         ------------------------------------        ||
    ||  You have 2 options:                                ||
    ||  1. Download with 1 link only                       ||
    ||  2. Download with a list of links                   ||
     =======================================================
    ```

- If you choose `1`, you have to provide a url of the video you want to download.
- If you choose `2`, you have to provide a file that contains all the video urls you want to download.
- The download folder is not compulsory.