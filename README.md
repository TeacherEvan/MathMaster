Excellent brain training. 

can run the file from the welcomescreen.py or create a desktop shortcut copy and run from desktop

## 📥 Installation & Play Guide

Below are step-by-step instructions for running **MathMaster** on the two most-requested platforms: macOS and Android.  The game ships in two flavours – a desktop Python build (Tkinter) and a browser-based HTML/JS build.  Choose whichever experience best suits your device.

### macOS

#### 1. Web (No install required – Recommended)
1. Download or clone this repository.
2. In Finder, double-click **`index.html`** (or right-click ➜ *Open With* ➜ *Safari/Chrome*).  The game will load instantly in your default browser – no internet connection or extra packages needed.
3. Play with your mouse/track-pad.  Press *⌘ + Q* or simply close the tab when you are finished.

*Troubleshooting*: If macOS blocks local file URLs, start a tiny local server from Terminal:
```bash
cd path/to/MathMaster
python3 -m http.server 8000
```
Then visit `http://localhost:8000/index.html` in your browser.

#### 2. Native Python Desktop App (Full-screen Tkinter build)
Prerequisites: Python 3.9 + (with Tk support – the Python.org installer and Homebrew builds already include this).

```bash
# Install Python via Homebrew if you don’t have it already
brew install python

# Grab the project
git clone https://github.com/your-repo/MathMaster.git
cd MathMaster

# (Optional) create a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# No external packages are required – everything is in the standard library
python welcome_screen.py
```
The window launches in full-screen; press the **Esc** key at any time to exit.

---

### Android

#### 1. Web (Zero-install – Works on every modern phone)
1. Copy the project folder to your phone **OR** download the latest release ZIP and extract it.
2. Open a mobile browser (Chrome, Firefox, Samsung Internet, etc.).
3. Use your file-manager app to locate `index.html`, tap it, and choose the browser to open it.
4. Enjoy the game with touch controls – single taps reveal solution characters.

*Tip*: Some browsers restrict direct file access.  If `index.html` does not open, run a tiny web-server:
   • Install **Termux** from F-Droid or Play Store.  
   • Run the following commands inside the project folder:
   ```bash
   pkg install python -y
   python -m http.server 8080
   ```
   • Open `http://127.0.0.1:8080` in Chrome.

#### 2. Python (Experimental – Requires Pydroid 3)
Tkinter is not natively supported on Android, but you can still try the desktop build:
1. Install **Pydroid 3** from the Google Play Store, then open the in-app *Plugin* menu and install the **Tkinter** add-on.
2. Copy this repository into the `Pydroid3/scripts` directory (`/storage/emulated/0/Pydroid3/scripts`).
3. In Pydroid 3, browse to **`welcome_screen.py`** and press the ▶️ Run button.
4. Use touch input (or a Bluetooth mouse/keyboard) to interact.  Performance varies by device – the HTML build is generally smoother on phones.

---

### General Controls
• Click (or tap) individual characters to reveal solution steps.  
• Press **Esc** (desktop) or the back gesture/button (Android) to exit.
