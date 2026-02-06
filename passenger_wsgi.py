import sys
import os

# Agregar el directorio actual al path para encontrar la carpeta tools
sys.path.append(os.getcwd())

# Importar el objeto 'app' desde tools/server.py
from tools.server import app as application
