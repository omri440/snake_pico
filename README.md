# 🐍 Pico Snake Game with WebSocket

This project is a real-time Snake game running on a Raspberry Pi Pico W, with GPIO button control and live gameplay rendered in the browser using WebSocket.

---

## 📦 Features

- Multiplayer-style broadcast via WebSocket
- Real-time drawing using HTML `<canvas>`
- Control snake via 2 GPIO buttons (left/right rotation)
- Detects self-collision (game over)
- Dynamic speed: gets faster every time you eat
- Restart button in browser

---

## 🔧 Hardware Required

- Raspberry Pi Pico W
- 2 Push Buttons (for turning)
- Breadboard + Jumper Wires

### Button wiring:
- Connect button 1 to GPIO14 and GND  
- Connect button 2 to GPIO15 and GND  
- Code uses internal `Pin.PULL_UP`, no resistors needed

---

## 🌐 Setup

### 1. Install MicroPython firmware on your Pico W  
Follow [official guide](https://micropython.org/download/rp2-pico-w/)

### 2. Upload Files
- `main.py` — server + game logic
- `index.html` — client UI
- Use Thonny or rshell to upload

### 3. Set WiFi
Update SSID and password in `main.py`:

```python
ssid = 'Your_SSID'
password = 'Your_PASSWORD'
