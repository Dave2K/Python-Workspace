import logging
from CsprojAnalyzer.dependency_mapper import DependencyMapper
from _modules.xmlnode import XMLNode
from _modules.logging.logging import configure_logging, create_logger
import argparse
import os

logger = create_logger(__name__)

# python generate_csproj_xml.py --root /percorso/solution --output dependencies.xml

def generate_csproj_xml(root_path: str, output_file: str):
    """Genera XML con tutte le dipendenze"""
    try:
        logger.info("Avvio generazione XML...")
        mapper = DependencyMapper(root_path)
        
        # Fase 1: Ricerca progetti
        mapper.find_csproj_files()
        
        # Fase 2: Analisi dipendenze
        mapper.build_dependency_graph()
        
        # Fase 3: Costruzione XML
        root = XMLNode("SolutionProjects", {"SolutionPath": root_path})
        
        for project, deps in mapper.graph.items():
            project_node = XMLNode("Project", {"Path": project})
            
            # Aggiungi riferimenti
            refs_node = XMLNode("References")
            for ref_path in deps:
                ref_node = XMLNode("ProjectReference", {"Path": ref_path})
                refs_node.add_child(ref_node)
            
            project_node.add_child(refs_node)
            root.add_child(project_node)
        
        # Scrittura file
        root.write_file(output_file, indent_chars="  ")
        logger.info(f"XML generato correttamente: {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Errore generazione XML: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Configurazione logging
    configure_logging(
        enable_file_logging=False,
        file_prefix="csproj_analyzer",
        log_level=logging.DEBUG,
        console_style="both",
        enable_console_logging=True
    )
    
    # Parsing argomenti
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Cartella radice della solution")
    parser.add_argument("--output", default="csproj_dependencies.xml", help="File di output XML")
    
    args = parser.parse_args()
    
    if generate_csproj_xml(args.root, args.output):
        logger.info("Elaborazione completata con successo")
    else:
        logger.error("Elaborazione completata con errori")