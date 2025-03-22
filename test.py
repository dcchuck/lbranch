#!/usr/bin/env python3
import os
import subprocess
import tempfile
import unittest
from textwrap import dedent

class TestLBranch(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # self.test_dir = './test_dir'
        self.original_dir = os.getcwd()

        # Ensure bin/lbranch exists and is executable
        self.lbranch_path = os.path.join(self.original_dir, 'bin', 'lbranch')
        if not os.path.isfile(self.lbranch_path):
            raise FileNotFoundError(f"Could not find bin/lbranch at {self.lbranch_path}")
        if not os.access(self.lbranch_path, os.X_OK):
            raise PermissionError(f"bin/lbranch is not executable at {self.lbranch_path}")

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

    def test_no_commits(self):
        """Test behavior when repository has no commits"""
        # Create new branch without any commits
        subprocess.run(['git', 'checkout', '-b', 'empty-branch'],
                      capture_output=True, check=True)

        result = subprocess.run([self.lbranch_path], capture_output=True, text=True)
        clean_output = self.strip_color_codes(result.stdout)

        # Should show no branches
        expected_output = "No branch history found - repository has no commits yet"
        self.assertEqual(clean_output.strip(), expected_output.strip())

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

        result = subprocess.run([self.lbranch_path], capture_output=True, text=True)
        clean_output = self.strip_color_codes(result.stdout)

        expected_output = dedent("""\
            Last 5 branches:
            1) main
            """)

        self.assertEqual(clean_output.strip(), expected_output.strip())

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

        result = subprocess.run([self.lbranch_path], capture_output=True, text=True)
        clean_output = self.strip_color_codes(result.stdout)
        expected_output = dedent("""\
            Last 5 branches:
            1) feature
            """)

        self.assertEqual(clean_output.strip(), expected_output.strip())

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

        # Expected output (ignoring colors)
        expected_output = dedent("""\
            Last 5 branches:
            1) dev
            2) b3
            3) b1
            4) b2
            5) main
            """)

        # Run lbranch
        result = subprocess.run([self.lbranch_path], capture_output=True, text=True)
        clean_output = self.strip_color_codes(result.stdout)
        self.assertEqual(clean_output.strip(), expected_output.strip())

    def strip_color_codes(self, text):
        """Remove ANSI color codes from text"""
        import re
        return re.sub(r'\033\[[0-9;]*m', '', text)

if __name__ == '__main__':
    unittest.main()
