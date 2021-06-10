import yaml
import logging
import logging.config
from unittest import TestLoader
from unittest import TextTestRunner



def setup_logger(logger_type: str = 'test'):
    if(logger_type not in ('deployed', 'test')):
        logger_type = 'deployed'
    
    #with open('src/util/logging_config.yaml', 'r') as log_file:
    #    log_cfg = yaml.safe_load(log_file.read())

    #logging.config.dictConfig(log_cfg)
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    return logger
    

def run_all_tests():
    test_loader = TestLoader()
    test_suite  = test_loader.discover('.')
    test_runner = TextTestRunner()
    logger = logging.getLogger('test')
    logger.info('START TEST ' + __file__)
    test_runner.run(test_suite)
    logger.info('END TEST ' + __file__)

if __name__ == '__main__':
    setup_logger('test')
    run_all_tests()

