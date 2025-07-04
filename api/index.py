from flask import Flask, request, jsonify

app = Flask(__name__)

# Penyimpanan sementara hasil callback
callback_results = {}

@app.route("/suno-callback", methods=["POST"])
def suno_callback():
    data = request.json
    print("💖 Callback received:")
    print(data)

    if data.get("code") == 200:
        task_id = data["data"]["task_id"]
        callback_results[task_id] = data
        print(f"✅ Data saved for task_id: {task_id}")

    return jsonify({"message": "Callback received"}), 200

@app.route("/results/<task_id>", methods=["GET"])
def get_result(task_id):
    if task_id in callback_results:
        return jsonify({
            "message": "Result found",
            "data": callback_results[task_id]
        }), 200
    else:
        return jsonify({"message": "Result not found for this task_id"}), 404

@app.route("/", methods=["GET"])
def home():
    if callback_results:
        list_items = ""
        for tid, data in callback_results.items():
            items = data["data"].get("data", [])
            if not items:
                list_items += f"<li><em>No data available</em> <small>({tid})</small></li>"
                continue
            title = items[0].get("title", "(No Title)")
            audio_links = ""
            for idx, item in enumerate(items, start=1):
                urls = {
                    "audio_url": item.get("audio_url"),
                    "source_audio_url": item.get("source_audio_url"),
                    "stream_audio_url": item.get("stream_audio_url"),
                    "source_stream_audio_url": item.get("source_stream_audio_url")
                }
                valid_urls = {k: v for k, v in urls.items() if v}
                if valid_urls:
                    audio_links += f"<br><strong>Version {idx}:</strong>"
                    for label, url in valid_urls.items():
                        audio_links += f" <a href='{url}' target='_blank'>[{label}]</a>"
                else:
                    audio_links += f"<br><strong>Version {idx}:</strong> <em>No audio URLs available</em>"
            list_items += f"<li><strong>{title}</strong> <small>({tid})</small>{audio_links}</li>"
        html_list = f"<ul>{list_items}</ul>"
    else:
        html_list = "<p><em>No task IDs received yet.</em></p>"
    return f"""
    <h2>💖 Suno Callback Server</h2>
    <p>Click the audio links below to download or play the music.</p>
    <h3>Saved Songs:</h3>
    {html_list}
    """
