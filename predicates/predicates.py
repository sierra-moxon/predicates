import csv
import bmt
import requests
from biothings_explorer.smartapi_kg.dataload import load_specs

tk = bmt.Toolkit('https://raw.githubusercontent.com/biolink/biolink-model/2.2.12/biolink-model.yaml')
tsv_file = open("predicates.tsv", "w")
tsv_attributes = open("attributes.tsv", "w")
tsv_writer = csv.writer(tsv_file, delimiter='\t')
tsv_writer_att = csv.writer(tsv_attributes, delimiter='\t')


def sample_predicates():
    specs = load_specs()
    kp_titles = []
    for spec in specs:
        if 'x-translator' not in spec['info']:
            continue
        if spec['info']['x-translator']['component'] == 'KP':
            kp_titles.append(spec['info']['title'])
        if 'servers' not in spec:
            continue
        else:
            url = spec['servers'][0]['url']
            apititle = '_'.join(spec['info']['title'].split())
            if url.endswith('/'):
                url = url[:-1]
            predicates_url = f'{url}/meta_knowledge_graph'
            print(predicates_url)
            trapi, predicates = get_predicates(predicates_url)
            if not predicates:
                continue
            else:
                preds, attribs, url = dump_trapi_predicate_results(predicates, predicates_url)
                predicates = set(preds)
                attributes = set(attribs)
                for pred in predicates:
                    tsv_writer.writerow([apititle, url, pred])
                for attrib in attributes:
                    tsv_writer_att.writerow([url, attrib])


def in_biolink_model(predicate):
    is_predicate = tk.is_predicate(predicate)
    return is_predicate


def dump_trapi_predicate_results(predicates, url):
    preds = []
    attribs = []
    for edge in predicates.get('edges'):
        predicate = edge.get('predicate')
        subject = edge.get('subject')
        objectt = edge.get('object')
        preds.append(predicate)
        if 'attributes' in edge and edge.get('attributes') is not None:
            for attribute in edge.get('attributes'):
                print(attribute)
                attribs.append(attribute.get('attribute_type_id'))
                tsv_writer_att.writerow([url, subject, predicate, objectt, attribute])
    preds = set(preds)
    attribs = set(attribs)
    return preds, attribs, url


def get_predicates(pr_url):
    try:
        response = requests.get(pr_url)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {}
    except:
        return False, {}


if __name__ == '__main__':
    sample_predicates()
