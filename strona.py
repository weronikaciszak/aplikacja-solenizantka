import os
import requests
from flask import Flask, redirect, render_template_string, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

GOOGLE_SCRIPT_URL = os.environ.get("GOOGLE_SCRIPT_URL")

def zapisz_zyczenie(tekst, zdjecie):
    if GOOGLE_SCRIPT_URL:
        try:
            requests.post(GOOGLE_SCRIPT_URL, json={"tekst": tekst, "zdjecie": zdjecie})
        except Exception as e:
            print("Błąd wysyłania do arkusza:", e)

def load_zyczenia():
    if not GOOGLE_SCRIPT_URL:
        return []
    try:
        # Pobieramy dane z naszego skryptu Google (dodamy funkcję GET w skrypcie)
        response = requests.get(GOOGLE_SCRIPT_URL)
        if response.status_code == 200:
            dane = response.json()
            zyczenia = []
            for idx, row in enumerate(dane):
                # row to np. [tekst, zdjecie]
                text = row[0] if len(row) > 0 else ""
                img = row[1] if len(row) > 1 and row[1] != "" else None
                zyczenia.append({"id": idx, "text": text, "img": img})
            return list(reversed(zyczenia)) # Najnowsze na górze
    except Exception as e:
        print("Błąd pobierania z arkusza:", e)
    return []

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
        
        zapisz_zyczenie(text, filename or "")
        return redirect("/ksiega")
    return render_template_string(HTML_TEMPLATE, active_tab="ksiega", zyczenia=load_zyczenia())

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
