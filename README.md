### Comandos para crear el entorno vitual python
    pythonx -m venv <name-env>
## Para activar el entorno virutal
    source <name-env>/bin/activate
## Para descativar el entorno virtual
    deactivate
## !!Se pueden instalar las librerias necesarias con el entorno activado
### Generacion de los requerimientos del proyecto de python
#### Windows
    pip freeze > requirements.txt
#### Linux
    pip3 freeze > requirements.txt
### Instalacion de los paquetes de python
#### Windows
    pip install -r requirements.txt
#### Linux
    pip3 install -r requirements.txt
### Instalacion de cualquier otro paquete
    pip install <package-name>
### Generacion del ejecutable Windows (.exe)
    <name-env>/Scripts/pyinstaller.exe --onefile -w file_name.py
