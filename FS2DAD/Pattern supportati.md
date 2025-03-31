Pattern supportati (per cartelle/file):

1. Cartelle
*: Matcha qualsiasi nome (es: temp* → temp1, temporary)

**: Match ricorsivo (es: **/docs → ./docs, sub/folder/docs)

cartella/*: Tutto dentro cartella (non ricorsivo)

cartella/**/*.tmp: File .tmp in qualsiasi sottocartella di cartella

[abc]: Matcha a, b o c (es: project[123] → project1, project2)

2. File
*.py: Tutti i file Python

report_202?.docx: report_2021.docx, report_202A.docx

data_**.csv: data_01.csv, data_FINAL.csv

!secret*: Esclude file che iniziano con secret

3. Caratteri speciali
?: Matcha un singolo carattere (es: file?.txt → file1.txt, fileA.txt)

[!abc]: Esclusione caratteri (es: file[!x].log → fileA.log ma non filex.log)

{pattern1,pattern2}: Match multipli (es: *.{txt,md} → note.txt, README.md)

4. Case-insensitive
Tutti i pattern sono case-insensitive (es: *.TXT matcha file.txt, FILE.TXT).

Esempio completo:
include_folders = ["**/src", "lib/*"]  
ignore_folders = ["**/temp", "**/bin"]  
include_files = ["*.py", "README.*"]  
ignore_files = ["*.tmp", "!backup*"]  
