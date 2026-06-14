from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt-dlp
import os
import glob

app = Flask(__name__)
CORS(app)  # Allows your HTML file to communicate with this backend

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/download', methods=['POST'])
def download_media():
    data = request.json
    video_url = data.get('url')
    format_type = data.get('format') # 'mp4' or 'mp3'

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    # Clean out previous downloads to save space
    for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
        try: os.remove(f)
        except: pass

    # Configure yt-dlp based on user choice
    if format_type == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        }

    try:
        with yt-dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            if format_type == 'mp3':
                filename = os.path.splitext(filename)[0] + ".mp3"

        # Send the file back to the HTML interface
        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)