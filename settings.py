## MassCTRL settings file. 
## User defined values

# Location of group files
groupfiles = './groups/'

# Location of recipe files
recipefiles = './recipes/'

# Location of master log file
masterlogfile = './MassCTRL.log'

# Location (directory) of client log files
clientloglocation = './client_logs/'

# Location of key file
keyfile = '/home/humanizer/MassCTRL/keys.dat'

#Cipher key file
cipfile ='/home/humanizer/MassCTRL/cip.dat'

# Use a master account for all client connections
master_account = False

# Print clients name headliner before operation output
client_headline = True

# Prints output of executed command
exec_output = True

# Print executing command
command_output = True

# Print return code of executed command
return_code_output = True

# Use hostname instead of ip-address when connecting to client
use_hostname = True

# Use a master account for all client connections
master_account = False

# Accept missing host key when connecting to client
missing_host_key_accept = True

# Delimiter for executing command syntax
command_delimiter = '^'

# Client status ticker intervall between updates 
ticker_intervall = 10

# Write output to one log file
write_master_log = True

# Write to individual log files per client
write_client_log = True

# Renames recieved files with destination hostname in the beginnig of filename
# Must be True on multi host operations
get_file_rename = True
