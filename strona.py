def load_zyczenia():
    zyczenia = []
    
    # 1. Pobieramy z pliku zyczenia.txt (jeśli istnieje)
    if os.path.exists("zyczenia.txt"):
        with open("zyczenia.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                parts = line.strip().split("|||")
                text = parts[0]
                img = parts[1] if len(parts) > 1 and parts[1] != "" else None
                zyczenia.append({"text": text, "img": img})
    
    # 2. Pobieramy z Arkusza Google
    if GOOGLE_SCRIPT_URL:
        try:
            response = requests.get(GOOGLE_SCRIPT_URL)
            if response.status_code == 200:
                dane = response.json()
                for row in dane:
                    if len(row) > 0 and row[0]: # Jeśli wiersz nie jest pusty
                        text = row[0]
                        img = row[1] if len(row) > 1 and row[1] != "" else None
                        zyczenia.append({"text": text, "img": img})
        except Exception as e:
            print("Błąd pobierania z arkusza:", e)
            
    return list(reversed(zyczenia)) # Odwracamy, żeby najnowsze były na górze
