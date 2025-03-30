# help.py
def show_full_help():
    """Mostra guida completa con esempi"""
    help_text = """
    🛠️  Utilizzo base:
    python fs2dad.py [--config FILE] [--target CARTELLA] [--output FILE]

    📌 Esempi:
    1. Genera con config predefinita:
       python fs2dad.py

    2. Specifica un target personalizzato:
       python fs2dad.py --target ./mio_progetto

    3. Genera con configurazione custom:
       python fs2dad.py --config mio_config.json

    🔧 Parametri avanzati:
    --indent-content       Indenta il contenuto dei file testuali
    --include-files        Filtra file specifici (es: *.py,*.txt)
    """
    print(help_text)