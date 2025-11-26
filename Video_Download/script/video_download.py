import yt_dlp, os
import requests

def download_file_from_url(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"File '{filename}' downloaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during download: {e}")

def download_youtube_video(url, outdir):
    ydl_opts = {
        "noplaylist": True,
        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(outdir, "%(title).200s [%(id)s].%(ext)s"),
        "noprogress": False,
        "retries": 3,
        "concurrent_fragment_downloads": 4,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        print("\n✅ Done:", info.get("title"), "-", info.get("id"))

def main():
    banner = """
 =======================================================
||                                                     ||
||               Download video by Python              ||
||         ------------------------------------        ||
||  You have 2 options:                                ||
||  1. Download with 1 link only                       ||
||  2. Download with a list of links                   ||
 =======================================================
    """
    print(banner)
    choice = input("Choose an option (1 or 2): ")
    if choice == '1':
        url = input("Enter the video URL: ")
        outdir = input("Enter output directory (default 'downloads'): ") or "downloads"
        os.makedirs(outdir, exist_ok=True)

        if 'youtu.be' in url:
            download_youtube_video(url, outdir)
        else:
            filename = os.path.join(outdir, "video_url.mp4")
            download_file_from_url(url, filename)

    elif choice == '2':
        list_path = input("Enter the path to the file containing video URLs: ")
        outdir = input("Enter output directory (default 'downloads'): ") or "downloads"
        os.makedirs(outdir, exist_ok=True)

        with open(list_path, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]

        count = 1

        for url in urls:
            if 'youtu.be' in url:
                download_youtube_video(url, outdir)
            else:
                filename = os.path.join(outdir, f"video_url_{count:03d}.mp4")
                download_file_from_url(url, filename)
                count += 1
    else:
        print("Invalid choice. Please select 1 or 2.")
    return

if __name__ == "__main__":
    main()
