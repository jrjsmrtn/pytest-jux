# fish completion for pytest-jux commands
#
# Installation:
#   Copy this file to ~/.config/fish/completions/
#   Or to /usr/share/fish/vendor_completions.d/ for system-wide installation

# jux-keygen completions
complete -c jux-keygen -l type -d "Key algorithm" -xa "rsa ecdsa"
complete -c jux-keygen -l bits -d "RSA key size in bits" -xa "2048 3072 4096"
complete -c jux-keygen -l curve -d "ECDSA curve name" -xa "P-256 P-384 P-521"
complete -c jux-keygen -l output -d "Output file path for private key" -r -F
complete -c jux-keygen -l cert -d "Generate self-signed certificate"
complete -c jux-keygen -l subject -d "X.509 certificate subject" -x
complete -c jux-keygen -l days-valid -d "Certificate validity period in days" -xa "90 180 365"
complete -c jux-keygen -s c -l config -d "Configuration file path" -r -F
complete -c jux-keygen -l help -d "Show help message"

# jux-sign completions
complete -c jux-sign -s i -l input -d "Input JUnit XML report file" -r -F
complete -c jux-sign -s o -l output -d "Output path for signed XML" -r -F
complete -c jux-sign -l key -d "Path to private key file (PEM format)" -r -F
complete -c jux-sign -l cert -d "Path to X.509 certificate" -r -F
complete -c jux-sign -s c -l config -d "Configuration file path" -r -F
complete -c jux-sign -l help -d "Show help message"

# jux-verify completions
complete -c jux-verify -s i -l input -d "Input signed XML report file" -r -F
complete -c jux-verify -l cert -d "Path to X.509 certificate file" -r -F
complete -c jux-verify -s q -l quiet -d "Quiet mode - suppress all output"
complete -c jux-verify -l json -d "Output verification result in JSON format"
complete -c jux-verify -l help -d "Show help message"

# jux-inspect completions
complete -c jux-inspect -s i -l input -d "Input XML report file to inspect" -r -F
complete -c jux-inspect -l format -d "Output format" -xa "text json"
complete -c jux-inspect -l show-signature -d "Show signature details if present"
complete -c jux-inspect -l show-metadata -d "Show metadata if present"
complete -c jux-inspect -l help -d "Show help message"

# jux-cache completions
complete -c jux-cache -f -n "__fish_use_subcommand" -a "list" -d "List all cached reports"
complete -c jux-cache -f -n "__fish_use_subcommand" -a "show" -d "Show details of a specific cached report"
complete -c jux-cache -f -n "__fish_use_subcommand" -a "stats" -d "Show cache statistics"
complete -c jux-cache -f -n "__fish_use_subcommand" -a "clean" -d "Clean old reports from cache"
complete -c jux-cache -f -n "__fish_use_subcommand" -l help -d "Show help message"

# jux-cache list
complete -c jux-cache -n "__fish_seen_subcommand_from list" -l json -d "Output in JSON format"
complete -c jux-cache -n "__fish_seen_subcommand_from list" -l storage-path -d "Storage directory path" -r -a "(__fish_complete_directories)"
complete -c jux-cache -n "__fish_seen_subcommand_from list" -l help -d "Show help message"

# jux-cache show
complete -c jux-cache -n "__fish_seen_subcommand_from show" -l json -d "Output in JSON format"
complete -c jux-cache -n "__fish_seen_subcommand_from show" -l storage-path -d "Storage directory path" -r -a "(__fish_complete_directories)"
complete -c jux-cache -n "__fish_seen_subcommand_from show" -l help -d "Show help message"

# jux-cache stats
complete -c jux-cache -n "__fish_seen_subcommand_from stats" -l json -d "Output in JSON format"
complete -c jux-cache -n "__fish_seen_subcommand_from stats" -l storage-path -d "Storage directory path" -r -a "(__fish_complete_directories)"
complete -c jux-cache -n "__fish_seen_subcommand_from stats" -l help -d "Show help message"

# jux-cache clean
complete -c jux-cache -n "__fish_seen_subcommand_from clean" -l days -d "Delete reports older than N days" -xa "7 14 30 60 90"
complete -c jux-cache -n "__fish_seen_subcommand_from clean" -l dry-run -d "Show what would be deleted without deleting"
complete -c jux-cache -n "__fish_seen_subcommand_from clean" -l storage-path -d "Storage directory path" -r -a "(__fish_complete_directories)"
complete -c jux-cache -n "__fish_seen_subcommand_from clean" -l help -d "Show help message"

# jux-config completions
complete -c jux-config -f -n "__fish_use_subcommand" -a "list" -d "List all available configuration options"
complete -c jux-config -f -n "__fish_use_subcommand" -a "dump" -d "Show current effective configuration"
complete -c jux-config -f -n "__fish_use_subcommand" -a "view" -d "View contents of configuration file(s)"
complete -c jux-config -f -n "__fish_use_subcommand" -a "init" -d "Create new configuration file from template"
complete -c jux-config -f -n "__fish_use_subcommand" -a "validate" -d "Validate configuration file syntax and values"
complete -c jux-config -f -n "__fish_use_subcommand" -l help -d "Show help message"

# jux-config list
complete -c jux-config -n "__fish_seen_subcommand_from list" -l json -d "Output in JSON format"
complete -c jux-config -n "__fish_seen_subcommand_from list" -l help -d "Show help message"

# jux-config dump
complete -c jux-config -n "__fish_seen_subcommand_from dump" -l json -d "Output in JSON format"
complete -c jux-config -n "__fish_seen_subcommand_from dump" -l help -d "Show help message"

# jux-config view
complete -c jux-config -n "__fish_seen_subcommand_from view" -l all -d "View all configuration files"
complete -c jux-config -n "__fish_seen_subcommand_from view" -l help -d "Show help message"

# jux-config init
complete -c jux-config -n "__fish_seen_subcommand_from init" -l path -d "Configuration file path" -r -F
complete -c jux-config -n "__fish_seen_subcommand_from init" -l force -d "Overwrite existing configuration file"
complete -c jux-config -n "__fish_seen_subcommand_from init" -l template -d "Configuration template" -xa "minimal full development ci production"
complete -c jux-config -n "__fish_seen_subcommand_from init" -l help -d "Show help message"

# jux-config validate
complete -c jux-config -n "__fish_seen_subcommand_from validate" -l strict -d "Enable strict validation"
complete -c jux-config -n "__fish_seen_subcommand_from validate" -l json -d "Output in JSON format"
complete -c jux-config -n "__fish_seen_subcommand_from validate" -l help -d "Show help message"
