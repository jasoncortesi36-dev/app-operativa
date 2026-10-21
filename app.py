from flask import Flask, render_template_string, request
import json
import time
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "coordinamento.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS messaggi
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         autore TEXT,
                         testo TEXT,
                         stato TEXT,
                         creato_il REAL,
                         aggiornato_da TEXT)''')
        conn.commit()

init_db()

HTML_PAGE = """<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App Operativa Pro</title>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: sans-serif; padding: 15px; margin: 0; }
        h2 { color: #4CAF50; margin-bottom: 5px; }
        .box { background: #1e1e1e; padding: 12px; margin-bottom: 12px; border-radius: 8px; border-left: 5px solid #ff9800; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .box.Completato { border-left-color: #4CAF50; }
        .box.InCorso { border-left-color: #2196F3; }
        input, select, textarea, button { width: 100%; padding: 12px; margin-top: 8px; margin-bottom: 12px; background: #2d2d2d; color: white; border: 1px solid #444; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        textarea { resize: vertical; height: 70px; }
        button { background: #4CAF50; border: none; font-weight: bold; cursor: pointer; }
        button:active { background: #388E3C; }
        .filters { display: flex; gap: 5px; margin-bottom: 15px; overflow-x: auto; padding-bottom: 5px; }
        .filters button { background: #2d2d2d; border: 1px solid #555; font-size: 12px; padding: 6px 10px; margin: 0; width: auto; white-space: nowrap; }
        .filters button.active { background: #4CAF50; border-color: #4CAF50; }
    </style>
</head>
<body>
    <h2>App Operativa</h2>
    <div id="setup">
        <label>Il tuo Nome / Operatore:</label>
        <input type="text" id="nomeInput" placeholder="Es. Jason">
        <button onclick="salvaNome()">Accedi al sistema</button>
    </div>
    
    <div id="chat" style="display:none;">
        <p>Operatore: <span id="userDisplay" style="color: #4CAF50; font-weight: bold;"></span></p>
        <textarea id="testoInput" placeholder="Scrivi attività, nota o DDT..."></textarea>
        <button onclick="inviaMessaggio()">Invia Attività</button>
        
        <h3>Filtra per Stato</h3>
        <div class="filters">
            <button onclick="impostaFiltro('Tutti')" id="btn-Tutti" class="active">Tutti</button>
            <button onclick="impostaFiltro('In Attesa')" id="btn-In Attesa">In Attesa</button>
            <button onclick="impostaFiltro('In Corso')" id="btn-In Corso">In Corso</button>
            <button onclick="impostaFiltro('Completato')" id="btn-Completato">Completato</button>
        </div>

        <h3>Storico Attività</h3>
        <div id="messaggiLista"></div>
    </div>

    <script>
        let utente = "";
        let filtroAttuale = "Tutti";

        function salvaNome() {
            let val = document.getElementById("nomeInput").value.trim();
            if(!val) return;
            utente = val;
            document.getElementById("userDisplay").innerText = utente;
            document.getElementById("setup").style.display = "none";
            document.getElementById("chat").style.display = "block";
            caricaMessaggi();
            setInterval(caricaMessaggi, 3000);
        }

        function impostaFiltro(stato) {
            filtroAttuale = stato;
            document.querySelectorAll('.filters button').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + stato).classList.add('active');
            caricaMessaggi();
        }

        function caricaMessaggi() {
            fetch('/get_messaggi')
            .then(res => res.json())
            .then(data => {
                let html = "";
                data.forEach(m => {
                    let stato = m[3];
                    if (filtroAttuale !== "Tutti" && stato !== filtroAttuale) return;
                    
                    let classeStato = stato.replace(/\s+/g, '');
                    html += `<div class="box ${classeStato}">
                        <b>${m[1]}</b> <span style="font-size:11px; color:#aaa;">(${new Date(m[4]*1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})})</span><br>
                        <div style="margin: 6px 0; font-size: 15px;">${m[2]}</div>
                        <small>Stato attuale: <b>${stato}</b> ${m[5] ? '<i>(mod. da ' + m[5] + ')</i>' : ''}</small><br>
                        <select onchange="aggiornaStato(${m[0]}, this.value)">
                            <option value="">Aggiorna stato...</option>
                            <option value="In Attesa">In Attesa</option>
                            <option value="In Corso">In Corso</option>
                            <option value="Approvato">Approvato</option>
                            <option value="Completato">Completato</option>
                        </select>
                    </div>`;
                });
                document.getElementById("messaggiLista").innerHTML = html || '<p style="color:#777; text-align:center;">Nessuna attività trovata.</p>';
            });
        }

        function inviaMessaggio() {
            let testo = document.getElementById("testoInput").value.trim();
            if(!testo) return;
            fetch('/invia', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({autore: utente, testo: testo})
            }).then(() => {
                document.getElementById("testoInput").value = "";
                caricaMessaggi();
            });
        }

        function aggiornaStato(id, stato) {
            if(!stato) return;
            fetch('/stato', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id, stato: stato, autore: utente})
            }).then(() => caricaMessaggi());
        }
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/get_messaggi')
def get_messaggi():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messaggi ORDER BY id DESC")
        righe = cursor.fetchall()
    return json.dumps(righe)

@app.route('/invia', methods=['POST'])
def invia():
    dati = request.json
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO messaggi (autore, testo, stato, creato_il) VALUES (?, ?, ?, ?)",
                     (dati['autore'], dati['testo'], "In Attesa", time.time()))
        conn.commit()
    return "OK"

@app.route('/stato', methods=['POST'])
def stato():
    dati = request.json
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE messaggi SET stato=?, aggiornato_da=? WHERE id=?",
                     (dati['stato'], dati['autore'], dati['id']))
        conn.commit()
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
