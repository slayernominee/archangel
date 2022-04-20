# if the api is enabled to interact
import requests
import json

class API():
    def __init__(self, instance: str) -> None:
        """instance example: http://127.0.0.1:8080"""
        self.instance = instance
        self.apipath = '/api'
        self.link = instance + '/api'

    def search(self, query: str) -> list:
        response = requests.post(self.link + '/search', data='{"query": "' + query + '"}')
        return response.json()['results']

# example
#  api = API('http://127.0.0.1:8080')
#  print(api.search('overlord'))
# use case
#  discord bot
#  if you run an watchlist and wants support therefor