import sqlite3

# Listas de opciones por defecto
nombres_especial = [
  ("DNI FRONTAL", 1), ("DNI REVERSO", 2), 
  ("JUGADA", 3), ("COMPROBANTE", 4)
]
nombres_principal = [
  ("KASNET", 1), ("NIUBIZ", 2), ("LOTTINGO", 3), 
  ("GOLDEN", 4), ("BETSHOP", 5), ("VALE DE DESCUENTO", 6)
]
opciones_web = [
  ("MEGAJACKPOT", 1), ("LOTTINGO", 2), 
  ("WEB RETAIL", 3), ("CUMPLEAÑERO", 4)
]

def inicializar_db():
  conn = sqlite3.connect('escaner.db')
  cursor = conn.cursor()

  # Crear tabla con restricción en tipo
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS opciones (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nombre TEXT NOT NULL UNIQUE,
      orden INTEGER NOT NULL,
      tipo TEXT NOT NULL CHECK(tipo IN ('principal', 'especial', 'promocion')),
      activo BOOLEAN NOT NULL DEFAULT 1
    )''')
  conn.commit()

  # Insertar registros por defecto
  def insertar_opciones(lista, tipo):
    for item in lista:
      cursor.execute('''
        INSERT OR IGNORE INTO opciones (nombre, orden, tipo)
        VALUES (?, ?, ?)
      ''', (item[0], item[1], tipo))

  insertar_opciones(nombres_especial, "especial")
  insertar_opciones(nombres_principal, "principal")
  insertar_opciones(opciones_web, "promocion")

  conn.commit()
  conn.close()