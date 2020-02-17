#!/usr/bin/python3

## ######################################################################### ##
## script to close a window and focus the next available window
## ######################################################################### ##

## ========================================================================= ##
## import packages
## ========================================================================= ##

from linux_wmctrl_fnlib import *

## ========================================================================= ##
## main
## ========================================================================= ##

if __name__ == "__main__":
    ## get active window:
    win_id = get_active_window_id()

    ## get active windows, sorted by recent activity:
    dat_wmctrl = get_active_windows(sort=True)

    ## get application type of active window id:
    active_application = dat_wmctrl[dat_wmctrl["win_id"] == win_id][
        "application"
    ].values[0]

    ## close active window:
    subprocess.run(["/usr/bin/wmctrl", "-c", ":ACTIVE:"])

    ## remove active application from window list:
    dat_wmctrl = dat_wmctrl[dat_wmctrl["win_id"] != win_id]

    ## find next remaining instance of active application:
    dat_wmctrl_active = dat_wmctrl[dat_wmctrl["application"] == active_application]

    ## if there is one, focus it (e.g., wmctrl -i -a 0x00200007):
    if dat_wmctrl_active.shape[0] > 0:
        next_window = dat_wmctrl_active[0:1]["win_id"].values[0]
        outp_byte = subprocess.run(["wmctrl", "-i", "-a", next_window])
