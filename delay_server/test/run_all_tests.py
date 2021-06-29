"""Discover and run all tests."""
try:
    import coverage
    import_coverage = True
except ImportError:
    import_coverage = False
import unittest

if __name__ == '__main__':
    if import_coverage:
        cov = coverage.Coverage()
        cov.start()
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('.')
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(test_suite)
    if import_coverage:
        cov.stop()
        cov.save()
        cov.html_report()
