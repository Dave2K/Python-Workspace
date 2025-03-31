# PATTERN GUIDE (glob -> regex):
# =====================================================================
# 1. INCLUSIONE CARTELLE (include_folders):
# ---------------------------------------------------------------------
# - "docs"                -> Solo cartella /docs a root
# - "src/*"               -> Sottocartelle dirette di src (1 livello)
# - "src/**"              -> Tutta la gerarchia sotto src
# - "**/*.core.*"         -> Cartelle con ".core." in qualsiasi posizione
# - "project/*/modules"   -> Cartelle modules in sottodir di primo livello
# - "!temp/**"            -> Escludi cartella temp e sottocartelle
# - "**/test*/**"         -> Cartelle che iniziano con "test" in qualsiasi posizione

# 2. INCLUSIONE FILE (include_files):
# ---------------------------------------------------------------------
# - "*.core.*"            -> File con ".core." nel nome (es: app.core.py)
# - "*.config.ini"        -> File ini con "config" nel nome
# - "data/*.json"         -> JSON in cartella data (1 livello)
# - "**/settings/*.py"    -> Python in cartelle settings (qualsiasi livello)
# - "module-?.txt"        -> File come module-1.txt, module-A.txt
# - "[0-9]_report.*"      -> File con numero iniziale (es: 1_report.csv)

# 3. COMBINAZIONI TIPICHE:
# ---------------------------------------------------------------------
# A. Solo cartelle core e relativi file python:
#    include_folders = ["**/*.core.*/**"]
#    include_files = ["*.py"]

# B. Struttura a livelli con esclusioni:
#    include_folders = ["src/*/*", "!src/legacy/**"]
#    include_files = ["*.component.*", "*.service.*"]

# C. Raccolta da posizioni specifiche:
#    include_folders = ["docs/chapters/**", "assets/**"]
#    include_files = ["*.md", "*.png"]

# 4. SPECIAL CHARACTERS:
# ---------------------------------------------------------------------
# - *       -> Qualsiasi sequenza di caratteri (no /)
# - **      -> Qualsiasi sequenza incluso /
# - ?       -> Singolo carattere
# - [abc]   -> Match a, b o c
# - [!abc]  -> Escludi a, b o c
# - {a,b}   -> Match a o b

# 5. BEST PRACTICES:
# ---------------------------------------------------------------------
# - Testare i pattern con glob_to_regex()
# - Usare path Unix-style (/) anche su Windows
# - Ordinare i pattern dal più specifico al più generico
# - Verificare le esclusioni dopo le inclusioni
# =====================================================================

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
