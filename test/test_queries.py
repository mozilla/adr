from __future__ import absolute_import, print_function, unicode_literals

import json
from io import StringIO as IO
from threading import Thread
from time import sleep

import responses
import yaml

from adr import config, configuration
from adr import query
from adr.query import format_query, query_activedata


class RunQuery(object):
    def __init__(self, query_test):
        self.query_test = query_test

    def __call__(self, query, *args, **kwargs):
        return self.query_test['mock_data']


def test_query(monkeypatch, query_test, set_config):
    set_config(**{
        'query': query_test['query'],
        'fmt': 'json',
        'debug': False,
        'debug_url': "https://activedata.allizom.org/tools/query.html#query_id={}",
    })
    monkeypatch.setattr(query, 'query_activedata', RunQuery(query_test))

    def print_diff():

        buf = IO()
        yaml.dump(result, buf)
        print("Yaml formatted result for copy/paste:")
        print(buf.getvalue())

        buf = IO()
        yaml.dump(query_test['expected'], buf)
        print("\nYaml formatted expected:")
        print(buf.getvalue())

    if "--debug" in query_test["args"]:

        set_config(debug=True)
        monkeypatch.setattr(query, 'query_activedata', RunQuery(query_test))

        formatted_query = format_query(query_test['query'])
        result = json.loads(formatted_query[0])
        debug_url = formatted_query[1]

        print_diff()
        assert result == query_test["expected"]
        assert debug_url == config.debug_url.format(
            query_test["expected"]["meta"]["saved_as"])

    elif "--table" in query_test["args"]:

        set_config(fmt='table')
        monkeypatch.setattr(query, 'query_activedata', RunQuery(query_test))

        formatted_query = format_query(query_test['query'])
        result = formatted_query[0]
        debug_url = formatted_query[1]
        expected = query_test["expected"]["data"]

        print("Table formatted result:")
        print(result)
        print("Table formatted expected:")
        print(expected)
        assert result == expected
        assert debug_url is None

    else:

        formatted_query = format_query(query_test['query'])
        result = json.loads(formatted_query[0])
        debug_url = formatted_query[1]

        print_diff()
        assert result == query_test["expected"]
        assert debug_url is None


@responses.activate
def test_threaded_query():
    url = configuration.config.url
    dummy_query = json.dumps({"from": "dummy"})

    def request_callback(request):
        payload = json.loads(request.body)
        many_queries = payload.get("tuple")
        if many_queries is None:
            # THE FIRST QUERY WILL TAKE A WHILE, THIS WILL
            # GIVE TIME FOR THE OTHER THREADS WILL FILL activedata_work_items
            sleep(1)
            return 200, {}, json.dumps("x")
        assert len(many_queries) == 3
        return 200, {}, json.dumps({"data": ["a", "b", "c"]})

    responses.add_callback(responses.POST, url, callback=request_callback)

    result = [None] * 4

    def requestor(i):
        result[i] = query_activedata(dummy_query, url)

    threads = [Thread(target=requestor, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert result == ["x", "a", "b", "c"]
