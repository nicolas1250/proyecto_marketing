# 🎮 NexGen Store — Landing Page & Sistema de Cotizaciones

Landing page comercial enfocada en consolas, videojuegos y accesorios gaming.  
Incluye formulario de cotización conectado a PostgreSQL y automatización de leads con n8n.

---

#  Tecnologías utilizadas

- HTML5
- CSS3
- JavaScript
- Python
- Flask
- PostgreSQL
- n8n
- Google Sheets
- Supabase
- Faker

---

#  Estructura del proyecto

```text
nexgen/
├── index.html                 ← Landing page principal
├── app.py                     ← Backend API Flask
├── faker_test.py              ← Generador automático de datos falsos
├── requirements.txt           ← Dependencias Python
├── .gitignore
├── README.md
└── n8n/
    └── workflow.json          ← Export del workflow n8n
```

---

#  Instalación local

## 1. Clonar el proyecto

```bash
git clone https://github.com/tuusuario/nexgen.git
cd nexgen
```

---

#  2. Crear base de datos PostgreSQL

Abrir pgAdmin o psql y ejecutar:

```sql
CREATE DATABASE nexgen_db;
```

La tabla `cotizaciones` se crea automáticamente al iniciar Flask.

---

#  3. Configurar variables de entorno

Crear archivo `.env`

```bash
cp .env.example .env
```

---

## Configuración ejemplo

```env
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nexgen_db
DB_USER=postgres
DB_PASSWORD=tu_password

# n8n Webhook
WEBHOOK_URL=http://localhost:5777/webhook/cotizacion
```

---

#  4. Instalar dependencias

## Instalación manual

```bash
pip install flask flask-cors psycopg2-binary python-dotenv faker requests gunicorn
```

---

## Instalación desde requirements.txt

```bash
pip install -r requirements.txt
```




# ▶ 5. Ejecutar backend Flask

```bash
python app.py
```

Servidor local:

```text
http://localhost:5000
```

---

#  6. Abrir frontend

Abrir:

```text
index.html
```

El formulario enviará datos:
- al backend Flask
- o al webhook de n8n

según configuración.

---

#  Automatización con n8n

El proyecto utiliza un workflow automatizado para capturar cotizaciones y almacenarlas automáticamente en:

- Google Sheets
- Supabase

---

#  Flujo general

```text
Formulario HTML
        ↓
Webhook n8n
        ↓
 ┌───────────────┬────────────────┐
 ↓                               ↓
Google Sheets              Supabase
```

---

#  Workflow n8n

## Nombre del workflow

```text
PROYECTO :)
```

## Estado requerido

```text
Published / Active
```

Importante:  
El workflow debe estar publicado para recibir múltiples requests.

---

#  Webhook

## Método HTTP

```http
POST
```

## Endpoint

```text
/webhook/cotizacion
```

## URL local

```text
http://localhost:5777/webhook/cotizacion
```

 No usar:

```text
/webhook-test/cotizacion
```

porque solo escucha temporalmente.

---

#  Nodos del workflow

## 1. Webhook

Recibe solicitudes POST desde:
- formulario HTML
- scripts Python
- automatizaciones

---

## 2. Google Sheets — Append Row

Guarda automáticamente cada lead en:

```text
Cotizaciones NexGen
```

---

## 3. Supabase — Create Row

Inserta automáticamente cada lead en:

```text
cotizaciones
```

---

#  Ejemplo payload recibido

```json
{
  "nombre": "nicolas heredia perdomo",
  "empresa": "tienda lucho",
  "email": "nicolasp@gmail.com",
  "telefono": "2341234422",
  "ciudad": "neiva",
  "tipo_cliente": "particular",
  "plataformas": "Switch, PC",
  "cantidad": "1-5",
  "presupuesto": "1M-5M",
  "mensaje": "",
  "canal": "otro"
}
```

---

#  Estructura tabla `cotizaciones`

| Columna | Tipo |
|---|---|
| id | SERIAL |
| nombre | VARCHAR |
| empresa | VARCHAR |
| email | VARCHAR |
| telefono | VARCHAR |
| ciudad | VARCHAR |
| tipo_cliente | VARCHAR |
| plataformas | TEXT |
| cantidad | VARCHAR |
| presupuesto | VARCHAR |
| mensaje | TEXT |
| canal | VARCHAR |
| fecha_creacion | TIMESTAMP |
| estado | VARCHAR |



# 🤖 Testing automático con Faker

El proyecto incluye un script para generar datos falsos automáticamente y enviarlos al webhook.



##  Ejecutar testing automático

### 1. Publicar workflow n8n

Debe estar:

```text
Published / Active
```

---

### 2. Ejecutar script

```bash
python faker_test.py
```



###  Resultado esperado

Cada ejecución:

1. genera leads falsos
2. envía datos al webhook
3. guarda registros en:
   - Google Sheets
   - Supabase
4. registra la ejecución en n8n
