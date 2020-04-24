import copy
import time
from pathlib import Path

import boto3
import botocore
import pytest
import responses

from adr.util.cache_stores import RenewingFileStore, S3Store, SeededFileStore

here = Path(__file__).resolve().parent


@pytest.fixture
def archive_response():
    archive_dir = here / "files" / "cache_archives"

    def callback(resp):
        resp.callback_processd = True

        name = resp.url.split('/')[-1]
        fh = open(archive_dir / name, 'rb')
        resp.raw = fh

        return resp

    with responses.RequestsMock(response_callback=callback) as rsps:
        yield rsps


@pytest.mark.parametrize('archive_name', ['cache.tar'])
def test_seeded_file_store_download_and_extract(tmpdir, archive_response, archive_name):
    archive_response.add(
        responses.GET,
        f'https://example.com/{archive_name}'
    )

    path = tmpdir.mkdir('cache')
    config = {
        'path': path.strpath,
        'url': f"https://example.com/{archive_name}",
        'reseed_interval': 1440,
        'archive_relpath': 'cache',
    }
    fs = SeededFileStore(config)
    assert fs.get('foo') is None
    assert path.join('foo').check()
    assert path.join('bar').check()


def test_renewing_file_store(tmpdir, monkeypatch):
    path = tmpdir.mkdir('cache')
    config = {
        'path': path.strpath,
    }
    fs = RenewingFileStore(config, 1)

    cur_time = time.time()

    def mock_time():
        return cur_time

    monkeypatch.setattr(time, 'time', mock_time)

    # The cache is empty at first.
    assert fs.get('foo') is None

    # Store an element in the cache with a retention of one minute.
    fs.put('foo', 'bar', 1)
    assert fs.get('foo') == 'bar'

    # Mock time to make the cache think one minute has passed.
    cur_time += 60

    # The item expired, so it won't be in the cache anymore.
    assert fs.get('foo') is None

    # Store an element in the cache with a retention of one minute.
    fs.put('foo', 'bar', 1)
    assert fs.get('foo') == 'bar'

    # Mock time to make the cache think thirty seconds have passed.
    cur_time += 30

    # The item is still in the cache, since only thirty seconds have passed.
    assert fs.get('foo') == 'bar'

    # Mock time to make the cache think fourty-five seconds have passed.
    cur_time += 45

    # The item is still in the cache, as we renewed its expiration when we
    # accessed it after 30 seconds.
    assert fs.get('foo') == 'bar'

    # Mock time to make the cache think one minute has passed.
    cur_time += 60

    # The item expired, so it won't be in the cache anymore.
    assert fs.get('foo') is None


def test_s3_store(monkeypatch):
    copy_calls = 0

    def mock_client(t, aws_access_key_id, aws_secret_access_key, aws_session_token):
        assert t == "s3"
        assert aws_access_key_id == "aws_access_key_id"
        assert aws_secret_access_key == "aws_secret_access_key"
        assert aws_session_token == "aws_session_token"

        class Response:
            def __init__(self, data):
                self.data = data

            def read(self):
                return self.data

        class Client:
            def __init__(self):
                self.data = {}
                self.metadata = {}

            def head_object(self, Bucket, Key):
                assert Bucket == "myBucket"
                assert Key == "data/adr_cache/foo"
                if (Bucket, Key) in self.data:
                    if (Bucket, Key) in self.metadata:
                        return {"Metadata": copy.deepcopy(self.metadata[(Bucket, Key)])}
                    else:
                        return {"Metadata": {}}
                else:
                    raise botocore.exceptions.ClientError(
                        {"Error": {"Code": "404"}}, "head"
                    )

            def put_object(self, Body, Bucket, Key):
                assert Bucket == "myBucket"
                assert Key == "data/adr_cache/foo"
                self.data[(Bucket, Key)] = Body

            def copy_object(self, Bucket, CopySource, Key, Metadata, MetadataDirective):
                assert Bucket == "myBucket"
                assert Key == "data/adr_cache/foo"
                assert CopySource["Bucket"] == "myBucket"
                assert CopySource["Key"] == "data/adr_cache/foo"
                if (Bucket, Key) in self.metadata:
                    assert Metadata != self.metadata[(Bucket, Key)]
                assert MetadataDirective == "REPLACE"
                self.metadata[(Bucket, Key)] = copy.deepcopy(Metadata)

                nonlocal copy_calls
                copy_calls += 1

            def get_object(self, Bucket, Key):
                assert Bucket == "myBucket"
                assert Key == "data/adr_cache/foo"
                return {"Body": Response(self.data[(Bucket, Key)])}

        return Client()

    monkeypatch.setattr(boto3, "client", mock_client)

    config = {
        "bucket": "myBucket",
        "prefix": "data/adr_cache/",
    }
    fs = S3Store(
        config, "aws_access_key_id", "aws_secret_access_key", "aws_session_token"
    )

    # The cache is empty at first.
    assert fs.get("foo") is None

    # Store an element in the cache.
    fs.put("foo", "bar", 1)
    assert fs.get("foo") == "bar"
    assert copy_calls == 1

    # Ensure we update the metadata to renew the item expiration.
    assert fs.get("foo") == "bar"
    assert copy_calls == 2
