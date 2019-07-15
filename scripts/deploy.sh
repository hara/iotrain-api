#!/bin/sh

git archive --format=tar origin/master | gzip -9c | ssh $1 "tar --directory=/home/pi/src/github.com/hara/halalabs.iotrain -xvzf -"
