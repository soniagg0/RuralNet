
from fastapi import APIRouter, Request
import json
from storage import received_data
from BD.mongo import insert_ttn_payload_bd, get_all_payloads
from bson import ObjectId
from routes.bridge_mqqt import APP_ID, ACCES_KEY, API_URL
from routes.bridge_mqqt import send_downlink


router=APIRouter()

@router.post("/webhook/ttn")
async def ttn_webhook(request: Request):
    payload = await request.json()
    received_data.append(payload)
    insert_ttn_payload_bd(payload)
    payload_to_print = jsonify_payload(payload)
    print(" TTN payload recibido:", json.dumps(payload_to_print, indent=2))
    # PER VEURE QUE S'HA REBUT OK


    #COM QUE EN EL FRONT SHA POSAT QUE AQUELLS MISATGES SON DEL TIPUS "status" fem distinció i mirem quin és estatus i quin no
    #Si es estatus fer downlink a ttn

    if "status" in payload:
        send_downlink(payload)

    return {"status": "ok", "data": payload}


def jsonify_payload(payload):
    if "_id" in payload and isinstance(payload["_id"], ObjectId):
        payload["_id"] = str(payload["_id"])
    return payload

@router.get("/ttn/data")
def get_ttn_data():
    data=get_all_payloads()
    return{"data is":  data}

