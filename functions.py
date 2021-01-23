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
import random


# https://blessed.readthedocs.io/en/latest/colors.html
col = Terminal()

return_code = {
	'0': 'Success',
	'1': 'Catchall for general errors',
	'2': 'Misuse of shell builtins',
	'100': 'Access denied',
	'126': 'Command invoked cannot execute',
	'127': 'Command not found',
	'128': 'Invalid argument to exit',
}

# Date and time for log function
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


# Write to specified error log
def WriteErrorLog(logmessage):
	try:
		with open(errorlogfile, 'a+') as log:
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
	os.system('clear')


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

		if write_master_log == True:
			WriteMasterLog(str(host) + ': Error: Cant do host lookup @' + str(host) + '. No entry in hosts file?')

		if write_error_log == True:
			WriteErrorLog(str(host) + ': Error: Cant do host lookup @' + str(host) + '. No entry in hosts file?')

		if write_client_log == True:
			WriteClientLog(str(host), 'Error: Cant do host lookup @' + str(host) + '. No entry in hosts file?')

## Status of the specified clients
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

## Runs the ClientStatus Ticker
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

		if write_master_log == True:
			WriteMasterLog('Error: Cant collect groups and recipes from specified directory')

		if write_error_log == True:
			WriteErrorLog('Error: Cant collect groups and recipes from specified directory')
	

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
		
		if write_master_log == True:
			WriteMasterLog('Error: Cant open file ' + str(file))

		if write_error_log == True:
			WriteErrorLog('Error: Cant open file ' + str(file))

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
	
	elif private_key_login == True:
		shell = spur.SshShell(hostname=host, username=user)

	else:
		shell = spur.SshShell(hostname=host, username=user, password=passwd)

	try:
		with shell:
			result = shell.run(command, allow_error=True)
			command = ', '.join(command)
			command = command.replace('sh, -c, ','')
			
		passwd = ''

		if command_output == True:
			print('Executing command: ' + col.steelblue1 + command + col.normal + ' with result:')
					
		if exec_output == True:
			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				print(CleanString(str(result.output, 'utf-8')))
		
		if return_code_output == True:
				print('Execution ' + FormatReturnCode(str(result.to_error())))
		
		if write_master_log == True:
			WriteMasterLog(host + ': Executing command: ' + command + ' with result:')
			
			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				outputssh = CleanString(str(result.output, 'utf-8'))
				outputssh = outputssh.split('\n')

				for row in outputssh:				
					WriteMasterLog(host + ': ' + row)
			
			WriteMasterLog(host + ': Execution ' + FormatReturnCodeLog(str(result.to_error())))
		
		if write_client_log == True: 
			WriteClientLog(host, 'Executing command: ' + command + ' with result:')
			
			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				outputssh = CleanString(str(result.output, 'utf-8'))
				outputssh = outputssh.split('\n')

				for row in outputssh:					
					WriteClientLog(host, row)
			WriteClientLog(host, 'Execution ' + FormatReturnCodeLog(str(result.to_error())))
	

		if write_error_log == True:
			#print(result.to_error())
			executiontest = FormatReturnCodeErrorLog(str(result.to_error()))
			if executiontest != '0':
				WriteErrorLog(host + ': Execution of command ' + command + ' failed with return code ' + executiontest)

	except Exception as e:
		print(e)
		e = str(e).split('\n')
		passwd = ''
		print(col.red1 + 'Error: Cant connect to client ' + host)
		
		for error in e:
			print(str(error))
			
		print(col.normal)
		
		if write_master_log == True:
			WriteMasterLog(host + ': Error: Cant connect to client ' + host)
			
			for error in e:
				WriteMasterLog(host + ': ' + error)
		
		if write_client_log == True:
			WriteClientLog(host, 'Error: Cant connect to client ' + host)
			
			for error in e:
				WriteClientLog(host, error)

		if write_error_log == True:
			WriteErrorLog('Error: Cant connect to client ' + host)
			for error in e:
				WriteErrorLog(host + ': ' + error)


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
			print('Executing local command: ' + col.tan1 + command + col.normal + ' with result:')
		
		if exec_output == True:
			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				print(CleanString(str(result.output, 'utf-8')))
		
		if return_code_output == True:
			print('Execution ' + FormatReturnCode(str(result.to_error())))
	
		if write_master_log == True:
			WriteMasterLog('Executing local command: ' + command + ' with result:')
			
			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				outputlocal = CleanString(str(result.output, 'utf-8'))
				outputlocal = outputlocal.split('\n')
				
				for row in outputlocal:
					WriteMasterLog(row)
			
			WriteMasterLog('Execution ' + FormatReturnCodeLog(str(result.to_error())))
		
		if write_client_log == True:
			WriteClientLog('local', 'Executing local command: ' + command + ' with result:')

			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				outputlocal = CleanString(str(result.output, 'utf-8'))
				outputlocal = outputlocal.split('\n')

				for row in outputlocal:				
					WriteClientLog('local', row)
			WriteClientLog('local', 'Execution ' + FormatReturnCodeLog(str(result.to_error())))

		if write_error_log == True:
			executiontest = FormatReturnCodeErrorLog(str(result.to_error()))
			if executiontest != 0:
				WriteErrorLog('Local Execution of command ' + command + ' failed with return code ' + executiontest)			

	except:
		print(col.red1 + 'Error: Cant execute command' + col.normal)		

		if write_master_log == True:
			WriteMasterLog('local: Error: Cant execute command')

		if write_client_log == True:
			WriteClientLog('local', 'Error: Cant execute command')

		if write_error_log == True:
			WriteErrorLog('Local: Error: Cant execute command')


