# Minitel Web Controller

Interface web tactile pour piloter un Minitel depuis un **Raspberry Pi 5**.

Ce projet permet de sélectionner un serveur Minitel distant directement depuis l'écran tactile du Raspberry Pi, puis de lancer ou d'arrêter la connexion série USB sans avoir à utiliser le terminal.

La communication entre le serveur distant et le Minitel est assurée par le projet [`websocket2minitel`](https://github.com/cquest/websocket2minitel) de [cquest](https://github.com/cquest).

## ✨ Fonctionnalités

- 🖥️ Interface web adaptée à un écran tactile.
- 📡 Sélection du serveur Minitel depuis une liste déroulante.
- 🔌 Connexion au Minitel via un port série USB.
- ▶️ Lancement du client `websocket2minitel` depuis l'interface.
- ⏹️ Arrêt de la connexion depuis un bouton dédié.
- 📊 Affichage du serveur sélectionné et de l'état du script.
- 🌐 Accès à l'interface depuis le Raspberry Pi ou un autre appareil du réseau local.

## 🧰 Matériel

- Raspberry Pi 5.
- Écran tactile connecté au Raspberry Pi.
- Minitel compatible avec une interface série USB.
- Câble ou adaptateur USB-série adapté au Minitel.
- Connexion réseau pour accéder aux serveurs distants.

## 🏗️ Architecture

```text
┌──────────────────────────────────┐
│          Écran tactile           │
│       Interface web Flask        │
│                                  │
│  Sélection serveur / Connexion   │
│           Déconnexion            │
└────────────────┬─────────────────┘
                 │ HTTP
                 ▼
┌──────────────────────────────────┐
│       Raspberry Pi 5             │
│                                  │
│   Contrôleur Python + Flask      │
│                │                 │
│                ▼                 │
│         websocket2minitel        │
│                │                 │
│                ▼                 │
│          USB / Série             │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│             Minitel              │
└──────────────────────────────────┘

       websocket2minitel
                 │
                 ▼
        Serveur distant WebSocket
```

## 🌐 Serveurs disponibles

Les serveurs sont configurés directement dans le script Python.

| Nom | Adresse |
|---|---|
| MiniPAVI | `wss://go.minipavi.fr:8181` |
| Hacker | `ws://mntl.joher.com:2018` |
| Annuaire | `ws://3611.re/ws` |
| 3615 | `ws://3615co.de/ws` |
| Retrocampus | `wss://bbs.retrocampus.com:8051` |
| LABBEJ27 | `wss://minitel.labbej.fr:8182` |

Le serveur sélectionné par défaut est `LABBEJ27`.

## 📦 Installation

### 1. Installer les dépendances système

Sur Raspberry Pi OS :

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

### 2. Installer websocket2minitel

Cloner le projet de référence :

```bash
cd ~
git clone https://github.com/cquest/websocket2minitel.git
cd websocket2minitel
```

Créer et activer son environnement virtuel :

```bash
python3 -m venv venv
source venv/bin/activate
```

Installer les dépendances indiquées par le projet :

```bash
# Si le dépôt fournit un requirements.txt
pip install -r requirements.txt
```

Consulter le README de [`websocket2minitel`](https://github.com/cquest/websocket2minitel) pour les éventuelles étapes supplémentaires.

### 3. Installer l'interface web

Placer le script de contrôle Python dans le répertoire souhaité, puis installer Flask dans l'environnement Python utilisé pour exécuter ce script.

Par exemple, si le contrôleur utilise son propre environnement virtuel :

```bash
cd ~/minitel-web-controller
python3 -m venv venv
source venv/bin/activate
pip install flask
```

Adapter le chemin du répertoire `minitel-web-controller` à l'emplacement réel du projet.

## ⚙️ Configuration

Les paramètres principaux sont définis au début du script Python :

```python
PROJET2_PYTHON = "/home/labbej/websocket2minitel/venv/bin/python"
PROJET2_SCRIPT = "/home/labbej/websocket2minitel/websocket2minitel.py"
SERIAL_PORT = "/dev/ttyUSB0"
```

**À adapter à ton installation :**

- `PROJET2_PYTHON` : chemin vers l'interpréteur Python de l'environnement virtuel de `websocket2minitel`.
- `PROJET2_SCRIPT` : chemin vers le script `websocket2minitel.py`.
- `SERIAL_PORT` : port série du Minitel, généralement `/dev/ttyUSB0` ou `/dev/ttyACM0`, selon l'adaptateur.

La liste des serveurs peut être modifiée dans le dictionnaire `SERVEURS` du script.

### Accès au port série

Vérifier que l'adaptateur USB-série est détecté :

```bash
ls /dev/ttyUSB*
ls /dev/ttyACM*
```

Si nécessaire, ajouter l'utilisateur au groupe donnant accès au port série :

```bash
sudo usermod -aG dialout "$USER"
```

Une reconnexion de la session peut être nécessaire pour appliquer ce changement.

## 🚀 Utilisation

### Démarrer l'interface

Lancer le contrôleur Python :

```bash
python3 app.py
```

Remplacer `app.py` par le nom réel du fichier contenant le code du contrôleur.

Le serveur Flask écoute sur le port `8080` et rend l'interface accessible sur toutes les interfaces réseau du Raspberry Pi.

### Ouvrir l'interface

Depuis le navigateur du Raspberry Pi :

```text
http://localhost:8080
```

Depuis un autre appareil connecté au même réseau, utiliser l'adresse IP du Raspberry Pi :

```text
http://IP_DU_RASPBERRY:8080
```

### Se connecter à un serveur Minitel

1. Sélectionner le serveur distant dans la liste.
2. Appuyer sur **APPLIQUER**.
3. Appuyer sur **CONNEXION** pour lancer `websocket2minitel`.
4. Utiliser le Minitel normalement.
5. Appuyer sur **DÉCONNEXION** pour arrêter le script.

L'interface affiche le serveur sélectionné et l'état du processus piloté.

## 🔄 Fonctionnement technique

L'interface repose sur :

- **Flask** pour le serveur web et les routes HTTP.
- **HTML et CSS** pour une interface sombre, responsive et adaptée au tactile.
- **Python `subprocess`** pour démarrer et arrêter `websocket2minitel`.
- **WebSocket** pour la connexion au serveur Minitel distant.
- **USB série** pour la communication avec le Minitel.

Lorsqu'une connexion est demandée, le contrôleur lance le script externe avec l'adresse du serveur choisi et le port série configuré.

Lors d'une déconnexion, il envoie d'abord un signal d'interruption au processus, puis tente de le terminer si nécessaire.

## 🛠️ Dépannage

### Le Minitel ne répond pas

- Vérifier le branchement de l'adaptateur USB-série.
- Vérifier le port défini dans `SERIAL_PORT`.
- Vérifier les permissions de l'utilisateur sur le port série.
- Tester le fonctionnement de `websocket2minitel` indépendamment de l'interface web.

### L'interface web ne démarre pas

Vérifier que Flask est installé dans l'environnement Python utilisé :

```bash
python3 -m pip install flask
```

Vérifier également que le port `8080` n'est pas déjà utilisé.

### La connexion au serveur échoue

- Vérifier la connexion réseau du Raspberry Pi.
- Vérifier l'adresse WebSocket configurée.
- Vérifier que le serveur distant est disponible.
- Consulter les messages affichés dans le terminal qui exécute le contrôleur.

### Le port série n'est pas détecté

```bash
dmesg | tail -n 30
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

## 🔒 Sécurité

L'interface actuelle ne comporte pas de mécanisme d'authentification et écoute sur toutes les interfaces réseau (`0.0.0.0:8080`).

Il est donc recommandé de l'utiliser sur un réseau local de confiance et de ne pas exposer directement le port `8080` à Internet.

## 🙏 Crédits

- [`cquest/websocket2minitel`](https://github.com/cquest/websocket2minitel) — client de communication entre WebSocket et Minitel.
- Les serveurs Minitel distants référencés dans la configuration.

---

*Projet personnel : transformer un Raspberry Pi 5 équipé d'un écran tactile en console de sélection et de contrôle de serveurs Minitel.*
