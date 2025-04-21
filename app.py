import sys
import os
import glob
import tempfile
import subprocess
import fitz
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTableWidget, QTableWidgetItem, QDialog, QComboBox, QCheckBox
)
from PyPDF2 import PdfMerger

class DialogoCompresion(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Opciones de compresión")

        self.niveles = ["25%", "50%", "75%", "90%"]
        self.combo = QComboBox()
        self.combo.addItems(self.niveles)
        self.combo.setCurrentIndex(2)

        self.checkbox = QCheckBox("Rasterizar PDF (convierte a imágenes)")
        self.checkbox.setChecked(False)

        self.boton_ok = QPushButton("Aceptar")
        self.boton_ok.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Selecciona el nivel de compresión:"))
        layout.addWidget(self.combo)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.boton_ok)

        self.setLayout(layout)

    def obtener_opciones(self):
        return self.combo.currentText(), self.checkbox.isChecked()

class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unir PDFs")
        self.setGeometry(100, 100, 550, 410)

        self.main_directory = ""
        self.pdf_files = {}

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Botones de selección
        btn_layout = QHBoxLayout()
        btn_dir = QPushButton("Seleccionar Directorio")
        btn_dir.clicked.connect(self.seleccionar_directorio)
        btn_docs = QPushButton("Seleccionar Documentos")
        btn_docs.clicked.connect(self.seleccionar_documentos)
        btn_layout.addWidget(btn_dir)
        btn_layout.addWidget(btn_docs)
        layout.addLayout(btn_layout)

        # Label principal
        self.label_info = QLabel("Documentos a procesar: 0")
        layout.addWidget(self.label_info)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(1)
        self.tabla.setHorizontalHeaderLabels(["Archivo"])
        layout.addWidget(self.tabla)

        # Botón de guardar
        btn_guardar = QPushButton("Guardar PDF")
        btn_guardar.clicked.connect(self.guardar_pdf)
        layout.addWidget(btn_guardar)

        #butón de compresión
        btn_comprimir = QPushButton("Comprimir PDF")
        btn_comprimir.clicked.connect(self.comprimir_pdf_dialogo)
        layout.addWidget(btn_comprimir)

        # Mensaje de error
        self.label_error = QLabel("")
        self.label_error.setStyleSheet("color: red;")
        layout.addWidget(self.label_error)

        self.setLayout(layout)

    def seleccionar_directorio(self):
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar directorio")
        if directorio:
            patron_pdf = os.path.join(directorio, "*.pdf")
            self.agregar_elementos(glob.glob(patron_pdf))

    def seleccionar_documentos(self):
        documentos, _ = QFileDialog.getOpenFileNames(self, "Seleccionar documentos", "", "Archivos PDF (*.pdf)")
        if documentos:
            self.agregar_elementos(documentos)

    def agregar_elementos(self, archivos):
        self.pdf_files.clear()
        self.tabla.setRowCount(0)
        for pdf in archivos:
            nombre = os.path.basename(pdf)
            if nombre.lower().endswith(".pdf"):
                clave = nombre.replace(".pdf", "")
                self.pdf_files[clave] = pdf
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                self.tabla.setItem(fila, 0, QTableWidgetItem(clave))
        self.label_info.setText(f"Documentos a procesar: {len(self.pdf_files)}")

    def guardar_pdf(self):
        ruta_salida, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "", "PDF Files (*.pdf)")
        if ruta_salida:
            merger = PdfMerger()
            for nombre, ruta in self.pdf_files.items():
                with open(ruta, 'rb') as f:
                    merger.append(f)
                print(f"\"{nombre}\" unido")
            with open(ruta_salida, 'wb') as salida:
                merger.write(salida)
            self.label_error.setText("")
        else:
            self.label_error.setText("Operación de guardado cancelada.")
    
    def comprimir_con_ghostscript(self, input_pdf, output_pdf, nivel_compresion):
        calidades = {
            "25%": "screen",     # muy baja calidad
            "50%": "ebook",      # calidad media
            "75%": "printer",    # buena calidad
            "90%": "prepress"    # muy buena calidad
        }
        calidad = calidades.get(nivel_compresion, "ebook")

        comando = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS=/{calidad}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_pdf}",
            input_pdf
        ]

        subprocess.run(comando)

    def comprimir_con_rasterizacion(self, input_pdf, output_pdf, nivel_compresion):
        porcentaje = int(nivel_compresion.replace("%", ""))
        zoom = porcentaje / 100.0
        mat = fitz.Matrix(zoom, zoom)

        doc_in = fitz.open(input_pdf)
        doc_out = fitz.open()

        for pagina in doc_in:
            pix = pagina.get_pixmap(matrix=mat)

            # Crear nueva página en el PDF de salida con tamaño igual al de la imagen
            page = doc_out.new_page(width=pix.width, height=pix.height)

            # Insertar el contenido del pixmap como imagen en la nueva página
            rect = fitz.Rect(0, 0, pix.width, pix.height)
            page.insert_image(rect, pixmap=pix)

        doc_out.save(output_pdf, garbage=4, deflate=True)
        doc_in.close()
        doc_out.close()

    def comprimir_pdf_dialogo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar PDF a comprimir", "", "PDF Files (*.pdf)")
        if not archivo:
            return

        # Mostrar diálogo personalizado
        dialogo = DialogoCompresion(self)
        if dialogo.exec_() == QDialog.Accepted:
            nivel, rasterizar = dialogo.obtener_opciones()

            salida, _ = QFileDialog.getSaveFileName(self, "Guardar PDF Comprimido", "", "PDF Files (*.pdf)")
            if salida:
                if rasterizar:
                    self.comprimir_con_rasterizacion(archivo, salida, nivel)
                else:
                    self.comprimir_con_ghostscript(archivo, salida, nivel)

                self.label_error.setText("¡PDF comprimido exitosamente!")
            else:
                self.label_error.setText("Guardado cancelado.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = PDFMergerApp()
    ventana.show()
    sys.exit(app.exec_())