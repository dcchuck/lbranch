#!/usr/bin/env python3

# Last Branch (lbranch) - Git branch history utility

import subprocess
import sys
import re
import argparse

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# Version - should match pyproject.toml
__version__ = "0.1.0"

def print_error(message):
    """Print error message and exit"""
    print(f"{RED}Error: {message}{NC}", file=sys.stderr)
    sys.exit(1)

def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and handle errors"""
    try:
        result = subprocess.run(
            cmd, 
            check=check, 
            text=True, 
            shell=isinstance(cmd, str),
            capture_output=capture_output
        )
        return result
    except subprocess.CalledProcessError as e:
        if not check:
            return e
        print_error(f"Command failed: {e}")
        sys.exit(1)

def parse_arguments():
    """Parse command line arguments using argparse"""
    parser = argparse.ArgumentParser(
        description="Show recently checked out Git branches in chronological order",
        epilog="Example: lbranch -n 10 -c (shows the last 10 branches with option to choose one)"
    )
    
    parser.add_argument('-n', '--number', type=int, default=5,
                        help='Number of branches to display (default: 5)')
    parser.add_argument('-c', '--choose', action='store_true',
                        help='Enter interactive mode to checkout a listed branch')
    parser.add_argument('-v', '--version', action='version',
                        version=f'%(prog)s {__version__}',
                        help='Show version information and exit')
    
    return parser.parse_args()

def main():
    """Main entry point for the lbranch command."""
    args = parse_arguments()
    
    # Check if git is installed
    try:
        run_command(["git", "--version"], capture_output=True)
    except FileNotFoundError:
        print_error("git command not found. Please install git first.")

    # Check if we're in a git repository
    if run_command(["git", "rev-parse", "--is-inside-work-tree"], check=False, capture_output=True).returncode != 0:
        print_error("Not a git repository. Please run this command from within a git repository.")

    # Check if the repository has any commits
    if run_command(["git", "rev-parse", "--verify", "HEAD"], check=False, capture_output=True).returncode != 0:
        print(f"{BLUE}No branch history found - repository has no commits yet{NC}")
        sys.exit(0)

    # Get current branch name
    try:
        current_branch = run_command(["git", "symbolic-ref", "--short", "HEAD"], capture_output=True).stdout.strip()
    except subprocess.CalledProcessError:
        current_branch = run_command(["git", "rev-parse", "--short", "HEAD"], capture_output=True).stdout.strip()

    # Get unique branch history
    reflog_output = run_command(["git", "reflog"], capture_output=True).stdout

    branches = []
    for line in reflog_output.splitlines():
        # Look for checkout lines without using grep
        if 'checkout: moving from' in line.lower():
            # Parse the branch name after "from"
            parts = line.split()
            try:
                from_index = parts.index("from")
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
        print(f"{BLUE}Last {args.number} branches:{NC}")
        sys.exit(0)

    branch_limit = min(args.number, total_branches)
    branches = branches[:branch_limit]  # Limit to requested count

    # Display branches
    print(f"{BLUE}Last {args.number} branches:{NC}")
    for i, branch in enumerate(branches, 1):
        print(f"{i}) {branch}")

    # Handle choose mode
    if args.choose:
        try:
            print(f"\n{GREEN}Enter branch number to checkout (1-{branch_limit}):{NC}")
            branch_num = input()
            
            if not re.match(r'^\d+$', branch_num) or int(branch_num) < 1 or int(branch_num) > branch_limit:
                print_error(f"Invalid selection: {branch_num}")
                
            selected_branch = branches[int(branch_num) - 1]
            print(f"\nChecking out: {selected_branch}")
            
            # Attempt to checkout the branch
            result = run_command(["git", "checkout", selected_branch], check=False, capture_output=True)
            if result.returncode != 0:
                print_error(f"Failed to checkout branch:\n{result.stderr}")
                
            print(f"{GREEN}Successfully checked out {selected_branch}{NC}")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(1)

if __name__ == '__main__':
    main() 