from mltrace import backtrace, get_history, get_components_for_owner

import logging
import pprint

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

logging.info(get_history('etl'))
logging.info(get_components_for_owner('shreya'))

while(True):
    inp = input(
        'Input output id you want to trace or press enter to quit. ').strip()
    if inp == '':
        exit(0)
    try:
        trace = backtrace(inp)
        for depth, cr in trace:
            logging.info(''.join(['\t' for _ in range(depth)]) + str(cr))
    except:
        logging.info(f'{inp} not recognized. Please try again.')
        continue
