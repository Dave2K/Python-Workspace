# PATTERN GUIDE (glob -> regex):

{
  "target_path_folder": "C:\\Users\\david\\WorkSpace\\Sources\\FlexCore-Workspace",
  "output_path_file": ".\\_artifacts\\{target}.xml",
  "indent_content": true,
  "sanitize": false,

  "include_folders": [
    "FlexCore.*",        // Include tutte le cartelle che iniziano con "FlexCore"
    "**/FlexCore.*"      // Include tutte le cartelle "FlexCore" in qualsiasi sottocartella
  ],
  "include_files": [
    "Directory.Build.props",      // Include esattamente questo file
    "Directory.Build.targets",    // Include esattamente questo file
    "*appsettings.json"           // Include tutti i file che terminano con "appsettings.json"
  ],
  "exclude_folders": [
    "**/bin",    // Escludi tutte le cartelle "bin" in qualsiasi sottocartella
    "**/obj",    // Escludi tutte le cartelle "obj" in qualsiasi sottocartella
    "**/.git"    // Escludi tutte le cartelle ".git" in qualsiasi sottocartella
  ],
  "exclude_files": [
    ".gitignore",       // Escludi esattamente il file ".gitignore"
    "*.md"              // Escludi tutti i file che terminano con ".md"
  ]
}
