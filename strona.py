import os
import requests
from flask import Flask, redirect, render_template_string, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Wklej tutaj swój adres URL z Apps Script (z końcówką /exec)
GOOGLE_SCRIPT_URL = "TUTAJ_WKLEJ_SWOJ_ADRES_URL_Z_EXEC"

def load_zyczenia():
    zyczenia = []
    try:
        response = requests.get(GOOGLE_SCRIPT_URL, timeout=10)
        if response.status_code == 200:
            dane = response.json()
            # Pomijamy pierwszy wiersz (nagłówki)
            for row in dane[1:]:
                if row and len(row) > 0 and row[0]:
                    zyczenia.append({"text": row[0], "img": row[1] if len(row) > 1 else None})
    except Exception as e:
        print("Błąd pobierania:", e)
    return list(reversed(zyczenia))

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, active_tab="home")

@app.route("/ksiega", methods=["GET", "POST"])
def ksiega():
    if request.method == "POST":
        text = request.form.get("tekst")
        file = request.files.get("zdjecie")
        filename = ""
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Wysyłamy nowe życzenie do arkusza
        try:
            requests.post(GOOGLE_SCRIPT_URL, json={"tekst": text, "zdjecie": filename})
        except: pass
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
        body { font-family: sans-serif; background: #eef6ff; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; }
        .nav { display: flex; gap: 15px; margin-bottom: 25px; }
        .nav a { padding: 10px 20px; border-radius: 8px; background: #d0e1fd; text-decoration: none; }
        .wpis { background: #f4f8ff; padding: 15px; margin-bottom: 15px; border-left: 4px solid #0056b3; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Strona Główna</a>
            <a href="/ksiega">Księga Życzeń</a>
            <a href="/film">Film / Wideo</a>
        </div>
        {% if active_tab == 'ksiega' %}
            <h1>Księga Życzeń</h1>
            <form method="POST" enctype="multipart/form-data">
                <textarea name="tekst" required style="width:100%; height:100px;"></textarea><br>
                <input type="file" name="zdjecie" accept="image/*"><br>
                <button type="submit">Zapisz życzenia</button>
            </form>
            <h2>Wpisy gości:</h2>
            {% for z in zyczenia %}
                <div class="wpis">
                    <p>{{ z.text }}</p>
                    {% if z.img and z.img != "None" %}<img src="/uploads/{{ z.img }}" style="max-width:150px;">{% endif %}
                </div>
            {% endfor %}
        {% endif %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
