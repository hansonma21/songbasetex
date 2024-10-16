import re
from flask import Flask, render_template, request, jsonify
from search import Search
from songlist import SongList


app = Flask(__name__)
es = Search()
song_list = SongList()

@app.get('/')
def index():
    return render_template('index.html')

# end point that retrieves the title then id (list of json objects)
@app.get('/autocomplete') # return all songs with title and id, EVERYTHING, do not use query
def autocomplete():
    index_name = 'songs'
    query = request.args.get('query', '')
    if query == '':
        search_query = {'match_all': {}}
    else:
        search_query = {
            "match_phrase_prefix": {
                "title": {
                    "query": query,
                }
            }
        }

    print("Search_query: ")
    print(search_query)
    results = es.search(
        index_name=index_name, 
        body={
            'query': search_query,
            '_source': ['title']
        }, 
        size=5000
    )

    song_list.add_songs_from_autocomplete_results(results)
    return song_list.get_song_list()

@app.get('/song/<song_id>')
def get_song_info(song_id):
    index_name = 'songs'
    song_info = es.retrieve_document(song_id, index_name)
    song_info = song_info['_source']
    # print("movie_info:")
    # print(movie_info)

    # Find the most similar songs to the provided song - return list of objects with song id and song name
    # Using TF-IDF model to search for similar documents, using more-like-this query
    similar_song_list = SongList()
    similarity_query = {
        "more_like_this": {
            "fields": ['lyrics_without_chords', 'title', 'lang'],
            "like": [
                {
                    "_index": index_name,
                    "_id": song_id
                }
            ],
            "min_term_freq": 1,
            "min_doc_freq": 1
        }
    }
    print("Similarity query: ")
    print(similarity_query)
    response = es.search(index_name=index_name, query=similarity_query)
    print("Response from similarity search: ")
    print(response)
    similar_song_list.add_songs_from_similarity_results(response)
    similar_songs = similar_song_list.get_song_list()

    final_response = {
        'song_info': song_info,
        'similar_songs': similar_songs
    }
    return final_response, 200
    # return movie_info, 200



@app.post('/')
def handle_search():
    index_name = 'songs'
    query = request.form.get('query', '')
    filters, parsed_query = extract_filters(query)
    from_ = request.form.get('from_', type=int, default=0)
    # Multi-match search on name, summary, and content fields
    # Retrieves 5 results, from_ can get more additional pages of results
    # Filter restricts search to a specific category
    if parsed_query:
        search_query = {
            'must': {
                'multi_match': {
                    'query': parsed_query,
                    'fields': ['lyrics_without_chords', 'title', 'lang'],
                }
            }
        }
    else:
        # In case search is empty, still will be able to filter on categories
        search_query = {
            'must': {
                'match_all': {}
            }
        }

    results = es.search(
        index_name=index_name,
        body = {
            'query': {
                'bool': {
                    **search_query,
                    **filters
                }
            },
            'aggs': {  # Use bucket aggregation to create buckets for the category field
                'langs-agg': {
                    'terms': {
                        'field': 'lang.keyword',
                    }
                },
            }
        },
        size=50, from_=from_
    )

    # Dictionary of aggregations
    aggs = {
        'Languages': {
            bucket['key']: bucket['doc_count'] for bucket in results['aggregations']['langs-agg']['buckets']
        },
    }

    return render_template('index.html', results=results['hits']['hits'],
                           query=query, from_=from_,
                           total=results['hits']['total']['value'], aggs=aggs)


@app.get('/document/<id>')
def get_document(id):
    index_name = 'songs'
    document = es.retrieve_document(id, index_name)
    title = document['_source']['title']
    language = document['_source']['lang']
    lyrics_with_chords = document['_source']['lyrics']
    return render_template('document.html', title=title, language=language, lyrics_with_chords=lyrics_with_chords)

@app.cli.command()
def reindex(index_name='songs'):
    """Regenerate a specific Elasticsearch index."""
    response = es.reindex(index_name)
    print(f'Index {index_name} with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')

# Extracts keyword filters from a query and returns a tuple with the filters and the query with the filters removed
# User enters search term with category e.g. 'some text to search category:sharepoint'
# User can also enter search term with year e.g. 'some text to search category:sharepoint year:2020'
def extract_filters(query):
    filters = []

    filter_regex = r'languages:([^\s]+)\s*'  # filter_regex = r'genres:([^\s]+(?:\s+[^\s]+)*)\s*'
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'term': {
                'lang.keyword': {
                    'value': m.group(1)
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    return {'filter': filters}, query