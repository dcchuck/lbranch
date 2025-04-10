#!/usr/bin/env python3
import os
import subprocess
import tempfile
import unittest
from textwrap import dedent
import sys
from io import StringIO
from lbranch.main import main

class TestLBranch(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()

        # Setup test repository
        os.chdir(self.test_dir)
        subprocess.run(['git', 'init'], capture_output=True, check=True)
        subprocess.run(['git', 'config', '--local', 'user.email', 'test@example.com'],
                      capture_output=True, check=True)
        subprocess.run(['git', 'config', '--local', 'user.name', 'Test User'],
                      capture_output=True, check=True)

    def tearDown(self):
        os.chdir(self.original_dir)
        subprocess.run(['rm', '-rf', self.test_dir], capture_output=True, check=True)

    def create_branch_with_commit(self, branch_name, file_content):
        """Create a branch and add a commit to it"""
        subprocess.run(['git', 'checkout', '-b', branch_name],
                      capture_output=True, check=True)
        with open(f'{branch_name}.txt', 'w') as f:
            f.write(file_content)
        subprocess.run(['git', 'add', f'{branch_name}.txt'],
                      capture_output=True, check=True)
        subprocess.run(['git', 'commit', '-m', f'commit on {branch_name}'],
                      capture_output=True, check=True)

    def run_lbranch(self, args=None):
        """Run lbranch and capture its output"""
        if args is None:
            args = []
        # Save original stdout
        original_stdout = sys.stdout
        # Create a string buffer to capture output
        output = StringIO()
        sys.stdout = output
        try:
            # Save original argv
            original_argv = sys.argv
            sys.argv = ['lbranch'] + args
            try:
                main()
            except SystemExit as e:
                # Only handle exit code 0 (success)
                if e.code != 0:
                    raise
        finally:
            # Restore stdout and argv
            sys.stdout = original_stdout
            sys.argv = original_argv
        return output.getvalue()

    def test_no_commits(self):
        """Test behavior when repository has no commits"""
        # Create new branch without any commits
        subprocess.run(['git', 'checkout', '-b', 'empty-branch'],
                      capture_output=True, check=True)

        output = self.run_lbranch()
        self.assertIn("No branch history found - repository has no commits yet", output)

    def test_first_branch_scenario(self):
        """Test behavior with main branch and new branch"""
        # Create initial commit on main
        with open('README.md', 'w') as f:
            f.write('initial')
        subprocess.run(['git', 'add', 'README.md'],
                      capture_output=True, check=True)
        subprocess.run(['git', 'commit', '-m', 'initial'],
                      capture_output=True, check=True)

        # Create and checkout new branch
        subprocess.run(['git', 'checkout', '-b', 'feature'],
                      capture_output=True, check=True)

        output = self.run_lbranch()
        self.assertIn("Last 5 branches:", output)
        self.assertIn("1) main", output)

    def test_exclude_current_branch(self):
        """Test that current branch is excluded from results"""
        # Create initial commit on main
        with open('README.md', 'w') as f:
            f.write('initial')
        subprocess.run(['git', 'add', 'README.md'],
                      capture_output=True, check=True)
        subprocess.run(['git', 'commit', '-m', 'initial'],
                      capture_output=True, check=True)

        # Create feature branch with commit
        self.create_branch_with_commit('feature', 'feature content')

        # Checkout main
        subprocess.run(['git', 'checkout', 'main'],
                      capture_output=True, check=True)

        output = self.run_lbranch()
        self.assertIn("Last 5 branches:", output)
        self.assertIn("1) feature", output)

    def test_branch_order_and_format(self):
        # Create initial commit on main
        with open('README.md', 'w') as f:
            f.write('initial')
        subprocess.run(['git', 'add', 'README.md'],
                      capture_output=True, check=True)
        subprocess.run(['git', 'commit', '-m', 'initial'],
                      capture_output=True, check=True)

        # Create branches with actual commits
        self.create_branch_with_commit('dev', 'dev content')
        self.create_branch_with_commit('b1', 'b1 content')
        subprocess.run(['git', 'checkout', 'dev'],
                      capture_output=True, check=True)
        self.create_branch_with_commit('b2', 'b2 content')
        subprocess.run(['git', 'checkout', 'b1'],
                      capture_output=True, check=True)
        self.create_branch_with_commit('b3', 'b3 content')
        subprocess.run(['git', 'checkout', 'dev'],
                      capture_output=True, check=True)
        self.create_branch_with_commit('b4', 'b4 content')

        output = self.run_lbranch()
        self.assertIn("Last 5 branches:", output)
        self.assertIn("1) dev", output)
        self.assertIn("2) b3", output)
        self.assertIn("3) b1", output)
        self.assertIn("4) b2", output)
        self.assertIn("5) main", output)

if __name__ == '__main__':
    unittest.main() 