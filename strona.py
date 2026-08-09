import base64
import os
import requests
from flask import (
    Flask,
    redirect,
    render_template_string,
    request,
    send_from_directory,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw24VDFhBMITCva5NiO9gO6AetZhJAVgtybTHi2KZ9dJJV5zMb48tMlyGDIytJxQ0H8/exec"


def load_zyczenia():
  try:
    response = requests.get(GOOGLE_SCRIPT_URL, timeout=10)
    dane = response.json()
    zyczenia = []
    for row in dane[1:]:
      if row and len(row) > 0 and str(row[0]).strip() != "":
        text = str(row[0]).strip()
        img = (
            str(row[1]).strip()
            if len(row) > 1 and str(row[1]).strip() != ""
            else None
        )
        zyczenia.append({"text": text, "img": img})

    wynik = []
    for idx, z in enumerate(reversed(zyczenia)):
      wynik.append({"id": idx, "text": z["text"], "img": z["img"]})
    return wynik
  except Exception as e:
    print("Błąd pobierania:", e)
    return []


@app.route("/")
def home():
  return render_template_string(HTML_TEMPLATE, active_tab="home")


@app.route("/ksiega", methods=["GET", "POST"])
def ksiega():
  if request.method == "POST":
    text = request.form.get("tekst")
    file = request.files.get("zdjecie")

    payload = {"tekst": text, "zdjecie_base64": "", "nazwa": "", "mimeType": ""}
    if file and file.filename != "":
      payload["zdjecie_base64"] = base64.b64encode(file.read()).decode("utf-8")
      payload["nazwa"] = secure_filename(file.filename)
      payload["mimeType"] = file.content_type

    try:
      requests.post(GOOGLE_SCRIPT_URL, json=payload)
    except Exception as e:
      print("Błąd zapisu:", e)

    return redirect("/ksiega")
  return render_template_string(
      HTML_TEMPLATE, active_tab="ksiega", zyczenia=load_zyczenia()
  )


@app.route("/film")
def film():
  return render_template_string(HTML_TEMPLATE, active_tab="film")


@app.route("/zdjecie")
def get_zdjecie():
  return send_from_directory(".", "solenizantka.png.png")


@app.route("/wideo")
def get_wideo():
  return send_from_directory(".", "hailuo_1786178926.mp4..mp4")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
  return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


HTML_TEMPLATE = """
<!doctype html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <title>Strona dla Solenizantki</title>
    <style>
        body { font-family: sans-serif; background: #eef6ff; padding: 20px; color: #333; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .nav { display: flex; gap: 15px; margin-bottom: 25px; border-bottom: 2px solid #d0e1fd; padding-bottom: 10px; }
        .nav a { text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; background: #d0e1fd; color: #0056b3; }
        .nav a.active { background: #0056b3; color: white; }
        .solenizantka-img { width: 100%; max-height: 350px; object-fit: cover; border-radius: 10px; margin-bottom: 20px; }
        textarea { width: 100%; height: 100px; padding: 10px; border: 1px solid #b8d4fd; border-radius: 8px; margin-bottom: 10px; }
        button { background: #0056b3; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
        .wpis { background: #f4f8ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/" class="{% if active_tab == 'home' %}active{% endif %}">Strona Główna</a>
            <a href="/ksiega" class="{% if active_tab == 'ksiega' %}active{% endif %}">Księga Życzeń</a>
            <a href="/film" class="{% if active_tab == 'film' %}active{% endif %}">Film / Wideo</a>
        </div>
        {% if active_tab == 'home' %}
            <img src="/zdjecie" class="solenizantka-img">
            <h1>Witaj!</h1>
        {% elif active_tab == 'ksiega' %}
            <h1>Księga Życzeń</h1>
            <form method="POST" enctype="multipart/form-data">
                <textarea name="tekst" required></textarea><br>
                <input type="file" name="zdjecie" accept="image/*"><br>
                <button type="submit">Zapisz życzenia</button>
            </form>
            <h2>Wpisy gości:</h2>
            {% for z in zyczenia %}
                <div class="wpis">
                    <p style="white-space: pre-wrap;">{{ z.text }}</p>
                    {% if z.img and z.img != "None" and z.img != "" %}
                        {% if ".png" in z.img or ".jpg" in z.img or ".jpeg" in z.img %}
                            <img src="/uploads/{{ z.img }}" style="max-width: 200px; display: block; margin-top: 10px; border-radius: 5px;">
                        {% else %}
                            <img src="https://lh3.googleusercontent.com/d/{{ z.img }}" style="max-width: 200px; display: block; margin-top: 10px; border-radius: 5px;">
                        {% endif %}
                    {% endif %}
                </div>
            {% endfor %}
        {% elif active_tab == 'film' %}
            <video width="100%" controls><source src="/wideo" type="video/mp4"></video>
        {% endif %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
