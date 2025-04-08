#!/usr/bin/env python3

# Last Branch (lbranch) - Git branch history utility
# Usage: lbranch [count] [-c|--choose]

import subprocess
import sys
import re

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

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

def main():
    """Main entry point for the lbranch command."""
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

    # Parse arguments
    branch_count = 5
    choose_mode = False

    for arg in sys.argv[1:]:
        if arg in ['-c', '--choose']:
            choose_mode = True
        elif re.match(r'^\d+$', arg):
            branch_count = int(arg)
        else:
            print_error(f"Invalid argument: {arg}")

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
        print(f"{BLUE}Last {branch_count} branches:{NC}")
        sys.exit(0)

    branch_limit = min(branch_count, total_branches)
    branches = branches[:branch_limit]  # Limit to requested count

    # Display branches
    print(f"{BLUE}Last {branch_count} branches:{NC}")
    for i, branch in enumerate(branches, 1):
        print(f"{i}) {branch}")

    # Handle choose mode
    if choose_mode:
        try:
            print(f"\n{GREEN}Enter branch number to checkout (1-{branch_count}):{NC}")
            branch_num = input()
            
            if not re.match(r'^\d+$', branch_num) or int(branch_num) < 1 or int(branch_num) > branch_count:
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