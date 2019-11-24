#!/usr/bin/python3

## ######################################################################### ##
## script to start an application or focus the most recently used 
## window of that application
## ######################################################################### ##

## ========================================================================= ##
## import packages
## ========================================================================= ##

from linux_wmctrl_fnlib import *
import argparse

## ========================================================================= ##
## main
## ========================================================================= ##

## read command line arguments:
parser = argparse.ArgumentParser(
  description = "Start an application or focus the most recently used " +
  "window of that application")
parser.add_argument("application_binary", type = str, 
  help = "Command to start the application from the command line")
parser.add_argument("window_name", type = str,
  help = "Name of the window as listed by `wmctrl -lx`. " + 
  "Can be the full name of the window (e.g., 'Msgcompose.Thunderbird' " + 
  "or 'Mail.Thunderbird') to only match specific windows " +
  "of an application, " + 
  "or just the second part of that string to find any window of " + 
  "that application (e.g., 'Thunderbird')")
args = parser.parse_args()

  
