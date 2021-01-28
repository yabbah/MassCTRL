## MassCTRL settings file. 
## User defined values

# Location of group files
groupfiles = './groups/'

# Location of recipe files
recipefiles = './recipes/'

# Location (directory) of client log files
clientloglocation = './client_logs/'

# Location of master log file
masterlogfile = './MassCTRL.log'

# Location of error log file
errorlogfile = './MassCTRL_error.log'

# Location of key file
keyfile = '/home/USER/MassCTRL/keys.dat'

# Specify location of private key if not in default path
private_key = '/home/USER/.ssh/id_rsa'

# Enable this if you have an envoirment with a working 
# passwordless ssh-keys solution
private_key_login = False

# Accept missing host key when connecting to client
missing_host_key_accept = True

# Use a master account for all client connections
master_account = False

# Print clients name headliner before operation output to terminal
client_headline = True

# Prints and logs output of executed command
exec_output = True

# Print and log executing command
command_output = True

# Print and log return code of executed command
return_code_output = True

# Use hostname instead of ip-address when connecting to 
# client
use_hostname = True

# Delimiter if needed in recipes 
# for executing command syntax
command_delimiter = '^'

# Client status ticker intervall between updates 
ticker_intervall = 10

# Write output to one log file
write_master_log = True

# Write to individual log files per client
write_client_log = True

# Separate error log file where only errors will be written
write_error_log = True

# Renames recieved files with destination hostname in 
# the beginnig of filename
# Must be True on multi host operations. Otherwise 
# files will be overwritten
get_file_rename = True



