import time
from pathlib import Path

import pytest
import responses

from adr.util.cache_stores import RenewingFileStore, SeededFileStore

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
