from commands import Context, build_command, CommandError
import sys

def run(env=None, docker_fingerprinter=None, file_fingerprinter=None):
    try:
        context = Context(env, docker_fingerprinter, file_fingerprinter)
        command = build_command(context)
        print(f"MERKELY_COMMAND={command.name.value}")
        command.check()
        return command()
    except CommandError as exc:
        print(f"Error: {str(exc)}")
        sys.exit(144)


