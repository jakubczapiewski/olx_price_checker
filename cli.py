import concurrent.futures
import logging
import os
import sys
import time

from main import main

opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
only_profitable = True

if ('-h' in opts) or ('--help' in opts):
    print(
        '''
            Usage:
                      cli <client id> <client secret> 
                      cli <client id> <client secret> -np 
                      cli <client id> <client secret> -np --json
                      cli <client id> <client secret> -np --json -db
                      cli -h | --help
                    
            Options:
                      -h --help     Show this screen.
                      -np           Add non profitable result to output 
                      -j --json     Output in json file  "result.json"
                      -db --debug   Debug mode'''
    )
    sys.exit()

if ('-db' in opts) or ('--debug' in opts):
    logging.basicConfig(level='DEBUG')

if '-np' in opts:
    only_profitable = False
try:
    client_id = args[0]
    secret_key = args[1]
except IndexError:
    raise SystemExit(f"Add client id and secret key arguments!")

with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    thread = executor.submit(main, client_id, secret_key, only_profitable=only_profitable)
    while True:
        for x in range(4):
            sys.stdout.write('\r' + 'wait' + '.' * x)
            time.sleep(0.5)

        if not thread.running():
            break
    result = thread.result()

if not (('--json' in opts) or ('-j' in opts)):
    print(result)
else:
    file = open('result.json', 'w')
    file.write(result)
