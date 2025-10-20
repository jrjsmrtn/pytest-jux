# bash completion for pytest-jux commands
#
# Installation:
#   Copy this file to /etc/bash_completion.d/ or /usr/local/etc/bash_completion.d/
#   Or source it in your ~/.bashrc:
#     source /path/to/jux.bash

_jux_keygen_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Options
    opts="--type --bits --curve --output --cert --subject --days-valid --config --help"

    # Handle option arguments
    case "${prev}" in
        --type)
            COMPREPLY=( $(compgen -W "rsa ecdsa" -- ${cur}) )
            return 0
            ;;
        --bits)
            COMPREPLY=( $(compgen -W "2048 3072 4096" -- ${cur}) )
            return 0
            ;;
        --curve)
            COMPREPLY=( $(compgen -W "P-256 P-384 P-521" -- ${cur}) )
            return 0
            ;;
        --output|--config)
            # File completion
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --subject)
            # Suggest DN format
            COMPREPLY=( $(compgen -W "CN=pytest-jux" -- ${cur}) )
            return 0
            ;;
        --days-valid)
            COMPREPLY=( $(compgen -W "90 180 365" -- ${cur}) )
            return 0
            ;;
    esac

    # Complete options
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

_jux_sign_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Options
    opts="-i --input -o --output --key --cert -c --config --help"

    # Handle option arguments
    case "${prev}" in
        -i|--input|-o|--output|--key|--cert|-c|--config)
            # File completion
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
    esac

    # Complete options
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

_jux_verify_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Options
    opts="-i --input --cert -q --quiet --json --help"

    # Handle option arguments
    case "${prev}" in
        -i|--input|--cert)
            # File completion
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
    esac

    # Complete options
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

_jux_inspect_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Options
    opts="-i --input --format --show-signature --show-metadata --help"

    # Handle option arguments
    case "${prev}" in
        -i|--input)
            # File completion
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "text json" -- ${cur}) )
            return 0
            ;;
    esac

    # Complete options
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

_jux_cache_completions() {
    local cur prev opts subcommand
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Find subcommand
    subcommand=""
    for ((i=1; i<COMP_CWORD; i++)); do
        case "${COMP_WORDS[i]}" in
            list|show|stats|clean)
                subcommand="${COMP_WORDS[i]}"
                break
                ;;
        esac
    done

    # If no subcommand yet, complete subcommands
    if [ -z "$subcommand" ]; then
        opts="list show stats clean --help"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    # Complete options for each subcommand
    case "${subcommand}" in
        list)
            opts="--json --storage-path --help"
            ;;
        show)
            opts="--json --storage-path --help"
            # First positional argument is hash (no completion)
            ;;
        stats)
            opts="--json --storage-path --help"
            ;;
        clean)
            opts="--days --dry-run --storage-path --help"
            case "${prev}" in
                --days)
                    COMPREPLY=( $(compgen -W "7 14 30 60 90" -- ${cur}) )
                    return 0
                    ;;
                --storage-path)
                    COMPREPLY=( $(compgen -d -- ${cur}) )
                    return 0
                    ;;
            esac
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

_jux_config_completions() {
    local cur prev opts subcommand
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Find subcommand
    subcommand=""
    for ((i=1; i<COMP_CWORD; i++)); do
        case "${COMP_WORDS[i]}" in
            list|dump|view|init|validate)
                subcommand="${COMP_WORDS[i]}"
                break
                ;;
        esac
    done

    # If no subcommand yet, complete subcommands
    if [ -z "$subcommand" ]; then
        opts="list dump view init validate --help"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    # Complete options for each subcommand
    case "${subcommand}" in
        list)
            opts="--json --help"
            ;;
        dump)
            opts="--json --help"
            ;;
        view)
            opts="--all --help"
            # First positional argument is path (file completion)
            if [ "${prev}" == "view" ] || [ "${prev}" == "--help" ]; then
                COMPREPLY=( $(compgen -f -- ${cur}) )
                return 0
            fi
            ;;
        init)
            opts="--path --force --template --help"
            case "${prev}" in
                --path)
                    COMPREPLY=( $(compgen -f -- ${cur}) )
                    return 0
                    ;;
                --template)
                    COMPREPLY=( $(compgen -W "minimal full development ci production" -- ${cur}) )
                    return 0
                    ;;
            esac
            ;;
        validate)
            opts="--strict --json --help"
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

# Register completions for each command
complete -F _jux_keygen_completions jux-keygen
complete -F _jux_sign_completions jux-sign
complete -F _jux_verify_completions jux-verify
complete -F _jux_inspect_completions jux-inspect
complete -F _jux_cache_completions jux-cache
complete -F _jux_config_completions jux-config
