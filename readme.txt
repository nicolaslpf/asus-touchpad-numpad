# 🧮 Asus Touchpad Numpad for Linux

This script turns your ASUS Vivobook / Zenbook touchpad into a **numeric keypad**, similar to how it works on Windows.  
It detects long presses on the top-right corner of the touchpad to **toggle between normal touchpad and numpad modes** — complete with optional sounds and notifications.

---

## ✨ Features

- 🖱️ Toggle between **Touchpad Mode** and **Numpad Mode** with a long press on the top-right corner  
- 🔢 Simulates keypresses for numbers, operations, and `Enter`  
- 🔊 Optional notification sounds and desktop popups  
- ⚙️ Works automatically via a **systemd service**  
- 🧠 Automatically detects and grabs the touchpad input device when needed  
- 🪄 Fully compatible with GNOME, KDE, and other modern desktop environments

---

## 🧰 Requirements

Tested on:
- **Ubuntu 25.10**
- **Python 3.8+**
- **Asus Vivobook x1405**

### Dependencies
Install these with:

```bash
sudo apt install python3-evdev python3-notify2 python3-gi libnotify-bin pulseaudio-utils

# Copy the files to your user binary folder
sudo cp asus_numpad.py /usr/local/bin/touchpad_numpad.py
sudo chmod +x /usr/local/bin/touchpad_numpad.py

# Instal systemd service
sudo cp numpad_service.service /etc/systemd/system/touchpad-numpad.service

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable touchpad-numpad.service
sudo systemctl start touchpad-numpad.service
```


### 🔧 Usage

Once active, the service runs automatically in the background.

Hold the top-right corner of the touchpad for 2 seconds to toggle between:

- 🖱️ Touchpad Mode

- 🔢 Numpad Mode

Desktop notifications and short sound feedback will indicate mode changes!.
