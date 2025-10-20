# Shell Completion Scripts for pytest-jux

This directory contains shell completion scripts for pytest-jux CLI commands.

## Supported Shells

- **Bash** (`jux.bash`)
- **Zsh** (`jux.zsh`)
- **Fish** (`jux.fish`)

## Features

All completion scripts provide:

- Command name completion (jux-keygen, jux-sign, jux-verify, jux-inspect, jux-cache, jux-config)
- Subcommand completion (for jux-cache and jux-config)
- Option name completion (--key, --cert, --input, etc.)
- Option value completion where applicable:
  - File paths for file-based options
  - Predefined values (e.g., key types, templates, formats)
- Help text descriptions for all options

## Installation

### Bash

**Option 1: System-wide installation (requires root)**
```bash
sudo cp jux.bash /etc/bash_completion.d/jux
# OR on macOS with Homebrew bash-completion:
sudo cp jux.bash /usr/local/etc/bash_completion.d/jux
```

**Option 2: User installation**
```bash
# Create directory if it doesn't exist
mkdir -p ~/.bash_completion.d

# Copy the completion script
cp jux.bash ~/.bash_completion.d/jux

# Add to ~/.bashrc or ~/.bash_profile:
echo 'source ~/.bash_completion.d/jux' >> ~/.bashrc

# Reload your shell or source the file
source ~/.bashrc
```

### Zsh

**Option 1: Using oh-my-zsh**
```bash
# Copy to oh-my-zsh custom completions
mkdir -p ~/.oh-my-zsh/custom/completions
cp jux.zsh ~/.oh-my-zsh/custom/completions/_jux

# Reload completions
rm -f ~/.zcompdump
autoload -U compinit && compinit
```

**Option 2: Manual installation**
```bash
# Find a directory in your fpath (run: echo $fpath)
# Typically ~/.zsh/completions or /usr/local/share/zsh/site-functions

# Create directory if needed
mkdir -p ~/.zsh/completions

# Copy completion file with underscore prefix
cp jux.zsh ~/.zsh/completions/_jux

# Add to ~/.zshrc if not already present:
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
echo 'autoload -U compinit && compinit' >> ~/.zshrc

# Reload your shell
exec zsh
```

### Fish

**Option 1: User installation (recommended)**
```bash
# Create directory if it doesn't exist
mkdir -p ~/.config/fish/completions

# Copy the completion script
cp jux.fish ~/.config/fish/completions/

# Completions are loaded automatically
# Restart fish or run: source ~/.config/fish/config.fish
```

**Option 2: System-wide installation (requires root)**
```bash
sudo cp jux.fish /usr/share/fish/vendor_completions.d/jux.fish
```

## Usage

After installation, you can use tab completion with all pytest-jux commands:

### Examples

```bash
# Complete command names
jux-<TAB>
# Shows: jux-cache  jux-config  jux-inspect  jux-keygen  jux-sign  jux-verify

# Complete options
jux-sign --<TAB>
# Shows: --cert  --config  --help  --input  --key  --output

# Complete option values
jux-keygen --type <TAB>
# Shows: rsa  ecdsa

jux-keygen --bits <TAB>
# Shows: 2048  3072  4096

jux-config init --template <TAB>
# Shows: ci  development  full  minimal  production

# Complete subcommands
jux-cache <TAB>
# Shows: clean  list  show  stats

jux-config <TAB>
# Shows: dump  init  list  validate  view

# File path completion
jux-sign --key ~/.jux/<TAB>
# Shows available files in ~/.jux/
```

## Troubleshooting

### Bash

**Completions not working:**
1. Check if bash-completion is installed:
   ```bash
   # On Debian/Ubuntu:
   sudo apt-get install bash-completion

   # On macOS with Homebrew:
   brew install bash-completion@2
   ```

2. Verify the script is sourced:
   ```bash
   # Check if jux completions are loaded
   complete -p jux-keygen
   ```

3. Reload bash:
   ```bash
   source ~/.bashrc
   # OR
   exec bash
   ```

### Zsh

**Completions not working:**
1. Clear completion cache:
   ```zsh
   rm -f ~/.zcompdump*
   autoload -U compinit && compinit
   ```

2. Verify fpath includes completion directory:
   ```zsh
   echo $fpath | grep -o '[^ ]*completions[^ ]*'
   ```

3. Check if the file has the correct name (must start with underscore):
   ```zsh
   ls -la ~/.zsh/completions/_jux
   ```

4. Reload zsh:
   ```zsh
   exec zsh
   ```

### Fish

**Completions not working:**
1. Check if the file exists in the correct location:
   ```fish
   ls -la ~/.config/fish/completions/jux.fish
   ```

2. Reload fish completions:
   ```fish
   fish_update_completions
   ```

3. Restart fish:
   ```fish
   exec fish
   ```

## Testing

To test if completions are working correctly:

1. **Type a partial command and press TAB:**
   ```bash
   jux-ke<TAB>
   # Should complete to: jux-keygen
   ```

2. **Test option completion:**
   ```bash
   jux-keygen --ty<TAB>
   # Should complete to: jux-keygen --type
   ```

3. **Test option value completion:**
   ```bash
   jux-keygen --type <TAB>
   # Should show: rsa  ecdsa
   ```

4. **Test subcommand completion:**
   ```bash
   jux-config <TAB>
   # Should show: dump  init  list  validate  view
   ```

## Supported Commands

### jux-keygen
- Options: --type, --bits, --curve, --output, --cert, --subject, --days-valid, --config
- Value completion for: type (rsa/ecdsa), bits (2048/3072/4096), curve (P-256/P-384/P-521)

### jux-sign
- Options: -i/--input, -o/--output, --key, --cert, -c/--config
- File completion for all path options

### jux-verify
- Options: -i/--input, --cert, -q/--quiet, --json
- File completion for path options

### jux-inspect
- Options: -i/--input, --format, --show-signature, --show-metadata
- Value completion for format (text/json)

### jux-cache
- Subcommands: list, show, stats, clean
- Options vary by subcommand
- Value completion for --days (7/14/30/60/90)

### jux-config
- Subcommands: list, dump, view, init, validate
- Options vary by subcommand
- Value completion for --template (minimal/full/development/ci/production)

## Contributing

If you find issues with the completion scripts or want to add improvements:

1. Test your changes in a clean shell environment
2. Verify completions work for all commands and options
3. Check that file path completion works correctly
4. Ensure subcommand completion works for jux-cache and jux-config

## License

These completion scripts are part of pytest-jux and are licensed under the Apache License 2.0.
