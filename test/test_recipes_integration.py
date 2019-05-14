import json
import os
import subprocess

from pytest import mark, xfail

from adr.recipe import is_fail

TEST_CASES = []


@mark.skipif(os.getenv("TRAVIS_EVENT_TYPE") != "cron", reason="Not run by cron job")
@mark.parametrize("recipe_name", TEST_CASES)
def test_recipe_integration(recipe_name):
    command = ['adr', '--format', 'json']
    command.extend(recipe_name.split(" "))
    try:
        data = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = json.loads(data)
        assert result
        assert len(result)
    except Exception as e:
        if is_fail(command[3]):
            xfail(str(e))
        else:
            raise e
