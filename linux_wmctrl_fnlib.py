## ######################################################################### ##
## function library to work with windows in linux
## (KDE mainly, but other window managers should work as well)
## ######################################################################### ##

## ========================================================================= ##
## import packages
## ========================================================================= ##

import subprocess
import re
import pandas as pd
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
  pandas dataframe: One row per currently open application window, 
    with the following columns: 
    ['win_id', 'win_status', 'win_type', 'win_os', 'win_name', 
    'application']
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
  TYPEDICT_WMCTRL = {
    "win_id": str,
    "win_status": int,
    "win_type": str,
    "win_os": str,
    "win_name": str
  }
  ## without StringIO (takes ages to import):
  dat_wmctrl = pd.DataFrame([x.split('\t') for x in wmctrl_csv_str.split('\n')])
  dat_wmctrl.columns = ["win_id", "win_status", "win_type", "win_os", "win_name"]
  dat_wmctrl = dat_wmctrl.dropna()
  dat_wmctrl = dat_wmctrl.astype(TYPEDICT_WMCTRL)
  dat_wmctrl = dat_wmctrl.astype(TYPEDICT_WMCTRL)
  ## still not equal: dat_cmtrl.equals(df): nan vs. N/A

  # dat_wmctrl = pd.read_csv(
  #   StringIO(wmctrl_csv_str), 
  #   sep = "\t", header = None, 
  #   names = ["win_id", "win_status", "win_type", "win_os", "win_name"],
  #   index_col = False)
  
  ## add application (derived from win_type):
  dat_wmctrl["application"] = [i[1] for i in dat_wmctrl["win_type"].str.split(".")]
  return(dat_wmctrl)


def get_active_windows(sort = True):
  """
  Gets currently open windows including a ranking of when they were last active
  
  Uses the `wmctrl` command line tool (with the `-lx` option) to list all 
  currently open windows (IDs, names and some other data), and also the 
  ranking of when those windows were last active (as obtained via `xprop`).
  See also get_client_stacking() function.
  note: function returns pandas dataframe without an index without any 
  information (index only contains only an enumeration).
  
  Parameters:
  boolean sort: whether or not the active window list (DataFrame) should
    be sorted by the activity ranking (most recently active windows on top)
  
  Returns:
  pandas dataframe: One row per currently open application window, with the
    following columns: 
    ['win_id', 'win_status', 'win_type', 'win_os', 'win_name', 'active_rank']
  """
  ## get wmctrl data:
  dat_wmctrl = get_wmctrl_data()
  ## get client stacking:
  client_stack = get_client_stacking()
  ## create data frame with client stack rank:
  dat_client_stack = pd.DataFrame(
    data = {'win_id': client_stack, 
            'active_rank': reversed(range(len(client_stack)))})
  ## join to wmctrl data:
  dat_wmctrl = pd.merge(dat_wmctrl, dat_client_stack, left_on = "win_id", right_on = "win_id")
  ## sort by active rank, if needed:
  if sort == True:
    dat_wmctrl = dat_wmctrl.sort_values(by = ['active_rank'])
  return(dat_wmctrl)
