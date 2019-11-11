# `configure_with_sudo`

## Description

A Python module to handle executing system commands using sudo.

## Usage

Extend `GenericConfigure`, setting at a minimum an appropriate `argv` command & argument list.

## Example

The following class will check if `pip` is installed and, if not, install it system-wide using `sudo easy_install pip`:

```Python
from configure_with_sudo import GenericConfigure

class InstallPip(GenericConfigure):

    def __init__(self, kill_sudo_cred=True):
        # Initial argv is simply to check if 'pip' is installed
        argv = ["/usr/local/bin/pip", "-V"]
        super(InstallPip, self).__init__(
            argv, use_sudo=True, kill_sudo_cred=kill_sudo_cred)

        try:
            # Execute to check if pip is already installed
            # if it is, self.configured will be set to True
            # and subsequent calls to execute() will do nothing
            self.execute(use_sudo=False)

        except Exception:
            # If pip -V failed, assume pip is not installed.
            # Replace self.argv with the installation command.
            self.argv = ["/usr/bin/easy_install", "pip"]

pip_installer = InstallPip()
pip_installer.execute()
```

The following example will capture the output of `sudo ls -l /private/var/root`, and print it line-by-line:

```Python
class DirectoryLister(GenericConfigure):

    def __init__(self, path):
        argv = ["ls", "-l", path]
        super().__init__(argv, use_sudo=True)

path = "/private/var/root"
lister = DirectoryLister(path)
output = lister.execute(return_output=True)

for line in output:
    print(line)
```
