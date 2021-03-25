import os
import json
import jsonlines
import subprocess
import urllib
import pysolr


def load_json(directory, id_field):
    for path, subdir, file in os.walk(directory):
        extensions = tuple([".jsonl"])
        files = [f for f in file if f.endswith(extensions)]
        for f in files:
            with jsonlines.open(os.path.join(path, f), 'r') as reader:
                for obj in reader:
                    del obj['links']
                    yield obj


class Ranker(object):

    def __init__(self):
        self.core = 'livivo'
        self.base_url = 'http://0.0.0.0:8983'
        self.core_url = '/solr/{}/'.format(self.core)
        self.documents_path = '/data/livivo/documents/'

    def test(self):
        return 200

    def index(self):
        command = "/opt/solr-8.8.1/bin/solr create_core -c {} -d server/solr/configsets/livivo".format(self.core)
        subprocess.call(command.split())

        files = [os.path.join(self.documents_path, f) for f in os.listdir(self.documents_path) if os.path.isfile(os.path.join(self.documents_path, f))]

        for file in files:
            command = "/opt/solr-8.8.1/bin/post -c livivo "+file
            subprocess.call(command.split())

        return 'Index built', 200

    def rank_publications(self, query, page, rpp):
        start = page * rpp

        if query is not None:
            params = ['indent=on', 'wt=json', 'fl=DBRECORDID,score', 'rows=' + str(rpp), 'start=' + str(start)]
            solrParams = '&'.join(params)

            solr_query = 'TITLE:' + '(' + query + ')'

            solrURL = self.base_url + self.core_url + "select?" + solrParams + "&q=" + str(urllib.parse.quote(solr_query))
            response = urllib.request.urlopen(solrURL)
            results = json.loads(response.read().decode('utf-8'))

            itemlist = results['response']['docs']

        return {
            'page': page,
            'rpp': rpp,
            'query': query,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }


class Recommender(object):

    def __init__(self):
        self.base_url = 'http://localhost:8983'
        self.documents_path = '/data/gesis-search/documents/'
        self.datasets_path = '/data/gesis-search/datasets/'

        self.core_documents = 'gesis_documents'
        self.core_documents_url = '/solr/{}/'.format(self.core_documents)
        self.solr_docs = pysolr.Solr(self.base_url + self.core_documents_url, always_commit=True)

        self.core_datasets = 'gesis_datasets'
        self.core_datasets_url = '/solr/{}/'.format(self.core_datasets)
        self.solr_data = pysolr.Solr(self.base_url + self.core_datasets_url, always_commit=True)



    def index(self):
        # Datasets
        command = "/opt/solr-8.8.1/bin/solr create_core -c {} -d server/solr/configsets/datasets".format(self.core_datasets)
        subprocess.call(command.split())

        files = [os.path.join(self.datasets_path, f) for f in os.listdir(self.datasets_path) if
                 os.path.isfile(os.path.join(self.datasets_path, f))]

        for file in files:
            command = "/opt/solr-8.8.1/bin/post -c {} ".format(self.core_datasets) + file
            subprocess.call(command.split())



        # Documents
        command = "/opt/solr-8.8.1/bin/solr create_core -c {} -d server/solr/configsets/documents".format(
            self.core_documents)
        subprocess.call(command.split())

        for path, subdir, file in os.walk(self.documents_path):
            extensions = tuple([".jsonl"])
            files = [f for f in file if f.endswith(extensions)]
            for f in files:
                with jsonlines.open(os.path.join(path, f), 'r') as reader:
                    self.solr_docs.add(list(reader))

        return 'Indices built', 200


    def recommend_datasets(self, item_id, page, rpp):

        results = self.solr_docs.search('id:' + item_id)
        doc = list(results)[0]

        q = doc['title'][0]

        itemlist = list(self.solr_data.search('title:(' + q.replace(':', '') + ')'))

        return {
            'page': page,
            'rpp': rpp,
            'item_id': item_id,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }