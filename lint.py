import os
import subprocess
import json
from datetime import datetime

# Ruta de la carpeta docs y result
docs_folder = 'docs'
result_folder = 'result'

# Asegurarse de que la carpeta result existe
os.makedirs(result_folder, exist_ok=True)

# Cargar las excepciones de markdownlint desde un archivo JSON
with open('markdownlint.json', 'r') as f:
    exceptions = json.load(f)

# Función para registrar la ejecución en EXECUTIONLOG.md
def log_execution(doc_file, result_file_path, compliance_percentage, missing_sections):
    """
    Registra la ejecución de la validación de markdown en un archivo de log.

    Args:
        doc_file (str): Nombre del archivo de documento procesado.
        result_file_path (str): Ruta del archivo de resultados.
        compliance_percentage (int): Porcentaje de cumplimiento de las reglas de markdown.
        missing_sections (bool): Indica si faltan secciones en el documento.
    """
    log_file_path = 'EXECUTIONLOG.md'
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = "Operación Exitosa" if compliance_percentage == 100 and not missing_sections else "Operación Fallida"
    
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"### {current_time}\n")
        log_file.write(f"- **Documento:** {doc_file}\n")
        log_file.write(f"- **Resultado:** {result}\n")
        log_file.write(f"- **Fichero de Resultados:** {result_file_path}\n")
        log_file.write("\n")

# Función para procesar cada archivo .md
def process_markdown_file(file_path):
    """
    Procesa un archivo markdown, ejecuta markdownlint y guarda los resultados.

    Args:
        file_path (str): Ruta del archivo markdown a procesar.
    """
    file_name = os.path.basename(file_path)
    result_file_name = file_name.replace('.md', f'_result_mdlint_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt')
    result_file_path = os.path.join(result_folder, result_file_name)
    
    try:
        # Ejecutar markdownlint con las excepciones
        result = subprocess.run(['markdownlint', file_path, '-c', 'markdownlint.json'], capture_output=True, text=True)
        
        # Escribir el resultado en el archivo de resultados
        with open(result_file_path, 'w') as result_file:
            if result.returncode == 0:
                result_file.write('Operación exitosa\n')
                compliance_percentage = 100
                missing_sections = False
            else:
                result_file.write('Operación fallida\n')
                compliance_percentage = 0
                missing_sections = True
            result_file.write(result.stdout)
            result_file.write(result.stderr)
        
        # Registrar la ejecución en EXECUTIONLOG.md
        log_execution(file_name, result_file_path, compliance_percentage, missing_sections)
        
        print(f'Procesado: {file_name}')
    except Exception as e:
        print(f'Error procesando {file_name}: {e}')

# Procesar todos los archivos .md en la carpeta docs
for file_name in os.listdir(docs_folder):
    if file_name.endswith('.md'):
        process_markdown_file(os.path.join(docs_folder, file_name))
