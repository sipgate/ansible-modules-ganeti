import pytest

@pytest.fixture(scope="session", autouse=True)
def prepare_python_environment():
    import sys
    sys.path.append("./plugins/modules")
    sys.path.append("./plugins/module_utils")