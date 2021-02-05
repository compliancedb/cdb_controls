import os
from commands import Command, CommandError
from cdb.api_schema import ApiSchema
from cdb.http import http_put_payload


class LogArtifactCommand(Command):
    """
    Command subclass for handling MERKELY_COMMAND=log_artifact
    """
    @property
    def args_list(self):
        return [
            self.api_token,
            self.artifact_git_commit,
            self.artifact_git_url,
            self.ci_build_number,
            self.ci_build_url,
            self.display_name,
            self.is_compliant,
            self.fingerprint,
            self.host
        ]

    @property
    def artifact_git_commit(self):
        description = "The sha of the git commit that produced this build"
        return self._required_env_var('ARTIFACT_GIT_COMMIT', description)

    @property
    def artifact_git_url(self):
        description = "Link to the source git commit this build was based on"
        return self._required_env_var('ARTIFACT_GIT_URL', description)

    @property
    def ci_build_number(self):
        description = "The ci build number"
        return self._required_env_var('CI_BUILD_NUMBER', description)

    @property
    def ci_build_url(self):
        description = "Link to the build in the ci system"
        return self._required_env_var('CI_BUILD_URL', description)

    @property
    def display_name(self):
        description = ""
        return self._optional_env_var("DISPLAY_NAME", description)

    @property
    def is_compliant(self):
        description = "Whether this artifact is considered compliant from you build process"
        return self._required_env_var('IS_COMPLIANT', description)

    @property
    def fingerprint(self):
        description = ""
        return self._required_env_var("FINGERPRINT", description)

    def execute(self):
        file_protocol = "file://"
        docker_protocol = "docker://"
        sha_protocol = "sha256://"
        fp = self.fingerprint.value
        if fp.startswith(file_protocol):
            artifact_name = fp[len(file_protocol):]
            return self._log_artifact_file(file_protocol, artifact_name)
        elif fp.startswith(docker_protocol):
            artifact_name = fp[len(docker_protocol):]
            return self._log_artifact_docker_image(docker_protocol, artifact_name)
        elif fp.startswith(sha_protocol):
            sha256 = fp[len(sha_protocol):]
            return self._log_artifact_sha(sha256)
        else:
            raise CommandError(f"{self.fingerprint.name} has unknown protocol {fp}")

    def _log_artifact_file(self, protocol, filename):
        print(f"Getting SHA for {protocol} artifact: {filename}")
        sha256 = self._context.sha_digest_for_file('/'+filename)
        print(f"Calculated digest: {sha256}")
        self._print_compliance()
        return self._create_artifact(sha256, os.path.basename(filename))

    def _log_artifact_docker_image(self, protocol, image_name):
        print(f"Getting SHA for {protocol} artifact: {image_name}")
        sha256 = self._context.sha_digest_for_docker_image(image_name)
        print(f"Calculated digest: {sha256}")
        self._print_compliance()
        return self._create_artifact(sha256, image_name)

    def _log_artifact_sha(self, sha256):
        self._print_compliance()
        return self._create_artifact(sha256, self.display_name.value)

    def _create_artifact(self, sha256, display_name):
        description = f"Created by build {self.ci_build_number.value}"
        payload = {
            "sha256": sha256,
            "filename": display_name,
            "description": description,
            "git_commit": self.artifact_git_commit.value,
            "commit_url": self.artifact_git_url.value,
            "build_url": self.ci_build_url.value,
            "is_compliant": self.is_compliant.value == 'TRUE'
        }
        url = ApiSchema.url_for_artifacts(self.host.value, self.merkelypipe)
        http_put_payload(url, payload, self.api_token.value)
        return 'Putting', url, payload

    def _print_compliance(self):
        env_var = self.is_compliant
        print(f"{env_var.name}: {env_var.value == 'TRUE'}")
