"""
Generatore XML con supporto a:
- Pattern di inclusione/esclusione
- Gestione gerarchica delle cartelle
- CDATA per file di testo
- vuoto per file binari (non riconosciuti come testo)
"""
from _modules.logging.logging import create_logger  # <-- POSIZIONE ORIGINALE
logger = create_logger(__name__)  # <-- POSIZIONE ORIGINALE

# Altri import ESATTAMENTE come nel tuo codice originale
import re
import os
import fnmatch
import datetime
from xmlnode import XMLNode
from _modules.file_utils import FileHandler
import xml.etree.ElementTree as ET

# def glob_to_regex(pattern: str) -> str:
#     """Converte pattern glob in regex, supportando * e **."""
#     pattern = pattern.replace("\\", "/")
    
#     # Caso speciale: pattern "*" deve matchare qualsiasi cartella/file
#     if pattern == "*":
#         return r"^.*$"  # Match completo
    
#     pattern = pattern.replace("**", "<GLOB_STAR>")
#     regex = re.escape(pattern)
#     regex = regex.replace("<GLOB_STAR>", ".*")
#     regex = regex.replace(r"\*", "[^/\\\\]*")  # Match qualsiasi carattere tranne / o \
#     regex = regex.replace(r"\/", r"[/\\]")      # Match esplicito per / o \
#     return f"^{regex}$"
def glob_to_regex(pattern: str) -> str:
    """Converte pattern glob in regex, supportando * e **.
    
    Args:
        pattern: Stringa glob da convertire (es. "**/*.py")
        
    Returns:
        Stringa regex con flag case-insensitive (?i)
    """
    pattern = pattern.replace("\\", "/")
    
    # Caso speciale: pattern "*" deve matchare qualsiasi cartella/file
    if pattern == "*":
        return r"(?i)^.*$"  # Aggiunto (?i) per ignorecase
    
    pattern = pattern.replace("**", "<GLOB_STAR>")
    regex = re.escape(pattern)
    regex = regex.replace("<GLOB_STAR>", ".*")
    regex = regex.replace(r"\*", "[^/\\\\]*")  # Match qualsiasi carattere tranne / o \
    regex = regex.replace(r"\/", r"[/\\]")      # Match esplicito per / o \
    
    return f"(?i)^{regex}$"  # Aggiunto (?i) all'inizio per ignorecase

def create_xml_with_indent(    
    target_path_folder: str,
    output_file: str,
    ignore_folders: list = [],
    ignore_files: list = [],
    indent: str = "",
    include_folders: list = ["*"],
    indent_content: bool = True,
    include_files: list = []
) -> tuple:
    """
    Genera un XML rappresentante la struttura del filesystem.
    
    :param target_path_folder: Percorso della cartella da analizzare
    :param output_file: Percorso del file XML di output
    :param ignore_folders: Lista di cartelle da ignorare
    :param ignore_files: Lista di file da ignorare
    :param indent: Stringa di indentazione
    :param include_folders: Lista di pattern per includere cartelle
    :param indent_content: Flag per indentare il contenuto
    :param include_files: Lista di pattern per includere file
    :return: Tupla (successo: bool, messaggio: str)
    """
    include_folder_regex = [re.compile(glob_to_regex(p)) for p in include_folders]
    exclude_folder_regex = [re.compile(glob_to_regex(p)) for p in ignore_folders]
    include_file_regex = [re.compile(glob_to_regex(p)) for p in include_files]

    def process_content(file_handler_instance: FileHandler, indent_level: int, indent: str, indent_content: bool):
        fh = file_handler_instance
        if not fh.has_info_been_read:
            fh.get_info()
        
        content_processed = None
        msg_err = None
        
        content_file, msg_err = fh.read()
        if content_file:
            is_text, msg_err = fh.is_text()
            if is_text:
                if indent_content:
                    indent_str = indent * (indent_level + 1)
                    lines = content_file.splitlines()
                    formatted_content = "\n".join(f"{indent_str}{line}" for line in lines)
                    indent_str_closed_tag = indent * indent_level
                    content_processed = f"<![CDATA[\n{formatted_content}\n{indent_str_closed_tag}]]>"
                else:
                    content_processed = f"<![CDATA[{content_file}]]>"
            else:
                msg = f"File binario: {fh.file_path} (MIME: {fh.mime}, Encoding: {fh.encoding})"
                content_processed = msg
                logger.warning(msg)
        else:
            msg = f"Errore lettura file: {fh.file_path} - {msg_err}"
            logger.error(msg)
        return content_processed, msg_err

    def add_element(
            parent: XMLNode, 
            current_dir: str, 
            indent_level: int, 
            ignore_folders: list, 
            ignore_files: list, 
            include_folder_regex: list, 
            root_path: str,
            indent_content: bool,
            include_file_regex: list
        ):
        abs_path = os.path.abspath(current_dir).replace("\\", "/")  # Percorso assoluto normalizzato
        
        # CASE SENSITIVE
        is_folder_included = any(re.search(rgx, abs_path) for rgx in include_folder_regex)
        is_folder_excluded = any(re.search(rgx, abs_path) for rgx in exclude_folder_regex)
        
        if not is_folder_included or is_folder_excluded:
            return

        folder_node = XMLNode("Folder", {"Name": os.path.basename(current_dir)})
        parent.add_child(folder_node)
        indent_level += 1

        # for entry in os.scandir(current_dir):
        for entry in sorted(os.scandir(current_dir), key=lambda e: e.name.lower()):
            entry_path = os.path.join(current_dir, entry.name)
            
            if entry.is_dir():
                add_element(
                    folder_node, 
                    entry_path, 
                    indent_level, 
                    ignore_folders, 
                    ignore_files, 
                    include_folder_regex, 
                    root_path, 
                    indent_content,
                    include_file_regex
                )
            else:
                file_name = entry.name
                is_file_included = not include_file_regex or any(rgx.match(file_name) for rgx in include_file_regex)
                is_file_excluded = any(fnmatch.fnmatch(file_name, p) for p in ignore_files)
                
                if not is_file_included or is_file_excluded:
                    continue

                fh = FileHandler(entry_path)
                if not fh.exists()[0]:
                    continue
                fh.get_info()

                node_file = XMLNode("File", {"Name": fh.name, "Size": str(fh.size)})
                indent_level += 1

                node_content = XMLNode("Content", {
                    "MIME": fh.mime,
                    "Encoding": fh.encoding
                })
                if fh.bom:
                    node_content.attributes["BOM"] = "True"
                indent_level += 1

                content, msg_err = process_content(fh, indent_level, indent, indent_content)

                node_content.set_text(content)
                node_file.add_child(node_content)
                folder_node.add_child(node_file)

    node_dad = XMLNode("DataArchitectureDesign", {"Author": "Davide"})
    indent_initial_level = 0

    node_creation = XMLNode("Creation", {
        "Date": datetime.datetime.now().strftime("%d-%m-%Y"),
        "Hour": datetime.datetime.now().strftime("%H:%M:%S")
    })
    node_dad.add_child(node_creation)
    indent_initial_level += 1
    
    node_filesystem = XMLNode("FileSystem")
    node_dad.add_child(node_filesystem)
    indent_initial_level += 1
    
    add_element(
        node_filesystem, 
        target_path_folder, 
        indent_initial_level, 
        ignore_folders, 
        ignore_files, 
        include_folder_regex, 
        target_path_folder, 
        indent_content,
        include_file_regex
    )

    content_xml = f'<?xml version="1.0" encoding="utf-8"?>\n{node_dad.to_xml(indent=indent)}'
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content_xml)
    
    return True, f"XML generato: {output_file}"