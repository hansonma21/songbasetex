class SongList:
    def __init__(self) -> None:
        self.song_list = []
    
    def add_songs_from_autocomplete_results(self, results):
        """Add movies to movie list from results of ElasticSearch .search call"""
        self.song_list = [{'song_id': hit['_id'], 'song_name': hit['_source']['title']} for hit in results['hits']['hits']]
    
    def add_songs_from_similarity_results(self, results):
        """Add movies to movie list from results of ElasticSearch .search call"""
        self.song_list = [{'song_id': hit['_id'], 'similarity_score': hit['_score'], 'source': hit['_source']} for hit in results['hits']['hits']]
    
    def get_song_list(self):
        return self.song_list