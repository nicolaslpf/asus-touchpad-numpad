#!/usr/bin/env python3
import evdev
from evdev import InputDevice, ecodes, UInput
import time
import subprocess
import os

# -------------------------------
# Sonidos de toggle
# -------------------------------
SOUND_ON = "/usr/share/sounds/freedesktop/stereo/complete.oga"
SOUND_OFF = "/usr/share/sounds/freedesktop/stereo/device-removed.oga"

# -------------------------------
# Detectar touchpad
# -------------------------------
dev = None
for i in range(32):
    try:
        d = InputDevice(f"/dev/input/event{i}")
        if 'touchpad' in d.name.lower() or 'synaptics' in d.name.lower():
            dev = d
            break
    except FileNotFoundError:
        continue

if not dev:
    print("❌ No se detectó el touchpad")
    exit(1)

# -------------------------------
# Rango de coordenadas
# -------------------------------
caps = dev.capabilities(absinfo=True)
abs_info = caps.get(ecodes.EV_ABS, [])

x_info = y_info = None
for code, info in abs_info:
    if code == ecodes.ABS_X:
        x_info = info
    elif code == ecodes.ABS_Y:
        y_info = info

if not x_info or not y_info:
    print("❌ No se detectaron coordenadas válidas")
    exit(1)

X_MIN, X_MAX = x_info.min, x_info.max
Y_MIN, Y_MAX = y_info.min, y_info.max
WIDTH = X_MAX - X_MIN
HEIGHT = Y_MAX - Y_MIN

# -------------------------------
# Mapeo de teclas
# -------------------------------
KEY_MAP = {
    '0': ecodes.KEY_0, '1': ecodes.KEY_1, '2': ecodes.KEY_2, '3': ecodes.KEY_3,
    '4': ecodes.KEY_4, '5': ecodes.KEY_5, '6': ecodes.KEY_6, '7': ecodes.KEY_7,
    '8': ecodes.KEY_8, '9': ecodes.KEY_9, '.': ecodes.KEY_DOT, '+': ecodes.KEY_KPPLUS,
    '-': ecodes.KEY_MINUS, '*': ecodes.KEY_KPASTERISK, '/': ecodes.KEY_SLASH,
    'enter': ecodes.KEY_ENTER, '=': ecodes.KEY_EQUAL, 'backspace': ecodes.KEY_BACKSPACE,
}
KEY_MAP_SHIFT = {'%': ecodes.KEY_5}

ui = UInput({ecodes.EV_KEY: list(KEY_MAP.values()) + [ecodes.KEY_LEFTSHIFT]},
            name="Virtual Touchpad Numpad")

# -------------------------------
# Layout numpad
# -------------------------------
rows, cols = 4, 5
row_height, col_width = HEIGHT / rows, WIDTH / cols
KEY_RECTS = [
    (0*col_width, 1*col_width, 0*row_height, 1*row_height, '7'),
    (1*col_width, 2*col_width, 0*row_height, 1*row_height, '8'),
    (2*col_width, 3*col_width, 0*row_height, 1*row_height, '9'),
    (3*col_width, 4*col_width, 0*row_height, 1*row_height, '/'),
    (4*col_width, WIDTH,       0*row_height, 1*row_height, 'backspace'),

    (0*col_width, 1*col_width, 1*row_height, 2*row_height, '4'),
    (1*col_width, 2*col_width, 1*row_height, 2*row_height, '5'),
    (2*col_width, 3*col_width, 1*row_height, 2*row_height, '6'),
    (3*col_width, 4*col_width, 1*row_height, 2*row_height, '*'),
    (4*col_width, WIDTH,       1*row_height, 2*row_height, 'backspace'),

    (0*col_width, 1*col_width, 2*row_height, 3*row_height, '1'),
    (1*col_width, 2*col_width, 2*row_height, 3*row_height, '2'),
    (2*col_width, 3*col_width, 2*row_height, 3*row_height, '3'),
    (3*col_width, 4*col_width, 2*row_height, 3*row_height, '-'),
    (4*col_width, WIDTH,       2*row_height, 3*row_height, '%'),

    (0*col_width, 1*col_width, 3*row_height, HEIGHT,       '0'),
    (1*col_width, 2*col_width, 3*row_height, HEIGHT,       '.'),
    (2*col_width, 3*col_width, 3*row_height, HEIGHT,       'enter'),
    (3*col_width, 4*col_width, 3*row_height, HEIGHT,       '+'),
    (4*col_width, WIDTH,       3*row_height, HEIGHT,       '='),
]

