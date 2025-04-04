import json
from dataclasses import dataclass

import requests
from genson import SchemaBuilder
from jsonschema import validate
from requests import Response as Rs

from . import logger


@dataclass
class Response:
    status_code: int
    text: str
    json: object
    headers: dict
    schema: dict


class APIRequest:
    def __get_responses(self, response: Rs):
        try:
            headers = response.headers
            status_code = response.status_code
            text = response.text
            json = response.json()
        except Exception:
            json = {}
        try:
            builder = SchemaBuilder()
            builder.add_object(json)
            schema = builder.to_schema()
        except Exception:
            schema = {}
        return Response(status_code, text, json, headers, schema)

    def get(self, url, **kwargs):
        try:
            response = requests.get(url, **kwargs, timeout=60)
            return self.__get_responses(response)
        except Exception as exc:
            logger.error(exc)

    def post(self, url, payload, headers, **kwargs):
        try:
            response = requests.post(url, data=payload, headers=headers, **kwargs, timeout=60)
            return self.__get_responses(response)
        except Exception as exc:
            logger.error(exc)

    def put(self, url, payload, headers, **kwargs):
        try:
            response = requests.put(url, data=payload, headers=headers, **kwargs, timeout=60)
            return self.__get_responses(response)
        except Exception as exc:
            logger.error(exc)

    def delete(self, url, **kwargs):
        try:
            response = requests.delete(url, **kwargs, timeout=60)
            return self.__get_responses(response)
        except Exception as exc:
            logger.error(exc)

    def validate_schema(self, json, schema):
        try:
            validate(json, schema)
        except Exception as exc:
            logger.error(exc)
