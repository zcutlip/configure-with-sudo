import logging
import os
import shlex
import subprocess

DEFAULT_SUDO_PATH = os.path.join(os.sep, "usr", "bin", "sudo")


class ConfigureUsingExec:
    def __init__(self, argv, logger=None):
        if not logger:
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger()
        self.logger = logger
        self.argv = argv

    def wait(self, encoding: str = "utf-8") -> tuple[int, str, str]:
        ret: int = None
        output: bytes = None
        err_output: bytes = None
        self.logger.debug("Waiting for job.")

        if self.process:
            ret = self.process.wait()
            output, err_output = self.process.communicate()
            output = output.decode(encoding)
            err_output = err_output.decode(encoding)
        else:
            self.logger.debug("No process to wait for")

        return (ret, output, err_output)

    def go(self,
           argv: list[str] = None,
           capture_out: bool = False,
           capture_err: bool = False,
           err_to_out: bool = False,
           dry_run: bool = True,
           wait: bool = False,
           encoding: str = "utf-8"
           ) -> tuple[int | None, str | None, str | None]:
        if not argv:
            argv = self.argv
        ret = None
        output = None
        err_out = None
        out_cap: int = None
        err_cap = None
        if capture_out:
            out_cap = subprocess.PIPE
        if err_to_out:
            err_cap = subprocess.STDOUT
        if capture_err and not err_to_out:
            err_cap = subprocess.PIPE

        self.logger.debug(f"Running: [{self.runstring(argv=argv)}]")

        if dry_run:
            self.logger.info("Dry run. Not running command")
            self.process = None
        else:
            self.process = subprocess.Popen(
                argv, stdout=out_cap, stderr=err_cap, bufsize=0
            )
            if wait:
                ret, output, err_out = self.wait()

        return (ret, output, err_out)

    def output_lines(self, output: str | bytes, encoding: str = "utf-8") -> list[str]:
        output_lines = []
        if output is not None:
            if isinstance(output, bytes):
                output = output.decode(encoding)
            _lines = output.splitlines()
            for line in _lines:
                line = line.rstrip()
                output_lines.append(line)
        return output_lines

    def go_wait(self, argv=None, return_output=False, encoding="utf-8"):
        ret, stdout, stderr = self.go(argv=argv,
                                      capture_out=return_output,
                                      capture_err=False,
                                      err_to_out=False,
                                      dry_run=False,
                                      wait=True,
                                      encoding=encoding)
        if ret != 0:
            print(stdout)
            print(stderr)
            # emulate subprocess.check_output()/check_call() like we used to call
            raise subprocess.CalledProcessError(
                ret, self.process.args, output=stdout, stderr=stderr)

        output_lines = self.output_lines(stdout)
        return output_lines

    def runstring(self, argv=None):
        runstring = ""
        if not argv:
            argv = self.argv
        if argv:
            argv = [shlex.quote(arg) for arg in argv]
            runstring = " ".join(argv)
            runstring = runstring.rstrip()
        return runstring

    def __str__(self):
        runstring = self.runstring()
        if not runstring:
            runstring = self.TITLE
        return runstring


class ConfigureUsingSudo(ConfigureUsingExec):
    def __init__(
        self,
        argv,
        logger=None,
        kill_sudo_cred=True,
        sudo_user="root",
        sudo_path=DEFAULT_SUDO_PATH,
    ):
        super().__init__(argv, logger=logger)
        self.kill_sudo_cred = kill_sudo_cred
        self.sudo_user = sudo_user
        self.sudo_path = sudo_path

    def sudo_kill(self):
        self.logger.info("Killing sudo credential.")
        subprocess.check_call([self.sudo_path, "-K"])

    def sudo_argv(self, sudo_set_home=False):
        sudo_argv = [self.sudo_path]

        if sudo_set_home:
            sudo_argv += ["-H"]

        if not self.sudo_user == "root":
            sudo_argv += ["-u", self.sudo_user]
        sudo_argv += self.argv
        return sudo_argv

    def sudo(self, return_output=False, sudo_set_home=False, encoding="utf-8"):
        sudo_argv = self.sudo_argv(sudo_set_home=sudo_set_home)
        out = None
        try:
            out = self.go_wait(sudo_argv, return_output=return_output,
                               encoding=encoding)
        except Exception:
            if self.kill_sudo_cred:
                self.sudo_kill()
            raise

        if self.kill_sudo_cred:
            self.sudo_kill()
        return out


class GenericConfigure(ConfigureUsingSudo):
    def __init__(
        self,
        argv,
        logger=None,
        use_sudo=False,
        kill_sudo_cred=True,
        sudo_user="root",
        sudo_set_home=False,
        sudo_path=DEFAULT_SUDO_PATH,
    ):
        """
        A generic system configuration object that optionally uses sudo.
        The configured command is not executed until the 'execute()' method is called.

        Params:
        - argv: System configuration command/argument list that will be passed to subprocess
        - use_sudo: Whether to use 'sudo' to execute the command. If false, the command is run
                    as the current user. Defaults to False.
        - kill_sudo_cred: Optionally kill the sudo credential using 'sudo -k' immediately afterwards
        - sudo_user: Optional name of the user to sudo to using 'sudo -u <user>'. Defaults to 'root'
        - sudo_set_home: Optionally set the HOME variable to the sudo user's home directory using 'sudo -H'
        - sudo_path: Optional path to 'sudo'. Defaults to /usr/bin/sudo

        """
        super().__init__(
            argv,
            logger=logger,
            kill_sudo_cred=kill_sudo_cred,
            sudo_user=sudo_user,
            sudo_path=sudo_path,
        )
        self.configured = False
        self.use_sudo = use_sudo
        self.sudo_set_home = sudo_set_home

    def execute(
        self,
        use_sudo=None,
        return_output=False,
        set_configured=True,
        sudo_set_home=None,
        encoding="utf-8",
    ):
        """
        Execute self.argv, optionally using sudo

        Params:
        - use_sudo: Override object's 'use_sudo' flag.
        - return_output: Whether to execute the command using subprocess.check_output(), returning its output
                         or to use subprocess.check_call(), and return no output.
        - set_configured: Whether to mark this object as if the command executes without raising an exception
                          Objects marked configured can safely have 'execute()' called and will not run.
        - sudo_set_home: Override object's 'sudo_set_home' flag.
        - encoding: Optional unicode encoding to apply when decoding output. Defaults to "utf-8"

        Returns:
        - A list of output strings split on line breaks, or None if return_output=False

        Raises:
        - Any exeptions raised by subprocess.check_output() or subprocess.check_call()
        """

        out = None
        if not self.configured:
            if sudo_set_home is None:
                sudo_set_home = self.sudo_set_home

            if use_sudo is None:
                use_sudo = self.use_sudo
            if use_sudo:
                out = self.sudo(
                    return_output=return_output,
                    sudo_set_home=sudo_set_home,
                    encoding=encoding,
                )
            else:
                out = self.go_wait(
                    return_output=return_output, encoding=encoding)
        if set_configured:
            self.configured = True
        return out

    def __str__(self):
        if self.use_sudo:
            argv = self.sudo_argv(sudo_set_home=self.sudo_set_home)
        else:
            argv = self.argv
        runstring = self.runstring(argv=argv)
        return runstring
