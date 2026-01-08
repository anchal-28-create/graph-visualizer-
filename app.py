from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
IMAGES_FOLDER = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)

ALLOWED_EXT = {"csv"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route("/", methods=["GET", "POST"])
def index():
    # If user uploaded a file (first step)
    if request.method == "POST" and request.form.get("action") == "upload":
        file = request.files.get("file")
        if not file or file.filename == "":
            return render_template("index.html", error="No file uploaded")

        if not allowed_file(file.filename):
            return render_template("index.html", error="Only CSV files allowed")

        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(save_path)

        try:
            df = pd.read_csv(save_path)
        except Exception as e:
            return render_template("index.html", error=f"Error reading CSV: {e}")

        columns = df.columns.tolist()
        # Render index with columns populated and pass the saved filename (hidden)
        return render_template("index.html", columns=columns, saved_file=unique_name)

    # If user clicked "Plot" (second step)
    if request.method == "POST" and request.form.get("action") == "plot":
        saved_file = request.form.get("saved_file")
        x_column = request.form.get("x_column")
        y_column = request.form.get("y_column")
        chart_type = request.form.get("chart_type")

        if not saved_file:
            return render_template("index.html", error="No uploaded CSV found. Please upload again.")

        csv_path = os.path.join(UPLOAD_FOLDER, saved_file)
        if not os.path.exists(csv_path):
            return render_template("index.html", error="Uploaded file missing on server. Please upload again.")

        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            return render_template("index.html", error=f"Error reading saved CSV: {e}")

        if x_column not in df.columns or y_column not in df.columns:
            return render_template("index.html", error="Selected columns not found in CSV. Please upload again.")

        x = df[x_column]
        y = df[y_column]

        # Generate image
        img_name = f"{uuid.uuid4().hex}.png"
        img_path = os.path.join(IMAGES_FOLDER, img_name)

        plt.figure(figsize=(8, 5))
        if chart_type == "line":
            plt.plot(x, y, marker="o")
        elif chart_type == "bar":
            plt.bar(x, y)
        elif chart_type == "scatter":
            plt.scatter(x, y)
        else:
            plt.plot(x, y, marker="o")

        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(f"{chart_type.title()} of {y_column} vs {x_column}")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(img_path)
        plt.close()

        # Render the plot page
        return render_template("plot.html", image=img_name)

    # GET request
    return render_template("index.html")

if __name__ == "__main__":
    import webbrowser, threading, time, logging
    # optional: enable simple logging to console
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    def open_browser():
        time.sleep(1.0)  # wait a moment for server to start
        try:
            webbrowser.open("http://127.0.0.1:5000")
        except Exception:
            pass

    # start browser opener in background (optional)
    threading.Thread(target=open_browser, daemon=True).start()

    # start Flask server; use_reloader=False avoids double-start when packaged
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
