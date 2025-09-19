import sqlite3
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from db import inicializar_db
from controladores.opciones import actualizar_o_agregar_opcion, cargar_opciones_por_tipo, restablecer_opciones

inicializar_db()

tipo = "principal"  # Tipo de opciones a cargar: 'principal', 'especial', 'promocion'
if len(sys.argv) > 1:
    tipo = str(sys.argv[1])   # El primer argumento después del nombre del script

# estado global para drag
dragged_item = None
datos = {}

def centrar_ventana_hija(ventana, ancho, alto, padre):

    ventana.withdraw()  # Ocultar mientras se configura

    # Obtener la posición de la ventana padre
    padre_x = padre.winfo_rootx()
    padre_y = padre.winfo_rooty()
    padre_ancho = padre.winfo_width()
    padre_alto = padre.winfo_height()
    
    # Calcular posición centrada respecto a la ventana padre
    x = padre_x + (padre_ancho - ancho) // 2
    y = padre_y + (padre_alto - alto) // 2
    
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    ventana.deiconify() # Mostrar la ventana después de configurar

"""
FUNCIONES DE FORMULARIO PRINCIPAL
- activar_guardar: Activa el botón guardar
- guardar_opciones: Guarda los cambios en la base de datos
"""
def activar_guardar():
    menu_bar.entryconfig("Guardar Cambios", state="normal")

def reasignar_orden(tree):
    items = tree.get_children()

    # Reasignar el orden en el diccionario
    for idx, i in enumerate(items, start=1):
        id_item = int(tree.item(i)["text"])
        if id_item in datos:
            datos[id_item]["orden"] = idx # Actualizar el orden segun la posición en el Treeview

def guardar_opciones(ventana, datos):

    """
    BASE DE DATOS
    - Se apertura la base de datos 
    - Se itera sobre el diccionario de datos modificando la base de datos
    - Se cierra la base de datos
    """
    conn = sqlite3.connect("escaner.db")
    cursor = conn.cursor()

    # Iterar sobre las filas obtenidas dentro de la base de datos
    for clave, opcion in datos.items():
        try:
            actualizar_o_agregar_opcion(cursor, clave, opcion)
        except Exception as e:
            print(f"⚠️ Error al guardar clave {clave}: {e}")

    conn.commit() # Guardar cambios
    conn.close() # Cerramos la base de datos
    messagebox.showinfo("Guardado", "Los cambios han sido guardados.", parent=ventana)
    menu_bar.entryconfig("Guardar Cambios", state="disabled")

"""
FUNCIONES DE VENTANA AGREGAR
- ventana_agregar_opcion: Crea la ventana para agregar una opción
- agregar_opcion: Lógica para agregar la opción al diccionario y actualizar el Treeview
"""
def ventana_agregar_opcion(tipo):
    
    """
    DISEÑO DE VENTANA AGREGAR
    """
    ventana_agregar = tk.Toplevel(root)
    centrar_ventana_hija(ventana_agregar, 200, 80, root)
    ventana_agregar.title("Agregar opción")
    # ventana_agregar.iconbitmap(icon_path)
    ventana_agregar.resizable(False, False)
    ventana_agregar.grab_set()
    ventana_agregar.focus_force()

    """
    FRAME DE ENTRADA
    """
    frame_entrada = tk.Frame(ventana_agregar)
    frame_entrada.pack(fill="both", padx=8, pady=8)
    """
    Frame de entrada contiene:
    - Entrada de texto para nombre
    - Botón agregar
    """
    entry_nombre = tk.Entry(frame_entrada)
    entry_nombre.pack(side="top", fill="x", expand=True)
    entry_nombre.focus_set()

    btn_add = tk.Button(frame_entrada, text="Agregar", command=lambda: agregar_opcion(entry_nombre, ventana_agregar, tipo), width=10)
    btn_add.pack(side="bottom", pady=6)

    ventana_agregar.mainloop()

