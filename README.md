# lbranch
lbranch ("last branch") is a git utility that shows your recently checked out branches in chronological order, with an optional interactive checkout.

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

## License
Distributed under the MIT License. See `LICENSE`