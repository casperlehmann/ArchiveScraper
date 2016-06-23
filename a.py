import logging

logging.basicConfig(#filename='log.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.warning('AH! %10s end', '???')
logging.info('lol')