# -------------------------------
# Hotspot esquina superior derecha
# -------------------------------
HOT_X_MIN, HOT_X_MAX = WIDTH * 0.80, WIDTH
HOT_Y_MIN, HOT_Y_MAX = 0, HEIGHT * 0.25
HOLD_TIME, DEBOUNCE_TIME = 0.8, 0.3

# -------------------------------
# Estados
# -------------------------------
numpad_enabled = False
touch_active = False
touch_start_time = 0
touch_start_x = 0
touch_start_y = 0
key_emitted = False
x = y = 0

# -------------------------------
# Funciones auxiliares
# -------------------------------
def play_sound(enable=True):
    sound_file = SOUND_ON if enable else SOUND_OFF
    try:
        env = os.environ.copy()
        env["XDG_RUNTIME_DIR"] = f"/run/user/{os.getuid()}"
        subprocess.Popen(['paplay', sound_file],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    except Exception as e:
        print(f"⚠️ No se pudo reproducir sonido: {e}")

def show_notification(enable=True):
    msg = "✅ Numpad ACTIVADO" if enable else "❌ Numpad DESACTIVADO"
    try:
        env = os.environ.copy()
        env["DISPLAY"] = ":0"
        env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{os.getuid()}/bus"
        subprocess.Popen(['notify-send', '-t', '1500', 'Touchpad Numpad', msg],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    except Exception as e:
        print(f"⚠️ No se pudo mostrar notificación: {e}")

def emit_key(key):
    if key in KEY_MAP_SHIFT:
        ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTSHIFT, 1)
        ui.syn()
        ui.write(ecodes.EV_KEY, KEY_MAP_SHIFT[key], 1)
        ui.syn()
        time.sleep(0.01)
        ui.write(ecodes.EV_KEY, KEY_MAP_SHIFT[key], 0)
        ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTSHIFT, 0)
        ui.syn()
    elif key in KEY_MAP:
        ui.write(ecodes.EV_KEY, KEY_MAP[key], 1)
        ui.syn()
        time.sleep(0.01)
        ui.write(ecodes.EV_KEY, KEY_MAP[key], 0)
        ui.syn()

# -------------------------------
# Loop principal
# -------------------------------
print("🎹 Touchpad Numpad iniciado")
print("📍 Mantén presionado esquina superior derecha 2 seg para activar/desactivar")
print("⚠️  Usa Ctrl+C para salir")
print("="*70)

try:
    for event in dev.read_loop():
        # Actualizar coordenadas
        if event.type == ecodes.EV_ABS:
            if event.code in (ecodes.ABS_X, ecodes.ABS_MT_POSITION_X):
                x = event.value
            elif event.code in (ecodes.ABS_Y, ecodes.ABS_MT_POSITION_Y):
                y = event.value

        elif event.type == ecodes.EV_KEY and event.code == 330:  # BTN_TOUCH
            if event.value == 1:
                touch_active = True
                touch_start_time = time.time()
                touch_start_x, touch_start_y = x, y
                key_emitted = False
            elif event.value == 0:
                touch_active = False
                key_emitted = False

        # Detectar toggle (mantener 2 seg esquina superior derecha)
        if touch_active:
            duration = time.time() - touch_start_time
            in_hotspot = (HOT_X_MIN <= touch_start_x <= HOT_X_MAX and
                          HOT_Y_MIN <= touch_start_y <= HOT_Y_MAX)
            if in_hotspot and duration >= HOLD_TIME:
                numpad_enabled = not numpad_enabled
                play_sound(numpad_enabled)
                show_notification(numpad_enabled)

                if numpad_enabled:
                    try:
                        dev.grab()
                        print("🔢 Numpad ACTIVADO (grabbed)")
                    except OSError as e:
                        print(f"⚠️ Error al hacer grab: {e}")
                else:
                    try:
                        dev.ungrab()
                        print("🖱️ Numpad DESACTIVADO (released)")
                    except OSError as e:
                        print(f"⚠️ Error al hacer ungrab: {e}")

                touch_active = False
                key_emitted = True
                continue

        # Emitir tecla si numpad activo
        if numpad_enabled and touch_active and not key_emitted:
            if not (HOT_X_MIN <= touch_start_x <= HOT_X_MAX and HOT_Y_MIN <= touch_start_y <= HOT_Y_MAX):
                for x_min, x_max, y_min, y_max, k in KEY_RECTS:
                    if x_min <= touch_start_x < x_max and y_min <= touch_start_y < y_max:
                        emit_key(k)
                        key_emitted = True
                        break

except KeyboardInterrupt:
    print("\n\n✓ Touchpad Numpad detenido")
finally:
    try:
        dev.ungrab()
    except:
        pass
    ui.close()
