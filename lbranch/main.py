#!/usr/bin/env python3

# Last Branch (lbranch) - Git branch history utility

import argparse
import os
import platform
import re
import subprocess
import sys

# Exit codes - following sysexits.h conventions
EXIT_SUCCESS = 0  # successful execution
EXIT_USAGE = 64  # command line usage error
EXIT_DATAERR = 65  # data format error
EXIT_NOINPUT = 66  # cannot open input
EXIT_NOUSER = 67  # addressee unknown
EXIT_NOHOST = 68  # host name unknown
EXIT_UNAVAILABLE = 69  # service unavailable
EXIT_SOFTWARE = 70  # internal software error
EXIT_OSERR = 71  # system error (e.g., can't fork)
EXIT_OSFILE = 72  # critical OS file missing
EXIT_CANTCREAT = 73  # can't create (user) output file
EXIT_IOERR = 74  # input/output error
EXIT_TEMPFAIL = 75  # temp failure; user is invited to retry
EXIT_PROTOCOL = 76  # remote error in protocol
EXIT_NOPERM = 77  # permission denied
EXIT_CONFIG = 78  # configuration error

# Custom mapping of our error conditions to sysexits.h values
EXIT_GIT_NOT_FOUND = EXIT_UNAVAILABLE  # Git command not found (69)
EXIT_NOT_A_GIT_REPO = EXIT_USAGE  # Not in a git repository (64)
EXIT_NO_COMMITS = EXIT_NOINPUT  # No branch history/no commits (66)
EXIT_INVALID_SELECTION = EXIT_USAGE  # Invalid branch selection (64)
EXIT_CHECKOUT_FAILED = EXIT_TEMPFAIL  # Branch checkout failed, retry possible (75)
EXIT_INTERRUPTED = 130  # Operation interrupted (Ctrl+C) - shell standard


# Colors for output - with fallback detection
def supports_color():
    """
    Returns True if the terminal supports color, False otherwise.
    Falls back to no-color on non-TTY or Windows (unless FORCE_COLOR is set).
    """
    # Return True if the FORCE_COLOR environment variable is set
    if os.environ.get('FORCE_COLOR', '').lower() in ('1', 'true', 'yes', 'on'):
        return True

    # Return False if NO_COLOR environment variable is set (honor convention)
    if os.environ.get('NO_COLOR', ''):
        return False

    # Return False if not connected to a terminal
    if not sys.stdout.isatty():
        return False

    # On Windows, check if running in a terminal that supports ANSI
    if platform.system() == 'Windows':
        # Windows Terminal and modern PowerShell support colors
        # Older Windows consoles may not
        # Simple check for modern Windows terminals
        return (
            os.environ.get('WT_SESSION')
            or os.environ.get('TERM')
            or 'ANSICON' in os.environ
        )

    # Most Unix terminals support colors
    return True


# Set up colors based on environment
if supports_color():
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
else:
    # No colors if not supported
    RED = ''
    GREEN = ''
    BLUE = ''
    NC = ''

# Version - should match pyproject.toml
__version__ = '0.1.0'


def print_error(message, exit_code=EXIT_SOFTWARE):
    """Print error message and exit with specified code"""
    print(f'{RED}Error: {message}{NC}', file=sys.stderr)
    sys.exit(exit_code)


