#/usr/bin/env python3
# -*- coding: utf-8 -*-

from settings import *
from blessed import Terminal
import functions as fn
import os
import subprocess
import sys
import pathlib

bad_chars = ["'", ",", "[", "]"]
col = Terminal()

def ReadArguments():
	group = [arg for arg in sys.argv if 'group=' in arg]
	recipe = [arg for arg in sys.argv if 'recipe=' in arg]

	if group != [] and recipe != []:
		group = ''.join(char for char in group)
		group = group.split('=')
		group = group[1]
	
		recipe = ''.join(char for char in recipe)
		recipe = recipe.split('=')
		recipe = recipe[1]
		return group, recipe

	elif sys.argv[1] == 'list':
		fn.InventoryList()
		sys.exit(0)

	elif sys.argv[1] == 'test':
		pass
		sys.exit(0)
	
	else:
		print(col.red2('Not enough parameters passed to MassCTRL.py. Needs both group and recipe.'))    
		sys.exit(1)


def main():
	os.chdir(pathlib.Path(__file__).parent.absolute())
	fn.CreateClientLogLocation(clientloglocation)
	group, recipe =	ReadArguments()
	
	if recipe == 'status':
		fn.ClientStatusTicker(group)
	
	elif recipe == 'list':
		fn.InventoryList()
	
	else:
		fn.ExecCommand(group, recipe)


if __name__ == '__main__':
	main()
