import os
import requests
from flask import (
    Flask,
    redirect,
    render_template_string,
    request,
    send_from_directory,
)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzBFffCPUl2Lc14mL7Ukeob1iD6h8PC6qVBGK65OSmA7DJRLBLdS90jYqnp18Oec6M1/exec"


def load_zyczenia():
  try:
    response = requests.get(GOOGLE_SCRIPT_URL, timeout=10)
    dane = response.json()
    zyczenia = []
    for idx, row in enumerate(dane[1:], start=1):
      if row and len(row) > 0 and str(row[0]).strip() != "":
        text = str(row[0]).strip()
        zyczenia.append({"row_index": idx, "text": text})
    return list(reversed(zyczenia))
  except Exception as e:
    print("Błąd pobierania:", e)
    return []


@app.route("/")
def home():
  return render_template_string(HTML_TEMPLATE, active_tab="home")


@app.route("/ksiega", methods=["GET", "POST"])
def ksiega():
  if request.method == "POST":
    row_to_delete = request.form.get("usun_row")
    if row_to_delete:
      try:
        requests.post(
            GOOGLE_SCRIPT_URL,
            json={"akcja": "usun", "row": row_to_delete},
            timeout=10,
        )
      except Exception as e:
        print("Błąd usuwania:", e)
      return redirect("/ksiega")

    text = request.form.get("tekst")
    if text:
      try:
        requests.post(
            GOOGLE_SCRIPT_URL, json={"akcja": "dodaj", "tekst": text}, timeout=10
        )
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
        
        /* Zmienione na contain, dzięki czemu całe zdjęcie będzie widać i nic się nie uetnie */
        .solenizantka-img { width: 100%; max-height: 500px; object-fit: contain; display: block; margin: 0 auto 20px auto; border-radius: 10px; background: #f8fbff; }
        
        .zyczenia-tekst { font-size: 22px; font-weight: bold; color: #0056b3; text-align: center; margin-top: 20px; line-height: 1.4; }
        textarea { width: 100%; height: 100px; padding: 10px; border: 1px solid #b8d4fd; border-radius: 8px; margin-bottom: 10px; }
        button { background: #0056b3; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
        .wpis { background: #f4f8ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #0056b3; position: relative; }
        .btn-usun { background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 5px; font-size: 12px; cursor: pointer; float: right; }
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
            <div class="zyczenia-tekst">Betko! Z okazji Twoich Urodzin chcielibyśmy złożyć Ci najserdeczniejsze życzenia!</div>
        {% elif active_tab == 'ksiega' %}
            <h1>Księga Życzeń</h1>
            <form method="POST">
                <textarea name="tekst" required placeholder="Wpisz swoje życzenia..."></textarea><br>
                <button type="submit">Zapisz życzenia</button>
            </form>
            <h2>Wpisy gości:</h2>
            {% for z in zyczenia %}
                <div class="wpis">
                    <form method="POST" style="display:inline;">
                        <input type="hidden" name="usun_row" value="{{ z.row_index }}">
                        <button type="submit" class="btn-usun" onclick="return confirm('Na pewno usunąć ten wpis?');">Usuń</button>
                    </form>
                    <p style="white-space: pre-wrap; margin-right: 50px;">{{ z.text }}</p>
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
