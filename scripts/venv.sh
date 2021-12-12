#!/bin/sh

quit(){
    if [ $# -gt 1 ];
    then
        echo "$1"
        shift
    fi
    exit $1
}

if [ -f ~/.dotfiles/virtualenvwrapper/virtualenvwrapper.rc ];
then
    . ~/.dotfiles/virtualenvwrapper/virtualenvwrapper.rc
fi

mkvirtualenv -r ./dev-reqs.txt "configure_with_sudo" || quit "Unable to make virtual environment." 1
