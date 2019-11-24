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
import sys

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

## debug:
# args = parser.parse_args(["thunderbird", "Mail.Thunderbird"])
# print(args.application_binary)
# print(args.window_name)

## check of window_name is a window type or an application:
dot_position = args.window_name.find(".")

## extract window type and application:
if dot_position == -1:
  win_type = None
  application = args.window_name
else:
  win_type = args.window_name
  application = args.window_name[(dot_position + 1):]

## get active windows, sorted by recent activity:
dat_wmctrl = get_active_windows(sort = True)

## check if specific window type is already open:
dat_wmctrl_active = dat_wmctrl[(dat_wmctrl["win_type"] == win_type)]

## if so, focus that window and exit:
if dat_wmctrl_active.shape[0] > 0:
  next_window = dat_wmctrl_active[0:1]["win_id"].values[0]
  outp_byte = subprocess.run(["wmctrl", "-i", "-a", next_window])
  sys.exit()

## check if another window of that application is already open:
dat_wmctrl_active = dat_wmctrl[dat_wmctrl["application"] == application]

## if so, focus that window and exit:
if dat_wmctrl_active.shape[0] > 0:
  next_window = dat_wmctrl_active[0:1]["win_id"].values[0]
  outp_byte = subprocess.run(["wmctrl", "-i", "-a", next_window])
  sys.exit()

## if not, run application binary to start a new instance:
subprocess.run([args.application_binary])

