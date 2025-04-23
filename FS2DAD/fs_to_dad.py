"""
Generatore XML con supporto a:
- Pattern di inclusione/esclusione
- Gestione gerarchica delle cartelle
- CDATA per file di testo
- vuoto per file binari (non riconosciuti come testo)
"""
from _modules.logging.logging import create_logger 
logger = create_logger(__name__) 

import re
import os
import datetime
from _modules.xmlnode import XMLNode
from _modules.file_utils import FileHandler
import xml.etree.ElementTree as ET

def cb(value): # color boolean
    if value:
        return f"\033[32m{value}\033[0m"   
    return f"\033[31m{value}\033[0m"


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
    indent_chars: str = "",
    sanitize: bool = False,
    split_size: int = 0,
    remove_xml_comments : bool = False,
    ignore_folders: list = [],
    ignore_files: list = [],
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

    if not os.path.exists(target_path_folder):
        return False, f"Cartella {target_path_folder} non trovata"

    include_folder_regex = [re.compile(glob_to_regex(p)) for p in include_folders]
    exclude_folder_regex = [re.compile(glob_to_regex(p)) for p in ignore_folders]
    
    # include_file_regex = [re.compile(glob_to_regex(p)) for p in include_files]
    include_file_regex = [re.compile(glob_to_regex(p)) for p in include_files]
    exclude_file_regex = [re.compile(glob_to_regex(p)) for p in ignore_files]

    def add_element(
            parent: XMLNode, 
            current_dir: str, 
            ignore_folders: list, 
            ignore_files: list, 
            include_folder_regex: list, 
            root_path: str,
            indent_content: bool,
            include_file_regex: list,
            exclude_file_regex:list,
            is_folder_included:False 
        ):
        # # Percorso assoluto normalizzato
        # abs_path = os.path.abspath(current_dir).replace("\\", "/")  
                    
        # # Verifica se la cartella deve essere inclusa (match con almeno un pattern di inclusione)
        # is_folder_included = any(re.search(rgx, abs_path) for rgx in include_folder_regex)
        # # Verifica se la cartella deve essere esclusa (match con almeno un pattern di esclusione)
        # is_folder_excluded = any(re.search(rgx, abs_path) for rgx in exclude_folder_regex)

        # msg = f"incluso:{is_folder_included}, escluso:{is_folder_excluded}, path:{abs_path}, "
        # logger.debug(msg)
        # Percorso assoluto 
        abs_path = os.path.abspath(current_dir)  
        # Percorso relativo normalizzato
        rel_path = os.path.relpath(abs_path, root_path).replace("\\", "/")       
        # Verifica se la cartella deve essere inclusa (match con almeno un pattern di inclusione)
        if not is_folder_included:
            is_folder_included = any(re.search(rgx, rel_path) for rgx in include_folder_regex)
        # Verifica se la cartella deve essere esclusa (match con almeno un pattern di esclusione)
        is_folder_excluded = any(re.search(rgx, rel_path) for rgx in exclude_folder_regex)

        msg = f"incluso:{is_folder_included}, escluso:{is_folder_excluded}, path:{rel_path}, "
        logger.debug(msg)

        # # se non sono inclusi o sono esclusi allora esce
        # if not is_folder_included or is_folder_excluded:
        #     return
        # se non sono inclusi o sono esclusi allora esce
        if is_folder_excluded:
            return

        folder_node = XMLNode("Folder", {"Name": os.path.basename(current_dir)})
        # parent.add_child(folder_node)
        founded_file_included = False

        # scansione, prima file poi cartelle
        entries = sorted(
            os.scandir(current_dir),
            key=lambda e: (
                0 if e.is_file() else 1,  # Prima i file (0), poi le cartelle (1)
                e.name.lower()            # Ordine alfabetico per nome
            )
        )
        for entry in entries:
            entry_path = os.path.join(current_dir, entry.name)
            if entry.is_dir():
                node = add_element(
                    folder_node, 
                    entry_path, 
                    ignore_folders, 
                    ignore_files, 
                    include_folder_regex, 
                    root_path, 
                    indent_content,
                    include_file_regex,
                    exclude_file_regex,
                    is_folder_included
                )
                if node:
                    folder_node.add_child(node)
                    founded_file_included = True
                    logger.debug(f"aggiungo nodo a {rel_path}")
                else:
                    logger.debug(f"NON aggiungo nodo a {rel_path}")

            else:
                file_name = entry.name
                # is_file_included = not include_file_regex or any(rgx.match(file_name) for rgx in include_file_regex)
                # is_file_excluded = any(rgx.search(file_name) for rgx in exclude_file_regex)   
                # if not is_file_included or is_file_excluded:
                #     continue
                # controlla se il file è da escludere o da includere 
                is_file_included = not include_file_regex or any(rgx.match(file_name) for rgx in include_file_regex)   
                is_file_excluded = any(rgx.search(file_name) for rgx in exclude_file_regex)   

                logger.debug(" ")
                # msg = f"FILE incluso:{cb(is_file_included)}, escluso:{cb(is_file_excluded)}, file:{file_name}, "
                msg = f"FILE incluso:{is_file_included}, escluso:{is_file_excluded}, file:{file_name}, "
                logger.debug(msg)

                if is_file_excluded:
                    continue

                msg = f"incluso {is_folder_included}, PATH :{rel_path}"
                logger.debug(msg)

                if not is_folder_included and not is_file_included:
                    continue 

                msg = f"includo {file_name}, "
                logger.debug(msg)


                fh = FileHandler(entry_path)
                if not fh.exists()[0]:
                    continue
                fh.get_info()

                node_file = XMLNode("File", {
                    "Name": fh.name, 
                    # "Size": str(fh.size),
                    # "MIME": fh.mime,
                    # "Encoding": fh.encoding
                })
                # if fh.bom:
                #     node_file.attributes["BOM"] = "True"

                content_file, msg_err = fh.read()
                if content_file:
                    is_text, msg_err = fh.is_text()
                    if not is_text:
                        msg = f"File binario: [MIME: {fh.mime}, Encoding: {fh.encoding}] {fh.file_path}"
                        content_file = msg
                        logger.warning(msg)
                elif msg_err:
                    msg = f"Errore [{msg_err}] - lettura file: {fh.file_path}"
                    content_file = msg
                    logger.warning(msg)

                node_file.set_text(content_file)
                folder_node.add_child(node_file)
                founded_file_included = True

        return folder_node if founded_file_included else None


    node_dad = XMLNode("DataArchitectureDesign", {"Author": "Davide"})

    node_creation = XMLNode("Create", {
        "Date": datetime.datetime.now().strftime("%d-%m-%Y"),
        "Hour": datetime.datetime.now().strftime("%H:%M:%S")
    })
    node_dad.add_child(node_creation)
    
    node_filesystem = XMLNode("FileSystem")
    node_dad.add_child(node_filesystem)

    node = add_element(
        node_filesystem, 
        target_path_folder, 
        ignore_folders, 
        ignore_files, 
        include_folder_regex, 
        target_path_folder, 
        indent_content,
        include_file_regex,
        exclude_file_regex,
        False
    )
    if node:
        node_filesystem.add_child(node)

    node_dad.write_file(file_name=output_file, 
                        indent_chars=indent_chars, 
                        sanitize=sanitize, 
                        split_size=split_size, 
                        remove_xml_comments=remove_xml_comments)
    
    return True, f"XML generato: {output_file}"