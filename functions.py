from settings import *
from datetime import datetime
from blessed import Terminal
import os
import subprocess
import spur
import socket
import curses
import sys
import time
import shutil


# https://blessed.readthedocs.io/en/latest/colors.html
col = Terminal()


return_code = {
	'0': 'Success',
	'1': 'Catchall for general errors',
	'2': 'Misuse of shell builtins',
	'126': 'Command invoked cannot execute',
	'127': 'Command not found',
	'128': 'Invalid argument to exit',
}


def TimeDate():
	dateandtime = datetime.now()
	date_time = dateandtime.strftime('%Y-%m-%d %H:%M:%S')
	
	return str(date_time)


# Write log message to specified log file
def WriteMasterLog(logmessage):
	try:
		with open(masterlogfile, 'a+') as log:
			log.write(TimeDate() + ': ' + str(logmessage) + '\n')
	except:
		print(col.red1 + 'Error: Cant write to log' + col.normal)


# Write log message to specified log file
def WriteClientLog(client, logmessage):
	try:
		with open(clientloglocation + client + '.log', 'a+') as log:
			log.write(TimeDate() + ': ' + str(logmessage) + '\n')
	except:
		print(col.red1 + 'Error: Cant write to log' + col.normal)


## Clear screen
def ClearScreen():
	curses.setupterm() 
	clear = str(curses.tigetstr('clear'), 'ascii') 
	sys.stdout.write(clear) 


## Check client response on ssh port
def CheckClient(address):
	client_response = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_response.settimeout(0.5)
	host = address
	address = (address, 22)
	try:
		result = client_response.connect_ex(address)
	
		if result == 0:
		
			return True
	
		else:
		
			return False
	
	except:
		print(col.red1 + 'Error: Cant do host lookup @' + str(host) + '. No entry in hosts file?' + col.normal)

def ClientStatus(group):
	clients = GetClients(group)
	ClearScreen()
	print('')
	print(format(col.bold_white('Client'), '44'), col.bold_white('Status'))
	print (col.bold_snow4('-') * 36)
	for client in clients:
		if CheckClient(client) == True:
			print(format(col.yellow1(client), '52'), col.green2('Online'))
		else:
			print(format(col.yellow1(client), '52'), col.blink_red1('Offline'))
	print ('')


def ClientStatusTicker(group):
	while True:
		ClientStatus(group)
		time.sleep(ticker_intervall)

    
## Collect Files
def CollectFiles(path):
	files = []
	
	if os.path.isdir(path):
		for r, d, f in os.walk(path):
			for file in f:
				files.append(os.path.join(r, file))

		return files
	
	else:
		print(col.red1('Error: Cant collect groups and recipes from specified directory'))
	

## String cleanup
def CleanString(string):
	string = string.replace("\\n'", '').replace('b\'', '')
	string = string.strip()
	
	return string


## Read group and recipe files
def ReadFile(file):
	content = []
	
	try:
		with open(file) as file:
			for row in file:
				content.append(CleanString(row))

		return content
	
	except:
		print(col.red1 + 'Error: Cant open file ' + str(file) + col.normal)


## Get the working directory of MassCTRL ## UNUSED ##
def WorkingDirectory():
	dirpath = os.getcwd()
	
	return str(dirpath)	


## Return date and time to log file
def TimeDate():
	dateandtime = datetime.now()
	date_time = dateandtime.strftime('%Y-%m-%d %H:%M:%S')
	
	return str(date_time)


## Executes the command on client
def SshExecute(host, user, passwd, string):
	command = ['sh', '-c']
	string = string.split(command_delimiter)
	command.extend(string)
	if missing_host_key_accept == True:
		shell = spur.SshShell(hostname=host, username=user, password=passwd, missing_host_key=spur.ssh.MissingHostKey.accept)
	else:
		shell = spur.SshShell(hostname=host, username=user, password=passwd)
	#try:
	with shell:
		result = shell.run(command, allow_error=True)
		#command = str(command).replace(command_delimiter, ' ')
		command = ', '.join(command)
		command = command.replace('sh, -c, ','')
	
	if command_output == True:
		print('Executing command: ' + col.steelblue1 + command + col.normal + ' with result:')
		WriteClientLog(host, 'Executing command: ' + command + ' with result:')
		
	if exec_output == True:
		if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
			print(CleanString(str(result.output, 'utf-8')))
	
	if return_code_output == True:
		print('Execution ' + FormatReturnCode(str(result.to_error())))
		passwd = ''
	
	#except:
	#	print(col.red1 + 'Error: Cant connect to client  ' + host + col.normal)		
	#	passwd = ''


