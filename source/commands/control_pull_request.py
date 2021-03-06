import json
import requests

from commands import Command
from env_vars import *
from errors import ChangeError
from lib.api_schema import ApiSchema


class ControlPullRequest(Command):

    def doc_summary(self):
        return "Fail the pipeline unless approved pull_request for this commit"
        # Checks the bitbucket pull request associated with this commit.
        # Fails the pipeline if no approved pull request found.

    def doc_volume_mounts(self):
        return ["/var/run/docker.sock:/var/run/docker.sock"]

    def doc_ref(self):
        return {}

    def __call__(self):
        url = ApiSchema.url_for_artifact(self.host.value, self.merkelypipe, self.fingerprint.sha)
        is_compliant, pull_requests = self._get_pull_request_for_current_commit(self.env)
        payload = {
            "evidence_type": self.evidence_type.value,
            "contents": {
                "is_compliant": is_compliant,
                "description": self.description.value,
                "url": self.ci_build_url.value,
                "source": pull_requests,
            }
        }

        def callback(_response):
            if not is_compliant:
                raise ChangeError(f"Artifact with sha {self.fingerprint.sha} is not compliant")
            return 'PUT', url, payload
        return 'PUT', url, payload, callback

    @property
    def description(self):
        return DescriptionEnvVar(self.env)

    @property
    def evidence_type(self):
        return EvidenceTypeEnvVar(self.env)

    @property
    def _merkely_env_var_names(self):
        # Print according to this order
        return [
            'name',
            'fingerprint',
            'ci_build_url',
            'description',
            'evidence_type',
            'owner',
            'pipeline',
            'api_token',
            'host',
            'dry_run'
        ]

    def _print(self, string):
        return self._external.stdout.print(string)

    def _get_pull_request_for_current_commit(self, env):
        workspace = env.get('BITBUCKET_WORKSPACE', None)
        repository = env.get('BITBUCKET_REPO_SLUG', None)
        commit = env.get('BITBUCKET_COMMIT', None)
        user = env.get('BITBUCKET_API_USER', None)
        password = env.get('BITBUCKET_API_TOKEN', None)

        is_compliant, pull_requests = self._get_pull_requests_from_bitbucket_api(
            workspace=workspace, repository=repository, commit=commit,
            username=user, password=password)

        return is_compliant, pull_requests

    def _get_pull_requests_from_bitbucket_api(self, workspace, repository, commit, username, password):
        is_compliant = False
        pull_requests_evidence = []

        url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repository}/commit/{commit}/pullrequests"
        self._print("Getting pull requests from " + url)
        response = requests.get(url, auth=(username, password))
        if response.status_code == 200:
            is_compliant = self._parse_response(commit, password, pull_requests_evidence, response, username)
        elif response.status_code == 202:
            message = "Repository pull requests are still being indexed, please retry."
            raise ChangeError(message)
        elif response.status_code == 404:
            message = " ".join([
                "Repository does not exist or pull requests are not indexed.",
                "Please make sure Pull Request Commit Links app is installed"
            ])
            raise ChangeError(message)
        else:
            message = " ".join([
                "Exception occurred in fetching pull requests.",
                f"Http return code is {response.status_code}"
            ])
            message += f"\n    {response.text}"
            raise ChangeError(message)

        return is_compliant, pull_requests_evidence

    def _parse_response(self, commit, password, pull_requests_evidence, response, username):
        self._print("Pull requests response: " + response.text)
        pull_requests_json = json.loads(response.text)
        pull_requests = pull_requests_json["values"]
        for pr in pull_requests:
            pr_evidence = {}

            pr_html_url = pr['links']['html']['href']
            pr_api_url = pr['links']['self']['href']

            pr_evidence['pullRequestMergeCommit'] = commit
            pr_evidence['pullRequestURL'] = pr_html_url

            pr_evidence = self._get_pull_request_details_from_bitbucket(pr_evidence, pr_api_url, username, password)

            pull_requests_evidence.append(pr_evidence)
        is_compliant = pull_requests_evidence != []
        return is_compliant

    def _get_pull_request_details_from_bitbucket(self, pr_evidence, pr_api_url, username, password):
        response = requests.get(pr_api_url, auth=(username, password))
        if response.status_code == 200:
            pr_json = json.loads(response.text)
            pr_evidence['pullRequestState'] = pr_json['state']
            participants = pr_json['participants']
            approvers = ""
            if len(participants) > 0:
                for participant in participants:
                    if participant['approved']:
                        approvers = approvers + participant['user']['display_name'] + ","
                approvers = approvers[:-1]
                pr_evidence['approvers'] = approvers
            else:
                self._print("No approvers found")
        else:
            self._print("Error occurred in fetching pull request details. Please review repository permissions.")
        return pr_evidence


class DescriptionEnvVar(StaticDefaultedEnvVar):

    def __init__(self, env):
        default = "Bitbucket pull request"
        super().__init__(env, "MERKELY_DESCRIPTION", default)

    def doc_example(self, _ci_name, _command_name):
        return False, ""

    def doc_note(self, _ci_name, _command_name):
        return "Bitbucket pull request."


class EvidenceTypeEnvVar(StaticDefaultedEnvVar):

    def __init__(self, env):
        default = "pull_request"
        super().__init__(env, "MERKELY_EVIDENCE_TYPE", default)

    def doc_example(self, _ci_name, _command_name):
        return False, ""

    def doc_note(self, _ci_name, _command_name):
        return f"The evidence type. Defaults to :code:`{self.default}`"


"""
Notes for future implementation on Github Actions
https://docs.github.com/en/rest/reference/pulls#list-pull-requests
GET /repos/{owner}/{repo}/pulls/{pull_number}/commits
This needs the pull_number. Also, this is limited to 100.
See https://github.com/actions/checkout/issues/58
Uses the env-var $GITHUB_EVENT_PATH
Eg:
    const fs = require('fs')
    const ev = JSON.parse(
      fs.readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8')
    )
    const prNum = ev.pull_request.number 

The information in the file $GITHUB_EVENT_PATH needs to get inside 
the merkely/change container somehow. 
Will also need (username,password)
"""