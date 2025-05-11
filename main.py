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
    allow_origins=["*"], 
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
    # Chats Cerrados
    # Chats Cerrados: calcular duración real entre apertura y cierre
    chats_cerrados_ref = db.collection("chatsCerrados")
    chats_cerrados_docs = chats_cerrados_ref.stream()

    chats_cerrados_data = []
    for doc in chats_cerrados_docs:
        data = doc.to_dict()
        time_opened = data.get("timeOpened")
        time_closed = data.get("timeClosed")

        if isinstance(time_opened, datetime.datetime) and isinstance(time_closed, datetime.datetime):
            duracion = (time_closed - time_opened).total_seconds() / 60  # duración en minutos
            chats_cerrados_data.append({
                "chat_id": data.get("chatId", "")[:6] + "...",
                "duracion_min": round(duracion, 2)  
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
        "chats": chats_days_data,
        "chats_cerrados": chats_cerrados_data
    }


@app.get("/favoritos-promedio-compra")
async def favoritos_promedio_compra():
    # Obtener todos los usuarios
    users_ref = db.collection("users")
    users_docs = users_ref.stream()

    # Diccionario para guardar la cantidad de favoritos por usuario
    uid_to_favoritos_count = {}

    for doc in users_docs:
        data = doc.to_dict()
        uid = data.get("uid")
        favoritos = data.get("favoritos", [])
        if isinstance(favoritos, list):
            uid_to_favoritos_count[uid] = len(favoritos)
        else:
            uid_to_favoritos_count[uid] = 0  # Si no tiene lista, se asume 0 favoritos

    # Obtener todos los tiempos de compra
    purchase_ref = db.collection("purchaseTime")
    purchase_docs = purchase_ref.stream()

    # Agrupar tiempos de compra por cantidad de favoritos
    favoritos_to_elapsed_times = {}

    for doc in purchase_docs:
        data = doc.to_dict()
        uid = data.get("uid")
        elapsed = data.get("elapsedTime")
        if uid is None or elapsed is None:
            continue

        count_favoritos = uid_to_favoritos_count.get(uid)
        if count_favoritos is None:
            continue  # No se encuentra el usuario o no tiene favoritos

        if count_favoritos not in favoritos_to_elapsed_times:
            favoritos_to_elapsed_times[count_favoritos] = []

        favoritos_to_elapsed_times[count_favoritos].append(elapsed)

    # Calcular promedio para cada cantidad de favoritos
    resultado = {}
    for count, times in favoritos_to_elapsed_times.items():
        if times:
            promedio = sum(times) / len(times)
            resultado[count] = round(promedio, 2)

    return resultado

