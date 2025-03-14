# lbranch
lbranch ("last branch") is a git utility that shows your recently checked out branches in chronological order, with an optional interactive checkout.

## Installation
1. Ensure you have Python 3.6+ installed
2. Clone this repository:
```bash
git clone https://github.com/yourusername/lbranch.git ~/.lbranch
```
3. Create a symlink or add to your PATH:
```bash
# Option 1: Symlink to /usr/local/bin
ln -s ~/.lbranch/bin/lbranch /usr/local/bin/lbranch
# Option 2: Add to your PATH in ~/.zshrc or ~/.bashrc
export PATH="$PATH:~/.lbranch/bin"
```
4. (Optional) Add an alias in your shell config:
```bash
alias lb=lbranch
```

## Usage
```bash
# Show last 5 branches
lbranch
# Show last N branches
lbranch 3
# Show branches and choose one to checkout
lbranch -c
lbranch --choose
# Show last N branches and choose one
lbranch 3 -c
```

## Example Output
```bash
Last 5 branches:
1) feature/new-ui
2) main
3) bugfix/login
4) feature/api
5) develop
```

## Requirements
- Python 3.6+
- Git
- Unix-like environment (Linux, macOS, WSL)

## Development
To run tests:
```bash
python test.py
```

## Uninstall
```bash
# Remove symlink (if you used Option 1)
rm /usr/local/bin/lbranch

# Remove the repository
rm -rf ~/.lbranch

# Remove PATH addition (if you used Option 2)
# Edit ~/.zshrc or ~/.bashrc and remove the line:
# export PATH="$PATH:~/.lbranch/bin"

# Remove alias (if you added it)
# Edit ~/.zshrc or ~/.bashrc and remove the line:
# alias lb=lbranch
```

## License
Distributed under the MIT License. See `LICENSE` file for more information.
