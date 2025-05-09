from _modules.logging.logging import create_logger
logger = create_logger(__name__)

import xml.sax.saxutils as saxutils
import re

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

    def to_xml(self, indent_chars="", indent_level=0, sanitize=False, remove_xml_comments=False):
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
            """Rimuove i commenti XML ///"""
            if remove_xml_comments:
                content = self.remove_xml_doc_comments(content)
            indent_str_content = indent_chars * (indent_level + 1)
            if indent_chars:
                lines = content.splitlines()
                _text = "\n".join(f"{indent_str_content}{line}" for line in lines)
                xml_content.append(f"{_text}")
            else:
                _text = content
                xml_content.append(f"{indent_str_content}{_text}")

        for child in self.children:
            if child:
                xml_content.append(child.to_xml(indent_chars=indent_chars, indent_level=indent_level + 1, sanitize=sanitize, remove_xml_comments=remove_xml_comments))
        xml_content.append(closing_tag)

        separator = "" if not indent_chars else "\n"
        return separator.join(xml_content)
    
    def write_file(self, file_name, 
                   indent_chars="", 
                   indent_level=0, 
                   encoding="utf-8", 
                   sanitize=False, 
                   split_size=0,
                   remove_xml_comments=False
        ):
        separator = "" if not indent_chars else "\n"
        header = '<?xml version="1.0" encoding="utf-8"?>'
        to_xml_content = self.to_xml(indent_chars=indent_chars, indent_level=indent_level, sanitize=sanitize, remove_xml_comments=remove_xml_comments)
        content_xml = f'{header}{separator}{to_xml_content}'
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
        return self.sanitize_xml(sanitized_text)
    
    def remove_xml_doc_comments(self, code: str) -> str:
        """
        Rimuove le righe di commento C# che iniziano con '///', inclusi i newline di apertura e chiusura.

        Parametri:
            code (str): Codice C# come stringa.

        Ritorna:
            str: Codice senza righe di commento ///.
        """
        # Rimuove tutte le righe che iniziano con '///' (incluso il \n)
        return re.sub(r'\n[ \t]*///.*', '', code)
