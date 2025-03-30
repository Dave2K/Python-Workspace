"""
Modulo per visualizzare l'aiuto avanzato con documentazione sui pattern
"""

def display_help(name_main: str):
    help_text = f"""
    UTILIZZO AVANZATO: Pattern Matching

    ╔══════════════════════════╦══════════════════════════════════════╗
    ║       PATTERN GLOB       ║             DESCRIZIONE              ║
    ╠══════════════════════════╬══════════════════════════════════════╣
    ║ *                       ║ Match qualsiasi nome in un livello   ║
    ║ **                      ║ Match ricorsivo qualsiasi livello    ║
    ║ cartella                ║ Match esatto del nome                ║
    ║ **/cartella             ║ Match cartella in qualsiasi posizione║
    ║ *.ext                   ║ Match estensione specifica           ║
    ║ **/*.ext                ║ Match estensione in qualsiasi path   ║
    ╚══════════════════════════╩══════════════════════════════════════╝

    GERARCHIA DI APPLICAZIONE:
    1. Se la cartella NON è in include_folders → Salta tutto
    2. Se la cartella è in exclude_folders → Salta tutto
    3. Altrimenti controlla i file:
       - File NON in include_files → Salta
       - File in exclude_files → Salta
       - Altrimenti processa

    ESEMPI PRATICI:
    ► Escludere TUTTA una cartella:
      {{
        "exclude_folders": ["**/_artifacts"]
      }}

    ► Escludere solo i contenuti:
      {{
        "exclude_files": ["**/_artifacts/**"]
      }}

    ► Include/Exclude combinato:
      {{
        "include_folders": ["**/src/**"],
        "exclude_folders": ["**/temp"],
        "exclude_files": ["*.log"]
      }}

    UTILIZZO BASE:
    python {name_main} [OPZIONI]
    
    OPZIONI:
      --config <file>    File di configurazione JSON
      --target <dir>     Directory da analizzare
      --output <file>    File XML di output
      --help             Mostra questo messaggio
    """
    print(help_text)