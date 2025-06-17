import logging

logging.basicConfig(format='%(asctime)s %(levelnames)s %(message)s')
 #create a logger
logger = logging.getLogger(__name__)
#Configure logging levels
logger.setLevel(logging.INFO)