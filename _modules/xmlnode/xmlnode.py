from _modules.logging.logging import create_logger
logger = create_logger(__name__)

import xml.sax.saxutils as saxutils

class XMLNode:
    """Classe per rappresentare un nodo XML."""

    class NodeContent:
        """Classe per gestire il contenuto di un nodo XML."""
        
        def __init__(self, text="", is_cdata=False, is_text=False):
            self.text = text
            self.is_cdata = is_cdata
            self.is_text = is_text        
        def __str__(self):
            return self.text
    
    def __init__(self, tag, attributes=None):
        """
        Inizializza un nodo XML.
        :param tag: Nome del tag
        :param attributes: Dizionario degli attributi
        """
        self.tag = tag
        self.attributes = attributes if attributes else {}
        self.children = []
        self.content = self.NodeContent()

    def add_child(self, child):
        """Aggiunge un nodo figlio."""
        self.children.append(child)

    def set_cdata(self, content, is_text=True, indent_content=False):
        self.content.text = content
        self.content.is_cdata = True
        self.content.is_text = is_text
        self.content.indent_content = indent_content

    def set_text(self, text):
        self.content.text = text
        self.content.is_text = True
        self.content.is_cdata = False

    def to_xml(self, indent_chars="", indent_level=0, sanitize=False):
        """Converte il nodo in stringa XML."""
        indent_str = indent_chars * indent_level
        attrs = " ".join([f'{k}="{v}"' for k, v in self.attributes.items()])

        if not self.children and not self.content.text:
            return f"{indent_str}<{self.tag}{' ' + attrs if attrs else ''}/>"

        opening_tag = f"{indent_str}<{self.tag}{' ' + attrs if attrs else ''}>"
        closing_tag = f"{indent_str}</{self.tag}>"

        xml_content = [opening_tag]
        if self.content.text:
            content = self.content.text if not sanitize else self.sanitize_xml(self.content.text)
            indent_str_content = indent_chars * (indent_level + 1)
            if indent_chars:
                lines = content.splitlines()
                _text = "\n".join(f"{indent_str_content}{line}" for line in lines)
                xml_content.append(f"{_text}")
            else:
                _text = content
                xml_content.append(f"{indent_str_content}{_text}")

        for child in self.children:
            xml_content.append(child.to_xml(indent_chars=indent_chars, indent_level=indent_level + 1, sanitize=sanitize))
        xml_content.append(closing_tag)

        separator = "" if not indent_chars else "\n"
        return separator.join(xml_content)
    
    def write_file(self, file_name, indent_chars="", indent_level=0, encoding="utf-8", sanitize=False):
        separator = "" if not indent_chars else "\n"
        header = '<?xml version="1.0" encoding="utf-8"?>'
        content_xml = f'{header}{separator}{self.to_xml(indent_chars=indent_chars, indent_level=indent_level, sanitize=sanitize)}'
        with open(file_name, "w", encoding=encoding) as f:
            f.write(content_xml)
 

    def sanitize_xml(self, text: str) -> str:
        """
        Sanifica il testo per evitare caratteri speciali in un tag XML.
        Escapa i caratteri speciali come <, >, &, ", '.
        
        Args:
            text (str): Il testo da sanificare.
        
        Returns:
            str: Il testo sanificato, pronto per l'uso in un tag XML.
        """
        return saxutils.escape(text)

    def sanitize_cdata(self, text: str) -> str:
        """
        Sanifica il testo per essere sicuro in un blocco CDATA XML.
        Sostituisce ']]>' con ']]]]><![CDATA[' per evitare la chiusura prematura del CDATA
        e scappa i caratteri speciali.
        
        Args:
            text (str): Il testo da sanificare.
        
        Returns:
            str: Il testo sanificato, pronto per l'uso in un blocco CDATA.
        """
        # Sostituisce la sequenza "]]>" con "]]]]><![CDATA["
        sanitized_text = text.replace("]]>", "]]]]><![CDATA[")
        # Escapa i caratteri speciali per evitare conflitti con la sintassi XML
        return saxutils.escape(sanitized_text)