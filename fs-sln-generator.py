#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FS-SLN-Generator - Generatore di soluzioni Visual Studio strutturate
"""

import os
import sys
import uuid
import subprocess
import argparse
import re
from pathlib import Path

def run_command(command):
    """Esegue un comando shell con gestione avanzata degli errori."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"✅ Comando eseguito: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Errore durante l'esecuzione: {e.cmd}")
        print(f"   Codice uscita: {e.returncode}")
        print(f"   Errore: {e.stderr.strip()}")
        return False

def generate_guid():
    return str(uuid.uuid4()).upper()

def extract_project_guid(csproj_path):
    try:
        with open(csproj_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'<ProjectGuid>\{(.*?)\}</ProjectGuid>', content)
            if match:
                return "{" + match.group(1).upper() + "}"
    except Exception:
        pass
    return "{" + generate_guid() + "}"

def parse_sln_projects(sln_path):
    """Estrae i GUID dei progetti dal file .sln"""
    projects = {}
    sln_dir = os.path.dirname(sln_path)
    with open(sln_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Project("):
                parts = [p.strip().strip('"') for p in line.split(',')]
                if len(parts) >= 3:
                    guid = parts[-1].upper().strip('{}')
                    project_path = Path(sln_dir) / parts[1]
                    rel_path = os.path.relpath(project_path, sln_dir)
                    projects[rel_path.replace(os.sep, '/')] = guid
    return projects

def remove_existing_virtual_folders(content):
    lines = content.splitlines()
    new_lines = []
    in_folder_section = False
    
    for line in lines:
        if line.strip().startswith("Project(") and "{2150E333-8FDC-42A3-9474-1A3956D46DE8}" in line:
            in_folder_section = True
            continue
        if in_folder_section and line.strip() == "EndProject":
            in_folder_section = False
            continue
        if not in_folder_section:
            new_lines.append(line)
    
    return "\n".join(new_lines)

def remove_existing_nested_section(content):
    if "NestedProjects" not in content:
        return content
        
    start = content.find("GlobalSection(NestedProjects)")
    end = content.find("EndGlobalSection", start) + len("EndGlobalSection")
    return content[:start] + content[end:]

def create_solution_structure(target_folder, solution_file):
    """
    Crea la struttura della soluzione con percorsi assoluti
    """
    target_path = Path(target_folder).resolve()
    solution_path = Path(solution_file).resolve()
    
    projects = list(target_path.rglob("*.csproj"))
    print(f"🔍 Trovati {len(projects)} progetti in: {target_path}")

    if not projects:
        print("❌ Nessun progetto .csproj trovato")
        sys.exit(1)

    if not solution_path.exists():
        print(f"🆕 Creazione nuova soluzione: {solution_path}")
        if not run_command(f'dotnet new sln -n "{solution_path.stem}" -o "{solution_path.parent}"'):
            sys.exit(1)

    project_data = []
    folder_guids = {}

    print("\n" + "="*50)
    print("🗂  Inizio analisi progetti...")
    
    for csproj in projects:
        abs_csproj = csproj.resolve()
        print(f"\n📌 Progetto: {abs_csproj.name}")
        print(f"📂 Posizione fisica: {abs_csproj.parent}")

        # Calcola percorso relativo dalla solution
        rel_path_from_solution = Path(os.path.relpath(abs_csproj, solution_path.parent))
        print(f"📦 Percorso relativo soluzione: {rel_path_from_solution}")

        # Calcola percorso cartella virtuale
        folder_in_target = os.path.relpath(abs_csproj.parent, target_path)
        virtual_folder = folder_in_target.replace(os.sep, '/')
        
        # Rimuovi cartella padre ridondante
        project_name = abs_csproj.stem
        parent_dir = abs_csproj.parent.name
        if parent_dir == project_name:
            virtual_folder = str(Path(virtual_folder).parent).replace(os.sep, '/')
            if virtual_folder == ".":
                virtual_folder = ""

        virtual_folder = virtual_folder.rstrip('/').replace('/.', '').replace('//', '/')
        print(f"🖇️ Cartella virtuale assegnata: '{virtual_folder if virtual_folder else '(root)'}'")

        project_guid = extract_project_guid(abs_csproj)
        project_data.append({
            'path': rel_path_from_solution,
            'guid': project_guid,
            'folder': virtual_folder
        })

        # Genera GUID per la gerarchia
        folder_parts = virtual_folder.split('/') if virtual_folder else []
        current_virtual_path = ""
        
        for part in folder_parts:
            current_virtual_path = f"{current_virtual_path}/{part}" if current_virtual_path else part
            current_virtual_path = current_virtual_path.replace('//', '/')
            
            if current_virtual_path not in folder_guids:
                new_guid = "{" + generate_guid() + "}"
                folder_guids[current_virtual_path] = new_guid
                print(f"  🆔 Creata cartella: '{current_virtual_path}' [{new_guid}]")

    print("\n" + "="*50)
    print("🔨 Aggiunta progetti alla soluzione (usando percorsi assoluti)...")
    for idx, csproj in enumerate(projects, 1):
        abs_csproj = csproj.resolve()
        print(f"  {idx}/{len(projects)} Aggiungo: {abs_csproj}")
        if not run_command(f'dotnet sln "{solution_path}" add "{abs_csproj}"'):
            print("⏭️  Saltato progetto a causa di errori")
            continue

    # Leggi i GUID reali dalla soluzione
    sln_projects = parse_sln_projects(solution_path)
    
    # Aggiorna GUID progetti
    for project in project_data:
        rel_path = str(project['path']).replace(os.sep, '/')
        project['guid'] = "{" + sln_projects.get(rel_path, generate_guid()).upper() + "}"

    print("\n" + "="*50)
    print("🏗  Costruzione struttura cartelle virtuali...")
    
    with open(solution_path, "r", encoding="utf-8") as f:
        sln_content = f.read()

    # Pulizia sezioni
    sln_content = remove_existing_virtual_folders(sln_content)
    sln_content = remove_existing_nested_section(sln_content)

    # Genera dichiarazioni cartelle
    folder_declarations = []
    for folder_path, guid in folder_guids.items():
        folder_name = os.path.basename(folder_path) if folder_path else "Solution Items"
        decl = (
            f'Project("{{2150E333-8FDC-42A3-9474-1A3956D46DE8}}") = '
            f'"{folder_name}", "{folder_path}", "{guid}"\n'
            'EndProject'
        )
        folder_declarations.append(decl)
        print(f"  📂 Dichiarata cartella: '{folder_path}'")

    # Genera relazioni gerarchiche
    nested_entries = []
    print("\n" + "="*50)
    print("🔗 Collegamento gerarchie...")
    
    # 1. Cartelle -> Cartelle padre
    for folder_path, guid in folder_guids.items():
        if not folder_path:
            continue
            
        parent = '/'.join(folder_path.split('/')[:-1])
        if parent in folder_guids:
            nested_entries.append(f"        {guid} = {folder_guids[parent]}\n")
            print(f"  ⬆️ Collegamento: {folder_path} -> {parent}")

    # 2. Progetti -> Cartelle
    for project in project_data:
        if project['folder'] in folder_guids:
            nested_entries.append(f"        {project['guid']} = {folder_guids[project['folder']]}\n")
            print(f"  📎 Progetto collegato: {project['path'].name} -> {project['folder']}")
        else:
            print(f"  ⚠️ Attenzione: progetto {project['path'].name} non collegato!")

    # Aggiorna contenuto SLN
    insertion_point = sln_content.find("Global")
    new_content = sln_content[:insertion_point] + "\n".join(folder_declarations) + "\n" + sln_content[insertion_point:]
    
    global_section_end = new_content.find("EndGlobal", new_content.find("Global"))
    nested_section = "\tGlobalSection(NestedProjects) = preSolution\n" + "".join(nested_entries) + "\tEndGlobalSection\n"
    final_content = new_content[:global_section_end] + nested_section + new_content[global_section_end:]

    with open(solution_path, "w", encoding="utf-8") as f:
        f.write(final_content)

    print("\n" + "="*50)
    print("✅ Operazione completata!")
    print(f"• Progetti elaborati: {len(projects)}")
    print(f"• Cartelle create: {len(folder_guids)}")
    print(f"• Collegamenti gerarchici: {len(nested_entries)}")
    print(f"• Percorso soluzione: {solution_path}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera soluzione Visual Studio strutturata")
    parser.add_argument("target_folder", nargs="?", default=".", help="Cartella contenente i progetti")
    parser.add_argument("solution_file", nargs="?", default="FS-SLN-ALL.sln", help="Percorso del file .sln")
    
    args = parser.parse_args()
    
    try:
        print("🗃️  Avvio generazione soluzione...")
        create_solution_structure(args.target_folder, args.solution_file)
        print("🎉 Operazione completata con successo!")
    except Exception as e:
        print(f"\n⛔ Errore critico: {str(e)}")
        sys.exit(1)