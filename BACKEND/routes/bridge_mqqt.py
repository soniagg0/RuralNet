import json
import requests
import paho.mqtt.client as mqtt

APP_ID = "app-pbe2@pbe2"
ACCES_KEY = "NNSXS.BVMOPBFYN2MZCWJCOXBWTSYY6A6WBV544QCQBVI.PEIH3XJFNSVW7URY7STYMD3G32AIFWQIDK3OPMFZRJ3QKJO4D4BA"
BROKER = "eu1.cloud.thethings.industries"
DEVICE_ID = "arduino-pbe2"
PORT = 1883  # cSon cifrado
TOPIC_UP = f"v3/{APP_ID}/devices/{DEVICE_ID}/up"
TOPIC_DOWN = f"v3/{APP_ID}/devices/{DEVICE_ID}/down"
API_URL = "http://127.0.0.1:8000/webhook/ttn"


# client global per publicar
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(APP_ID, ACCES_KEY)
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()  # no bloqueja el FastAPI


# Función de conexión
def on_connect(client, userdata, flags, rc):
    print("Conectado a TTN con código:", rc)
    client.subscribe(TOPIC_UP)
    print("Subscrito al topic:", TOPIC_UP)

# Función que maneja mensajes recibidos
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print("Mensaje recibido de TTN:", json.dumps(payload, indent=2))

        # Enviar a tu API
        response = requests.post(API_URL, json=payload)
        print("Mensaje enviado a API, status:", response.status_code)
    except Exception as e:
        print("Error procesando mensaje:", e)

def start_mqtt():
    # CREAR CLIENTE MQTT
    client = mqtt.Client()
    client.username_pw_set(APP_ID, ACCES_KEY)
    #client.tls_set() security 
    client.on_connect = on_connect
    client.on_message = on_message
    # CONEXIÓN Y LOOP
    client.connect(BROKER, PORT, 60)
    client.loop_forever()


#AQUÍ FARE ER ENVIAR ELS MISATGES DOWNLINK DE LA APP A TTN
def send_downlink(payload: dict):

    downlink_msg = {
        "downlinks": [
            {
                "f_port": 1,
                "frm_payload": json.dumps(payload).encode("utf-8").hex(),
                "priority": "NORMAL"
            }
        ]
    }
    mqtt_client.publish(TOPIC_DOWN, json.dumps(downlink_msg))
    print("Downlink enviat a TTN:", downlink_msg)