## Executes the command locally
def LocalExecute(string):
	command = ['sh', '-c']
	string = string.split(command_delimiter)
	command.extend(string)
	shell = spur.LocalShell()
	try:
		with shell:
			result = shell.run(command, allow_error=True)
			command = ', '.join(command)
			command = command.replace('sh, -c, ','')
		
		if command_output == True:
			print('Executing local command: ' + col.steelblue1 + command + col.normal + ' with result:')
		
		if exec_output == True:
			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				print(CleanString(str(result.output, 'utf-8')))
		
		if return_code_output == True:
			print('Execution ' + FormatReturnCode(str(result.to_error())))
	
	except:
		print(col.red1 + 'Error: Cant execute command' + col.normal)		


## Main function for executing remote commands
def exec_command(group, recipe):
	ClearScreen()
	clients = GetClients(group)
	recipe = GetRecipe(recipe)
	local_validator = ''

	if recipe != []:
		for client in clients:
			if client_headline == True:
				print(col.bold_yellow1(client) + '\n' + (col.darkgray('=') * len(client)))
			
			if CheckClient(client) == True:
				user, passwd = GetCredentials(client)
				
				try:
					for ingredient in recipe:
						ingredient = ingredient.split(':')
						
						if ingredient[0] == str('EXEC'):
							ingredient = str(ingredient[1])
							SshExecute(client, user, passwd, ingredient)
						
						elif ingredient[0] == str('LOCAL'):
							ingredient = str(ingredient[1])
							if local_validator != ingredient:						
								LocalExecute(ingredient)
								local_validator = ingredient
	
						elif ingredient[0] == str('PUT'):
							ingredient = str(ingredient[1])
							ingredient = ingredient.split(' ')
							source = str(ingredient[0])
							dest = str(ingredient[1])
							FileOperation(client, user, passwd, source, dest, 'put')
						
						elif ingredient[0] == str('GET'):
							ingredient = str(ingredient[1])
							ingredient = ingredient.split(' ')
							source = str(ingredient[0])
							dest = str(ingredient[1])
							FileOperation(client, user, passwd, source, dest, 'get')	
	
					print('-' * 30)
					print('')
					passwd = ''
					
				except Exception as error:
					print(str(error))
					passwd = ''
				
			else:
				passwd = ''
				print(col.red1 + 'Client: ' + str(client) + ' does not respond' + col.normal)
				print('-' * 30)
			print('')
	else:
		print(col.red1 + 'Error: The recipe file has no ingredients' + col.normal)


## Format the return code of executed command
def FormatReturnCode(returncode):
	returncode = returncode.split('\n')
	returncode = str(returncode[0])
	returnnum = str(returncode).split(' ')
	rc_message = return_code.get(str(returnnum[2]))

	if str(returnnum[2]) == '0':
		return (returncode + ' - ' + col.green2 + rc_message + col.normal)
	else:
		return (returncode + ' - ' + col.red1 + rc_message + col.normal)


## Get login credentials from key file.
def GetCredentials(host):
	if os.path.exists(keyfile):
		user = ''
		passwd = ''
		content = ReadFile(keyfile)
		
		if master_account == True:
			for row in content:
				if 'masteraccount' in str(row):
					row = row.split(' ')
					user = row[2]
					passwd = row[3]
		
		else:
			for row in content:
				if str(host) in str(row):
					row = row.split(' ')
					user = row[2]
					passwd = row[3]
	
		return user, passwd
	
	else:
		print(col.red1 + 'The keyfile ' + keyfile + ' does not exist' + col.normal)
		sys.exit(1)		


