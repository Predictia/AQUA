import pytest
from aqua import Reader, catalogue

@pytest.fixture(params=[(model, exp, source) 
                        for model in catalogue() 
                        for exp in catalogue()[model] 
                        for source in catalogue()[model][exp]])
def reader(request):
    model, exp, source = request.param
    myread = Reader(model=model, exp=exp, source=source, areas=False)
    myread.retrieve(fix=False)
    return myread

def test_catalog(reader):
    assert isinstance(reader, Reader)