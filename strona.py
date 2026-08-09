import os
import requests
from flask import Flask, redirect, render_template_string, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
FILENAME = "zyczenia.txt"

GOOGLE_SCRIPT_URL = os.environ.get("GOOGLE_SCRIPT_URL")

def zapisz_zyczenie(tekst, zdjecie):
    # Zapisz lokalnie do pliku
    with open(FILENAME, "a", encoding="utf-8") as f:
        f.write(f"{tekst}|||{zdjecie or ''}\n")
    
    # Wyślij do Arkusza Google
    if GOOGLE_SCRIPT_URL:
        try:
            requests.post(GOOGLE_SCRIPT_URL, json={"tekst": tekst, "zdjecie": zdjecie or ""}, timeout=5)
        except Exception as e:
            print("Błąd wysyłania do arkusza:", e)

def load_zyczenia():
    zyczenia_zbior = []
    
    # 1. Pobieramy z pliku lokalnego
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                parts = line.strip().split("|||")
                if parts and parts[0]:
                    text = parts[0]
                    img = parts[1] if len(parts) > 1 and parts[1] != "" else None
                    zyczenia_zbior.append({"text": text, "img": img})
        except Exception as e:
            print("Błąd odczytu pliku:", e)
            
    # 2. Pobieramy z Arkusza Google (chmura)
    if GOOGLE_SCRIPT_URL:
        try:
            response = requests.get(GOOGLE_SCRIPT_URL, timeout=5)
            if response.status_code == 200:
                dane = response.json()
                for row in dane:
                    if row and len(row) > 0 and row[0]:
                        text = str(row[0])
                        img = str(row[1]) if len(row) > 1 and row[1] != "" and row[1] is not None else None
                        wpis = {"text": text, "img": img}
                        # Dodajemy tylko jeśli jeszcze tego nie ma, żeby nie było duplikatów
                        if wpis not in zyczenia_zbior:
                            zyczenia_zbior.append(wpis)
        except Exception as e:
            print("Błąd pobierania z arkusza:", e)
            
    # Odwracamy kolejność, żeby najnowsze były na górze, i nadajemy indeksy do usuwania
    wynik = []
    for idx, z in enumerate(reversed(zyczenia_zbior)):
        wynik.append({"id": idx, "text": z["text"], "img": z["img"]})
    return wynik

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
        
        zapisz_zyczenie(text, filename)
        return redirect("/ksiega")
    return render_template_string(HTML_TEMPLATE, active_tab="ksiega", zyczenia=load_zyczenia())

@app.route("/usun/<int:index>")
def usun_wpis(index):
    if os.path.exists(FILENAME):
        with open(FILENAME, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if 0 <= index < len(lines):
            del lines[index]
            with open(FILENAME, "w", encoding="utf-8") as f:
                f.writelines(lines)
    return redirect("/ksiega")

@app.route("/film")
def film():
    return render_template_string(HTML_TEMPLATE, active_tab="film")

@app.route("/zdjecie")
def get_zdjecie(): return send_from_directory('.', 'solenizantka.png.png')

@app.route("/wideo")
def get_wideo(): return send_from_directory('.', 'hailuo_1786178926.mp4..mp4')

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
