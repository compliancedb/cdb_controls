from env_vars import DefaultedEnvVar

NOTES = "\n".join([
    "The sha of the git commit that produced this build.",
    #"On Github, defaults to ${GITHUB_SHA}.",
    #"On BitBucket, defaults to ${BITBUCKET_COMMIT}."
])

DEFAULTS = {
    'bitbucket': 'BITBUCKET_COMMIT',
    'github': 'GITHUB_SHA',
}

class ArtifactGitCommitEnvVar(DefaultedEnvVar):

    def __init__(self, env):
        super().__init__(env, "ARTIFACT_GIT_COMMIT", '')

    def notes(self, ci):
        def bash(s):
            return "${"+s+"}"
        #return f"{note}. Defaults to {bash(DEFAULTS[ci])}."
        return NOTES

    @property
    def is_required(self):
        return True  # To keep Docs the same for now

    @property
    def value(self):
        if self.is_set:
            return self.string
        bit_bucket = self._get(name="BITBUCKET_COMMIT", default=None)
        if bit_bucket is not None:
            return bit_bucket
        github = self._get(name="GITHUB_SHA", default=None)
        if github is not None:
            return github
        # Error if both are set
