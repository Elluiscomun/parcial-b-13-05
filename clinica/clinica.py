from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
import pika
import time
import threading

# Configuración de la base de datos
DB_PATH = "/data/clinica.db"  # Ruta dentro del volumen montado por Docker
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

RABBITMQ_HOST = "rabbitmq_clinica"  # Nombre del contenedor RabbitMQ en Docker Compose
QUEUE_NAME = "appointments"

# Crear la tabla si no existe
with sqlite3.connect(DB_PATH) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)

# Inicializar la aplicación FastAPI
app = FastAPI()

while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            break
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ is not ready. Retrying in 5 seconds...")
            time.sleep(5)



# Modelos de datos
class AppointmentCreate(BaseModel):
    patient_name: str

class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    status: str

# Endpoint para crear una reserva
@app.post("/book/", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO appointments (patient_name) VALUES (?, ?)",
            (appointment.patient_name),
        )
        conn.commit()
        appointment_id = cursor.lastrowid
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        row = cursor.fetchone()
    return {"id": row[0], "patient_name": row[1], "status": row[2]}


# Endpoint para consultar el estado de una reserva
@app.get("/book/{id}", response_model=AppointmentResponse)
def get_appointment(id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Appointment not found")
    return {"id": row[0], "patient_name": row[1], "status": row[2]}



# Función para procesar las reservas desde la cola
def process_appointments():
    while True:
        method_frame, header_frame, body = channel.basic_get(queue=QUEUE_NAME, auto_ack=True)
        if body:
            appointment_id = int(body.decode())
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE appointments SET status = 'agendado' WHERE id = ?",
                    (appointment_id,)
                )
                conn.commit()
                print(f"Processed appointment ID: {appointment_id}")
        time.sleep(10)  # Esperar 10 segundos antes de procesar la siguiente

# Iniciar el procesamiento de la cola en un hilo separado
threading.Thread(target=process_appointments, daemon=True).start()