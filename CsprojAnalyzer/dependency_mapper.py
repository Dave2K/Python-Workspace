from collections import defaultdict
import os
from CsprojAnalyzer.csproj_parser import parse_csproj
from _modules.logging.logging import create_logger

logger = create_logger(__name__)

class DependencyMapper:
    def __init__(self, root_path):
        self.root_path = os.path.abspath(root_path)
        self.graph = defaultdict(list)
        self.all_projects = []
        logger.info(f"Inizializzato mapper per: {self.root_path}")

    def find_csproj_files(self):
        """Cerca ricorsivamente tutti i file .csproj"""
        logger.info("Ricerca file .csproj in corso...")
        try:
            for root, _, files in os.walk(self.root_path):
                for file in files:
                    if file.endswith('.csproj'):
                        full_path = os.path.join(root, file)
                        self.all_projects.append(full_path)
                        logger.debug(f"Trovato .csproj: {full_path}")
            
            logger.info(f"Trovati {len(self.all_projects)} progetti .csproj")
        
        except Exception as e:
            logger.error(f"Errore durante la ricerca file: {str(e)}", exc_info=True)

    def build_dependency_graph(self):
        """Costruisce il grafo delle dipendenze"""
        logger.info("Costruzione grafo dipendenze...")
        try:
            for project in self.all_projects:
                dependencies = parse_csproj(project)['project_references']
                valid_deps = []
                
                for p in dependencies:
                    if os.path.exists(p):
                        valid_deps.append(os.path.normpath(p))
                    else:
                        logger.warning(f"Riferimento inesistente: {p} in {project}")
                
                self.graph[project] = valid_deps
                logger.debug(f"Progetto: {project} - Dipendenze: {len(valid_deps)}")
            
            logger.info(f"Grafo costruito con {len(self.graph)} nodi")
        
        except Exception as e:
            logger.error(f"Errore costruzione grafo: {str(e)}", exc_info=True)