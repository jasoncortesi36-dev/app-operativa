from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = 'attivita.json'

def carica_dati():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def salva_dati(dati):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(dati, f, indent=4)
    except Exception:
        pass

@app.route('/')
def index():
    dati = carica_dati()
    return render_template('index.html', attivita=dati)

@app.route('/api/attivita', methods=['GET', 'POST'])
def api_attivita():
    if request.method == 'POST':
        nuova = request.json
        dati = carica_dati()
        if nuova:
            dati.insert(0, nuova)
            salva_dati(dati)
        return jsonify({"status": "success", "data": dati})
    return jsonify(carica_dati())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
