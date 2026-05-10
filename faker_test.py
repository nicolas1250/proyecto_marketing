from faker import Faker
from dotenv import load_dotenv
import requests
import random
import os
import time

load_dotenv()

fake = Faker("es_ES")

# Url de n8n webhook

url = os.getenv("WEBHOOK_URL")

# Opciones del formulario

tipos_clientes=[
    "Mayorista / Distribuidor",
    "Minorista / Tienda",
    "Partticular",
    "Empresa / Corporativo",
]

plataformas_disponibles=[
    "PlayStation 5",
    "Xbox Series X/S",
    "Nintendo Switch",
    "PC Gaming",
    "Accesorios",
    "Solo juegos"
]

cantidades = [
    "1 - 5 unidades",
    "6 - 20 unidades",
    "21 - 50 unidades",
    "Mas de 50 unidades"
]

presupuestos = [
    "Menos de 1.000.000",
    "1.000.000 - 5.000.000",
    "5.000.000 - 20.000.000",
    "Mas de 20.000.000"
]

canales = [
    "Google / Busqueda",
    "Instagram",
    "Facebook",
    "TikTok",
    "Referido",
    "Otro"
]

mensajes = [
    "",
    "Quiero cotizar consolas para mi tienda.",
    "Estoy buscando precios al por mayor.",
    "Necesito accesorios para gaming.",
    "Me interesa comprar varias unidades.",
    "Quiero más información de disponibilidad.",
    "Busco productos para reventa.",
    "Estoy comparando opciones."
]

# Generador de datos falsos

for i in range(20):

    plataformas = random.sample(plataformas_disponibles,random.randint(1, 3))

    datos = {
        "nombre": fake.name(),
        "empresa": fake.company(),
        "email": fake.email(),
        "telefono": fake.msisdn()[:10],
        "ciudad": fake.city(),

        "tipo_cliente": random.choice(tipos_clientes),

        # checkbox múltiple
        "plataformas": ", ".join(plataformas),

        "cantidad": random.choice(cantidades),

        "presupuesto": random.choice(presupuestos),

        "mensaje": random.choice(mensajes),

        "canal": random.choice(canales)
    }
   # Envio de datos al webhook
    respuesta = requests.post(url, json=datos)
    print(f"\nRegistro {i+1}")
    print(datos)
    print("Status:", respuesta.status_code)

    time.sleep(10)  # Pausa de  entre registros
 