import sys
import os
import glob
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTableWidget, QTableWidgetItem
)
from PyPDF2 import PdfMerger


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = PDFMergerApp()
    ventana.show()
    sys.exit(app.exec_())