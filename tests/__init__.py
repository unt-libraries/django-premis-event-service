import os
from functools import partial


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_DATA_DIR = os.path.join(TESTS_DIR, 'test_data')

AppEventTestXml = partial(open, os.path.join(TEST_DATA_DIR, 'app_event.xml'))
