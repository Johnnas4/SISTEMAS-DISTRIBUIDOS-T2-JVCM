
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)
import sqlite3
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave-local-para-desarrollo"

# La base de datos se guardará junto a este archivo.
DB_PATH = Path(app.root_path) / "incidencias.db"


def conectar_db():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_db():
    with conectar_db() as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS incidencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solicitante TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                prioridad TEXT NOT NULL DEFAULT 'Media',
                estado TEXT NOT NULL DEFAULT 'Abierta',
                fecha TEXT NOT NULL
            )
        """)


@app.route("/")
def inicio():
    with conectar_db() as conexion:
        incidencias = conexion.execute(
            "SELECT * FROM incidencias ORDER BY id DESC"
        ).fetchall()

    return render_template(
        "index.html",
        incidencias=incidencias
    )


@app.route("/incidencias", methods=["POST"])
def crear():
    solicitante = request.form.get("solicitante", "").strip()
    titulo = request.form.get("titulo", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    prioridad = request.form.get("prioridad", "Media")

    if not solicitante or not titulo or not descripcion:
        flash("Completa todos los campos obligatorios.")
        return redirect(url_for("inicio"))

    if prioridad not in ("Baja", "Media", "Alta"):
        flash("La prioridad seleccionada no es válida.")
        return redirect(url_for("inicio"))

    fecha = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")

    with conectar_db() as conexion:
        conexion.execute(
            """
            INSERT INTO incidencias
            (solicitante, titulo, descripcion, prioridad, estado, fecha)
            VALUES (?, ?, ?, ?, 'Abierta', ?)
            """,
            (solicitante, titulo, descripcion, prioridad, fecha)
        )

    flash("Incidencia registrada correctamente.")
    return redirect(url_for("inicio"))


@app.route("/incidencias/<int:incidencia_id>/estado", methods=["POST"])
def cambiar_estado(incidencia_id):
    estado = request.form.get("estado", "")

    if estado not in ("Abierta", "En proceso", "Resuelta"):
        flash("El estado seleccionado no es válido.")
        return redirect(url_for("inicio"))

    with conectar_db() as conexion:
        resultado = conexion.execute(
            "UPDATE incidencias SET estado = ? WHERE id = ?",
            (estado, incidencia_id)
        )

    if resultado.rowcount == 0:
        flash("No se encontró la incidencia.")
    else:
        flash("Estado actualizado correctamente.")

    return redirect(url_for("inicio"))


@app.route("/incidencias/<int:incidencia_id>/eliminar", methods=["POST"])
def eliminar(incidencia_id):
    with conectar_db() as conexion:
        resultado = conexion.execute(
            "DELETE FROM incidencias WHERE id = ?",
            (incidencia_id,)
        )

    if resultado.rowcount == 0:
        flash("No se encontró la incidencia.")
    else:
        flash("Incidencia eliminada correctamente.")

    return redirect(url_for("inicio"))


if __name__ == "__main__":
    inicializar_db()
    app.run(debug=True)
