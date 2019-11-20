#!/usr/bin/python3

## ######################################################################### ##
## script to close a window and focus the next available window
## ######################################################################### ##

## ========================================================================= ##
## import packages
## ========================================================================= ##

import subprocess
import re
import pandas as pd
from io import StringIO
import warnings

## ========================================================================= ##
## function definitions
## ========================================================================= ##

def get_client_stacking():
  """
  Get client stacking, i.e., last active windows
  
  Returns a list of the windows in the order that they were last actively used.
  Returns None if the client stacking list was not found.
  Uses `xprop` under the hood.
  
  Parameters: None.
  
  Returns:
  list of strings: window ids in the order they were last active.
  """
  outp_byte = subprocess.check_output(["xprop", "-root"]) #|grep "^_NET_CLIENT_LIST_STACKING""])
  outp_str = outp_byte.decode("utf-8")
  outp_clientstack = re.search(r"_NET_CLIENT_LIST_STACKING.+?# (.+?)\n", outp_str)
  if outp_clientstack:
    ret = outp_clientstack.group(1).split(", ")
    ## add leading zero to conform to wmctrl output (8-digit hex):
    ret = [re.sub(r"0x", "0x0", i) for i in ret]
  else:
    warnings.warn("Client stacking not found in output from `xprop`.")
    ret = None
  return(ret)


def get_active_window_id():
  """
  Get ID of active window
  
  Uses `xprop` command line tools to get the ID of the currently active window in KDE. 
  
  Paramters: None.
  
  Returns: 
  string: hexadeximal ID of currently active window, with 8 digits (e.g., '0x0220000a')
  """
  ## get active window ID via xprop and convert to utf-8:
  win_id_byte = subprocess.check_output(["/usr/bin/xprop", "-root", "_NET_ACTIVE_WINDOW"])
  win_id_str = win_id_byte.decode("utf-8")
  
  ## extract active window ID from results string:
  win_id = win_id_str
  win_id = re.sub(r"^.*?: window id # ", "", win_id)
  win_id = re.sub(r"\n", "", win_id)
  
  ## add leading zero to conform to wmctrl output (8-digit hex):
  win_id = re.sub(r"0x", "0x0", win_id)
  return(win_id)


def get_wmctrl_data():
  """
  Gets currently open windows
  
  Uses the `wmctrl` command line tool (with the `-lx` option) to list all 
  currently open windows (IDs, names and some other data).
  note: function returns pandas dataframe without an index without any 
  information (index only contains only an enumeration).
  
  Parameters: None.
  
  Returns:
  pandas dataframe: One row per currently open application window, with the
    following columns: 
    ['win_id', 'win_status', 'win_type', 'win_os', 'win_name']
  """
  ## get window wmctrl output and convert to utf-8:
  wmctrl_byte = subprocess.check_output(["/usr/bin/wmctrl", "-lx"])
  wmctrl_str = wmctrl_byte.decode("utf-8")
  
  ## replace column seps by an actual colum sepr where appropriate:
  wmctrl_csv_str = re.sub(
    pattern = r"([0-9a-fx]+?)[ \t]+([-0-9]+)[ \t]+([^ \t]+?)[ \t]+?([^ \t]+?)[ \t]+?([^\n]*)", 
    #repl = r"\1, \2, \3, \4, \5", 
    repl = r"\1\t\2\t\3\t\4\t\5", 
    string = wmctrl_str)
  
  ## parse results into pandas dataframe and return it:
  dat_wmctrl = pd.read_csv(
    StringIO(wmctrl_csv_str), 
    sep = "\t", header = None, 
    names = ["win_id", "win_status", "win_type", "win_os", "win_name"],
    index_col = False)
  return(dat_wmctrl)


## ========================================================================= ##
## main
## ========================================================================= ##

## get active window:
win_id = get_active_window_id()

## get wmctrl data:
dat_wmctrl = get_wmctrl_data()

## get application type of active window id:
win_type = dat_wmctrl[dat_wmctrl["win_id"] == win_id]["win_type"].values[0]

## get client stacking:
## as series? or keep as list?
client_stack = get_client_stacking()

## create data frame with client stack rank:
dat_client_stack = pd.DataFrame(
  data = {'win_id': client_stack, 
          'active_rank': reversed(range(len(client_stack)))})

## join to wmctrl data:
dat_wmctrl = pd.merge(dat_wmctrl, dat_client_stack, left_on = "win_id", right_on = "win_id")

## sort by active rank:
dat_wmctrl = dat_wmctrl.sort_values(by = ['active_rank'])

## close active window:
subprocess.run(["/usr/bin/wmctrl", "-c", ":ACTIVE:"])

## remove active application from this list:
dat_wmctrl = dat_wmctrl[dat_wmctrl["win_id"] != win_id]

## find next remaining instance of active application:
dat_wmctrl_active = dat_wmctrl[dat_wmctrl["win_type"] == win_type]

## if there is one, focus it (e.g., wmctrl -i -a 0x00200007):
if dat_wmctrl_active.shape[0] > 0:
  next_window = dat_wmctrl_active[0:1]["win_id"].values[0]
  outp_byte = subprocess.run(["wmctrl", "-i", "-a", next_window])
  

  
