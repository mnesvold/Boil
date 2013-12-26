import os
import shutil
import sys
import tempfile
import unittest

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import boiler


class BoilerTests(unittest.TestCase):
    def setUp(self):
        self.boiler = boiler.Boiler()
        self.temp_dirs = []
    
    def tearDown(self):
        for temp_dir in self.temp_dirs:
            shutil.rmtree(temp_dir)
    
    def _mkdtemp(self):
        temp_dir = tempfile.mkdtemp(prefix='test-temp-', dir=os.curdir)
        self.temp_dirs.append(temp_dir)
        return temp_dir

    def _write_file(self, filename, contents):
        with open(filename, 'w') as f:
            f.write(contents)
    
    def _read_file(self, filename):
        with open(filename) as f:
            return f.read()

    def test_templates_dir_default(self):
        """
        A Boiler object should expose a `templates_dir` variable which
        is a string and defaults to the absolute path of a `.boiler` folder
        in the user's home directory.
        """
        expected_dir = os.path.abspath(os.path.expanduser('~/.boiler'))
        actual_dir = self.boiler.templates_dir
        self.assertEqual(expected_dir, actual_dir)

    def test_templates_dir_cli_arg(self):
        """
        A Boiler object should expose a 'parse_arguments' method
        which accepts a `--templates-dir=DIR` argument which sets the Boiler's
        `templates_dir` variable.
        """
        self.boiler.parse_arguments(['--templates-dir=/foo/bar'])
        expected_dir = '/foo/bar'
        actual_dir = self.boiler.templates_dir
        self.assertEqual(expected_dir, actual_dir)

    def test_output_dir_default(self):
        """
        A Boiler object should expose an `output_dir` variable which
        is a string and defaults to the current directory.
        """
        expected_dir = os.curdir
        actual_dir = self.boiler.output_dir
        self.assertEqual(expected_dir, actual_dir)

    def test_output_dir_cli_arg(self):
        """
        A Boiler object should expose a 'parse_arguments' method
        which accepts a `--output-dir=DIR` argument which sets the Boiler's
        `output_dir` variable.
        """
        self.boiler.parse_arguments(['--output-dir=../qux'])
        expected_dir = '../qux'
        actual_dir = self.boiler.output_dir
        self.assertEqual(expected_dir, actual_dir)

    def test_apply_boilerplate(self):
        """
        A Boiler object should expose an `apply_boilerplate` method which
        accepts a template name and copies the like-named file from its current
        templates_dir folder into its current output_dir folder.
        """
        templates_dir = self.boiler.templates_dir = self._mkdtemp()
        output_dir = self.boiler.output_dir = self._mkdtemp()
        template_name = 'foo.tmpl'
        template_path = os.path.join(templates_dir, template_name)
        output_path = os.path.join(output_dir, template_name)
        self._write_file(template_path, 'Hello, world!')
        self.boiler.apply_boilerplate(template_name)
        output = self._read_file(output_path)
        self.assertEqual(output, 'Hello, world!')

    def test_cli_arg_parse_ok(self):
        """
        A Boiler object should expose a `parse_arguments` method which returns
        True when the arguments parse successfully.
        """
        self.assertTrue(self.boiler.parse_arguments([]))
        self.assertTrue(self.boiler.parse_arguments(['--templates-dir=/']))
        self.assertTrue(self.boiler.parse_arguments(['--output-dir=.']))

    def test_cli_arg_parse_fail(self):
        """
        A Boiler object should expose a `parse_arguments` method which returns
        False if any argument fails to parse.
        """
        self.assertFalse(self.boiler.parse_arguments(['--fail']))
        self.assertFalse(self.boiler.parse_arguments([
            '--templates-dir=/', '--nope']))

    def test_stderr(self):
        """
        A Boiler object should expose a `stderr` variable which defaults to
        `sys.stderr`.
        """
        self.assertIs(self.boiler.stderr, sys.stderr)

    def test_usage(self):
        """
        A Boiler object should expose a `print_usage` method which prints
        information to the Boiler's `stderr` variable, then raises 'SystemExit'.
        """
        stderr = self.boiler.stderr = StringIO()
        with self.assertRaises(SystemExit):
            self.boiler.print_usage()
        self.assertNotEqual(stderr.getvalue(), '')

    def test_template_list_default(self):
        """
        A Boiler object should expose a `template_list` variable which defaults
        to an empty list.
        """
        self.assertEqual(self.boiler.template_list, [])

    def test_template_list_cli_arg(self):
        """
        A Boiler object should expose a `parse_arguments` method which accepts
        positional arguments and uses them to populate the Boiler's
        `template_list` variable.
        """
        self.boiler.parse_arguments(['foo.tmpl', 'bar', 'bam.qux'])
        expected = ['foo.tmpl', 'bar', 'bam.qux']
        actual = self.boiler.template_list
        self.assertSequenceEqual(expected, actual)
    
    def test_main_ok(self):
        """
        A Boiler object should expose a `main` method which forwards its
        argument to parse_arguments, then (if parse_arguments returns True)
        calls apply_boilerplate with each element of the `template_list`
        variable.
        """
        parse_argument_calls = []
        apply_calls = []
        def mock_parse_arguments(args):
            self.assertSequenceEqual([], parse_argument_calls)
            parse_argument_calls.append(args)
            self.boiler.template_list = ['blue', 'red', 'green']
            return True
        def mock_apply(arg):
            apply_calls.append(arg)
        self.boiler.parse_arguments = mock_parse_arguments
        self.boiler.apply_boilerplate = mock_apply
        self.boiler.main(['--foo', '--bar=bam', 'hallo'])
        self.assertSequenceEqual([['--foo', '--bar=bam', 'hallo']],
            parse_argument_calls)
        self.assertSequenceEqual(['blue', 'red', 'green'], apply_calls)

    def test_main_empty(self):
        """
        A Boiler object should expose a `main` method which forwards its
        argument to parse_arguments, then (if template_list is empty)
        calls print_usage.
        """
        usage_calls = []
        def mock_parse_arguments(args):
            self.boiler.template_list = []
            return True
        def mock_usage():
            usage_calls.append(0)
        self.boiler.parse_arguments = mock_parse_arguments
        self.boiler.print_usage = mock_usage
        self.boiler.main([])
        self.assertSequenceEqual([0], usage_calls)

    def test_main_fail(self):
        """
        A Boiler object should expose a `main` method which forwards its
        argument to parse_arguments, then (if parse_arguments returns False)
        calls print_usage.
        """
        class MockSystemExit(Exception):
            pass
        usage_calls = []
        def mock_parse_arguments(args):
            self.boiler.template_list = ['foo']
            return False
        def mock_usage():
            usage_calls.append(0)
            raise MockSystemExit
        self.boiler.parse_arguments = mock_parse_arguments
        self.boiler.print_usage = mock_usage
        with self.assertRaises(MockSystemExit):
            self.boiler.main([])
        self.assertSequenceEqual([0], usage_calls)

if __name__ == '__main__':
    unittest.main()

