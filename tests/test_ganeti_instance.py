import pytest

@pytest.fixture(scope="session", autouse=True)
def prepare_python_environment():
    import sys
    sys.path.append("./plugins/modules")
    sys.path.append("./plugins/module_utils")

def test_dummy():
    assert True

def test_import_module_works():
    import ganeti_instance