import os
import re
import shutil

def copy_and_rename_projects(source_folder, dest_folder, old_prefix, new_prefix):
    # Controlla se la cartella di destinazione esiste già
    if os.path.exists(dest_folder):
        print(f"Errore: La cartella di destinazione {dest_folder} esiste già.")
        return

    # Copia tutta la cartella di origine nella cartella di destinazione
    shutil.copytree(source_folder, dest_folder)
    print(f"Tutti i file sono stati copiati da {source_folder} a {dest_folder}")

    # Scansiona la cartella di destinazione per file .csproj e .sln
    for root, dirs, files in os.walk(dest_folder):
        for file in files:
            if file.endswith('.csproj'):
                file_path = os.path.join(root, file)
                rename_project_file(file_path, old_prefix, new_prefix)
            elif file.endswith('.cs'):
                file_path = os.path.join(root, file)
                rename_code_file(file_path, old_prefix, new_prefix)
            elif file.endswith('.sln'):
                file_path = os.path.join(root, file)
                update_solution_file(file_path, old_prefix, new_prefix)

def rename_project_file(file_path, old_prefix, new_prefix):
    # Leggi il contenuto del file .csproj
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Modifica il nome del progetto (nel file .csproj)
    if old_prefix in file_path:
        new_file_path = file_path.replace(old_prefix, new_prefix)
        os.rename(file_path, new_file_path)
        print(f"Rinominato: {file_path} -> {new_file_path}")
        file_path = new_file_path
    
    # Modifica tutte le occorrenze di references (riferimenti a progetti con il vecchio prefisso)
    updated_content = re.sub(r'(<ProjectReference.*Include=")(FlexCore\..*\.csproj")', 
                            lambda match: match.group(1) + match.group(2).replace(old_prefix, new_prefix), content)
    
    # Modifica anche il RootNamespace
    updated_content = re.sub(r'(<RootNamespace>)(FlexCore)(</RootNamespace>)', 
                            lambda match: match.group(1) + new_prefix + match.group(3), updated_content)

    # Aggiorna anche i namespaces e i riferimenti ai tipi (C#)
    updated_content = updated_content.replace('FlexCore.', 'DSx.')

    # Scrivi il file aggiornato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"File {file_path} aggiornato.")

def rename_code_file(file_path, old_prefix, new_prefix):
    # Rinomina i file .cs con il vecchio prefisso
    if old_prefix in file_path:
        new_file_path = file_path.replace(old_prefix, new_prefix)
        os.rename(file_path, new_file_path)
        print(f"Rinominato file di codice: {file_path} -> {new_file_path}")
        
        # Leggi il contenuto del file .cs
        with open(new_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Modifica il namespace nel codice sorgente
        updated_content = content.replace(f'{old_prefix}.', f'{new_prefix}.')
        
        # Scrivi il file aggiornato
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"File di codice {new_file_path} aggiornato.")

def update_solution_file(file_path, old_prefix, new_prefix):
    # Leggi il contenuto del file .sln
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Modifica tutti i riferimenti ai progetti
    updated_content = re.sub(r'(".*)FlexCore(\..*\.csproj")', 
                            lambda match: match.group(1) + new_prefix + match.group(2), content)

    # Scrivi il file aggiornato
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"File {file_path} della soluzione aggiornato.")

# Esegui lo script
if __name__ == "__main__":
    source_folder = "path/to/your/source"  # Modifica con il percorso della tua cartella sorgente
    dest_folder = "path/to/your/destination"  # Modifica con il percorso della tua cartella destinazione
    old_prefix = "FlexCore"
    new_prefix = "DSx"
    
    copy_and_rename_projects(source_folder, dest_folder, old_prefix, new_prefix)
