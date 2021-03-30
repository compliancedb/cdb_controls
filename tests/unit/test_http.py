from lib.http import http_put_payload, http_post_payload

from tests.utils import *


def test_put_dry_run_doesnt_call(mocker, capsys):
    requests = mocker.patch('lib.http.req')

    with silent(capsys), dry_run({}):
        http_put_payload("https://www.example.com", {}, "")

    requests.put.assert_not_called()


def test_post_dry_run_doesnt_call(mocker, capsys):
    requests = mocker.patch('lib.http.req')

    with silent(capsys), dry_run({}):
        http_post_payload("https://www.example.com", {}, "")

    requests.post.assert_not_called()
