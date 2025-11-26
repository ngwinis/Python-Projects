# VIDEO DOWNLOADER BY PYTHON

## Getting Started
This project helps you download any video with an URL:
- Link download
- Youtube video

## Installation
To use this tool, you need to install some pip packages:

```
pip install -r requirements.txt
```

In Linux, install ffmpeg with this command:

```
sudo apt update
sudo apt install ffmpeg
```

## Run Script
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

## GUI Application
You may find it inconvenient to run this tool directly in the terminal. To make things easier, I built a GUI application where you can enter the video links you want to download, customize the filename for each video, and location to save them in your computer. They are all on the left side, and the download progress for each video appears on the right.
- Unfortunately, you have to run this app by python

    ```cmd
    python app.py
    ```

- Why do you have to run this app with python even though it uses GUI? Because Youtube constantly updates in an effort to block Python-based video downloading, the `yt_dlp` library must be updated frequently. I initially planned to pack everything tinto a single executable file (app.exe), but for this reason, I decided not to. Instead, users can update the library themselves and run the app directly with python.
- To update the library, run this command before run the app:

    ```
    pip install --upgrade yt_dlp
    ```

- `Usage:` With the video links and the filename, you have to paste one per line.

    ![alt text](design/demo_video_downloader.gif)