# snake_game_pico/main.py
import network
import time
import uasyncio as asyncio
from microdot import Microdot, send_file
from microdot.websocket import with_websocket
import json
import random
from machine import Pin

btn_left = Pin(14, Pin.IN, Pin.PULL_UP)
btn_right = Pin(15, Pin.IN, Pin.PULL_UP)

ssid = 'wifi-name'
password = 'password'

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(ssid, password)
        timeout = 10
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                print("Connection timed out")
                return
            time.sleep(1)
    print("✅ Connected! IP =", wlan.ifconfig()[0])

connect_to_wifi()

app = Microdot()

BOARD_SIZE = 10
snake = []
food = []
dir = 1  # 0=up, 1=down, 2=right, 3=left
score = 0
game_over = False
speed = 0.3  # זמן התחלה בין צעדים

# direction deltas
UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3
dx = [0, 0, 1, -1]
dy = [-1, 1, 0, 0]

# direction transitions
STATE_TRANSITIONS = {
    (DOWN, 'left'): RIGHT,
    (DOWN, 'right'): LEFT,
    (UP, 'left'): LEFT,
    (UP, 'right'): RIGHT,
    (LEFT, 'left'): DOWN,
    (LEFT, 'right'): UP,
    (RIGHT, 'left'): UP,
    (RIGHT, 'right'): DOWN
}

def reset_game():
    global snake, dir, food, score, game_over, speed
    snake = [[5, 5], [5, 4], [5, 3]]
    dir = DOWN
    food = [random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)]
    score = 0
    game_over = False
    speed = 0.3

reset_game()

async def handle_buttons():
    global dir
    while True:
        action = None
        if btn_left.value() == 0:
            action = 'left'
        elif btn_right.value() == 0:
            action = 'right'

        if action:
            key = (dir, action)
            if key in STATE_TRANSITIONS:
                dir = STATE_TRANSITIONS[key]
            await asyncio.sleep(0.2)

        await asyncio.sleep(0.01)

def move_snake():
    global snake, dir, food, score, game_over, speed

    if game_over:
        return

    head_x, head_y = snake[0]
    new_head = [(head_x + dx[dir]) % BOARD_SIZE, (head_y + dy[dir]) % BOARD_SIZE]

    if new_head in snake:
        game_over = True
        return

    new_snake = [new_head]
    for i in range(len(snake) - 1):
        new_snake.append(snake[i])
    snake[:] = new_snake

    if new_head == food:
        snake.append(snake[-1])
        score += 1
        speed = max(0.05, speed - 0.01)  # הגבלת מינימום מהירות
        food[:] = [random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)]

snake_clients = set()

async def broadcast_snake_state():
    global speed
    while True:
        move_snake()
        data = json.dumps({
            'snake': snake,
            'food': food,
            'score': score,
            'game_over': game_over
        })
        for client in list(snake_clients):
            try:
                await client.send(data)
            except:
                snake_clients.remove(client)
        await asyncio.sleep(speed if not game_over else 1.0)

@app.route('/')
async def index(req):
    return send_file('index.html')

@app.route('/snake')
@with_websocket
async def snake_ws(request, ws):
    snake_clients.add(ws)
    try:
        while True:
            try:
                msg = await asyncio.wait_for(ws.receive(), timeout=0.5)
                if msg == "reset":
                    reset_game()
            except asyncio.TimeoutError:
                pass
    except:
        pass
    finally:
        snake_clients.remove(ws)

async def main():
    asyncio.create_task(handle_buttons())
    asyncio.create_task(broadcast_snake_state())
    app.run(port=80)

asyncio.run(main())
