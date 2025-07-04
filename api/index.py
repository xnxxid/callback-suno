from flask import Flask, request, jsonify

app = Flask(__name__)

# Penyimpanan sementara hasil callback
callback_results = {}


@app.route("/suno-callback", methods=["POST"])
def suno_callback():
    data = request.json
    print("💖 Callback received:")
    print(data)

    if isinstance(data, dict) and data.get("code") == 200:
        task_id = (data.get("data", {}).get("task_id") if isinstance(
            data.get("data"), dict) else None)
        if task_id:
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
        cards = ""
        for tid, data in callback_results.items():
            raw_data = data.get("data") if isinstance(data, dict) else {}
            items = raw_data.get("data") if isinstance(raw_data, dict) else []

            if not items:
                cards += f"""
                <div class="card">
                    <h3>(No Data)</h3>
                    <p><small>Task ID: {tid}</small></p>
                </div>
                """
                continue

            title = items[0].get("title", "(No Title)")

            # Ambil satu gambar dari salah satu versi
            image_url = None
            for item in items:
                if isinstance(item, dict) and item.get("image_url"):
                    image_url = item.get("image_url")
                    break
            if not image_url:
                image_url = "https://via.placeholder.com/300x200?text=No+Image"

            # Kumpulkan semua versi audio
            versions_html = ""
            for idx, item in enumerate(items, start=1):
                if not isinstance(item, dict):
                    continue

                urls = {
                    "Audio Url": item.get("audio_url"),
                    "Source Audio Url": item.get("source_audio_url"),
                    "Stream Audio Url": item.get("stream_audio_url"),
                    "Source Stream Audio Url":
                    item.get("source_stream_audio_url"),
                }
                valid_urls = {k: v for k, v in urls.items() if v}

                version_html = f"""
                <div class='version'>
                    <strong>Version {idx}</strong>
                    <div class='button-group'>
                """
                if valid_urls:
                    for label, url in valid_urls.items():
                        version_html += (
                            f"<a href='{url}' target='_blank' class='btn'>{label}</a>"
                        )
                else:
                    version_html += "<em>No audio URLs available</em>"
                version_html += "</div></div>"

                versions_html += version_html

            # Card HTML
            cards += f"""
            <div class="card">
                <div class="image-container">
                    <a href="{image_url}" download>
                        <img src="{image_url}" alt="Song Image">
                    </a>
                </div>
                <div class="content-container">
                    <h3>{title}</h3>
                    <p class="task-id">Task ID: {tid}</p>
                    {versions_html}
                </div>
            </div>
            """
    else:
        cards = "<p><em>No task IDs received yet.</em></p>"

    return f"""
    <html>
    <head>
        <title>Suno Callback Results</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            h2 {{
                text-align: center;
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            p.description {{
                text-align: center;
                color: #555;
                margin-bottom: 30px;
            }}
            .container {{
                display: flex;
                flex-direction: column;
                gap: 20px;
                max-width: 900px;
                margin: 0 auto;
            }}
            .card {{
                display: flex;
                flex-wrap: wrap;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.05);
                overflow: hidden;
                transition: transform 0.2s ease;
            }}
            .card:hover {{
                transform: translateY(-2px);
            }}
            .image-container {{
                flex: 1 1 200px;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 10px;
            }}
            .image-container img {{
                width: 180px;
                height: auto;
                display: block;
                cursor: pointer;
                border-radius: 4px;
            }}
            .content-container {{
                flex: 2 1 300px;
                padding: 15px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }}
            .content-container h3 {{
                margin: 0 0 5px 0;
                color: #34495e;
                font-size: 18px;
            }}
            .task-id {{
                font-size: 12px;
                color: #888;
                margin-bottom: 10px;
            }}
            .version {{
                margin-top: 8px;
            }}
            .version strong {{
                display: block;
                margin-bottom: 4px;
                color: #555;
            }}
            .button-group {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }}
            .btn {{
                display: inline-block;
                padding: 8px 12px;
                font-size: 13px;
                background-color: #3498db;
                color: #fff;
                text-decoration: none;
                border-radius: 4px;
                transition: background-color 0.2s ease;
            }}
            .btn:hover {{
                background-color: #2980b9;
            }}
            @media (max-width: 768px) {{
                .card {{
                    flex-direction: column;
                }}
                .image-container {{
                    width: 100%;
                }}
                .image-container img {{
                    width: 100%;
                    max-height: none;
                    border-radius: 0;
                }}
                .content-container {{
                    padding: 15px;
                }}
                .button-group {{
                    justify-content: center;
                }}
                .btn {{
                    flex: 1 1 100%;
                    text-align: center;
                }}
            }}
        </style>
    </head>
    <body>
        <h2>💖 Suno Callback Server</h2>
        <p class="description">Click the image to download it, or use the buttons to play or download the audio.</p>
        <div class="container">
            {cards}
        </div>
    </body>
    </html>
    """