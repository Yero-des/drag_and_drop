import sqlite3
import tkinter as tk
from tkinter import messagebox
from db import nombres_especial, nombres_principal, opciones_web

# Carga opciones activas desde la base de datos y las devuelve como diccionario
def cargar_opciones_activas(tipo):
  conn = sqlite3.connect("escaner.db")
  cursor = conn.cursor()

  cursor.execute("""
    SELECT id, nombre, orden, tipo, activo
    FROM opciones
    WHERE activo = 1 AND tipo = ?
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
  conn.commit()

  # Eliminar todos los registros (más rápido que borrar tabla)
  cursor.execute("DELETE FROM opciones")
  conn.commit()

  # Reiniciar contador de IDs (opcional, solo si quieres que empiece en 1 de nuevo)
  cursor.execute("DELETE FROM sqlite_sequence WHERE name='opciones'")
  conn.commit()

  # Insertar registros por defecto
  def insertar_opciones(lista, tipo):
    for item in lista:
      cursor.execute('''
        INSERT INTO opciones (nombre, orden, tipo, activo)
        VALUES (?, ?, ?, 1)
      ''', (item[0], item[1], tipo))

  insertar_opciones(nombres_especial, "especial")
  insertar_opciones(nombres_principal, "principal")
  insertar_opciones(opciones_web, "promocion")

  conn.commit()
  conn.close()

def cargar_opciones(tree, tipo):
  for fila in tree.get_children():
    tree.delete(fila)

  conn = sqlite3.connect('escaner.db')
  cursor = conn.cursor()
  cursor.execute('SELECT nombre, tipo, esta_activo FROM opciones WHERE tipo = ?', (tipo,))
  for opcion in cursor.fetchall():
    tree.insert('', tk.END, values=opcion.upper())

  conn.close()

def agregar_opcion(ventana, nombre, tipo, entry_nombre, cargar_opciones):

  if not nombre or not tipo:
    messagebox.showerror("Error", "Por favor, ingrese datos válidos")
    return
  
  nombre = nombre.upper()

  conn = sqlite3.connect('escaner.db')
  cursor = conn.cursor()
  cursor.execute('INSERT INTO opciones (nombre, tipo, esta_activo) VALUES (?, ?, ?)', (nombre, tipo, 1))
  conn.commit()
  conn.close()

  entry_nombre.delete(0, tk.END)

  cargar_opciones()
  messagebox.showinfo("Éxito", "Opción agregada exitosamente", parent=ventana)

def eliminar_opcion(tree, cargar_opciones):
  seleccion = tree.selection()

  if not seleccion:
    messagebox.showerror("Error", "Seleccione una opción para eliminar")
    return

  opcion_id = tree.item(seleccion[0])['values'][0]

  conn = sqlite3.connect('escaner.db')
  cursor = conn.cursor()
  cursor.execute('DELETE FROM opciones WHERE id = ?', (opcion_id,))
  conn.commit()
  conn.close()

  cargar_opciones()
  messagebox.showinfo("Éxito", "Opción eliminada exitosamente")

def actualizar_opcion(tree, entry_nombre, entry_tipo, check_activo, cargar_opciones):
  seleccion = tree.selection()

  if not seleccion:
    messagebox.showerror("Error", "Seleccione una opción para actualizar")
    return

  opcion_id = tree.item(seleccion[0])['values'][0]
  nombre = entry_nombre.get()
  tipo = entry_tipo.get()
  esta_activo = 1 if check_activo.get() else 0

  if not nombre or not tipo:
    messagebox.showerror("Error", "Por favor, ingrese datos válidos")
    return

  conn = sqlite3.connect('escaner.db')
  cursor = conn.cursor()
  cursor.execute('UPDATE opciones SET nombre = ?, tipo = ?, esta_activo = ? WHERE id = ?', (nombre, tipo, esta_activo, opcion_id))
  conn.commit()
  conn.close()

  entry_nombre.delete(0, tk.END)
  entry_tipo.delete(0, tk.END)
  check_activo.set(1)

  cargar_opciones()
  messagebox.showinfo("Éxito", "Opción actualizada exitosamente")