import mintapi
import json
from contextlib import closing
import datetime
import pandas
import time
import argparse


def default(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, pandas.DataFrame):
        return obj.to_dict(orient='records')
    raise TypeError('invalid type %s' % obj.__class__.__name__)


def get_transactions(mint, page):
    offset = (page - 1) * 50
    params = {
        'offset': offset,
        'filterType': 'cash',
        'comparableType': 8,
        'acctChanged': 'T',
        'task': 'transactions',
        'rnd': mintapi.Mint.get_rnd()
    }

    return json.loads(mint.get(
        'https://wwws.mint.com/app/getJsonData.xevent',
        params=params, headers=mint.headers).content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email', help='mint email address')
    parser.add_argument('-p', '--password', help='mint password')
    args = parser.parse_args()

    mint = mintapi.Mint(args.email, args.password)

    with closing(open('data/accounts.json', 'w')) as f:
        json.dump(mint.get_accounts(), f, default=default, indent=2)

    num_pages = 20
    for page in range(1, num_pages):
        transactions = get_transactions(mint, page)
        with closing(open('data/txns-%02d.json' % page, 'w')) as f:
            json.dump(transactions, f, default=default, indent=2)
            print 'page %d: %d results' % (
                page, len(transactions['set'][0]['data']))
            time.sleep(5)


if __name__ == '__main__':
    main()
