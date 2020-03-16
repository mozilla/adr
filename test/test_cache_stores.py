from pathlib import Path

import pytest
import responses

from adr.util.cache_stores import SeededFileStore

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
