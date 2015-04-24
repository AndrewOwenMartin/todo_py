#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import todo_py

script_name = sys.argv[0]
args = sys.argv[1:]
arg_count = len(args)
usage = (
	"USAGE FOR \"{script_name}\"\n\n"
	"{script_name} <path> \n\tQuick list\n\n"
	"{script_name} <path> s NUM\n\t[S]how verbose task.\n\n"
	"{script_name} <path> u\n\tVerbose list of [U]rgent tasks.\n\n"
	"{script_name} <path> v\n\t[V]erbose list.\n\n"
).format(script_name=script_name)

if arg_count == 0:
	print usage
	sys.exit(1)
else:
	args_dict = todo_py.args_to_dict(args)
	task_list = todo_py.load_tasks(args_dict['path'])
	if 'command' in args_dict:
		display_function = todo_py.get_function_for_command(
			args_dict['command'])
		if display_function:
			response = display_function(task_list,args_dict)
			if response:
				print response
				sys.exit(0)
			else:
				print usage
				sys.exit(1)
		else:
			print usage
			sys.exit(1)
	else:
		print todo_py.quick_list(task_list)
		sys.exit(0)
