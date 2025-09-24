import os
import pytest
from aqua.lra_generator import lra_util
from aqua.util import replace_intake_vars

@pytest.fixture
def tmp_directory(tmpdir):
    return str(tmpdir)

@pytest.fixture
def output_directory(tmpdir):
    return str(tmpdir)

@pytest.fixture(
    params=[("IFS", "test-tco79", "long")]
)
def lra_arguments(request):
    return request.param

# @pytest.mark.aqua
# def test_opa_catalog_entry(tmp_directory, lra_arguments):
#     model, exp, source = lra_arguments
#     fixer_name = 'fixer'
#     frequency = 'monthly'
#     loglevel = 'WARNING'
#     entry_name = lra_util.opa_catalog_entry(datadir=tmp_directory, model=model, exp=exp, 
#                                             source=source, fixer_name=fixer_name, frequency=frequency, 
#                                             loglevel=loglevel, catalog='ci')

#     # Create temporary files
#     tmp_file1 = os.path.join(tmp_directory, f'test_{frequency}_mean.nc')
#     with open(tmp_file1, 'w') as f:
#         f.write('Temporary file 1')

#     reader = Reader(model='IFS', exp='test-tco79', source='opa_long', areas=False, loglevel='DEBUG')

#     assert entry_name == 'opa_long'
#     assert reader.esmcat.metadata['fixer_name'] == 'fixer'
#     assert reader.esmcat.describe()['args']['urlpath'] == os.path.join(tmp_directory, f'*{frequency}_mean.nc')

@pytest.mark.aqua
def test_move_tmp_files(tmp_directory, output_directory):
    tmp_file1 = os.path.join(tmp_directory, 'file1_tmp.nc')
    tmp_file2 = os.path.join(tmp_directory, 'file2.nc')
    output_file1 = os.path.join(output_directory, 'file1.nc')
    output_file2 = os.path.join(output_directory, 'file2.nc')

    # Create temporary files
    with open(tmp_file1, 'w') as f:
        f.write('Temporary file 1')
    with open(tmp_file2, 'w') as f:
        f.write('Temporary file 2')

    lra_util.move_tmp_files(tmp_directory, output_directory)

    #assert not os.path.exists(tmp_file1)
    #assert not os.path.exists(tmp_file2)
    assert os.path.exists(output_file1)
    assert os.path.exists(output_file2)

# Test replace_intake_vars
@pytest.mark.aqua
def test_replace_intake_vars():

    path = './AQUA_tests/models/paperino/pluto'
    assert replace_intake_vars(path, catalog='ci') == '{{ TEST_PATH }}/paperino/pluto'