## Gets clients from group file
def GetClients(group):
	hosts = []
	groups = group.split(',')
	
	for group in groups:
		if os.path.exists(groupfiles + group):
			content = ReadFile(groupfiles + group)
			
			for client in content:
				if client != '' and client != '\n':
					client = client.split(' ')
					
					if use_hostname == True:
						hosts.append(client[0])
					
					else:
						hosts.append(client[1])
	
		else:
			print(col.red1 + 'The group ' + group + ' does not exist' + col.normal)
			sys.exit(1)
	
	return hosts


## Get commands from recipe file
def GetRecipe(recipe):
	ingredients = []
	recipes = str(recipe).split(',')
	for recipe in recipes:
		if os.path.exists(recipefiles + recipe):
			recipe = ReadFile(recipefiles + recipe)
			
			for command in recipe:
				if command != '' and command[0] != '#':
					if 'EXEC:' in command or 'GET:' in command or 'PUT:' in command or 'LOCAL:' in command: 
						ingredients.append(command)

					else:
						print(col.red1 + 'The recipe file is invalid and does not contain mandatory trigger commands' + col.normal)
						sys.exit(1)
				
				else:
					continue
		
		else:
			print(col.red1 + 'The recipe ' + recipe + ' does not exist' + col.normal)
			sys.exit(1)
	
	return ingredients


## Show a list of groups and recipes
def InventoryList():
	if os.path.exists(groupfiles):
		print(col.bold_green3('\nGroups:'))
		print(col.bold_snow4('-' * 20))
		groups = CollectFiles(groupfiles)
		groups.sort()
		
		for entry in groups:
			print(entry.replace('./groups/', ''))
		
		print('')
	else:
		print(col.red1 + 'Error: Group directory ' + groupfiles + ' does not exist' + col.normal)
		sys.exit(1)

	if os.path.exists(recipefiles):
		print(col.bold_green3('\nRecipes:'))
		print(col.bold_snow4('-' * 20))
		recipes = CollectFiles(recipefiles)
		recipes.sort()
		
		for entry in recipes:
			print(entry.replace('./recipes/', ''))
				
	else:
		print(col.red1 + 'Error: Recipe directory ' + recipefiles + ' does not exist' + col.normal)
		sys.exit(1)
	print('')


## Function to handle file transfers
def FileOperation(host, user, passwd, source, dest, direction):
	command = ['sh', '-c']
	if missing_host_key_accept == True:
		if direction == 'put':
			scp_command = ['sshpass -p ' + passwd + ' scp -v -p ' + source + ' ' +user + '@' + host + ':' + dest]
		elif direction == 'get':
			scp_command = ['sshpass -p ' + passwd + ' scp -v -p ' + user + '@' + host + ':' + source + ' ' + dest]

	else:
		if direction == 'put':
			scp_command = ['scp -v -p ' + source + ' ' +user + '@' + host + ':' + dest]
		elif direction == 'get':
			scp_command = ['scp -v -p ' + user + '@' + host + ':' + dest + ' ' + source]

	command.extend(scp_command)
	shell = spur.LocalShell()
	
	if command_output == True and direction == 'put':
		print('Sending file: ' + col.yellow1 + source + col.normal + ' to remote: ' + col.orange + dest + col.normal)
	elif command_output == True and direction == 'get':
		print('Receiving file: ' + col.yellow1 + source + col.normal + ' from remote: ' + col.orange + dest + col.normal)
	try:
		with shell:
			result = shell.run(command)
		
		passwd = ''
		filename = source.rsplit('/', 1)[-1]

		if command_output == True:
			print(direction + ' ' + source + ' -> ' + dest)

		if exec_output == True:
			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				print(CleanString(str(result.output, 'utf-8')))
		
		if return_code_output == True:
			print('Execution ' + FormatReturnCode(str(result.to_error())))
		
		if get_file_rename == True and direction == 'get' and os.path.exists(dest + filename):
			shutil.move(dest + filename, dest + host + '_' + filename)
	
	except:
		print(col.red1 + 'Error: I probably couldnt find the requested file @' + host + col.normal)		
		passwd = ''
