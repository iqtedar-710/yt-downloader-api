from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@app.route("/download", methods=["POST"])
def download_video():

    data = request.json

    video_url = data.get("url")
    download_type = data.get("type", "mp4")
    quality = data.get("quality", "720")

    if not video_url:
        return jsonify({
            "error": "No URL provided"
        }), 400

    unique_id = str(uuid.uuid4())

    output_template = os.path.join(
        DOWNLOAD_FOLDER,
        f"{unique_id}.%(ext)s"
    )

    try:

        if download_type == "mp3":

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'cookiefile': 'cookies.txt',
                'impersonate': 'chrome',
                'noplaylist': True,
                'quiet': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android']
                    }
                },
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
            }

        else:

            format_map = {
                "144": "bestvideo[height<=144]+bestaudio/best/best",
                "240": "bestvideo[height<=240]+bestaudio/best/best",
                "360": "bestvideo[height<=360]+bestaudio/best/best",
                "480": "bestvideo[height<=480]+bestaudio/best/best",
                "720": "bestvideo[height<=720]+bestaudio/best/best",
                "1080": "bestvideo[height<=1080]+bestaudio/best/best",
                "1440": "bestvideo[height<=1440]+bestaudio/best/best",
                "2160": "bestvideo[height<=2160]+bestaudio/best/best",
                "4320": "bestvideo[height<=4320]+bestaudio/best/best"
            }

            selected_format = format_map.get(
                quality,
                "best"
            )

            ydl_opts = {
                'format': selected_format,
                'merge_output_format': 'mp4',
                'outtmpl': output_template,
                'cookiefile': 'cookies.txt',
                'impersonate': 'chrome',
                'noplaylist': True,
                'quiet': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android']
                    }
                },
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                video_url,
                download=True
            )

            filename = ydl.prepare_filename(info)

            if download_type == "mp3":
                filename = os.path.splitext(filename)[0] + ".mp3"
            else:
                filename = os.path.splitext(filename)[0] + ".mp4"

        return send_file(
            filename,
            as_attachment=True
        )

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )