#!/bin/bash

# remote='Kelvin@10.0.1.14:/home/code/cpp'
remote='/Volumes/home/code/'
local='/Users/tomoaki/Dropbox/code/python_micropython'
rsync --update -vr --exclude "CMakeF*" --exclude "main" --exclude "*.vtu" --exclude "*.vtp" --exclude "*.mov" --exclude "*.mp4" --exclude ".git*" --exclude "*.key" ${local} ${remote}