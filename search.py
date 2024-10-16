from fuzzywuzzy import process

import loadSongs as ls

import json
from pprint import pprint
import os
import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv(dotenv_path='.flaskenv')

class Search:
    def __init__(self):
        self.es = Elasticsearch("http://localhost:9200")
        client_info = self.es.info()
        print('Connected to Elasticsearch!')
        pprint(client_info)
    
    # Deletes index index_name if it exists and then creates it
    def create_index(self, index_name: str):
        self.es.indices.delete(index=index_name, ignore_unavailable=True)
        self.es.indices.create(index=index_name)
    
    # Insert a single document
    def insert_document(self, document, index_name):
        return self.es.index(index=index_name, body=document)

    # Inserts documents in a bulk call
    # documents: list of documents
    def insert_documents(self, documents: list, index_name):
        operations = []
        for document in documents:
            operations.append({'index': {'_index': index_name}})
            operations.append(document)
        return self.es.bulk(operations)

    # Regenerate index - delete old index and create new one and populate it
    def reindex(self, index_name):
        self.create_index(index_name)
        with open('songs_updated.json', 'rt', encoding="utf-8") as f:
            documents = json.loads(f.read())
        return self.insert_documents(documents[index_name], index_name)

    # Search helper method
    def search(self, index_name, **query_args):
        return self.es.search(index=index_name, **query_args)

    def retrieve_document(self, id, index_name):
        return self.es.get(index=index_name, id=id)




# List of strings to search within
# return match, score
def return_best_match(query, list_of_lyrics):
    res = process.extractOne(query, list_of_lyrics)
    return res

def return_title_from_id(id, songs):
    for s in songs:
        # ids are stored as ints
        if s['id'] == int(id):
            return s['title']
    else:
        return ""

def test():
    db = ls.import_json('songs.json')
    #songs = ls.list_of_lyrics(db)
    songs = ls.list_of_titles(db)
    res = return_best_match('We love the church life', songs)

    match = res[0]
    score = res[1]
    ind = res[2]
    #print("Best match:", res)
    print(f"match: {match}, score: {score}, index: {ind}")

if __name__ == "__main__":
    test()
