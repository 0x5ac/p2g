#! /bin/bash
exec sed -e "s/\x1b\[[0-9;]*m//g" $*
