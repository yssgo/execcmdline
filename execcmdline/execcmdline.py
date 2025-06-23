import subprocess
import time
import shutil, shlex
import sys

"""cmd_execute executes cmdline.

cmd_execute executes cmdline
  using subprocess.Popen.

cmd_execute prints each line in blue,
  error msg in red,
  exit status in green
  using ansi escape sequences.

# Example Code

from cmdexecuter import cmd_execute

cmdline = "apt-get install imagemagick"
try:
    cmd_execute(cmdline)
except TypeMismatch as e:
    raise e
except UnknownException as e:
    raise e
"""


class UnknownException(Exception):
    pass


class TypeMismatch(ValueError):
    pass


def cmd_print(*a, **k):
    """cmd_print extends print function.
    cmd_print.
    Description:
        cmd_print exteds built-in print function
           with ansi escape sequences.
        cmd_print uses the same args and kwargs
           as the built-in print function.
        Additional keyword arguments
            out_c, err_c, and reset_c,
            are ANSI escape sequences
            to control colors..

    Keyword args:
        out_c:
           Color code to use if file=sys.stdout.
           Default is "\033[34m".
        err_c:
           Color code to use if file=sys.stderr.
           Default is "\033[34m".
    """
    import sys

    out_c = k.pop("out_c", "\033[34m")
    err_c = k.pop("err_c", "\033[1;91m")
    reset_c = k.pop("reset_c", "\033[0m")
    file = k.pop("file", sys.stdout)
    k["flush"] = False
    k["end"] = ""
    if file == sys.stdout:
        print(f"{out_c}", end="", flush=False)
        print(*a, **k)
        print(f"{reset_c}")
    elif file == sys.stderr:
        print(f"{err_c}", end="", flush=False)
        print(*a, **k)
        print(f"{reset_c}")


def exit_print(*a, **k):
    """exit_print calls cmd_print with out_c="\033[32m"

    For info about the args, use help(cmd_print)

    """
    exit_c = "\033[32m"
    k["out_c"] = exit_c
    cmd_print(*a, **k)


def cmd_execute(cmdline, printer=cmd_print, exitprinter=exit_print):
    """cmd_execute execute cmdline using subprocess.Popen.

    Description:

        cmd_execute prints each line as of standard output
          until the called process terminates.

    Args:

        cmdline:

            command line to execute.
            The type of it can be str, or else  list or tuple.

        printer:

             function(mg, file) to print messages
               to file. `file` is ssys.tdout or sys.stderr.

        exitprinter:

             function(msg, file) to print the exit code of
             the called process.
             `file` is ssys.tdout

    Returns:

        cmd_execute returns process.returncode.

        TypeMismatch exception is raised
            if the type of cmdline is wrong.

        UnknownException is raised
            if any other error occurs.

    """
    if isinstance(cmdline, str):
        args = cmdline
        shell = True
    elif isinstance(cmdline, (list, tuple)):
        args = list(cmdline)
        shell = False
        args[0] = shutil.which(args[0])
    else:
        raise TypeMismatch(
            "Type Mimatch:: The type of cmdline is not one of str, list, tuple."
        )
    try:
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=shell
        )

        while process.poll() is None:
            stdout_output = process.stdout.readline()
            if stdout_output:
                printer(f"{stdout_output.rstrip(chr(10))}", file=sys.stdout)
            time.sleep(0.1)  # Small delay to avoid busy-waiting

        # After process terminates, read any remaining output
        stdout_final, stderr_final = process.communicate()
        if stdout_final:
            printer(f"{stdout_final.strip(chr(10))}", sys.stdout)
        if stderr_final:
            printer(f"{stderr_final.strip(chr(10))}", sys.stderr)

        if exitprinter is not None:
            exitprinter(f"Process exited with code: {process.returncode}")
        return process.returncode

    except Exception as e:
        raise UnknownException(f"An error occurred: {e}")


def execute(
    cmdline,
    accept_=lambda msg: True,
    printer=cmd_print,
    exitprinter=exit_print,
):
    """execute cmdline using cmd_execute

    Args:
        accept_:
            function callback with a `msg` argument.
            `execute` prints msg only if `accept_` returns True.
    """

    def _print(msg, file=sys.stdout):
        if not accept_(msg):
            return
        printer(msg, file=file)

    cmd_execute(cmdline, printer=_print, exitprinter=exitprinter)
