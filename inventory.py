#!/usr/bin/env python
"""Inventory.

Usage: 
  inventory --list [--inventory-path=<path>]
  inventory --show --record <name>  [--inventory-path=<path>]
  inventory (--added | --used) --record <name> --amount <amount> [--notes=<notes> --date <date> --inventory-path=<path>]
  inventory (--ordered | --delivered) --record <name> --amount <amount> [--notes=<notes> --date <date> --inventory-path=<path>]


Options:
  --list               List stocks 
  --added              Specifies addition of new record, or new stock/order
  --used               Specifies consumption of stock
  --ordered            Specifies new order placed
  --delivered          Specifies order was delivered
  --record=<name>      Record name. Use --list to get overview
  --date=<date>        User specified date, string YYYY-MM-DD
  --amount=<amount>    User specified amount, string
  --inventory-path=<path>     Path to inventory files [default: ~/.inventory]
"""

from docopt import docopt
import pandas as pd
import os
import sys
import datetime

class Settings:
    def __init__(self, args):
        home = os.path.expanduser('~')
        self.path = args.get("--inventory-path").replace('~', home)
        self.records_path = self.path + '/.allrecords'
        self._verify_path()
        self._read_records()
        self.notes = args.get('--notes', None)
        self.list_records = args.get('--list', None)
        self.amount = args.get('--amount', None)
        if args['--date']:
            try:
                date = datetime.datetime.strptime(args['--date'], "%Y-%m-%d")
                self.date = date.strftime("%Y-%m-%d")
            except:
                print("Pleaes specify date as YYYY-MM-DD")
                sys.exit()
        else:
            self.date = datetime.date.today().isoformat()
        self.action = None
        if args['--added']:
            self.action = "added"
        elif args['--used']:
            self.action = "used"
        elif args['--ordered']:
            self.action = "ordered"
        elif args['--delivered']:
            self.action = "delivered"

        if self.action in ["added", "used"]:
            self.record_type = "stocks"
        elif self.action in ["ordered", "delivered"]:
            self.record_type = "orders"            

        self.record = args.get('--record',None)
        if self.record:
            self._normalize()
            
    def _verify_path(self):
        for p in self.path:
            if not os.path.exists(p):
                os.makedirs(p)

        if not os.path.exists(self.records_path):
            # touch
            with open(self.records_path,  'w') as out:
                out.write("date,amount,action,notes,record,type\n")

    def _normalize(self):
        self.normalized_record = self.record.replace(" ", "-").lower()
        
    def _read_records(self):
        self.recordsdf = pd.read_csv(self.records_path,
                            sep=',',
                            index_col=None)
                
def update_records(settings):
    details = {"date":settings.date,
               "amount":settings.amount,
               "action":settings.action,
               "notes":settings.notes,
               "record":settings.normalized_record,
               "type":settings.record_type}
    settings.recordsdf = settings.recordsdf.append(details, ignore_index=True)
    settings.recordsdf.to_csv(settings.records_path,index=False)

def list_records(settings):
    stocksdf = settings.recordsdf
    stocksdf = stocksdf.loc[(stocksdf["type"] == "stocks")]
    stocksdf.drop("type",axis="columns",inplace=True)
    stocksdf.reset_index(inplace=True)
    print("Stocks")
    for i, row in stocksdf.iterrows():
        print(f"%s\t\t\t%s\t%s\t%ss" % (row.record, row.amount, row.action, row.date))
    print("\n")
    ordersdf = settings.recordsdf
    ordersdf = ordersdf.loc[(ordersdf["type"] == "orders")]
    ordersdf.drop("type",axis="columns",inplace=True)
    ordersdf.reset_index(inplace=True)
    print("Orders")
    for i, row in ordersdf.iterrows():
        print(f"%s\t\t\t%s\t%s\t%ss" % (row.record, row.amount, row.action, row.date))

def show(settings):
    df = settings.recordsdf
    # filter
    df = df[df.record == settings.normalized_record]
    amount = get_current_amount(df)
    # last made
    date = None
    for i,row in df[::-1].iterrows():
        if row.action  == "added":
            date = row.date
            break

    print("__%s__"           % (settings.record))
    print("Last made on: %s" % (date))
    print("Amount left:  %0.1f" % (amount))

def get_current_amount(df):
    amount = 0
    for i, row in df.iterrows():
        sign = row.action
        if sign == "added":
            amount += float(row.amount)
        elif sign == "used":
            amount -= float(row.amount)
    return(amount)

if __name__ == '__main__':
    args = docopt(__doc__, version='')
    settings = Settings(args)
    if args['--list']:
        list_records(settings)
    #     if not records:
    #         print("Nothing here yet...")
    #         sys.exit()
    #     for i, r in enumerate(records):
    #         print("%d\t%s" % (i,r))

    if args['--show']:
        show(settings)
    
    if settings.action is not None:
        update_records(settings)
