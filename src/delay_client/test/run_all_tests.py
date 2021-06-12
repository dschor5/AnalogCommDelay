""" Discover and run all tests. """
from unittest import TestLoader
from unittest import TextTestRunner

if __name__ == '__main__':
    test_loader = TestLoader()
    test_suite  = test_loader.discover('.')
    test_runner = TextTestRunner()
    test_runner.run(test_suite)
