from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket
from routes.ttn_webhook import router as ttn_router
from storage import received_data
import csv
from fastapi.responses import StreamingResponse, JSONResponse
from io import StringIO
from BD.mongo import get_all_payloads
import json
import threading
from routes.bridge_mqqt import start_mqtt

app=FastAPI()


#LLISTA DE JSON, que arribem al node de ttn webhook
threading.Thread(target=start_mqtt, daemon=True).start()

@app.get("/")
def read_root():
    return {"status": "API corriendo"}


#PERMETRE EL CLIENT ACCEDIR A CERTS LLOCS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#S'executa un cop la app esta en marxa
@app.on_event("startup")
async def startup_event():
    print("Application is starting up...")

#S'executa quan es tanca la app
@app.on_event("shutdown")
async def shutdowm_event():
    print("App is shutting down...")

@app.get('/')
async def read_root():
    return {"message" :"Hello,World!"}

#ROUTER PER VEURE TMB el app.get amb direccó ttn
app.include_router(ttn_router)

#GET per poguer veure el json
#cada cop que faci un get al data es fara el return de recevied data

@app.get("/data")
async def get_data():
    return {"data": received_data}
import csv
from fastapi.responses import StreamingResponse
from io import StringIO



#EL RETURN DEL ARXIUS EN DATABASE MONGO

@app.get("/export/csv/mongo")
async def export_csv_mongo():
    payloads = get_all_payloads()
    return export_mongo_payloads(payloads)


# EXPORTAR SOLO DATOS DE SENSORES 
@app.get("/export/csv/sensors")
async def export_csv_sensors():
    payloads = get_all_payloads()
    sensor_data = [item for item in payloads if item.get("uplink_message")]

    if not sensor_data:
        return {"message": "No hay datos de sensores"}

    output = StringIO()
    writer = None
    for item in sensor_data:
        clean_item = {k: str(v) for k, v in item.items()}
        if writer is None:
            writer = csv.DictWriter(output, fieldnames=clean_item.keys())
            writer.writeheader()
        writer.writerow(clean_item)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sensors_data.csv"}
    )

# EXPORTAR SOLO MENSAJES DE APP 
@app.get("/export/csv/app")
async def export_csv_app():
    payloads = get_all_payloads()
    app_messages = [item for item in payloads if not item.get("uplink_message")]

    if not app_messages:
        return {"message": "No hay mensajes de app"}

    output = StringIO()
    writer = None
    for item in app_messages:
        clean_item = {k: str(v) for k, v in item.items()}
        if writer is None:
            writer = csv.DictWriter(output, fieldnames=clean_item.keys())
            writer.writeheader()
        writer.writerow(clean_item)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=app_messages.csv"}
    )



def export_mongo_payloads(payloads, filename="mongo_data.csv"):
    if not payloads:
        return {"message": "No hay datos para exportar"}

    # Obtener todos los campos posibles
    fieldnames = set()
    for item in payloads:
        fieldnames.update(item.keys())
    fieldnames = list(fieldnames)

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for item in payloads:
        row = {}
        for field in fieldnames:
            value = item.get(field, "")
            if isinstance(value, (dict, list)):
                row[field] = json.dumps(value, ensure_ascii=False)
            else:
                row[field] = str(value)
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )




