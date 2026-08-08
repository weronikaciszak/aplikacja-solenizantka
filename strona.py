
from flask import Flask, redirect, render_template_string, request, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
FILENAME = "zyczenia.txt"

def load_zyczenia():
    if not os.path.exists(FILENAME): return []
    with open(FILENAME, "r", encoding="utf-8") as f: lines = f.readlines()
    zyczenia = []
    for idx, line in enumerate(lines):
        parts = line.strip().split("|||")
        text = parts[0]
        img = parts[1] if len(parts) > 1 and parts[1] != "" else None
        zyczenia.append({"id": idx, "text": text, "img": img})
    return zyczenia

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, active_tab="home")

@app.route("/ksiega", methods=["GET", "POST"])
def ksiega():
    if request.method == "POST":
        text = request.form.get("tekst")
        file = request.files.get("zdjecie")
        filename = None
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        with open(FILENAME, "a", encoding="utf-8") as f: f.write(f"{text}|||{filename or ''}\n")
        return redirect("/ksiega")
    return render_template_string(HTML_TEMPLATE, active_tab="ksiega", zyczenia=load_zyczenia())

@app.route("/usun/<int:index>")
def usun_wpis(index):
    if os.path.exists(FILENAME):
        with open(FILENAME, "r", encoding="utf-8") as f: lines = f.readlines()
        if 0 <= index < len(lines):
            del lines[index]
            with open(FILENAME, "w", encoding="utf-8") as f: f.writelines(lines)
    return redirect("/ksiega")

@app.route("/film")
def film():
    return render_template_string(HTML_TEMPLATE, active_tab="film")

@app.route("/zdjecie")
def get_zdjecie(): return send_from_directory('.', 'solenizantka.png')

@app.route("/wideo")
def get_wideo(): return send_from_directory('.', 'hailuo_1786178926.mp4')

@app.route("/uploads/<filename>")
def uploaded_file(filename): return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

HTML_TEMPLATE = """
<!doctype html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <title>Strona dla Solenizantki</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef6ff; padding: 20px; color: #333; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .nav { display: flex; gap: 15px; margin-bottom: 25px; border-bottom: 2px solid #d0e1fd; padding-bottom: 10px; }
        .nav a { text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; background: #d0e1fd; color: #0056b3; transition: 0.3s; }
        .nav a.active { background: #0056b3; color: white; }
        .solenizantka-img { width: 100%; max-height: 350px; object-fit: cover; border-radius: 10px; margin-bottom: 20px; }
        textarea { width: 100%; height: 100px; padding: 10px; border: 1px solid #b8d4fd; border-radius: 8px; margin-bottom: 10px; resize: vertical; }
        button { background: #0056b3; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; }
        button:hover { background: #004085; }
        .wpis { background: #f4f8ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #0056b3; }
        .usun-btn { color: #dc3545; font-size: 13px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 5px; }
        .usun-btn:hover { text-decoration: underline; }
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
            <img src="/zdjecie" alt="Solenizantka" class="solenizantka-img">
            <h1>Witaj w wyjątkowej przestrzeni!</h1>
            <p style="font-size: 18px; line-height: 1.6;">Przygotowaliśmy tę stronę specjalnie dla Ciebie. Możesz tutaj przejść do <strong>Księgi Życzeń</strong>, aby dodać lub przeczytać wpisy od bliskich, albo obejrzeć pamiątkowe wideo w zakładce <strong>Film / Wideo</strong>.</p>
        
        {% elif active_tab == 'ksiega' %}
            <h1>Księga Życzeń</h1>
            <form method="POST" enctype="multipart/form-data">
                <textarea name="tekst" placeholder="Napisz coś miłego..." required></textarea><br>
                <input type="file" name="zdjecie" accept="image/*" style="margin-bottom: 10px;"><br>
                <button type="submit">Zapisz życzenia</button>
            </form>

            <h2 style="margin-top: 30px;">Wpisy gości:</h2>
            {% if zyczenia %}
                {% for z in zyczenia %}
                    <div class="wpis">
                        <p style="margin: 0 0 10px 0; white-space: pre-wrap;">{{ z.text }}</p>
                        {% if z.img %}
                            <img src="/uploads/{{ z.img }}" style="max-width: 200px; border-radius: 5px; display: block; margin-bottom: 10px;">
                        {% endif %}
                        <a href="/usun/{{ z.id }}" class="usun-btn">[Usuń wpis]</a>
                    </div>
                {% endfor %}
            {% else %}
                <p>Brak wpisów. Bądź pierwszą osobą, która coś doda!</p>
            {% endif %}

        {% elif active_tab == 'film' %}
            <h1>Pamiątkowy Film</h1>
            <video width="100%" controls style="border-radius: 10px; background: #000;">
                <source src="/wideo" type="video/mp4">
                Twoja przeglądarka nie obsługuje odtwarzacza wideo.
            </video>
        {% endif %}
    </div>
</body>
</html>
"""
import subprocess
import threading

def start_tunnel():
    # Uruchamia darmowy tunel przez localhost.run bez instalowania czegokolwiek
    url_command = "ssh -o StrictHostKeyChecking=no -R 80:127.0.0.1:5000 localhost.run"
    process = subprocess.Popen(url_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        if "tun.live" in line or "lhr.life" in line or "https://" in line:
            print("Twój publiczny link:", line.strip())

# Uruchamiamy tunel w tle, żeby nie blokował strony
threading.Thread(target=start_tunnel, daemon=True).start()




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
