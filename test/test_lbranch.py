#!/usr/bin/env python3
import os
import subprocess
import tempfile
import unittest
from textwrap import dedent
import sys
from io import StringIO
from unittest import mock
from lbranch.main import main, supports_color

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

    def test_custom_number(self):
        """Test specifying a custom number of branches to show"""
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

        # Test with -n flag
        output = self.run_lbranch(['-n', '2'])
        self.assertIn("Last 2 branches:", output)
        self.assertIn("1) dev", output)
        self.assertIn("2) b1", output)
        self.assertNotIn("3) main", output)

        # Test with --number flag
        output = self.run_lbranch(['--number', '3'])
        self.assertIn("Last 3 branches:", output)
        self.assertIn("1) dev", output)
        self.assertIn("2) b1", output)
        self.assertIn("3) main", output)

    def test_select_mode(self):
        """Test interactive select mode (without actually selecting)"""
        # Create initial commit on main
        with open('README.md', 'w') as f:
            f.write('initial')
        subprocess.run(['git', 'add', 'README.md'], 
                      capture_output=True, check=True)
        subprocess.run(['git', 'commit', '-m', 'initial'],
                      capture_output=True, check=True)

        # Create feature branch with commit
        self.create_branch_with_commit('feature', 'feature content')

        # We can't fully test interactive mode without mocking input()
        # But we can test that the prompt is displayed
        with mock.patch('builtins.input', return_value="invalid"):
            try:
                output = self.run_lbranch(['-s'])
                # This should not be reached as an invalid selection raises SystemExit
                self.fail("Should have raised SystemExit")
            except SystemExit:
                pass  # Expected behavior

    def test_color_flags(self):
        """Test --no-color and --force-color flags"""
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

        # Test with --no-color flag
        output_no_color = self.run_lbranch(['--no-color'])
        # Color codes shouldn't be present
        self.assertNotIn('\033[', output_no_color)
        
        # Test with --force-color flag 
        output_force_color = self.run_lbranch(['--force-color'])
        # Color codes should be present
        self.assertIn('\033[', output_force_color)


class TestColorSupport(unittest.TestCase):
    """Test color support detection functionality"""
    
    @mock.patch('sys.stdout.isatty')
    @mock.patch('platform.system')
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_no_tty(self, mock_platform, mock_isatty):
        """Test behavior when output is not to a TTY"""
        mock_isatty.return_value = False
        mock_platform.return_value = 'Linux'
        self.assertFalse(supports_color())
    
    @mock.patch('sys.stdout.isatty')
    @mock.patch('platform.system')
    @mock.patch.dict(os.environ, {'FORCE_COLOR': '1'}, clear=True)
    def test_force_color(self, mock_platform, mock_isatty):
        """Test behavior with FORCE_COLOR env var"""
        mock_isatty.return_value = False  # Should still return True due to FORCE_COLOR
        mock_platform.return_value = 'Linux'
        self.assertTrue(supports_color())
    
    @mock.patch('sys.stdout.isatty')
    @mock.patch('platform.system')
    @mock.patch.dict(os.environ, {'NO_COLOR': '1'}, clear=True)
    def test_no_color_env(self, mock_platform, mock_isatty):
        """Test behavior with NO_COLOR env var"""
        mock_isatty.return_value = True  # Would normally return True
        mock_platform.return_value = 'Linux'
        self.assertFalse(supports_color())
    
    @mock.patch('sys.stdout.isatty')
    @mock.patch('platform.system')
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_windows_no_color_support(self, mock_platform, mock_isatty):
        """Test behavior on Windows with no color support"""
        mock_isatty.return_value = True
        mock_platform.return_value = 'Windows'
        self.assertFalse(supports_color())
    
    @mock.patch('sys.stdout.isatty')
    @mock.patch('platform.system')
    @mock.patch.dict(os.environ, {'WT_SESSION': '1'}, clear=True)
    def test_windows_with_color_support(self, mock_platform, mock_isatty):
        """Test behavior on Windows with color support (Windows Terminal)"""
        mock_isatty.return_value = True
        mock_platform.return_value = 'Windows'
        self.assertTrue(supports_color())
    
    @mock.patch('sys.stdout.isatty')
    @mock.patch('platform.system')
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_unix_default(self, mock_platform, mock_isatty):
        """Test behavior on Unix with TTY"""
        mock_isatty.return_value = True
        mock_platform.return_value = 'Linux'
        self.assertTrue(supports_color())


if __name__ == '__main__':
    unittest.main() 