def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and handle errors"""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            text=True,
            shell=isinstance(cmd, str),
            capture_output=capture_output,
        )
        return result
    except subprocess.CalledProcessError as e:
        if not check:
            return e
        print_error(f'Command failed: {e}')
        sys.exit(EXIT_SOFTWARE)


def parse_arguments():
    """Parse command line arguments using argparse"""
    parser = argparse.ArgumentParser(
        description='Show recently checked out Git branches in chronological order',
        epilog='Example: lbranch -n 10 -s (shows the last 10 branches with option to '
        'select one)',
    )

    parser.add_argument(
        '-n',
        '--number',
        type=int,
        default=5,
        help='Number of branches to display (default: 5)',
    )
    parser.add_argument(
        '-s',
        '--select',
        action='store_true',
        help='Enter interactive mode to select a branch for checkout',
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
        help='Show version information and exit',
    )
    parser.add_argument(
        '-nc', '--no-color', action='store_true', help='Disable colored output'
    )
    parser.add_argument(
        '-fc',
        '--force-color',
        action='store_true',
        help='Force colored output even in non-TTY environments',
    )

    return parser.parse_args()


def main():
    """Main entry point for the lbranch command."""
    args = parse_arguments()

    # Handle manual color override options
    global RED, GREEN, BLUE, NC
    if args.no_color:
        RED = GREEN = BLUE = NC = ''
    elif args.force_color:
        RED = '\033[0;31m'
        GREEN = '\033[0;32m'
        BLUE = '\033[0;34m'
        NC = '\033[0m'

    # Check if git is installed
    try:
        run_command(['git', '--version'], capture_output=True)
    except FileNotFoundError:
        print_error(
            'git command not found. Please install git first.', EXIT_GIT_NOT_FOUND
        )

    # Check if we're in a git repository
    if (
        run_command(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            check=False,
            capture_output=True,
        ).returncode
        != 0
    ):
        print_error(
            'Not a git repository. Please run this command from within a git '
            'repository.',
            EXIT_NOT_A_GIT_REPO,
        )

    # Check if the repository has any commits
    if (
        run_command(
            ['git', 'rev-parse', '--verify', 'HEAD'], check=False, capture_output=True
        ).returncode
        != 0
    ):
        print(f'{BLUE}No branch history found - repository has no commits yet{NC}')
        sys.exit(EXIT_NO_COMMITS)

    # Get current branch name
    try:
        current_branch = run_command(
            ['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True
        ).stdout.strip()
    except subprocess.CalledProcessError:
        current_branch = run_command(
            ['git', 'rev-parse', '--short', 'HEAD'], capture_output=True
        ).stdout.strip()

    # Get unique branch history
    reflog_output = run_command(['git', 'reflog'], capture_output=True).stdout

    branches = []
    for line in reflog_output.splitlines():
        # Look for checkout lines without using grep
        if 'checkout: moving from' in line.lower():
            # Parse the branch name after "from"
            parts = line.split()
            try:
                from_index = parts.index('from')
                if from_index + 1 < len(parts):
                    branch = parts[from_index + 1]

                    # Skip empty, current branch, or branches starting with '{'
                    if not branch or branch == current_branch or branch.startswith('{'):
                        continue

                    # Only add branch if it's not already in the list
                    if branch not in branches:
                        branches.append(branch)
            except ValueError:
                continue  # "from" not found in this line

    # Limit to requested number of branches
    total_branches = len(branches)
    if total_branches == 0:
        print(f'{BLUE}Last {args.number} branches:{NC}')
        sys.exit(EXIT_SUCCESS)

    branch_limit = min(args.number, total_branches)
    branches = branches[:branch_limit]  # Limit to requested count

    # Display branches
    print(f'{BLUE}Last {args.number} branches:{NC}')
    for i, branch in enumerate(branches, 1):
        print(f'{i}) {branch}')

    # Handle select mode
    if args.select:
        try:
            print(f'\n{GREEN}Enter branch number to checkout (1-{branch_limit}):{NC}')
            branch_num = input()

            if (
                not re.match(r'^\d+$', branch_num)
                or int(branch_num) < 1
                or int(branch_num) > branch_limit
            ):
                print_error(f'Invalid selection: {branch_num}', EXIT_INVALID_SELECTION)

            selected_branch = branches[int(branch_num) - 1]
            print(f'\nChecking out: {selected_branch}')

            # Attempt to checkout the branch
            result = run_command(
                ['git', 'checkout', selected_branch], check=False, capture_output=True
            )
            if result.returncode != 0:
                print_error(
                    f'Failed to checkout branch:\n{result.stderr}', EXIT_CHECKOUT_FAILED
                )

            print(f'{GREEN}Successfully checked out {selected_branch}{NC}')
        except KeyboardInterrupt:
            print('\nOperation cancelled.')
            sys.exit(EXIT_INTERRUPTED)

    # Success
    return EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
