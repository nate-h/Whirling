import os
import json
import logging

def load_plan(plan_name):
    full_plan_loc = 'plans/{}.json'.format(plan_name)
    if not os.path.exists(full_plan_loc):
        logging.error('Couldn\'t find plan %s', full_plan_loc)
        quit()
    with open(full_plan_loc, 'r') as f:
        return json.load(f)
