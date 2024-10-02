import os
import re
import subprocess
from datetime import datetime

def get_sections_and_subsections(file_path):
    """
    Lee un archivo y organiza su contenido en secciones y subsecciones.

    Parámetros:
    file_path (str): Ruta del archivo a leer.

    Retorna:
    dict: Un diccionario con secciones como claves y listas de subsecciones como valores.
    """
    sections = {}
    with open(file_path, 'r') as file:
        current_section = None
        for line in file:
            line = line.strip()
            if line.startswith('#'):
                current_section = line
                sections[current_section] = []
            elif line.startswith('-') and current_section:
                sections[current_section].append(line)
    return sections

def compare_documents(template_sections, doc_sections):
    """
    Compara las secciones y subsecciones de dos documentos.

    Parámetros:
    template_sections (dict): Secciones del documento plantilla.
    doc_sections (dict): Secciones del documento a comparar.

    Retorna:
    tuple: 
        - compliance_percentage (float): Porcentaje de cumplimiento.
        - missing_sections (list): Lista de secciones y subsecciones faltantes.
    """
    total_elements = sum(len(subsections) + 1 for subsections in template_sections.values())
    matched_elements = 0
    missing_sections = []

    for section, subsections in template_sections.items():
        if section in doc_sections:
            matched_elements += 1
            for subsection in subsections:
                if subsection in doc_sections[section]:
                    matched_elements += 1
                else:
                    missing_sections.append(f"Missing subsection: {subsection} in section: {section}")
        else:
            missing_sections.append(f"Missing section: {section}")

    compliance_percentage = (matched_elements / total_elements) * 100
    return compliance_percentage, missing_sections

def log_execution(doc_file, template_file, result_file_path, compliance_percentage, missing_sections):
    """
    Registra la ejecución de la comparación en un archivo de log.

    Parámetros:
    doc_file (str): Nombre del documento.
    template_file (str): Nombre del archivo plantilla.
    result_file_path (str): Ruta del archivo de resultados.
    compliance_percentage (float): Porcentaje de cumplimiento.
    missing_sections (list): Lista de secciones y subsecciones faltantes.
    """
    log_file_path = 'EXECUTIONLOG.md'
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = "Operación Exitosa" if compliance_percentage == 100 and not missing_sections else "Operación Fallida"
    
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"### {current_time}\n")
        log_file.write(f"- **Documento:** {doc_file}\n")
        log_file.write(f"- **Template:** {template_file}\n")
        log_file.write(f"- **Resultado:** {result}\n")
        log_file.write(f"- **Fichero de Resultados:** {result_file_path}\n")
        log_file.write("\n")
            
def main():
    """
    Función principal que coordina la ejecución del script.
    """
    template_dir = 'template'
    docs_dir = 'docs'
    results_dir = 'result'
    config_file = 'markdownlint.json'

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")

    for doc_file in os.listdir(docs_dir):
        if doc_file.endswith('.md'):
            template_name = re.match(r"([^_]+)", doc_file).group(1)
            doc_file2 = template_name + "_"
            doc_file2 += re.match(r"^[^_]+_(.+)\.md$", doc_file).group(1)
            
            template_file = os.path.join(template_dir, f"{template_name}.md")
            doc_file_path = os.path.join(docs_dir, doc_file)

            if os.path.exists(template_file):
                print(f"Template file {template_file} found for document {doc_file}")
                template_sections = get_sections_and_subsections(template_file)
                doc_sections = get_sections_and_subsections(doc_file_path)

                compliance_percentage, missing_sections = compare_documents(template_sections, doc_sections)

                result_file_path = os.path.join(results_dir, f"{doc_file2}_result_schema_{current_time}.txt")
                with open(result_file_path, 'w') as result_file:
                    if compliance_percentage == 100 and not missing_sections:
                        result_file.write("Operación Exitosa\n")
                    else:
                        result_file.write("Operación Fallida\n")
                    for missing in missing_sections:
                        result_file.write(f"{missing}\n")
                    result_file.write(f"El documento tiene un % de compliance: {compliance_percentage:.2f}%\n")
                
                log_execution(doc_file, template_file, result_file_path, compliance_percentage, missing_sections)
            else:
                print(f"Template file {template_file} not found for document {doc_file}")

if __name__ == "__main__":
    main()