## Main function for executing remote commands
def ExecCommand(group, recipe):
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
					#print('')
					passwd = ''
					
				except Exception as error:
					print(str(error))
					passwd = ''
				
			else:
				passwd = ''
				print(col.red1 + 'Client: ' + str(client) + ' does not respond' + col.normal)
				print('-' * 30)

				if write_master_log == True:
					WriteMasterLog(str(client) + ': Client: ' + str(client) + ' does not respond')
				
				if write_client_log == True:
					WriteClientLog(str(client), 'Client: ' + str(client) + ' does not respond')
				
				if write_error_log == True:
					WriteErrorLog(str(client) + ': Client: ' + str(client) + ' does not respond')	

			print('')

	else:
		print(col.red1 + 'Error: The recipe file has no ingredients' + col.normal)

		if write_master_log == True:
			WriteMasterLog(str(client) + ': Error: The recipe file has no ingredients')
		
		if write_client_log == True:
			WriteClientLog(str(client), + 'Error: The recipe file has no ingredients')
		
		if write_error_log == True:
			WriteErrorLog(str(client), + 'Error: The recipe file has no ingredients')


## Format the return code of executed command
def FormatReturnCode(returncode):
	returncode = returncode.split('\n')
	returncode = str(returncode[0])
	returnnum = str(returncode).split(' ')
	rc_message = return_code.get(str(returnnum[2]))
	
	if rc_message is None:
		rc_message = returnnum[2]
	
	if str(returnnum[2]) == '0':
		return (returncode + ' - ' + col.green2 + rc_message + col.normal)
	else:
		return (returncode + ' - ' + col.red1 + rc_message + col.normal)


def FormatReturnCodeLog(returncode):
	returncode = returncode.split('\n')
	returncode = str(returncode[0])
	returnnum = str(returncode).split(' ')
	rc_message = return_code.get(str(returnnum[2]))
	
	if rc_message is None:
		rc_message = returnnum[2]

	if str(returnnum[2]) == '0':
		return (returncode + ' - ' + rc_message)
	
	else:
		return (returncode + ' - ' + rc_message)


def FormatReturnCodeErrorLog(returncode):
	returncode = returncode.split('\n')
	returncode = str(returncode[0])
	returnnum = str(returncode).split(' ')
	rc_message = return_code.get(str(returnnum[2]))
	
	if rc_message is None:
		rc_message = returnnum[2]

	return (str(returnnum[2]))


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
		WriteErrorLog('The keyfile ' + keyfile + ' does not exist')

		sys.exit(1)		


## Gets clients from group file
def GetClients(group):
	hosts = []
	groups = group.split(',')
	location = groupfiles
	
	if location[-1] != '/':
		location = location + '/'

	for group in groups:
		if os.path.exists(location + group):
			content = ReadFile(location + group)
			
			for client in content:
				if client != '' and client != '\n' and client[0] != '#':
					client = client.split(' ')
					
					if use_hostname == True:
						hosts.append(client[0])
					
					else:
						hosts.append(client[1])
	
		else:
			print(col.red1 + 'The group ' + group + ' does not exist' + col.normal)
			WriteErrorLog('The group ' + group + ' does not exist')
			sys.exit(1)
	
	return hosts


## Get commands from recipe file
def GetRecipe(recipe):
	ingredients = []
	recipes = str(recipe).split(',')
	location = recipefiles
	
	if location[-1] != '/':
		location = location + '/'
	for recipe in recipes:
		if os.path.exists(location + recipe):
			recipe = ReadFile(location + recipe)
			
			for command in recipe:
				if command != '' and command[0] != '#':
					if 'EXEC:' in command or 'GET:' in command or 'PUT:' in command or 'LOCAL:' in command: 
						ingredients.append(command)

					else:
						print(col.red1 + 'The recipe file ' + recipe + ' is invalid and does not contain mandatory trigger commands' + col.normal)
						
						if write_master_log == True:
							WriteMasterLog('The recipe file ' + recipe + ' is invalid and does not contain mandatory trigger commands')

						if write_error_log == True:
							WriteErrorLog('The recipe file ' + recipe + ' is invalid and does not contain mandatory trigger commands')
						
						sys.exit(1)
				
				else:
					continue
		
		else:
			print(col.red1 + 'The recipe ' + recipe + ' does not exist' + col.normal)
			
			if write_master_log == True:
				WriteMasterLog('The recipe ' + recipe + ' does not exist')

			if write_error_log == True:
				WriteErrorLog('The recipe ' + recipe + ' does not exist')
			
			sys.exit(1)
	
	return ingredients


