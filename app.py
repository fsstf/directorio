import tkinter as tk
from tkinter import ttk, messagebox
from database import *

crear_bd()

# ======== VENTANA ========
ventana = tk.Tk()
ventana.title("Directorio")
ventana.geometry("720x600")
ventana.resizable(False, False)

BG     = "#f5f6fa"
AZUL   = "#1a6b8a"
VERDE  = "#27ae60"
ROJO   = "#e74c3c"
GRIS   = "#7f8c8d"
BLANCO = "#ffffff"
FONT   = ("Segoe UI", 10)
BOLD   = ("Segoe UI", 10, "bold")

ventana.configure(bg=BG)

# ======== ESTILOS ========
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
    background=BLANCO, foreground="#2c3e50",
    rowheight=26, fieldbackground=BLANCO, font=FONT)
style.configure("Treeview.Heading",
    background=AZUL, foreground=BLANCO, font=BOLD, relief="flat")
style.map("Treeview",
    background=[("selected", AZUL)],
    foreground=[("selected", BLANCO)])

# ======== TÍTULO ========
frame_titulo = tk.Frame(ventana, bg=AZUL)
frame_titulo.pack(fill="x")
tk.Label(frame_titulo, text="Directorio",
         bg=AZUL, fg=BLANCO, font=("Segoe UI", 14, "bold"), pady=10).pack()

# ======== BÚSQUEDA ========
frame_busqueda = tk.Frame(ventana, bg=BG)
frame_busqueda.pack(fill="x", padx=15, pady=(10, 4))

tk.Label(frame_busqueda, text="Buscar:", bg=BG, font=FONT).pack(side="left")
buscar_entry = tk.Entry(frame_busqueda, width=34, font=FONT)
buscar_entry.pack(side="left", padx=8)

ttk.Separator(ventana, orient="horizontal").pack(fill="x", padx=15, pady=4)

# ======== FORMULARIO ========
frame_form = tk.Frame(ventana, bg=BG)
frame_form.pack(fill="x", padx=15, pady=4)

# Validaciones en tiempo real
def solo_numeros(val):
    return val == "" or val.isdigit()

def solo_numeros_max10(val):
    return (val == "" or val.isdigit()) and len(val) <= 10

vcmd    = (ventana.register(solo_numeros),    "%P")
vcmd10  = (ventana.register(solo_numeros_max10), "%P")

# Fila 1: Expediente + Nombre
fila1 = tk.Frame(frame_form, bg=BG)
fila1.pack(fill="x", pady=4)
tk.Label(fila1, text="Expediente *", bg=BG, font=FONT, width=22, anchor="e").pack(side="left")
expediente_entry = tk.Entry(fila1, font=FONT, width=12, validate="key", validatecommand=vcmd)
expediente_entry.pack(side="left", padx=(4, 20))
tk.Label(fila1, text="Nombre *", bg=BG, font=FONT, anchor="e").pack(side="left")
nombre_entry = tk.Entry(fila1, font=FONT, width=32)
nombre_entry.pack(side="left", padx=4)

# Fila 2: Teléfono
fila2 = tk.Frame(frame_form, bg=BG)
fila2.pack(fill="x", pady=4)
tk.Label(fila2, text="Teléfono * (10 dígitos)", bg=BG, font=FONT, width=22, anchor="e").pack(side="left")
telefono_entry = tk.Entry(fila2, font=FONT, width=14, validate="key", validatecommand=vcmd10)
telefono_entry.pack(side="left", padx=4)

ttk.Separator(ventana, orient="horizontal").pack(fill="x", padx=15, pady=6)

# ======== FUNCIONES ========

def validar_campos(expediente, nombre, telefono):
    if not expediente.strip():
        messagebox.showerror("Campo vacío", "El número de expediente es obligatorio.")
        expediente_entry.focus()
        return False
    if not nombre.strip():
        messagebox.showerror("Campo vacío", "El nombre es obligatorio.")
        nombre_entry.focus()
        return False
    if len(nombre.strip()) < 3:
        messagebox.showerror("Nombre inválido", "El nombre debe tener al menos 3 caracteres.")
        nombre_entry.focus()
        return False
    if not telefono.strip():
        messagebox.showerror("Campo vacío", "El teléfono es obligatorio.")
        telefono_entry.focus()
        return False
    if len(telefono.strip()) != 10:
        messagebox.showerror("Teléfono inválido", "El teléfono debe tener exactamente 10 dígitos.")
        telefono_entry.focus()
        return False
    return True


def cargar_datos(datos=None):
    for fila in tabla.get_children():
        tabla.delete(fila)
    if datos is None:
        datos = ver_directorio()
    for i, d in enumerate(datos):
        tag = "par" if i % 2 == 0 else "impar"
        tabla.insert("", tk.END, values=d, tags=(tag,))
    tabla.tag_configure("par",   background=BLANCO)
    tabla.tag_configure("impar", background="#eaf3fb")
    total = len(datos)
    sufijo = "s" if total != 1 else ""
    status_var.set(f"  {total} paciente{sufijo} encontrado{sufijo}")


