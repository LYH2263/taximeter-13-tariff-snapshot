import os
import shutil

import pytest

TEST_DATA_DIR = "/tmp/taximeter_pytest_data"
os.environ["DATA_DIR"] = TEST_DATA_DIR


@pytest.fixture(autouse=True)
def fresh_db():
    shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
    from app import seed
    seed.init_db()
    yield
