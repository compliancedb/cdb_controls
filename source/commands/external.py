import json
import os
from errors import ChangeError
from fingerprinters import *


class External:
    """
    Holds (some) external dependencies to make Classic style testing easier.
    """
    def __init__(self,
                 env=None,
                 docker_fingerprinter=None,
                 file_fingerprinter=None,
                 sha256_fingerprinter=None):

        self.__env = env
        self.__docker_fingerprinter = docker_fingerprinter
        self.__file_fingerprinter = file_fingerprinter
        self.__sha256_fingerprinter = sha256_fingerprinter

        if self.__env is None:
            self.__env = os.environ

        if self.__docker_fingerprinter is None:
            self.__docker_fingerprinter = DockerFingerprinter()

        if self.__file_fingerprinter is None:
            self.__file_fingerprinter = FileFingerprinter()

        if self.__sha256_fingerprinter is None:
            self.__sha256_fingerprinter = Sha256Fingerprinter()

    @property
    def merkelypipe(self):
        import os
        if os.path.exists("/Merkelypipe.json"):
            return self.load_json("/Merkelypipe.json")
        if os.path.exists("/data/Merkelypipe.json"):
            return self.load_json("/data/Merkelypipe.json")
        from errors import ChangeError
        raise ChangeError("Merkelypipe.json file not found.")

    @property
    def env(self):
        return self.__env

    def fingerprinter_for(self, string):
        d = self.__docker_fingerprinter
        f = self.__file_fingerprinter
        s = self.__sha256_fingerprinter
        if d.handles_protocol(string):
            return d
        elif f.handles_protocol(string):
            return f
        elif s.handles_protocol(string):
            return s
        else:
            raise ChangeError(f"Unknown protocol: {string}")

    def load_json(self, filename):
        try:
            with open(filename) as file:
                return json.load(file)
        except FileNotFoundError:
            raise ChangeError(f"{filename} file not found.")
        except IsADirectoryError:
            # Note: If you do this...
            # --volume ${MERKELYPIPE}:/Merkelypipe.json
            # And ${MERKELYPIPE} does not exist on the client
            # volume-mount weirdness can happen and you
            # get an empty dir created on the client!
            raise ChangeError(f"{filename} is a directory.")
        except json.decoder.JSONDecodeError as exc:
            raise ChangeError(f"{filename} invalid json - {str(exc)}")