from fingerprinters import DockerFingerprinter


class MockDockerFingerprinter(DockerFingerprinter):

    def __init__(self, image_name, digest):
        self._expected = image_name
        self._digest = digest
        self._called = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._called:
            print(exc_type)
            print(exc_val)
            print(exc_tb)
            self._failed(["Expected call did not happen"])

    def sha(self, image_name):
        self._called = True
        if image_name == self._expected:
            return self._digest
        else:
            lines = [
                f"Expected: image_name=={self._expected}",
                f"  Actual: image_name=={image_name}",
            ]
            self._failed(lines)

    def _failed(self, lines):
        message = "\n".join([
            f"{self.__class__.__name__}.sha(image_name)",
            "FAILED",
        ] + lines)
        raise RuntimeError(message)
