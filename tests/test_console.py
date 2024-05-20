import pytest
import os
import shutil
import sys
from aqua.aqua_main import AquaConsole, query_yes_no
from aqua.util import dump_yaml

testfile = 'testfile.txt'

# Helper function to simulate command line arguments
def set_args(args):
    sys.argv = ['aqua'] + args

@pytest.fixture(scope="session")
def tmpdir(tmp_path_factory):
    mydir = tmp_path_factory.mktemp('tmp')
    yield mydir 
    shutil.rmtree(str(mydir))

@pytest.fixture
def run_aqua_console_with_input(tmpdir):
    def _run_aqua_console(args, input_text):
        set_args(args)
        testfile = os.path.join(tmpdir, 'testfile')
        with open(testfile, 'w') as f:
            f.write(input_text)
        sys.stdin = open(testfile)
        AquaConsole()
        sys.stdin.close()
        os.remove(testfile)
    return _run_aqua_console


@pytest.mark.aqua
class TestAquaConsole():
    """Class for AQUA console tests"""

    def test_console_sequence(self, tmpdir, run_aqua_console_with_input):

        
        # Save the original HOME environment variable
        original_home = os.environ['HOME']

        # getting fixture
        mydir = str(tmpdir)
        os.environ['HOME'] = mydir

        set_args(['init'])
        AquaConsole()
        assert os.path.exists(os.path.join(mydir,'.aqua'))

        # do it twice!
        run_aqua_console_with_input(['-vv', 'init'], 'yes')
        assert os.path.exists(os.path.join(mydir,'.aqua'))

        # add catalog
        set_args(['add', 'ci'])
        AquaConsole()
        assert os.path.exists(os.path.join(mydir,'.aqua/machines/ci'))

        # add catalog again and error
        set_args(['-vv', 'add', 'ci'])
        AquaConsole()
        assert os.path.exists(os.path.join(mydir,'.aqua/machines/ci'))

        # run the list
        set_args(['list'])
        AquaConsole()

        # remove non-existing catalog
        os.makedirs(os.path.join(mydir,'.aqua/machines/ci'), exist_ok=True)
        set_args(['remove', 'pippo'])
        AquaConsole()

        # remove existing catalog
        set_args(['remove', 'ci'])
        AquaConsole()
        assert not os.path.exists(os.path.join(mydir,'.aqua/machines/ci'))

        # add wrong fix file
        fixtest = os.path.join(mydir, 'antani.yaml')
        dump_yaml(fixtest, {'fixer_name':  'antani'})
        set_args(['fixes-add', fixtest])
        AquaConsole()
        assert not os.path.exists(os.path.join(mydir,'config/dir/fixes/antani.yaml'))

        # add mock grid file
        gridtest = os.path.join(mydir, 'supercazzola.yaml')
        dump_yaml(gridtest, {'grids': {'sindaco': {'path': '{{ grids }}/comesefosseantani.nc'}}})
        set_args(['grids-add', gridtest])
        AquaConsole()
        assert os.path.exists(gridtest)

        # uninstall everything
        run_aqua_console_with_input(['uninstall'], 'yes')
        assert not os.path.exists(os.path.join(mydir,'.aqua'))

        # install from path
        run_aqua_console_with_input(['init', '-p', os.path.join(mydir, 'vicesindaco')], 'yes')
        assert os.path.exists(os.path.join(mydir, 'vicesindaco'))

        #Restore the original HOME environment variable
        os.environ['HOME'] = original_home

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
