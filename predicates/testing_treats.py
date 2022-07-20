import json
import pandas as pd
import requests
import csv
from pprint import pprint
import sqlite3
import bmt
from oaklib.implementations.ubergraph.ubergraph_implementation import UbergraphImplementation
from sqlalchemy import create_engine


oi = UbergraphImplementation()
conn = sqlite3.connect('test.db')
tk = bmt.Toolkit()


def run():

    engine = create_engine('sqlite://',
                           echo=False)

    r = requests.get('https://smart-api.info/api/metakg')
    metakg = r.json()['associations']
    metakg_small = []
    for association in metakg:
        if association.get('api').get('x-translator').get('component') == 'KP':
            assoc = {
                "subject": association.get('subject'),
                "object": association.get('object'),
                "predicate": association.get("predicate"),
                "provided_by": association.get("provided_by"),
                "api_name": association.get("api").get("name"),
                "api_id": association.get("api").get("smartapi").get("id")
            }
            metakg_small.append(assoc)

    metakg_df = pd.DataFrame.from_dict(metakg_small)
    engine.execute("drop table if exists metakg_table")
    metakg_df.to_sql('metakg_table',
                     con=engine)

    df = pd.read_sql(
        'SELECT distinct subject, object, provided_by, predicate, api_name, '
        'api_id from metakg_table where predicate = "ameliorates" or '
        'predicate = "approved_to_treat" or predicate = "treats"',
        engine)
    # write DataFrame to CSV file
    # df.to_csv('metakg.csv', index=False)
    rows = df.to_dict('records')
    for row in rows:
        subject = "biolink:"+row.get('subject')
        element = tk.get_element(subject)
        id_prefixes = element.id_prefixes
        if len(id_prefixes) == 0:
            ancestors = tk.get_ancestors(element)
            for ancestor in ancestors:
                id_prefixes.append(tk.get_element(ancestor).id_prefixes)
        resource = id_prefixes[0]
        print(resource)

