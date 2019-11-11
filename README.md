# `configure_with_sudo`

## Description

A Python class to handle executing system commands using sudo.

## Usage

Extend `GenericConfigure`, setting, at a minimum, an appropriate `argv` command & argument list.

## Example

The following class will install `pip` system-wide if it isn't already installed:

```Python
from configure_with_sudo import GenericConfigure

class InstallPip(GenericConfigure):

    def __init__(self, user="root", kill_sudo_cred=True):
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
