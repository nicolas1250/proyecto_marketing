"""
NexGen Store — Backend API
Flask + PostgreSQL para cotizaciones

Instalación:
  pip install flask flask-cors psycopg2-binary python-dotenv

Uso:
  python app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["*"])  # En producción, restringir al dominio del blog

# =============================================
# CONFIGURACIÓN DE BASE DE DATOS
# Edita el archivo .env o las variables aquí
# =============================================
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     os.getenv("DB_PORT",     "5432"),
    "database": os.getenv("DB_NAME",     "nexgen_db"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", "tu_password"),
}


def get_connection():
    """Retorna una conexión activa a PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """
    Crea la tabla cotizaciones si no existe.
    Ejecutar una vez al iniciar la app.
    """
    sql = """
    CREATE TABLE IF NOT EXISTS cotizaciones (
        id              SERIAL PRIMARY KEY,
        nombre          VARCHAR(120)  NOT NULL,
        empresa         VARCHAR(120),
        email           VARCHAR(150)  NOT NULL,
        telefono        VARCHAR(30)   NOT NULL,
        ciudad          VARCHAR(80),
        tipo_cliente    VARCHAR(30),
        plataformas     TEXT,
        cantidad        VARCHAR(20),
        presupuesto     VARCHAR(20),
        mensaje         TEXT,
        canal           VARCHAR(30),
        fecha_creacion  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
        estado          VARCHAR(20)   DEFAULT 'pendiente'
    );

    -- Índice para búsquedas frecuentes por email y estado
    CREATE INDEX IF NOT EXISTS idx_cotizaciones_email  ON cotizaciones(email);
    CREATE INDEX IF NOT EXISTS idx_cotizaciones_estado ON cotizaciones(estado);
    CREATE INDEX IF NOT EXISTS idx_cotizaciones_fecha  ON cotizaciones(fecha_creacion);
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("✅ Tabla 'cotizaciones' lista.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al inicializar DB: {e}")
    finally:
        conn.close()


# =============================================
# RUTAS API
# =============================================

@app.route("/api/cotizacion", methods=["POST"])
def crear_cotizacion():
    """Recibe el formulario y guarda en PostgreSQL."""
    data = request.get_json()

    # Validación básica
    required = ["nombre", "email", "telefono"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Campos requeridos: {', '.join(missing)}"}), 400

    sql = """
        INSERT INTO cotizaciones
            (nombre, empresa, email, telefono, ciudad,
             tipo_cliente, plataformas, cantidad, presupuesto, mensaje, canal)
        VALUES
            (%(nombre)s, %(empresa)s, %(email)s, %(telefono)s, %(ciudad)s,
             %(tipo_cliente)s, %(plataformas)s, %(cantidad)s, %(presupuesto)s,
             %(mensaje)s, %(canal)s)
        RETURNING id, fecha_creacion;
    """

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, {
                "nombre":       data.get("nombre", ""),
                "empresa":      data.get("empresa", ""),
                "email":        data.get("email", ""),
                "telefono":     data.get("telefono", ""),
                "ciudad":       data.get("ciudad", ""),
                "tipo_cliente": data.get("tipo_cliente", ""),
                "plataformas":  data.get("plataformas", ""),
                "cantidad":     data.get("cantidad", ""),
                "presupuesto":  data.get("presupuesto", ""),
                "mensaje":      data.get("mensaje", ""),
                "canal":        data.get("canal", ""),
            })
            row = cur.fetchone()
        conn.commit()
        return jsonify({
            "message": "Cotización recibida exitosamente.",
            "id":      row["id"],
            "fecha":   row["fecha_creacion"].isoformat(),
        }), 201
    except Exception as e:
        conn.rollback()
        print(f"Error al insertar cotización: {e}")
        return jsonify({"error": "Error interno del servidor."}), 500
    finally:
        conn.close()


@app.route("/api/cotizaciones", methods=["GET"])
def listar_cotizaciones():
    """
    Lista todas las cotizaciones (panel admin).
    Parámetros opcionales: ?estado=pendiente&limit=20&offset=0
    """
    estado = request.args.get("estado")
    limit  = int(request.args.get("limit",  50))
    offset = int(request.args.get("offset",  0))

    sql    = "SELECT * FROM cotizaciones"
    params = []

    if estado:
        sql += " WHERE estado = %s"
        params.append(estado)

    sql += " ORDER BY fecha_creacion DESC LIMIT %s OFFSET %s"
    params += [limit, offset]

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        # Convertir fechas a string
        result = []
        for r in rows:
            r = dict(r)
            r["fecha_creacion"] = r["fecha_creacion"].isoformat()
            result.append(r)
        return jsonify({"total": len(result), "cotizaciones": result}), 200
    except Exception as e:
        print(f"Error al listar cotizaciones: {e}")
        return jsonify({"error": "Error interno."}), 500
    finally:
        conn.close()


@app.route("/api/cotizacion/<int:cid>", methods=["PATCH"])
def actualizar_estado(cid):
    """Actualiza el estado de una cotización (pendiente / atendido / cerrado)."""
    data   = request.get_json()
    estado = data.get("estado")
    valid  = {"pendiente", "atendido", "cerrado"}
    if estado not in valid:
        return jsonify({"error": f"Estado inválido. Opciones: {', '.join(valid)}"}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE cotizaciones SET estado = %s WHERE id = %s RETURNING id;",
                (estado, cid)
            )
            row = cur.fetchone()
        conn.commit()
        if not row:
            return jsonify({"error": "Cotización no encontrada."}), 404
        return jsonify({"message": "Estado actualizado.", "id": cid}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Error interno."}), 500
    finally:
        conn.close()


@app.route("/api/stats", methods=["GET"])
def stats():
    """Estadísticas rápidas para dashboard."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE estado = 'pendiente') AS pendientes,
                    COUNT(*) FILTER (WHERE estado = 'atendido')  AS atendidos,
                    COUNT(*) FILTER (WHERE fecha_creacion >= NOW() - INTERVAL '30 days') AS ultimos_30_dias
                FROM cotizaciones;
            """)
            row = dict(cur.fetchone())
        return jsonify(row), 200
    except Exception as e:
        return jsonify({"error": "Error interno."}), 500
    finally:
        conn.close()


@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()}), 200


# =============================================
# INICIO
# =============================================
if __name__ == "__main__":
    print("🎮 NexGen Store — Iniciando servidor...")
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
