from commands import CommandError
from env_vars import RequiredEnvVar

FILE_PROTOCOL = 'file://'
DOCKER_PROTOCOL = 'docker://'
SHA256_PROTOCOL = 'sha256://'

DESCRIPTION = "\n".join([
    '1. If prefixed by docker:// the name+tag of the docker image to fingerprint.',
    '   The docker socket must be volume-mounted.',
    '   Example:',
    '   docker run ... \\',
    '     --env MERKELY_FINGERPRINT=”docker://${YOUR_DOCKER_IMAGE_AND_TAG}" \\',
    '     --volume /var/run/docker.sock:/var/run/docker.sock \\',
    '     ...',
    '',
    '2. If prefixed by file:// the full path of the file to fingerprint.',
    '   The full path must be volume-mounted.',
    '   Example:',
    '   docker run ... \\',
    '     --env MERKELY_FINGERPRINT=”file://${YOUR_FILE_PATH} \\',
    '     --volume=${YOUR_FILE_PATH}:${YOUR_FILE_PATH} \\',
    '     ...',
    '',
    "3. If prefixed by sha256:// the artifact's sha256, then /, then it's name."
    '   Example:',
    '   docker run ... \\',
    '     --env MERKELY_FINGERPRINT=”sha256://${YOUR_ARTIFACT_SHA256}/${YOUR_ARTIFACT_NAME}” \\',
    '     ...',
])


class FingerprintEnvVar(RequiredEnvVar):

    def __init__(self, command):
        super().__init__(command.env, "MERKELY_FINGERPRINT", DESCRIPTION)
        self._command = command

    @property
    def protocol(self):
        if self.value.startswith(FILE_PROTOCOL):
            return FILE_PROTOCOL
        elif self.value.startswith(DOCKER_PROTOCOL):
            return DOCKER_PROTOCOL
        elif self.value.startswith(SHA256_PROTOCOL):
            return SHA256_PROTOCOL
        else:
            raise self.unknown_protocol_error()

    @property
    def sha(self):
        if self.protocol == FILE_PROTOCOL:
            return self._command.file_fingerprinter(self.protocol, self.artifact_name)
        elif self.protocol == DOCKER_PROTOCOL:
            return self._command.docker_fingerprinter(self.protocol, self.artifact_name)
        elif self.protocol == SHA256_PROTOCOL:
            start = len(self.protocol)
            return self.value[start:start+64]
        else:
            raise self.unknown_protocol_error()

    @property
    def artifact_name(self):
        if self.protocol == FILE_PROTOCOL:
            return self._after(len(self.protocol))
        elif self.protocol == DOCKER_PROTOCOL:
            return self._after(len(self.protocol))
        elif self.protocol == SHA256_PROTOCOL:
            return self._after(len(self.protocol)+64+len('/'))

    def _after(self, n):
        return self.value[-(len(self.value)-n):]

    def unknown_protocol_error(self):
        return CommandError(f"Unknown protocol: {self.value}")