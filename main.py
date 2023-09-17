from PyPDF2 import PdfMerger
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import glob

# Variables de almacenamiento
main_directory = ""
pdf_files = {}


def seleccionar_directorio():
    directorio = filedialog.askdirectory()
    if directorio:
        main_directory = directorio
        print(f"{main_directory}")
        patron_pdf = os.path.join(main_directory, "*.pdf")
        agregarElementos(glob.glob(patron_pdf))


def seleccionar_documentos():
    opciones = {
        "filetypes": [("Archivos PDF", "*.pdf")],
    }
    documentos = filedialog.askopenfilenames(**opciones)
    if documentos:
        files = []
        for doc in documentos:
            files.append(doc)
        agregarElementos(files)


def limpiar_tabla():
    tabla.delete(*tabla.get_children())  # Elimina todas las filas de la tabla


def agregarElementos(files):
    pdf_files.clear()
    limpiar_tabla()
    for pdf in files:
        file_name = os.path.basename(pdf)
        if file_name.lower().endswith(".pdf"):
            key = file_name.replace(".pdf", "")
            pdf_files[key] = pdf
            tabla.insert("", "end", values=(key))
    desc = f"Documentos a procesar {len(pdf_files)}"
    label_1.config(text=desc)


def guardar_pdf():
    ubicacion = filedialog.asksaveasfilename(
        defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if ubicacion:
        fusionar = PdfMerger()
        for clave, valor in pdf_files.items():
            fusionar.append(open(valor, 'rb'))
            print(f"\"{clave}\" unido")
        with open(ubicacion, 'wb') as salida:
            fusionar.write(salida)
    else:
        mensaje_error.config(text="Operación de guardado cancelada.")


# Crear la ventana principal
ventana = tk.Tk()
ventana.title("UnirPDF's")

# Establecer un tamaño específico para la ventana (ancho x alto)
ventana.geometry("550x410")

# Crear un contenedor para los botones y colocarlos en una fila horizontal
botones_frame = tk.Frame(ventana)
botones_frame.pack(pady=10)

# Botones para seleccionar el directorio y los documentos
boton_directorio = tk.Button(
    botones_frame, text="Seleccionar Directorio", command=seleccionar_directorio)
boton_directorio.pack(side=tk.LEFT, padx=10)
boton_documentos = tk.Button(
    botones_frame, text="Seleccionar Documentos", command=seleccionar_documentos)
boton_documentos.pack(side=tk.LEFT, padx=10)


# Titulo de la tabla
label_1 = tk.Label(ventana, text="Documentos a procesar 0")
label_1.pack(pady=10)


# Crear la tabla con dos columnas
tabla = ttk.Treeview(ventana, columns=("Archivo"))
tabla.heading("Archivo", text="Archivo")
tabla.pack(pady=10)


# Botón para guardar el PDF
boton_guardar = tk.Button(ventana, text="Guardar PDF", command=guardar_pdf)
boton_guardar.pack(pady=10)

# Etiqueta para mostrar mensajes de error o éxito
mensaje_error = tk.Label(ventana, text="", fg="red")
mensaje_error.pack()

# Iniciar el bucle de la aplicación
ventana.mainloop()
