# lbranch
lbranch ("last branch") is a git utility that shows your recently checked out branches in chronological order, with an optional interactive checkout.

## Usage
```bash
# Show last 5 branches (default)
lbranch
# Show last N branches
lbranch -n 3
lbranch --number 3
# Show branches and select one to checkout
lbranch -s
lbranch --select
# Show last N branches and select one
lbranch -n 3 -s
# Color control
lbranch --no-color     # Disable colored output
lbranch --force-color  # Force colored output even in non-TTY environments
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

## Color Support
lbranch automatically detects if your terminal supports colors:
- Colors are disabled when output is not to a terminal (when piped to a file or another command)
- Colors are disabled on Windows unless running in a modern terminal (Windows Terminal, VS Code, etc.)
- You can force colors on with `--force-color` or off with `--no-color`
- lbranch respects the `NO_COLOR` and `FORCE_COLOR` environment variables

## Requirements
- Python 3.6+
- Git

## License
Distributed under the MIT License. See `LICENSE`