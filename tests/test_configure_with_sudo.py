# import stuff from your project here
# Run tests by doing:
# $ cd path/to/configure-with-sudo
# $ nosetests
import os

DATA_PATH = os.path.join("tests", "data")
TEST_DATA = os.path.join(DATA_PATH, "test-data.txt")


def setup_test_data():
    data = open(TEST_DATA, "r").read()
    return data


def test_hello():
    data = setup_test_data()
    assert "hello" in data
