import os
import shutil
import tarfile
import tempfile
from distutils.dir_util import copy_tree

from cachy.stores import FileStore, NullStore  # noqa
from loguru import logger

from adr.util.req import requests_retry_session


def extract_tar_zst(path, dest):
    import zstandard
    dctx = zstandard.ZstdDecompressor()
    with open(path, "rb") as f:
        with dctx.stream_reader(f) as reader:
            with tarfile.open(mode="r|", fileobj=reader) as tar:
                tar.extractall(dest)


class SeededFileStore(FileStore):
    RESEED_KEY = "adr:SeededFileStore:reseed"

    def __init__(self, config):
        """A FileStore instance that allows pre-seeding the cache from an archive
        downloaded from a URL.

        Example configuration:

            file = {
                driver = "seeded-file",
                path = "/path/to/cache",
                url = "https://example.com/cache.tar.gz"
            }

        Configuation can include:

            path: Path on the local file system to store the cache.
            url: Where to download the preseed data from.
            archive_relpath: Path within the archive pointing to the root of the cache data.
            reseed_interval: Time in minutes after which the data will be
                              seeded again (defaults to no reseeding).

        Supported archive formats include `.zip`, `.tar`, `.tar.gz`, `.tar.bz2` or `.tar.zst`.
        """
        self._url = config['url']
        self._reseed_interval = config.get('reseed_interval', 0)
        self._archive_relpath = config.get('archive_relpath')

        self._session = requests_retry_session()

        kwargs = {
            'directory': config['path'],
        }
        if 'hash_type' in config:
            kwargs['hash_type'] = config['hash_type']

        super(SeededFileStore, self).__init__(**kwargs)

    def seed(self):
        """Download and extract the seed data to the cache directory."""
        logger.info(f"Seeding adr cache at {self._directory} with contents from {self._url}")
        self._create_cache_directory(self._directory)

        filename = self._url.split('/')[-1]
        with self._session.get(self._url, stream=True) as r:
            r.raise_for_status()

            with tempfile.TemporaryDirectory() as tempdir:
                with tempfile.NamedTemporaryFile(suffix=filename) as fh:
                    shutil.copyfileobj(r.raw, fh)

                    if filename.endswith('.tar.zst'):
                        extract_tar_zst(fh.name, tempdir)
                    else:
                        shutil.unpack_archive(fh.name, tempdir)

                path = tempdir
                if self._archive_relpath:
                    path = os.path.join(tempdir, self._archive_relpath)

                copy_tree(path, self._directory)

        # Make sure we don't reseed again for another 'reseed_interval' minutes.
        self.put(self.RESEED_KEY, False, self._reseed_interval)

    def get(self, key):
        reseed = super(SeededFileStore, self).get(self.RESEED_KEY)
        if reseed is None:
            self.seed()

        return super(SeededFileStore, self).get(key)


class RenewingFileStore(FileStore):
    def __init__(self, config, retention):
        """A FileStore instance that renews items in the cache when they are
        accessed again.
        """
        kwargs = {
            'directory': config['path'],
        }
        if 'hash_type' in config:
            kwargs['hash_type'] = config['hash_type']

        self.retention = retention

        super(RenewingFileStore, self).__init__(**kwargs)

    def get(self, key):
        value = super(RenewingFileStore, self).get(key)
        if value is None:
            return None

        self.put(key, value, self.retention)
        return value