def limpiar_campos():
    expediente_entry.config(state="normal")
    expediente_entry.delete(0, tk.END)
    nombre_entry.delete(0, tk.END)
    telefono_entry.delete(0, tk.END)
    if tabla.selection():
        tabla.selection_remove(tabla.selection())


def agregar():
    expediente = expediente_entry.get().strip()
    nombre     = nombre_entry.get().strip()
    telefono   = telefono_entry.get().strip()

    if not validar_campos(expediente, nombre, telefono):
        return

    if not agregar_persona(expediente, nombre, telefono):
        messagebox.showerror("Expediente duplicado",
            f"Ya existe un paciente con el expediente {expediente}.")
        expediente_entry.focus()
        return

    limpiar_campos()
    cargar_datos()


def eliminar():
    seleccionado = tabla.selection()
    if not seleccionado:
        messagebox.showwarning("Sin selección", "Selecciona un paciente de la tabla para eliminar.")
        return
    valores = tabla.item(seleccionado)["values"]
    confirmar = messagebox.askyesno("Confirmar eliminación",
        f"¿Seguro que deseas eliminar a '{valores[1]}'\n(Expediente: {valores[0]})?")
    if confirmar:
        borrar_persona(valores[0])
        limpiar_campos()
        cargar_datos()


def actualizar():
    seleccionado = tabla.selection()
    if not seleccionado:
        messagebox.showwarning("Sin selección", "Selecciona un paciente de la tabla para actualizar.")
        return

    valores   = tabla.item(seleccionado)["values"]
    expediente = str(valores[0])
    nombre     = nombre_entry.get().strip()
    telefono   = telefono_entry.get().strip()

    if not validar_campos(expediente, nombre, telefono):
        return

    actualizar_persona(expediente, nombre, telefono)
    limpiar_campos()
    cargar_datos()


def buscar():
    query = buscar_entry.get().strip()
    if not query:
        cargar_datos()
        return
    resultados = buscar_personas(query)
    cargar_datos(resultados)
    if not resultados:
        messagebox.showinfo("Sin resultados", f"No se encontraron pacientes con '{query}'.")


def limpiar_busqueda():
    buscar_entry.delete(0, tk.END)
    cargar_datos()


def al_seleccionar(event):
    seleccionado = tabla.selection()
    if seleccionado:
        valores = tabla.item(seleccionado)["values"]
        expediente_entry.config(state="normal")
        expediente_entry.delete(0, tk.END)
        expediente_entry.insert(0, valores[0])
        expediente_entry.config(state="readonly")
        nombre_entry.delete(0, tk.END)
        nombre_entry.insert(0, valores[1])
        telefono_entry.delete(0, tk.END)
        telefono_entry.insert(0, valores[2])

# ======== BOTONES ========
frame_btns = tk.Frame(ventana, bg=BG)
frame_btns.pack(fill="x", padx=15, pady=(0, 6))

def btn(parent, text, color, cmd):
    f = tk.Frame(parent, bg=color, cursor="hand2")
    l = tk.Label(f, text=text, bg=color, fg=BLANCO, font=BOLD, padx=14, pady=5)
    l.pack()
    l.bind("<Button-1>", lambda e: cmd())
    f.bind("<Button-1>", lambda e: cmd())
    return f

btn(frame_btns, "Agregar",        VERDE, agregar).pack(side="left", padx=(0, 6))
btn(frame_btns, "Actualizar",     AZUL,  actualizar).pack(side="left", padx=6)
btn(frame_btns, "Eliminar",       ROJO,  eliminar).pack(side="left", padx=6)
btn(frame_btns, "Limpiar campos", GRIS,  limpiar_campos).pack(side="right")

# Botones de búsqueda (ahora que btn() existe)
btn(frame_busqueda, "Buscar",   AZUL, buscar).pack(side="left", padx=2)
btn(frame_busqueda, "Ver todos", GRIS, limpiar_busqueda).pack(side="left", padx=2)

# ======== TABLA ========
frame_tabla = tk.Frame(ventana, bg=BG)
frame_tabla.pack(fill="both", expand=True, padx=15, pady=(0, 4))

tabla = ttk.Treeview(frame_tabla,
    columns=("Expediente", "Nombre", "Telefono"),
    show="headings", height=11)
tabla.heading("Expediente", text="Expediente")
tabla.heading("Nombre",     text="Nombre")
tabla.heading("Telefono",   text="Teléfono")
tabla.column("Expediente", width=100, anchor="center")
tabla.column("Nombre",     width=380)
tabla.column("Telefono",   width=140, anchor="center")

scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
tabla.configure(yscrollcommand=scrollbar.set)
tabla.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ======== BARRA DE ESTADO ========
status_var = tk.StringVar(value="")
tk.Label(ventana, textvariable=status_var,
         bg=AZUL, fg=BLANCO, font=("Segoe UI", 9),
         anchor="w", padx=10, pady=4).pack(fill="x", side="bottom")

# ======== BINDINGS ========
tabla.bind("<<TreeviewSelect>>", al_seleccionar)
buscar_entry.bind("<Return>", lambda e: buscar())

cargar_datos()
ventana.mainloop()
