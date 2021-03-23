from mltrace import backtrace, get_history, get_components_for_owner

import logging

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

logging.info(get_history('etl'))
logging.info(get_components_for_owner('shreya'))

# while(True):
#     inp = input(
#         'Input output id you want to trace or press enter to quit. ').strip()
#     if inp == '':
#         exit(0)
#     try:
#         backtrace(inp)
#     except:
#         print(f'{inp} not recognized. Please try again.')
#         continue
