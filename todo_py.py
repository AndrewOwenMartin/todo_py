#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os


def load_tasks(task_list_file_name):
	with open(task_list_file_name,'r') as file:
		task_list_data = file.read()

	task_list = json.loads(task_list_data)['tasks']
	return task_list

complete_statuses = [
	'done',
	'abandoned'
]

urgent_statuses = [
	"[Bloody Urgent]",
	"[Urgent]"
]

default_status = "not done"

def get_field(task,field,num="unknown"):
	if field in task:
		return task[field]
	else:
		raise KeyError('Task {num} missing a "{field}" field'.format(
			num=num,
			field=field))

def task_incomplete(task):
	return (
		not 'status' in task 
		or task['status'] not in complete_statuses)

def task_urgent(task):
	return (
		not 'status' in task 
		or any((x in task['status'] for x in urgent_statuses)))

def quick_list(task_list):
	out_lines = []
	for num, task in enumerate(task_list):
		if task_incomplete(task):
			task_info = [get_field(task,'name',num)]
			#name = get_field(task,'name',num)
			status = get_field(task,'status',num)
			if not status == default_status:
				task_info.append(status)

			out_lines.append(
				"{num:3d}: {task_info}".format(
					num=num,
					task_info=" - ".join(task_info))
			)
	return "\n".join(out_lines)

def verbose_task(task,num):
	out_lines = []
	name = get_field(task,'name')
	out_lines.append("{num:3d}: {name}".format(
		num=num,
		name=name))
	detail = get_field(task,'detail',num)
	for detail_line in detail:
		out_lines.append("\t{detail_line}".format(
			detail_line=detail_line))
	other_fields = [x for x in task.keys() if x not in [
		'name',
		'detail',
		'status']]
	other_fields.sort()
	for field_name in other_fields:
		out_lines.append("\t{field_name}: {field_value}".format(
			field_name=field_name,
			field_value=task[field_name]))
	status = "\tStatus: {status}\n".format(
		status=get_field(task,'status',num))
	out_lines.append(status)
	return out_lines

def verbose_task_from_list(task_list,args):
	if 'num' in args and args['num'].isdigit():
		task_num = int(args['num'])
		task = task_list[task_num]
		return "\n".join(verbose_task(task,task_num))
	else:
		return None

def verbose_list(task_list,args):
	out_lines = []
	for num, task in enumerate(task_list):
		if task_incomplete(task):
			out_lines.extend(verbose_task(task,num))
	return "\n".join(out_lines)

def urgent_list(task_list,args):
	out_lines = []
	for num, task in enumerate(task_list):
		if task_urgent(task):
			out_lines.extend(verbose_task(task,num))
	return "\n".join(out_lines)
	

def get_function_for_command(first_arg):
	valid_args = {
		"s":verbose_task_from_list, # show
		"u":urgent_list, # urgent
		"v":verbose_list, # verbose
	}

	if first_arg in valid_args:
		return valid_args[first_arg]
	else:
		return None

def args_to_dict(args):
	args_dict = {}
	arg_list = ['path','command','num']
	for num,arg in enumerate(arg_list):
		if len(args) > num:
			args_dict[arg] = args[num]
	return args_dict
