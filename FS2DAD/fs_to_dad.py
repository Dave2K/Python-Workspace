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

def fs_to_dad(    
    target_path_folder: str,
    output_file: str,
    ignore_folders: list = [],
    ignore_files: list = [],
    indent_chars: str = "",
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

    def add_element(
            parent: XMLNode, 
            current_dir: str, 
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

        # for entry in os.scandir(current_dir):
        for entry in sorted(os.scandir(current_dir), key=lambda e: e.name.lower()):
            entry_path = os.path.join(current_dir, entry.name)
            
            if entry.is_dir():
                add_element(
                    folder_node, 
                    entry_path, 
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

                node_file = XMLNode("File", {
                    "Name": fh.name, 
                    # "Size": str(fh.size),
                    "MIME": fh.mime,
                    "Encoding": fh.encoding
                })
                if fh.bom:
                    node_file.attributes["BOM"] = "True"

                content_file, msg_err = fh.read()
                if content_file:
                    is_text, msg_err = fh.is_text()
                    if not is_text:
                        msg = f"File binario: {fh.file_path} (MIME: {fh.mime}, Encoding: {fh.encoding})"
                        content_file = msg
                        logger.warning(msg)
                else:
                    msg = f"Errore lettura file: {fh.file_path} - {msg_err}"
                    content_file = msg
                    logger.error(msg)
                node_file.set_text(content_file)
                folder_node.add_child(node_file)

    node_dad = XMLNode("DataArchitectureDesign", {"Author": "Davide"})

    node_creation = XMLNode("Creation", {
        "Date": datetime.datetime.now().strftime("%d-%m-%Y"),
        "Hour": datetime.datetime.now().strftime("%H:%M:%S")
    })
    node_dad.add_child(node_creation)
    
    node_filesystem = XMLNode("FileSystem")
    node_dad.add_child(node_filesystem)

    add_element(
        node_filesystem, 
        target_path_folder, 
        ignore_folders, 
        ignore_files, 
        include_folder_regex, 
        target_path_folder, 
        indent_content,
        include_file_regex
    )

    content_xml = f'<?xml version="1.0" encoding="utf-8"?>\n{node_dad.to_xml(indent_chars=indent_chars)}'
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content_xml)
    
    return True, f"XML generato: {output_file}"