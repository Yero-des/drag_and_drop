import sqlite3
import tkinter as tk
from tkinter import messagebox
from db import nombres_especial, nombres_principal, promociones

# Carga opciones activas desde la base de datos y las devuelve como diccionario
def cargar_opciones_por_tipo(tipo):
  conn = sqlite3.connect("escaner.db")
  cursor = conn.cursor()

  cursor.execute("""
    SELECT id, nombre, orden, tipo, activo
    FROM opciones
    WHERE tipo = ?
    ORDER BY orden ASC
  """, (tipo,))
  rows = cursor.fetchall()
  conn.close()

  # Convertir a diccionario: {id: {"nombre":..., "orden":..., "tipo":...}}
  datos = {
    row[0]: {"nombre": row[1], "orden": row[2], "tipo": row[3], "activo": row[4]}
    for row in rows
  }

  return datos

def restablecer_opciones():
  conn = sqlite3.connect('escaner.db')
  cursor = conn.cursor()

  # Aseguramos que la tabla exista
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS opciones (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nombre TEXT NOT NULL UNIQUE,
      orden INTEGER NOT NULL,
      tipo TEXT NOT NULL CHECK(tipo IN ('principal', 'especial', 'promocion')),
      activo BOOLEAN NOT NULL DEFAULT 1
    )
  ''')

  # Eliminar todos los registros (más rápido que borrar tabla)
  cursor.execute("DELETE FROM opciones")

  # Reiniciar contador de IDs (opcional, solo si quieres que empiece en 1 de nuevo)
  # TODO: no funciona el recontador de IDs
  cursor.execute("DELETE FROM sqlite_sequence WHERE name='opciones'")

  # Insertar registros por defecto
  def insertar_opciones(lista, tipo):
    for item in lista:
      try:
        cursor.execute('''
          INSERT OR IGNORE INTO opciones (nombre, orden, tipo, activo)
          VALUES (?, ?, ?, 1)
        ''', (item[0], item[1], tipo))
      except Exception as e:
          print(f"⚠️ Error al guardar {item[0]}: {e}")

  insertar_opciones(nombres_especial, "especial")
  insertar_opciones(nombres_principal, "principal")
  insertar_opciones(promociones, "promocion")

  conn.commit()
  conn.close()

"""
Aquí iría la lógica para guardar los datos en la base de datos
* Los datos con su id ya creado solo se modifican
* Los datos nuevos se insertan con un nuevo id (Autogenerado en la DB)
* En caso se quiera cerrar la ventana (root) sin hacer cambio debera aparece una 
  ventana que diga "hay cambios sin guardar ¿desea salir sin guardar?"
* En caso se guarde se deja en la misma ventana pero se desactiva el boton guardar
""" 
def actualizar_o_agregar_opcion(cursor, clave, opcion):

  opcion_id = clave
  
  nombre_actual = opcion["nombre"]
  tipo_actual = opcion["tipo"]
  orden_actual = opcion["orden"]
  esta_activo = opcion["activo"]

  # TODO: Problemas con los unicos y detergentes: posible solucion llamar a todas la base de datos y no solo a una parte
  # TODO: Falta arregla el tema del ID cuando es nuevo de manera critica
  cursor.execute("""
    INSERT INTO opciones (id, nombre, tipo, orden, activo)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
      nombre = excluded.nombre,
      tipo = excluded.tipo,
      orden = excluded.orden,
      activo = excluded.activo
  """, (opcion_id, nombre_actual, tipo_actual, orden_actual, esta_activo))