import os
import json
import jsonlines
import subprocess
import urllib

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

        itemlist = []
        start = page * rpp

        if query is not None:
            params = ['indent=on',
                      'wt=json',
                      'fl=DBRECORDID,score',
                      'rows=' + str(rpp),
                      'start=' + str(start)]

            solrParams = '&'.join(params)

            solr_query = 'TITLE:' + '(' + query + ')'

            solrURL = self.base_url + self.core_url + "select?" + solrParams + "&q=" + str(urllib.parse.quote(solr_query))
            response = urllib.request.urlopen(solrURL)
            results = json.loads(response.read().decode('utf-8'))

            for result in results['response']['docs']:
                try:
                    itemlist.append(result)
                except:
                    pass

        return {
            'page': page,
            'rpp': rpp,
            'query': query,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }


# class Recommender(object):
#
#     def __init__(self):
#         self.index_documents = 'documents'
#         self.index_documents_settings_path = os.path.join('index_settings', 'gesis-search_documents_settings.json')
#         self.documents_path = './data/gesis-search/documents'
#
#         self.index_datasets = 'datasets'
#         self.index_datasets_settings_path = os.path.join('index_settings', 'gesis-search_datasets_settings.json')
#         self.datasets_path = './data/gesis-search/datasets'
#
#         self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
#
#     def index(self):
#         self.es.indices.create(index=self.index_documents, body=load_settings(self.index_documents_settings_path))
#         self.es.indices.create(index=self.index_datasets, body=load_settings(self.index_documents_settings_path))
#
#         for success, info in helpers.parallel_bulk(self.es,
#                                                    load_json(self.documents_path,
#                                                              'id'), index=self.index_documents):
#             if not success:
#                 return 'A document failed: ' + info, 400
#
#         for success, info in helpers.parallel_bulk(self.es,
#                                                    load_json(self.documents_path,
#                                                              'id'), index=self.index_datasets):
#             if not success:
#                 return 'A document failed: ' + info, 400
#
#         return 'Indices built', 200
#
#     def recommend_datasets(self, item_id, page, rpp):
#         itemlist = []
#
#         start = page * rpp
#
#         if item_id is not None:
#
#             es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
#
#             result = es.search(index=self.index_documents,
#                                from_=start,
#                                size=rpp,
#                                body={"query": {"multi_match": {"query": item_id, "fields": ["id"]}}})
#
#             if result["hits"]["hits"]:
#                 title = result["hits"]["hits"][0]['_source']['title']
#                 es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
#
#                 result = es.search(index=self.index_datasets,
#                                    from_=start,
#                                    size=rpp,
#                                    body={"query": {"multi_match": {"query": title, "fields": ["title", 'abstract']}}})
#
#             for res in result["hits"]["hits"]:
#                 try:
#                     itemlist.append(res['_source']['id'])
#                 except:
#                     pass
#
#         return {
#             'page': page,
#             'rpp': rpp,
#             'item_id': item_id,
#             'itemlist': itemlist,
#             'num_found': len(itemlist)
#         }
#
#     def recommend_publications(self, item_id, page, rpp):
#         itemlist = []
#
#         return {
#             'page': page,
#             'rpp': rpp,
#             'item_id': item_id,
#             'itemlist': itemlist,
#             'num_found': len(itemlist)
#         }
