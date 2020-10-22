#!/bin/bash

rocketlogger stop
sleep 1s
# TODO: maybe should do something nicer than killall
killall teroslogger