def agregar_opcion(entry_nombre, ventana_agregar, tipo):
    global datos

    nombre = entry_nombre.get().strip().upper()
    esta_inactivo = False
    nuevo_id = 0

    if not nombre:
        messagebox.showwarning("Advertencia", "Ingrese un nombre.", parent=ventana_agregar)
        return

    # Validar duplicados (solo opciones activas)
    for clave, info in datos.items():
        # Si el nombre esta duplicado y esta activo se devuelve un error
        if info["nombre"] == nombre and info["activo"] == 1:
            messagebox.showerror("Error", f"El nombre '{nombre}' ya existe.", parent=ventana_agregar)
            return
        # Si el nombre esta duplicado pero esta inactivo se vuelve a activar
        elif info["nombre"] == nombre and info["activo"] == 0:
            nuevo_id = clave
            esta_inactivo = True

    if not esta_inactivo:
        nuevo_id = max(datos.keys(), default=0) + 1 # Crear nuevo ID (max actual + 1)
    
    datos[nuevo_id] = {
        "nombre": nombre,
        "orden": 0,
        "tipo": tipo,
        "activo": 1
    } # Agregar o modificar el diccionario

    tree.insert("", "end", text=str(nuevo_id), values=(nombre, "❌ Eliminar")) # Insertar en el Treeview
    entry_nombre.delete(0, tk.END)

    reasignar_orden(tree) # Funcion para reasignar el orden en el diccionario

    print("Nuevos datos:", datos)
    activar_guardar() # Activa el guardado
    messagebox.showinfo("Agregado", f"El nombre '{nombre}' ha sido agregado.", parent=ventana_agregar)
    ventana_agregar.destroy()


"""
VENTANA PRINCIPAL
"""
root = tk.Tk()
root.title("Tabla dinámica con Drag & Drop y agregar")

"""
MENU
"""
menu_bar = tk.Menu(root)
menu_bar.add_command(label="Guardar Cambios", command=lambda: guardar_opciones(root, datos))
menu_bar.add_command(label="Agregar", command=lambda: ventana_agregar_opcion(tipo=tipo))
menu_bar.add_command(label="Restablecer", command=lambda: restablecer_opciones())
root.config(menu=menu_bar)

"""
DISEÑO DE LA TABLA
"""
tree = ttk.Treeview(root, columns=("Nombre", "Acciones"), show="headings")
tree.heading("Nombre", text="Nombre")
tree.heading("Acciones", text="Acciones")
tree.column("Nombre", width=220, anchor="w")
tree.column("Acciones", width=100, anchor="center")
tree.pack(fill="both", expand=True, padx=8, pady=8)

datos = cargar_opciones_por_tipo(tipo=tipo)

# Insertar en Treeview 
for id_opcion, info in datos.items():
    if info["activo"] == 1:  # ✅ solo datos activos
        tree.insert(
            "",
            "end",
            text=str(id_opcion),
            values=(info["nombre"], "❌ Eliminar")
        )

"""
FUNCIONES DE DRAG & DROP
- on_start_drag: Inicia el arrastre
- on_drag: Mueve el elemento arrastrado
- on_drop: Suelta el elemento y reasigna el orden
- on_double_click: Elimina el elemento (marca como inactivo)
"""
def on_start_drag(event):
    global dragged_item
    col = tree.identify_column(event.x)
    row = tree.identify_row(event.y)
    if col == "#2":  # no arrastrar desde la columna acciones
        dragged_item = None
        return
    dragged_item = row

def on_drag(event):
    global dragged_item
    if not dragged_item:
        return
    row_under_mouse = tree.identify_row(event.y)
    if row_under_mouse and row_under_mouse != dragged_item:
        tree.move(dragged_item, '', tree.index(row_under_mouse))

def on_drop(event):
    global dragged_item, datos
    if not dragged_item:
        return
    
    reasignar_orden(tree) # Funcion para reasignar el orden en el diccionario

    print("Nuevos datos:", datos)
    activar_guardar() # Activa el guardado
    dragged_item = None

def on_double_click(event):
    global datos
    col = tree.identify_column(event.x)
    row = tree.identify_row(event.y)

    if col == "#2" and row:
        id_item = int(tree.item(row)["text"])
        tree.delete(row)
        if id_item in datos:
            datos[id_item]["activo"] = 0 # Marcar como inactivo
            datos[id_item]["orden"] = 0 # Reiniciar orden al eliminar
        
        reasignar_orden(tree) # Funcion para reasignar el orden en el diccionario
        activar_guardar() # Activa el guardado
        print("Nuevos datos:", datos)

# Eventos drag & drop
tree.bind("<ButtonPress-1>", on_start_drag, add='+')
tree.bind("<B1-Motion>", on_drag, add='+')
tree.bind("<ButtonRelease-1>", on_drop, add='+')

# Doble-clic eliminar
tree.bind("<Double-1>", on_double_click, add='+')

root.mainloop()
