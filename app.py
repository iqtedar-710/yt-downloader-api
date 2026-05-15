from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/download", methods=["POST"])
def download_video():

    data = request.json
    video_url = data.get("url")
    download_type = data.get("type", "mp4")
    quality = data.get("quality", "720")

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    unique_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.%(ext)s")

    try:

        base_opts = {
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "cookiefile": "cookies.txt",
        }

        if download_type == "mp3":

            ydl_opts = {
                **base_opts,
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": quality,
                }]
            }

        else:

            format_map = {
                "144": "best[height<=144]",
                "240": "best[height<=240]",
                "360": "best[height<=360]",
                "480": "best[height<=480]",
                "720": "best[height<=720]",
                "1080": "best[height<=1080]",
                "1440": "best[height<=1440]",
                "2160": "best[height<=2160]",
                "4320": "best[height<=4320]",
            }

            ydl_opts = {
                **base_opts,
                "format": format_map.get(quality, "best"),
                "merge_output_format": "mp4",
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

            if download_type == "mp3":
                filename = os.path.splitext(filename)[0] + ".mp3"
            else:
                filename = os.path.splitext(filename)[0] + ".mp4"

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)