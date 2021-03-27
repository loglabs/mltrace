from mltrace import backtrace, get_history, get_components_with_owner, get_components_with_tag

import json
import logging
import pprint

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

logging.info(get_history('etl'))
logging.info(get_components_with_owner('shreya'))
logging.info(get_components_with_tag('fuck'))

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
    # trace = backtrace(inp)
    # elems = []
    # for depth, cr in trace:
    #     elem = f'["{cr.component_name}", "{cr.component_name}", new Date({cr.start_timestamp.strftime("%s")}), new Date({cr.end_timestamp.strftime("%s")}), null, 100, "{",".join(cr.dependencies)}"]'
    #     d = cr.to_dictionary()
    #     d['inputs'] = [inp.name for inp in d['inputs']]
    #     d['outputs'] = [out.name for out in d['outputs']]
    #     d['start_timestamp'] = d['start_timestamp'].strftime("%s")
    #     d['end_timestamp'] = d['end_timestamp'].strftime("%s")
    #     if d['code_snapshot']:
    #         d['code_snapshot'] = d['code_snapshot'].decode('utf-8')
    #     elems.append(d)
    #     # elems.append(elem)
    #     # print(cr)
    # print(json.dumps(elems))
    # print(','.join(elems))
