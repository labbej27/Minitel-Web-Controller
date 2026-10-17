#!/usr/bin/env python3

import subprocess
import time
import signal
import atexit
import threading
from flask import Flask, request, redirect, render_template_string

# ================= PROJET 2 =================
PROJET2_PYTHON = "/home/labbej/websocket2minitel/venv/bin/python"
PROJET2_SCRIPT = "/home/labbej/websocket2minitel/websocket2minitel.py"
SERIAL_PORT   = "/dev/ttyUSB0"

# ================= SERVEURS MINITEL =================
SERVEURS = {
    "MiniPAVI": "wss://go.minipavi.fr:8181",
    "Hacker": "ws://mntl.joher.com:2018",
    "Annuaire": "ws://3611.re/ws",
    "3615": "ws://3615co.de/ws",
    "Retrocampus": "wss://bbs.retrocampus.com:8051",
    "LABBEJ27": "wss://minitel.labbej.fr:8182",
}

selected_server = "LABBEJ27"

# ================= ÉTAT =================
current_process = None
current_name = None
last_action = 0

# ================= OUTILS =================
def can_act():
    global last_action
    now = time.time()
    if now - last_action < 0.5:
        return False
    last_action = now
    return True

# ================= ACTIONS =================



def stop_current():
    global current_process, current_name

    if not can_act():
        return

    if current_process and current_process.poll() is None:
        print(f"Arrêt de {current_name}")
        current_process.send_signal(signal.SIGINT)
        time.sleep(1)
        if current_process.poll() is None:
            current_process.terminate()
        current_process = None
        current_name = None
    else:
        print("Aucun script en cours")


def run_script2():
    global current_process, current_name

    if not can_act() or current_process:
        return

    url = SERVEURS[selected_server]
    print(f"Lancement Minitel → {selected_server}")

    current_process = subprocess.Popen(
        [PROJET2_PYTHON, PROJET2_SCRIPT, url, SERIAL_PORT],
        start_new_session=True
    )
    current_name = "minitel"

# ================= SERVEUR WEB =================
app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Minitel - Console</title>

<style>
:root {
    color-scheme: dark;
    --bg: #101318;
    --panel: #1b2029;
    --border: #303846;
    --text: #f4f6fa;
    --muted: #aab4c4;
    --blue: #2878f0;
    --green: #168653;
    --orange: #d77b12;
    --red: #c83b43;
}

* {
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}

html, body {
    width: 100%;
    height: 100%;
    margin: 0;
    overflow: hidden;
}

body {
    font-family: system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 10px;
    font-size: 16px;
    touch-action: manipulation;
}

.app {
    width: 100%;
    max-width: 900px;
    height: 100%;
    margin: 0 auto;
    display: grid;
    grid-template-rows: 48px 112px 1fr 100px;
    gap: 10px;
}

header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 8px;
}

h1 {
    margin: 0;
    font-size: 27px;
    letter-spacing: 1px;
}

.subtitle {
    color: var(--muted);
    font-size: 13px;
}

.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 10px 12px;
    min-width: 0;
}

.section-title {
    display: block;
    color: var(--muted);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 7px;
}

.server-form {
    height: 100%;
    display: grid;
    grid-template-columns: minmax(0, 1fr) 180px;
    align-items: center;
    gap: 10px;
}

.server-field {
    min-width: 0;
}

select, button {
    font: inherit;
    font-weight: 650;
    border: 0;
    border-radius: 9px;
    width: 100%;
    min-width: 0;
    min-height: 56px;
    padding: 10px 12px;
}

select {
    background: #10151d;
    color: white;
    border: 1px solid #414b5c;
    font-size: 18px;
}

button {
    color: white;
    cursor: pointer;
    touch-action: manipulation;
    user-select: none;
    transition: filter 0.1s, transform 0.1s;
}

button:active {
    filter: brightness(0.82);
    transform: scale(0.98);
}

button:focus-visible, select:focus-visible {
    outline: 3px solid #8bb9ff;
    outline-offset: 2px;
}

.apply {
    background: var(--blue);
    height: 56px;
}

.actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    min-height: 0;
}

.action-form {
    min-width: 0;
    height: 100%;
}

