from urllib.parse import quote_plus
from requests_oauthlib import OAuth2Session
from requests_oauthlib import OAuth1Session
from oauthlib.oauth2 import TokenExpiredError
import json
from voluntarily.config import (
    HERE_CLIENT_ID,
    HERE_ACCESS_KEY_ID,
    HERE_ACCESS_KEY_SECRET
)

class Geocoder:
    def __init__(self, es_client):
        self.__base_url = 'https://geocode.search.hereapi.com/v1/geocode?q={}&limit=1'
        self.__here_client = self.__get_client()
        self.__es_client = es_client

    def __get_client(self):
        payload = {"grant_type": "client_credentials"}
        endpoint = 'https://account.api.here.com/oauth2/token'
        here = OAuth1Session(HERE_ACCESS_KEY_ID,
            client_secret=HERE_ACCESS_KEY_SECRET)
        token = here.post(endpoint, data=payload)
        client_id = HERE_CLIENT_ID
        here = OAuth2Session(client_id, token=token.json())
        return here

    def geocode_address_components(self, postalCode=None, stateCode=None, state=None, countryCode=None):
        geo_query = {"query": {"bool":{"must": []}}}
        if postalCode:
            geo_query["query"]["bool"]["must"].append(
                {
                    "match": {
                        "postalCode": postalCode
                    }
                }
            )
        if stateCode:
            geo_query["query"]["bool"]["must"].append(
                {
                    "match": {
                        "stateCode": stateCode
                    }
                }
            )
        if state:
            geo_query["query"]["bool"]["must"].append(
                {
                    "match": {
                        "state": state
                    }
                }
            )
        if countryCode:
            geo_query["query"]["bool"]["must"].append(
                {
                    "match": {
                        "countryCode": countryCode
                    }
                }
            )
        if geo_query["query"]["bool"]["must"]:
            return self.__es_client.search(index="geocode", body=geo_query)['hits']['hits']


    def geocode_raw_input(self, address):
        address = quote_plus(address)
        address_url = self.__base_url.format(address)
        try:
            here_response = self.__here_client.get(address_url)
        except TokenExpiredError as e:
            self.__here_client = __get_client()
            here_response = self.__here_client.get(address_url)
        geocode_items = here_response.json().get("items")
        geocode_result = {}
        if geocode_items:
            geocode_result = geocode_items[0]
            if "id" in geocode_result:
                geocode_result["id_"] = geocode_result.pop("id")
            position = geocode_result.get("position")
            if position:
                geocode_result["geo"] = {
                    "lat": position["lat"],
                    "lon": position["lng"]
                }
            for access in geocode_result.get("access") or []:
                access["lon"] = access.pop("lng")
            geocode_result["userInput"] = address
        return geocode_result