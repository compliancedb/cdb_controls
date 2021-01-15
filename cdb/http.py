import json
import os

import requests as req
from requests.auth import HTTPBasicAuth
from cdb.http_retry import http_retry


def http_get_json(url, api_token):
    print("Getting json:")
    print("From this url: " + url)
    resp = http_retry().get(url, auth=HTTPBasicAuth(api_token, 'unused'))
    print(resp.text)
    return resp.json()


def http_put_payload(url, payload, api_token):
    print("Putting this payload:")
    print(pretty_json(payload))
    print("To this url: " + url)
    if in_cdb_dry_run():
        print("DRY RUN: Put not sent")
    else:
        auth = HTTPBasicAuth(api_token, 'unused')
        headers = json_content_header()
        data = json.dumps(payload)
        response = http_retry().put(url, auth=auth, headers=headers, data=data)
        print(response.text)


def http_post_payload(url, payload, api_token):
    print("Posting this payload:")
    print(pretty_json(payload))
    print("To this url: " + url)
    if in_cdb_dry_run():
        print("DRY RUN: Post not sent")
    else:
        auth = HTTPBasicAuth(api_token, 'unused')
        headers = json_content_header()
        data = json.dumps(payload)
        response = http_retry().post(url, auth=auth, headers=headers, data=data)
        print(response.text)


def json_content_header():
    return {"Content-Type": "application/json"}


def pretty_json(payload):
    return json.dumps(payload, sort_keys=True, indent=4)


def in_cdb_dry_run():
    return os.getenv('CDB_DRY_RUN') == "TRUE"