.action-form button {
    height: 100%;
    min-height: 0;
    font-size: clamp(17px, 3vw, 23px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: 1px solid #ffffff20;
    border-radius: 14px;
}

.connect {
    background: linear-gradient(145deg, #168653, #10623d);
}

.disconnect {
    background: linear-gradient(145deg, #d77b12, #a8520b);
}

.symbol {
    font-size: 34px;
    line-height: 1;
}

.status {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.status-item {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
    padding: 8px 12px;
    border-radius: 10px;
    background: #151a22;
    border: 1px solid var(--border);
}

.status-label {
    font-size: 12px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.7px;
    margin-bottom: 5px;
}

.status-value {
    font-size: 18px;
    font-weight: 750;
    overflow-wrap: anywhere;
}

.running {
    color: #56e5a0;
}

.stopped {
    color: #ffbd70;
}

footer {
    text-align: center;
    color: #778294;
    font-size: 11px;
    padding-top: 2px;
}

/* Écrans plus petits ou orientation portrait */
@media (max-width: 520px) {
    body {
        padding: 7px;
    }

    .app {
        grid-template-rows: 42px 112px 1fr 100px;
        gap: 7px;
    }

    h1 {
        font-size: 23px;
    }

    .subtitle {
        font-size: 11px;
    }

    .server-form {
        grid-template-columns: minmax(0, 1fr) 120px;
        gap: 7px;
    }

    select {
        font-size: 15px;
        padding: 8px;
    }

    .apply {
        font-size: 14px;
        padding: 7px;
    }

    .actions {
        grid-template-columns: 1fr;
        grid-template-rows: 1fr 1fr;
    }

    .action-form button {
        flex-direction: row;
        gap: 12px;
        font-size: 18px;
    }

    .symbol {
        font-size: 25px;
    }

    .status-value {
        font-size: 15px;
    }
}

@media (max-height: 400px) {
    .app {
        grid-template-rows: 38px 88px 1fr 72px;
        gap: 6px;
    }

    body {
        padding: 6px;
    }

    h1 {
        font-size: 22px;
    }

    .panel {
        padding: 6px 10px;
    }

    .section-title {
        margin-bottom: 3px;
    }

    .server-form {
        grid-template-columns: minmax(0, 1fr) 160px;
    }

    select, .apply {
        min-height: 46px;
        height: 46px;
    }

    .symbol {
        font-size: 26px;
    }

    .status-value {
        font-size: 15px;
    }
}
</style>
</head>

<body>
<div class="app">

    <header>
        <h1>MINITEL</h1>
        <span class="subtitle">CONSOLE DE CONTRÔLE</span>
    </header>

    <section class="panel">
        <form method="post" class="server-form">
            <div class="server-field">
                <label class="section-title" for="server">
                    Serveur distant
                </label>
                <select name="server" id="server">
                {% for name in servers %}
                    <option value="{{ name }}"
                        {% if name == current %}selected{% endif %}>
                        {{ name }}
                    </option>
                {% endfor %}
                </select>
            </div>

            <button class="apply" type="submit">
                APPLIQUER
            </button>
        </form>
    </section>

    <main class="actions">
        <form method="post" action="/action/script2"
              class="action-form">
            <button class="connect" type="submit">
                <span class="symbol">▶</span>
                <span>CONNEXION</span>
                <span style="font-size:13px;font-weight:400">
                    Lancer le Minitel
                </span>
            </button>
        </form>

        <form method="post" action="/action/stop"
              class="action-form">
            <button class="disconnect" type="submit">
                <span class="symbol">■</span>
                <span>DÉCONNEXION</span>
                <span style="font-size:13px;font-weight:400">
                    Arrêter le script
                </span>
            </button>
        </form>
    </main>

    <section class="panel status">
        <div class="status-item">
            <span class="status-label">Serveur sélectionné</span>
            <span class="status-value">{{ current }}</span>
        </div>

        <div class="status-item">
            <span class="status-label">État du script</span>
            <span class="status-value
                {% if script != 'Aucun' %}running{% else %}stopped{% endif %}">
                {% if script != 'Aucun' %}
                    ● {{ script }}
                {% else %}
                    ○ À l'arrêt
                {% endif %}
            </span>
        </div>
    </section>

</div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    global selected_server
    if request.method == 'POST':
        selected_server = request.form['server']
        print(f"Serveur sélectionné via web : {selected_server}")
        return redirect('/')
    return render_template_string(
        HTML,
        servers=SERVEURS,
        current=selected_server,
        script=current_name or "Aucun"
    )

@app.route('/action/<name>', methods=['POST'])
def action(name):
    if name == "script2":
        run_script2()
    elif name == "stop":
        stop_current()
    return redirect('/')

def start_web():
    print("Serveur web actif sur http://0.0.0.0:8080")
    app.run(host="0.0.0.0", port=8080, debug=False)

# ================= CLEANUP =================
def cleanup():
    print("Nettoyage avant arrêt")
    if current_process and current_process.poll() is None:
        current_process.terminate()

atexit.register(cleanup)

# ================= LANCEMENT =================
threading.Thread(target=start_web, daemon=True).start()

# Boucle infinie propre
while True:
    time.sleep(1)
