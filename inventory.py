#!/usr/bin/env python
"""Inventory.

Usage: 
  inventory --list
  inventory --show <name> 
  inventory --added <name> --amount <aminput> [--date <dateinput>]
  inventory --used <name> --amount <aminput> [--date <dateinput>]

Options:
  --list               List stocks
  --show=<name>        Shows details of input
  --added=<name>       Add details to input
  --used=<name>        Add details to input
  --date=<date>        User specified date, string
  --amount=<amount>    User specified amount, string
"""

from docopt import docopt
import pandas as pd
import os
import sys
import datetime

def list_all_records():
    if not os.path.exists('.allrecords'):
        with open(".allrecords", 'w') as out:
            out.write("")
    with open(".allrecords",'r') as inp:
        records = [r.strip() for r in inp.readlines()]
    return(records)

def normalize(chemical):
    return(chemical.replace(" ", "-").lower())

def update_index(records, chemical):
    if normalize(chemical) not in records:
        with open(".allrecords", 'a') as out:
            out.write(f"%s\n" % (normalize(chemical)))

def update_details(chemical,
                   amount,
                   added=False,
                   used=False,
                   date=None):
    chem_fname = "." + normalize(chemical)
    if added:
        action = "added"
    elif used:
        sign = "used"
        
    details = {"date":[datetime.date.today().isoformat()],
               "amount":[amount],
               "action":[action]}
    
    if os.path.exists(chem_fname):
        df = pd.read_csv(chem_fname, sep=',',index_col=None)
        df.append(details, ignore_index='True')
    else:
        df = pd.DataFrame(details)
    df.to_csv(chem_fname,index=False)

def show(records, chemical):
    chem_fname = "." + normalize(chemical)
    if not os.path.exists(chem_fname) and chem_fname not in records:
        print("No records exist!")
        sys.exit()
    else:
        df = pd.read_csv(chem_fname, index_col=None, sep=',')
        amount = 0
        for i, row in df.iterrows():
            sign = row.action
            if sign == "added":
                amount += float(row.amount)
            elif sign == "used":
                amount -= float(row.amount)
        # last made
        for i,row in df[::-1].iterrows():
            if row.action  == "added":
                date = row.date
                break
        print("__%s__"           % (chemical))
        print("Last made on: %s" % (date))
        print("Amount left:  %0.1f" % (amount))
            
    
if __name__ == '__main__':
    args = docopt(__doc__, version='')
    records = list_all_records()
    
    if args['--list']:
        if not records:
            print("Nothing here yet...")
            sys.exit()
        for i, r in enumerate(records):
            print("%d\t%s" % (i,r))

    if args['--show']:
        chemical = args['--show']        
        show(records, chemical)
        
    if args['--added'] is not None:
        chemical = args['--added']
        amount = args['--amount']
        update_index(records, chemical)
        update_details(chemical, amount, added=True)

    if args['--used'] is not None:
        chemical = args['--used']
        amount = args['--amount']
        update_index(records, chemical)
        update_details(chemical, amount, used=True)
