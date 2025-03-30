class XMLNode:
    """Classe per rappresentare un nodo XML."""
    
    def __init__(self, tag, attributes=None):
        """
        Inizializza un nodo XML.
        :param tag: Nome del tag
        :param attributes: Dizionario degli attributi
        """
        self.tag = tag
        self.attributes = attributes if attributes else {}
        self.children = []
        self.text = ""

    def add_child(self, child):
        """Aggiunge un nodo figlio."""
        self.children.append(child)

    def set_text(self, text):
        """Imposta il testo del nodo."""
        self.text = text

    def to_xml(self, indent_level=0, indent=""):
        """Converte il nodo in stringa XML."""
        indent_str = indent * indent_level
        attrs = " ".join([f'{k}="{v}"' for k, v in self.attributes.items()])

        if not self.children and not self.text:
            return f"{indent_str}<{self.tag}{' ' + attrs if attrs else ''}/>"

        opening_tag = f"{indent_str}<{self.tag}{' ' + attrs if attrs else ''}>"
        closing_tag = f"{indent_str}</{self.tag}>"

        xml_content = [opening_tag]
        if self.text:
            xml_content.append(f"{indent * (indent_level + 1)}{self.text}")
        for child in self.children:
            xml_content.append(child.to_xml(indent_level + 1, indent))
        xml_content.append(closing_tag)

        # return ("" if indent == "" else "\n").join(xml_content)
        separator = "" if not indent else "\n"
        return separator.join(xml_content)

    def sanitize_cdata_content(content: str | bytes) -> str:
        """Pulisce il contenuto per renderlo sicuro in un blocco CDATA XML.
        
        Args:
            content: Contenuto originale (str o bytes)
            
        Returns:
            Stringa sanificata e pronta per CDATA
        """
        # Decodifica se è bytes (usa replace per caratteri non validi)
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                content = content.decode('latin-1', errors='replace')

        # Lista di sostituzioni per sequenze pericolose
        replacements = {
            ']]>': ']]]]><![CDATA[>',  # Previene chiusura prematura
            '--': '&#45;&#45;',         # Evita conflitti con commenti XML
            '\x00': '[NULL]',           # Carattere null (ASCII 0)
            '\x0B': '[VT]',             # Vertical Tab (ASCII 11)
            '\x0C': '[FF]'              # Form Feed (ASCII 12)
        }

        # Applica le sostituzioni
        for seq, replacement in replacements.items():
            content = content.replace(seq, replacement)

        # Filtra caratteri di controllo non validi (ASCII 0x00-0x1F)
        cleaned_chars = []
        for char in content:
            if 31 < ord(char) < 127:
                cleaned_chars.append(char)
            elif char in {'\t', '\n', '\r'}:
                cleaned_chars.append(char)
            else:
                cleaned_chars.append(f'[CTRL-{ord(char):02X}]')
        
        return ''.join(cleaned_chars)
