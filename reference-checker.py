#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FS-Reference-Checker - Strumento per riferimenti relativi in progetti .NET
Versione 3.0 - Solo percorsi relativi e log condizionali
"""

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import shutil

# ------------------------------
# FUNZIONI CORE
# ------------------------------

def log(message, level=0, symbol="▪️"):
    """Funzione di logging strutturato con emoji"""
    indent = "  " * level
    print(f"{indent}{symbol} {message}")

def calculate_relative_path(source_project, target_project):
    """Calcola il percorso relativo tra due progetti partendo dalla directory del progetto sorgente"""
    try:
        rel_dir = os.path.relpath(target_project.parent, source_project.parent)
        return (Path(rel_dir) / target_project.name).as_posix()
    except ValueError:
        return None

def check_project_references(project_path, projects_map, solution_root):
    """Verifica i riferimenti mostrando solo percorsi relativi in caso di problemi"""
    broken_refs = []

    try:
        ET.register_namespace('', 'http://schemas.microsoft.com/developer/msbuild/2003')
        tree = ET.parse(project_path)
        root = tree.getroot()
    except Exception as e:
        log(f"❌ ERRORE ANALISI: {project_path.relative_to(solution_root)}", level=0)
        log(str(e), level=1)
        return broken_refs

    references = root.findall('.//{http://schemas.microsoft.com/developer/msbuild/2003}ProjectReference') or root.findall('.//ProjectReference')
    
    for ref in references:
        original_ref = ref.get('Include')
        if not original_ref:
            continue

        target_name = Path(original_ref).name
        candidates = [p for p in projects_map.get(target_name, []) if p != project_path]

        # Verifica se il riferimento è valido
        abs_ref_path = (project_path.parent / original_ref).resolve()
        if not abs_ref_path.exists() or not abs_ref_path.suffix == '.csproj':
            suggestions = []
            for candidate in candidates:
                suggested_path = calculate_relative_path(project_path, candidate)
                if suggested_path:
                    suggestions.append({
                        'suggested': suggested_path,
                        'target_relative': candidate.relative_to(solution_root).parent
                    })

            if suggestions:
                broken_refs.append({
                    'original': original_ref,
                    'suggestions': suggestions
                })

    # Log solo se ci sono problemi
    if broken_refs:
        project_rel_path = project_path.relative_to(solution_root)
        log(f"\n🚨 PROBLEMA IN: {project_rel_path}", level=0)
        
        for broken in broken_refs:
            log(f"❌ Riferimento non valido: {broken['original']}", level=1)
            
            best = broken['suggestions'][0]
            log(f"💡 Percorso corretto suggerito: {best['suggested']}", level=2)
            log(f"📁 Cartella target: {best['target_relative']}", level=3)

    return broken_refs

def fix_project_references(project_path, projects_map, solution_root):
    """Corregge i riferimenti mantenendo percorsi relativi corretti"""
    modified = False

    try:
        ET.register_namespace('', 'http://schemas.microsoft.com/developer/msbuild/2003')
        tree = ET.parse(project_path)
        root = tree.getroot()
    except Exception as e:
        log(f"❌ ERRORE ANALISI: {project_path.relative_to(solution_root)}", level=0)
        log(str(e), level=1)
        return False

    references = root.findall('.//{http://schemas.microsoft.com/developer/msbuild/2003}ProjectReference') or root.findall('.//ProjectReference')

    for ref in references:
        original_ref = ref.get('Include')
        if not original_ref:
            continue

        target_name = Path(original_ref).name
        candidates = [p for p in projects_map.get(target_name, []) if p != project_path]
        
        if candidates:
            new_ref = calculate_relative_path(project_path, candidates[0])
            if new_ref and new_ref != original_ref:
                if not modified:
                    backup_path = project_path.with_suffix(project_path.suffix + '.bak')
                    shutil.copyfile(project_path, backup_path)
                    log(f"💾 Backup creato: {backup_path.relative_to(solution_root)}", level=1)

                ref.set('Include', new_ref)
                modified = True
                log(f"🔄 Modifica: {original_ref} -> {new_ref}", level=1)

    if modified:
        try:
            tree.write(project_path, encoding='utf-8', xml_declaration=True)
            log(f"✅ Salvate modifiche in: {project_path.relative_to(solution_root)}", level=1)
        except Exception as e:
            log(f"❌ Errore salvataggio: {str(e)}", level=1)
            return False

    return modified

# ------------------------------
# MAIN
# ------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Strumento per gestione riferimenti relativi in progetti .NET",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "target_folder",
        type=str,
        help="Cartella root contenente i progetti .NET"
    )
    
    parser.add_argument(
        "--fix", 
        action="store_true",
        help="Abilita la correzione automatica (crea backup .bak)"
    )
    
    args = parser.parse_args()
    
    try:
        solution_root = Path(args.target_folder).resolve()
        projects = list(solution_root.rglob("*.csproj"))
        projects_map = defaultdict(list)
        
        for p in projects:
            projects_map[p.name].append(p)

        total_problems = 0
        modified_files = 0

        print("\n" + "=" * 50)
        print("🔍 FS-Reference-Checker - Inizio analisi")

        for project in projects:
            broken_refs = check_project_references(project, projects_map, solution_root)
            total_problems += len(broken_refs)

            if args.fix and broken_refs:
                if fix_project_references(project, projects_map, solution_root):
                    modified_files += 1

        print("\n" + "=" * 50)
        if total_problems > 0 or modified_files > 0:
            print(f"🏁 Riferimenti problematici trovati: {total_problems}")
            if args.fix:
                print(f"✏️ File modificati: {modified_files}")
                print("💾 Backup creati con estensione .bak")
        else:
            print("✅ Nessun problema rilevato")

    except Exception as e:
        print(f"\n⛔ ERRORE CRITICO: {str(e)}")
        sys.exit(1)