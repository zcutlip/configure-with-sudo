from __future__ import print_function
import os
import subprocess


DEFAULT_SUDO_PATH = os.path.join(os.sep, "usr", "bin", "sudo")


class ConfigureUsingExec(object):
    def __init__(self, argv):

        self.argv = argv

    def go(self, argv=[], return_output=False, encoding="utf-8"):
        runstring = ""
        if not argv or len(argv) == 0:
            argv = self.argv

        for arg in argv:
            runstring += "%s " % arg
        print("about to run: %s" % runstring)
        output = None

        try:
            if return_output:
                output = subprocess.check_output(argv)
                if output:
                    output = [line.decode(encoding) for line in output.splitlines()]
            else:
                subprocess.check_call(argv)

        except Exception as e:
            print("Failed to run command: %s" % runstring)
            print(str(e))
            raise
        return output

    def __str__(self):
        runstring = ""
        if not self.argv:
            runstring = "[no command]"
        else:
            for arg in self.argv:
                runstring += "{} ".format(arg)
        runstring.rstrip()
        return runstring


class ConfigureUsingSudo(ConfigureUsingExec):
    def __init__(self, argv, kill_sudo_cred=True, sudo_user="root", sudo_path=DEFAULT_SUDO_PATH):
        super(ConfigureUsingSudo, self).__init__(argv)
        self.kill_sudo_cred = kill_sudo_cred
        self.sudo_user = sudo_user
        self.sudo_path = sudo_path

    def sudo_kill(self):
        print("Killing sudo credential.")
        subprocess.check_call([self.sudo_path, "-K"])

    def sudo(self, return_output=False, sudo_set_home=False, encoding="utf-8"):
        sudo_argv = [self.sudo_path]
        out = None
        if sudo_set_home:
            sudo_argv += ["-H"]

        if not self.sudo_user == "root":
            sudo_argv += ["-u", self.sudo_user]
        sudo_argv += self.argv

        try:
            out = self.go(sudo_argv, return_output=return_output, encoding=encoding)
        except Exception:
            if self.kill_sudo_cred:
                self.sudo_kill()
            raise

        if self.kill_sudo_cred:
            self.sudo_kill()
        return out


class GenericConfigure(ConfigureUsingSudo):
    def __init__(self, argv, use_sudo=False, kill_sudo_cred=True, sudo_user="root", sudo_set_home=False, sudo_path=DEFAULT_SUDO_PATH):
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
        super(GenericConfigure, self).__init__(
            argv, kill_sudo_cred=kill_sudo_cred, sudo_user=sudo_user, sudo_path=sudo_path)
        self.configured = False
        self.use_sudo = use_sudo
        self.sudo_set_home = sudo_set_home

    def execute(self, use_sudo=None, return_output=False, set_configured=True, sudo_set_home=None, encoding="utf-8"):
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
                out = self.sudo(return_output=return_output,
                                sudo_set_home=sudo_set_home, encoding=encoding)
            else:
                out = self.go(return_output=return_output, encoding=encoding)
        if set_configured:
            self.configured = True
        return out
