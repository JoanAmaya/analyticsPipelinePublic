from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
from collections import Counter

app = FastAPI()

# CORS para permitir acceso desde el frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir esto al dominio de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not firebase_admin._apps:
    cred = credentials.Certificate("marketandes2025-firebase-adminsdk-fbsvc-89a1f23edf.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.get("/metrics-data")
async def get_metrics():
    # Compra
    purchase_ref = db.collection("purchaseTime")
    purchase_docs = purchase_ref.stream()

    elapsed_times = []
    timestamps = []
    user_ids = []

    for doc in purchase_docs:
        data = doc.to_dict()
        elapsed_times.append(data.get("elapsedTime", 0))
        ts = data.get("timestamp")
        if ts:
            try:
                ts_dt = ts
                if hasattr(ts, 'to_datetime'):
                    ts_dt = ts.to_datetime()
                elif isinstance(ts, str):
                    ts_dt = datetime.datetime.fromisoformat(ts)
                timestamps.append(ts_dt)
            except Exception as e:
                print(f"Error al convertir timestamp: {e}")
                timestamps.append(None)
        else:
            timestamps.append(None)

        user_ids.append(data.get("uid"))

    # Login
    login_ref = db.collection("loginEvents")
    login_docs = login_ref.stream()

    login_devices = []
    login_platforms = []
    login_timestamps = []

    for doc in login_docs:
        data = doc.to_dict()
        if data.get("event") != "login":
            continue
        login_devices.append(data.get("device", "Desconocido"))
        login_platforms.append(data.get("platform", "Desconocido"))
        ts = data.get("timestamp")
        try:
            ts_dt = ts.to_datetime() if hasattr(ts, 'to_datetime') else datetime.datetime.fromisoformat(ts)
            login_timestamps.append(ts_dt.isoformat())
        except:
            login_timestamps.append(None)

    # Reviews
    reviews_ref = db.collection("shopping_reviews")
    reviews_docs = reviews_ref.stream()
    ratings = [doc.to_dict().get("rating") for doc in reviews_docs if doc.to_dict().get("rating") is not None]

    # Chats
    chats_ref = db.collection("chatsFlutter")
    chats_docs = chats_ref.stream()
    now = datetime.datetime.now(datetime.timezone.utc)
    chats_days_data = []

    for doc in chats_docs:
        data = doc.to_dict()
        razon = data.get("Razon", "Sin razón")
        time_begin = data.get("timeBegin")

        dias = None
        if isinstance(time_begin, datetime.datetime):
            diferencia = now - time_begin
            dias = diferencia.days

        chats_days_data.append({
            "razon": razon,
            "dias_desde_ultima_interaccion": dias
        })

    return {
        "purchase": {
            "elapsed_times": elapsed_times,
            "timestamps": timestamps,
            "user_counts": dict(Counter(user_ids))
        },
        "login": {
            "devices": dict(Counter(login_devices)),
            "platforms": dict(Counter(login_platforms)),
            "timestamps": login_timestamps
        },
        "reviews": {
            "ratings": ratings
        },
        "chats": chats_days_data
    }
