from fastapi import FastAPI, Response
import firebase_admin
from firebase_admin import credentials, firestore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from io import BytesIO
from collections import Counter
import datetime

app = FastAPI()

# Inicializamos Firebase Admin SDK SOLO si no está ya inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate("marketandes2025-firebase-adminsdk-fbsvc-89a1f23edf.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.get("/generate-report")
async def generate_report():
    # ===========================================
    # 1. PURCHASE TIME DATA
    # ===========================================
    collection_ref = db.collection("purchaseTime")
    docs = collection_ref.stream()

    elapsed_times = []
    timestamps = []
    user_ids = []

    for doc in docs:
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

    print(f"[INFO] Purchase times: {len(elapsed_times)} registros")

    # ===========================================
    # 2. LOGIN EVENTS DATA
    # ===========================================
    login_ref = db.collection("loginEvents")
    login_docs = login_ref.stream()

    login_devices = []
    login_platforms = []
    login_timestamps = []
    login_user_ids = []

    for doc in login_docs:
        data = doc.to_dict()

        if data.get("event") != "login":
            continue

        login_devices.append(data.get("device", "Desconocido"))
        login_platforms.append(data.get("platform", "Desconocido"))
        login_user_ids.append(data.get("uid"))

        ts = data.get("timestamp")
        if ts:
            try:
                ts_dt = ts
                if hasattr(ts, 'to_datetime'):
                    ts_dt = ts.to_datetime()
                elif isinstance(ts, str):
                    ts_dt = datetime.datetime.fromisoformat(ts)
                login_timestamps.append(ts_dt)
            except Exception as e:
                print(f"Error al convertir timestamp en login: {e}")
                login_timestamps.append(None)
        else:
            login_timestamps.append(None)

    print(f"[INFO] Login events: {len(login_timestamps)} registros")

    # ===========================================
    # 3. SHOPPING REVIEWS DATA
    # ===========================================
    reviews_ref = db.collection("shopping_reviews")
    reviews_docs = reviews_ref.stream()

    ratings = []

    for doc in reviews_docs:
        data = doc.to_dict()
        rating = data.get("rating")
        if rating is not None:
            ratings.append(rating)

    print(f"[INFO] Ratings encontrados: {len(ratings)} registros")

    # ===========================================
    # 4. GENERACIÓN DEL PDF
    # ===========================================
    pdf_buffer = BytesIO()

    with PdfPages(pdf_buffer) as pdf:
        # ===========================================
        # PURCHASE TIME GRÁFICAS
        # ===========================================
        plt.figure(figsize=(8, 6))
        if elapsed_times:
            plt.hist(elapsed_times, bins=10, color='skyblue', edgecolor='black')
        else:
            plt.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=12)
        plt.title("Distribución de Tiempos de Compra")
        plt.xlabel("Tiempo Transcurrido (segundos)")
        plt.ylabel("Cantidad de Compras")
        plt.grid(axis='y', alpha=0.75)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        plt.figure(figsize=(10, 6))
        if user_ids:
            user_purchase_counts = Counter(user_ids)
            usuarios_ordenados = sorted(user_purchase_counts.items(), key=lambda x: x[1], reverse=True)
            etiquetas_usuarios = [f'Usuario {i+1}' for i in range(len(usuarios_ordenados))]
            compras = [item[1] for item in usuarios_ordenados]

            bars = plt.bar(etiquetas_usuarios, compras, color='orange')

            for bar in bars:
                height = bar.get_height()
                plt.annotate(f'{int(height)}',
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3),
                             textcoords="offset points",
                             ha='center', va='bottom', fontsize=8)
        else:
            plt.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=12)

        plt.title("Número de Compras por Usuario")
        plt.xlabel("Usuarios")
        plt.ylabel("Cantidad de Compras")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        plt.figure(figsize=(12, 6))
        valid_times = [(ts, et) for ts, et in zip(timestamps, elapsed_times) if ts is not None]
        if valid_times:
            sorted_times = sorted(valid_times, key=lambda x: x[0])
            sorted_timestamps = [x[0] for x in sorted_times]
            sorted_elapsed = [x[1] for x in sorted_times]

            plt.plot(sorted_timestamps, sorted_elapsed, marker='o', linestyle='-', color='green')
        else:
            plt.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=12)

        plt.title("Evolución de los Tiempos de Compra en el Tiempo")
        plt.xlabel("Fecha y Hora de la Compra")
        plt.ylabel("Tiempo Transcurrido (segundos)")
        plt.xticks(rotation=45, ha="right")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # ===========================================
        # LOGIN EVENTS GRÁFICAS
        # ===========================================
        plt.figure(figsize=(8, 6))
        if login_platforms:
            platform_counts = Counter(login_platforms)
            labels = platform_counts.keys()
            sizes = platform_counts.values()

            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
        else:
            plt.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=12)

        plt.title("Distribución de Logins por Plataforma")
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        plt.figure(figsize=(10, 6))
        if login_devices:
            device_counts = Counter(login_devices)
            dispositivos = [f'Dispositivo {i+1}' for i in range(len(device_counts))]
            cantidades = list(device_counts.values())

            bars = plt.bar(dispositivos, cantidades, color='purple')

            for bar in bars:
                height = bar.get_height()
                plt.annotate(f'{int(height)}',
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3),
                             textcoords="offset points",
                             ha='center', va='bottom', fontsize=8)
        else:
            plt.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=12)

        plt.title("Número de Logins por Dispositivo")
        plt.xlabel("Dispositivos")
        plt.ylabel("Cantidad de Logins")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        plt.figure(figsize=(12, 6))
        valid_login_times = [ts for ts in login_timestamps if ts is not None]
        if valid_login_times:
            sorted_login_times = sorted(valid_login_times)

            plt.hist(sorted_login_times, bins=20, color='red', edgecolor='black')
        else:
            plt.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=12)

        plt.title("Evolución de los Logins en el Tiempo")
        plt.xlabel("Fecha y Hora del Login")
        plt.ylabel("Cantidad de Logins")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis='y', alpha=0.75)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # ===========================================
        # SHOPPING REVIEWS GRÁFICAS
        # ===========================================
        plt.figure(figsize=(8, 6))
        if ratings:
            plt.hist(ratings, bins=range(1, 7), color='gold', edgecolor='black', align='left', rwidth=0.8)
            plt.xticks(range(1, 6))
        else:
            plt.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=12)

        plt.title("Distribución de Calificaciones de Compras")
        plt.xlabel("Calificación")
        plt.ylabel("Cantidad de Reseñas")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    # ===========================================
    # 5. RESPUESTA DEL PDF
    # ===========================================
    pdf_buffer.seek(0)
    print("[INFO] PDF generado con éxito")
    return Response(content=pdf_buffer.read(),
                    media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=reporte_completo.pdf"})
