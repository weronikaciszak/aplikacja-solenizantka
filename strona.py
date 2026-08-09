import os, requests, base64
from flask import Flask, redirect, render_template_string, request, send_from_directory

app = Flask(__name__)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw24VDFhBMITCva5NiO9gO6AetZhJAVgtybTHi2KZ9dJJV5zMb48tMlyGDIytJxQ0H8/exec"

def load_zyczenia():
    try:
        response = requests.get(GOOGLE_SCRIPT_URL, timeout=10)
        dane = response.json()
        zyczenia = []
        for row in dane[1:]:
            if row[0]:
                zyczenia.append({"text": row[0], "img_id": row[1] if len(row) > 1 else None})
        return list(reversed(zyczenia))
    except: return []

@app.route("/ksiega", methods=["GET", "POST"])
def ksiega():
    if request.method == "POST":
        text = request.form.get("tekst")
        file = request.files.get("zdjecie")
        payload = {"tekst": text, "zdjecie_base64": "", "nazwa": "", "mimeType": ""}
        if file:
            payload["zdjecie_base64"] = base64.b64encode(file.read()).decode('utf-8')
            payload["nazwa"] = file.filename
            payload["mimeType"] = file.content_type
        requests.post(GOOGLE_SCRIPT_URL, json=payload)
        return redirect("/ksiega")
    return render_template_string(HTML_TEMPLATE, active_tab="ksiega", zyczenia=load_zyczenia())

# ... (reszta routingu tak jak wcześniej)

HTML_TEMPLATE = """
... 
{% for z in zyczenia %}
    <div class="wpis">
        <p>{{ z.text }}</p>
        {% if z.img_id %}
            <img src="https://lh3.googleusercontent.com/d/{{ z.img_id }}" style="max-width: 200px;">
        {% endif %}
    </div>
{% endfor %}
...
"""
# (wstaw tu resztę HTML z poprzedniej wersji)
