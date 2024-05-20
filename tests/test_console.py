import pytest
import os
import shutil
import sys
from aqua.aqua_main import AquaConsole, query_yes_no
from aqua.util import dump_yaml

testfile = 'tmp/testfile'

# Helper function to simulate command line arguments
def set_args(args):
    sys.argv = ['aqua'] + args

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: create necessary directories and files
    os.makedirs('tmp')
    yield
    # Teardown: remove created directories and files
    shutil.rmtree('tmp')

@pytest.mark.aqua
class TestAquaConsole():
    """Class for LRA Tests"""

    def test_console_sequence(self):
        os.environ['HOME'] = 'tmp'
        set_args(['init'])
        AquaConsole()
        assert os.path.exists('tmp/.aqua')

        # do it twice!
        set_args(['-vv', 'init'])
        with open(testfile, 'w') as f:
            f.write("yes")
        sys.stdin = open(testfile)
        AquaConsole()
        sys.stdin.close()
        assert os.path.exists('tmp/.aqua')

        # add catalog
        set_args(['add', 'ci'])
        AquaConsole()
        assert os.path.exists('tmp/.aqua/machines/ci')

        # add catalog again and error
        set_args(['-vv', 'add', 'ci'])
        AquaConsole()
        assert os.path.exists('tmp/.aqua/machines/ci')

        # run the list
        set_args(['list'])
        AquaConsole()

        # remove non-existing catalog
        os.makedirs('tmp/.aqua/machines/ci', exist_ok=True)
        set_args(['remove', 'pippo'])
        AquaConsole()

        # remove existing catalog
        set_args(['remove', 'ci'])
        AquaConsole()
        assert not os.path.exists('tmp/config/dir/machines/ci')

        # add wrong fix file
        fixtest = 'tmp/antani.yaml'
        dump_yaml(fixtest, {'fixer_name':  'antani'})
        set_args(['fixes-add', fixtest])
        AquaConsole()
        assert not os.path.exists('tmp/config/dir/fixes/antani.yaml')

        # add mock grid file
        gridtest = 'tmp/supercazzola.yaml'
        dump_yaml(gridtest, {'grids': {'sindaco': {'path': '{{ grids }}/comesefosseantani.nc'}}})
        set_args(['grids-add', gridtest])
        AquaConsole()
        assert os.path.exists(gridtest)

        # uninstall everything
        with open(testfile, 'w') as f:
            f.write("yes")
        sys.stdin = open(testfile)
        set_args(['uninstall'])
        AquaConsole()
        sys.stdin.close()
        assert not os.path.exists('tmp/.aqua')

        # install from path
        set_args(['init', '-p', 'tmp/vicesindaco/'])
        with open(testfile, 'w') as f:
            f.write("yes")
        sys.stdin = open(testfile)
        AquaConsole()
        sys.stdin.close()
        assert os.path.exists('tmp/vicesindaco')

@pytest.mark.aqua
class TestQuery():
    """Class for query test"""
    
    def test_query_yes_no_invalid_input(self):
        with open(testfile, 'w') as f:
            f.write("invalid\nyes")
        sys.stdin = open(testfile)
        assert query_yes_no("Question?", "yes") is True
        sys.stdin.close()

    def test_query_yes_no_explicit_yes(self):
        with open(testfile, 'w') as f:
            f.write("yes")
        sys.stdin = open(testfile)
        assert query_yes_no("Question?", "no") is True
        sys.stdin.close()

    def test_query_yes_no_explicit_no(self):
        with open(testfile, 'w') as f:
            f.write("no")
        sys.stdin = open(testfile)
        assert query_yes_no("Question?", "yes") is False
        sys.stdin.close()
