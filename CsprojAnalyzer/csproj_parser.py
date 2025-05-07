import xml.etree.ElementTree as ET
import os
from pathlib import Path
from _modules.logging.logging import create_logger

logger = create_logger(__name__)

def parse_csproj(csproj_path: str) -> dict:
    """Analizza un file .csproj e restituisce i riferimenti"""
    result = {
        'project_references': [],
        'package_references': [],
        'project_path': csproj_path
    }
    
    try:
        logger.debug(f"Inizio parsing: {csproj_path}")
        tree = ET.parse(csproj_path)
        root = tree.getroot()
        
        ns = {'msbuild': 'http://schemas.microsoft.com/developer/msbuild/2003'}
        
        # Project References
        for ref in root.findall(".//msbuild:ProjectReference", ns):
            include_path = ref.attrib.get('Include', '')
            if include_path:
                abs_path = str(Path(csproj_path).parent.joinpath(include_path).resolve())
                if os.path.exists(abs_path):
                    result['project_references'].append(abs_path)
                    logger.debug(f"Trovato riferimento a progetto: {abs_path}")
                else:
                    logger.warning(f"Riferimento non valido: {include_path}")

        # Package References
        for pkg in root.findall(".//msbuild:PackageReference", ns):
            pkg_name = pkg.attrib.get('Include', '')
            pkg_version = pkg.attrib.get('Version', '')
            if pkg_name:
                result['package_references'].append({
                    'name': pkg_name,
                    'version': pkg_version
                })
                logger.debug(f"Trovato pacchetto: {pkg_name} v{pkg_version}")

        logger.info(f"Parsing completato: {csproj_path} - {len(result['project_references'])} ref progetti, {len(result['package_references'])} ref pacchetti")
    
    except ET.ParseError as e:
        logger.error(f"Errore di parsing XML in {csproj_path}: {str(e)}")
    except Exception as e:
        logger.error(f"Errore generico in {csproj_path}: {str(e)}", exc_info=True)
    
    return result