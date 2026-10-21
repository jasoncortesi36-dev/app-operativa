from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = 'attivita.json'

def carica_dati():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salva_dati(dati):
    with open(DATA_FILE, 'w') as f:
        json.dump(dati, f, indent=4)

@app.route('/')
def index():
    dati = carica_dati()
    return render_template('index.html', attivita=dati)

@app.route('/api/attivita', methods=['GET', 'POST'])
def api_attivita():
    if request.method == 'POST':
        nuova = request.json
        dati = carica_dati()
        dati.insert(0, nuova)
        salva_dati(dati)
        return jsonify({"status": "success", "data": dati})
    return jsonify(carica_dati())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
