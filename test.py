#!/usr/bin/env python3
import os
import subprocess
import tempfile
import unittest
from textwrap import dedent

class TestLBranch(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        
        # Ensure bin/lbranch exists and is executable
        self.lbranch_path = os.path.join(self.original_dir, 'bin', 'lbranch')
        if not os.path.isfile(self.lbranch_path):
            raise FileNotFoundError(f"Could not find bin/lbranch at {self.lbranch_path}")
        if not os.access(self.lbranch_path, os.X_OK):
            raise PermissionError(f"bin/lbranch is not executable at {self.lbranch_path}")
            
        # Setup test repository
        os.chdir(self.test_dir)
        subprocess.run(['git', 'init'], capture_output=True)
        subprocess.run(['git', 'config', '--local', 'user.email', 'test@example.com'])
        subprocess.run(['git', 'config', '--local', 'user.name', 'Test User'])
        
        # Create initial commit on main
        subprocess.run(['touch', 'README.md'])
        subprocess.run(['git', 'add', 'README.md'])
        subprocess.run(['git', 'commit', '-m', 'initial'])

    def tearDown(self):
        os.chdir(self.original_dir)
        subprocess.run(['rm', '-rf', self.test_dir])

    def create_branch_with_commit(self, branch_name, file_content):
        """Create a branch and add a commit to it"""
        subprocess.run(['git', 'checkout', '-b', branch_name], capture_output=True)
        with open(f'{branch_name}.txt', 'w') as f:
            f.write(file_content)
        subprocess.run(['git', 'add', f'{branch_name}.txt'], capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'commit on {branch_name}'], capture_output=True)

    def test_branch_order_and_format(self):
        # Create branches with actual commits
        self.create_branch_with_commit('dev', 'dev content')
        self.create_branch_with_commit('b1', 'b1 content')
        subprocess.run(['git', 'checkout', 'dev'], capture_output=True)
        self.create_branch_with_commit('b2', 'b2 content')
        subprocess.run(['git', 'checkout', 'b1'], capture_output=True)
        self.create_branch_with_commit('b3', 'b3 content')
        subprocess.run(['git', 'checkout', 'dev'], capture_output=True)
        self.create_branch_with_commit('b4', 'b4 content')

        # Print reflog for debugging
        print("\nGit Reflog output:")
        subprocess.run(['git', 'reflog'], text=True)

        # Expected output (ignoring colors)
        expected_output = dedent("""\
            Last 5 branches:
            1) b4
            2) dev
            3) b3
            4) b1
            5) b2
            """)

        # Run lbranch
        result = subprocess.run([self.lbranch_path], capture_output=True, text=True)
        
        # Strip ANSI color codes from output for comparison
        clean_output = self.strip_color_codes(result.stdout)
        
        # Compare outputs
        self.assertEqual(clean_output.strip(), expected_output.strip())
        
        # Print both for visual inspection
        print("\nExpected output:")
        print(expected_output)
        print("Actual output:")
        print(clean_output)

    def test_custom_count(self):
        # Create branches with actual commits
        self.create_branch_with_commit('b1', 'b1 content')
        self.create_branch_with_commit('b2', 'b2 content')
        self.create_branch_with_commit('b3', 'b3 content')
        self.create_branch_with_commit('b4', 'b4 content')

        # Test with count of 3
        expected_output = dedent("""\
            Last 3 branches:
            1) b4
            2) b3
            3) b2
            """)

        result = subprocess.run([self.lbranch_path, '3'], capture_output=True, text=True)
        clean_output = self.strip_color_codes(result.stdout)
        
        self.assertEqual(clean_output.strip(), expected_output.strip())

    def test_no_repository(self):
        # Move to a non-git directory
        os.chdir('/tmp')
        
        result = subprocess.run([self.lbranch_path], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Not a git repository', self.strip_color_codes(result.stderr))

    def strip_color_codes(self, text):
        """Remove ANSI color codes from text"""
        import re
        return re.sub(r'\033\[[0-9;]*m', '', text)

if __name__ == '__main__':
    unittest.main()