## Show a list of groups and recipes
def InventoryList():
	if os.path.exists(groupfiles):
		grplocation = groupfiles
		
		if grplocation[-1] != '/':
			grplocation = grplocation + '/'

		print(col.bold_green3('\nGroups:'))
		print(col.bold_snow4('-' * 20))
		groups = CollectFiles(grplocation)
		groups.sort()
		
		for entry in groups:
			print(entry.replace(grplocation, ''))
		
		print('')
	
	else:
		print(col.red1 + 'Error: Group directory ' + grplocation + ' does not exist' + col.normal)
		sys.exit(1)

	if os.path.exists(recipefiles):
		reclocation = recipefiles
		
		if reclocation[-1] != '/':
			reclocation = reclocation + '/'

		print(col.bold_green3('\nRecipes:'))
		print(col.bold_snow4('-' * 20))
		recipes = CollectFiles(reclocation)
		recipes.sort()
		
		for entry in recipes:
			print(entry.replace(reclocation, ''))
				
	else:
		print(col.red1 + 'Error: Recipe directory ' + reclocation + ' does not exist' + col.normal)
		if write_error_log == True:
			WriteErrorLog('Error: Recipe directory ' + reclocation + ' does not exist' + col.normal)

		sys.exit(1)

	print('')


## Function to handle file transfers
def FileOperation(host, user, passwd, source, dest, direction):
	command = ['sh', '-c']
	if missing_host_key_accept == True:
		if direction == 'put':
			scp_command = ['sshpass -p ' + "'" + passwd + "'" + ' scp -o StrictHostKeyChecking=no -v -p ' + source + ' ' +user + '@' + host + ':' + dest]

		elif direction == 'get':
			scp_command = ['sshpass -p ' + "'" + passwd + "'" + ' scp -o StrictHostKeyChecking=no -v -p ' + user + '@' + host + ':' + source + ' ' + dest]

	else:
		if direction == 'put':
			scp_command = ['scp -v -p ' + source + ' ' +user + '@' + host + ':' + dest]

		elif direction == 'get':
			scp_command = ['scp -v -p ' + user + '@' + host + ':' + dest + ' ' + source]

	command.extend(scp_command)
	shell = spur.LocalShell()
	
	if command_output == True and direction == 'put':
		print('Sending file: ' + col.yellow1 + source + col.normal + ' to remote: ' + col.orange + dest + col.normal)

		if write_master_log == True:
			WriteMasterLog(host + ': Sending file ' + source + ' -> ' + dest)

		if write_client_log == True:
			WriteClientLog(host, ': Sending file ' + source + ' -> ' + dest)

	elif command_output == True and direction == 'get':
		print('Receiving file: ' + col.yellow1 + source + col.normal + ' from remote: ' + col.orange + dest + col.normal)

		if write_master_log == True:
			WriteMasterLog(host + ': Receiving file ' + source + ' from remote: ' + dest)

		if write_client_log == True:
			WriteClientLog(host, ': Receiving file ' + source + ' from remote: ' + dest)		


	try:
		with shell:
			result = shell.run(command)
		
		passwd = ''
		filename = source.rsplit('/', 1)[-1]

		if exec_output == True:
			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				print(CleanString(str(result.output, 'utf-8')))
		
		if return_code_output == True:
			print('Execution ' + FormatReturnCode(str(result.to_error())))
		
		if get_file_rename == True and direction == 'get' and os.path.exists(dest + filename):
			shutil.move(dest + filename, dest + host + '_' + filename)
	
		if write_master_log == True:
			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				WriteMasterLog(host + ': ' + CleanString(str(result.output, 'utf-8')))

			WriteMasterLog(host + ': ' + 'Execution ' + FormatReturnCodeLog(str(result.to_error())))
		
		if write_client_log == True:
			WriteClientLog(host, direction + ' ' + source + ' -> ' + dest)

			if CleanString(str(result.output, 'utf-8')) != '' and CleanString(str(result.output, 'utf-8')) != '\n':
				WriteClientLog(host, CleanString(str(result.output, 'utf-8')))

			WriteClientLog(host, 'Execution ' + FormatReturnCodeLog(str(result.to_error())))

		if write_error_log == True:
			executiontest = FormatReturnCodeErrorLog(str(result.to_error()))

			if executiontest != '0':
				WriteErrorLog(host + ': Execution of file transfer failed')

	except:
		passwd = ''
		print(col.red1 + 'Error: I probably couldnt find the requested file or directory @' + host + col.normal)		
		
		if write_master_log == True:
			WriteMasterLog(host + ': Error: I probably couldnt find the requested file or directory @' + host)
		
		if write_client_log == True:		
			WriteClientLog(host, 'Error: I probably couldnt find the requested file or directory @' + host)

		if write_error_log == True:
			WriteErrorLog(host + ': Error: I probably couldnt find the requested file or directory @' + host)
