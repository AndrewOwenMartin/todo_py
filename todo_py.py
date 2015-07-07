#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import uuid
import textedit


def load_tasks(task_list_file_name):
	with open(task_list_file_name,'r') as file:
		task_list_data = file.read()

	task_list = json.loads(task_list_data)
	for task in task_list:
		if not "id" in task:
			task["id"] = str(uuid.uuid4())
		if not "note" in task:
			task["note"] = ""
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

task_template = (''
'{\n'
'	"name": "",\n'
'	"detail": [\n'
'		""\n'
'	],\n'
'	"status": "not done",\n'
'	"note": ""\n'
'}\n')

def get_field(task,field):
	if field in task:
		return task[field]
	else:
		raise KeyError('Task {task_id} missing a "{field}" field'.format(
			task_id=task["id"][:8],
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
	for task in task_list:
		if task_incomplete(task):
			task_id = task["id"]
			task_info = [get_field(task,'name')]
			#name = get_field(task,'name')
			status = get_field(task,'status')
			if not status == default_status:
				task_info.append(status)

			out_lines.append(
				"{task_id}: {task_info}".format(
					task_id=task_id[:8],
					task_info=" - ".join(task_info))
			)
	return "\n".join(out_lines)

def verbose_task(task):
	out_lines = []
	name = get_field(task,'name')
	task_id = task["id"]
	out_lines.append("{name}".format(
		task_id=task_id[:8],
		name=name))
	detail = get_field(task,'detail')
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
		status=get_field(task,'status'))
	out_lines.append(status)
	return out_lines

# def ordered_json_task(task):
# 	out_lines = []
# 	top_fields = ["id","name","detail","status","note"]
# 	for field in top_fields:
# 		if field in task:
# 			out_lines.append("\"{field}\": \"{value}\"".format(
# 				field=field,
# 				value=task[field]))
# 	other_fields = [x for x in task.keys() if x not in top_fields]
# 	for field in other_fields:
# 		out_lines.append("\"{field}\": \"{value}\"".format(
# 			field=field,
# 			value=task[field]))
#
# 	return "{\n" + "\n".join(out_lines) + "\n}"


def get_task_by_id(task_list,task_id):
	for task in task_list:
		if task["id"].startswith(task_id):
			return task
	return None

def get_task_index_by_id(task_list,task_id):
	for num,task in enumerate(task_list):
		if task["id"].startswith(task_id):
			return num
	return None

def verbose_task_from_list(task_list,args):
	if 'task_id' in args:
		task_id = args["task_id"]
		task = get_task_by_id(task_list,task_id)
		if task:
			return "\n".join(verbose_task(task))
	return None

def get_empty_task():
	#with open(os.path.join('templates','task_template.json'),'r') as file:
	#	task_template = file.read()
	#empty_task = json.loads(task_template[:-2]) # remove trailing comma
	empty_task = {
		"name":"",
		"detail":[""],
		"status":"not done",
		"note":"",
		"id":str(uuid.uuid4())
	}
	return empty_task

def editor_task(original_text):
	valid_json = False
	text_to_edit = original_text
	while not valid_json:
		edited_task_text = textedit.read_from_editor(
			text_to_edit,
			suffix=".json")
		try:
			edited_task = json.loads(edited_task_text)
			valid_json = True
		except ValueError:
			valid_json = False
			text_to_edit = original_text + "\n==========\n" + edited_task_text
	return edited_task


def edit_task(task_list,args):
	task_to_edit_index = get_task_index_by_id(task_list,args["task_id"])
	task_list[task_to_edit_index] = editor_task(
		json.dumps(
			task_list[task_to_edit_index],
			sort_keys=True,
			indent=2,
			separators=(',', ': ')))

	#task_list[task_to_edit_index]["note"] += " edited"
	save_task_list(task_list,args["path"])
	return "Updated task:\n{task}".format(
		task="\n".join(verbose_task(task_list[task_to_edit_index])))


def save_task_list(task_list,path):
	with open(path,"w") as file:
		file.write(json.dumps(
			task_list,
			sort_keys=True,
			indent=2,
			separators=(',', ': ')))

def new_task(task_list,args):

	new_task = editor_task(task_template)

	#new_task_text = textedit.read_from_editor(
	#	task_template,suffix=".json")
	#new_task = json.loads(new_task_text)
	new_task["id"] = str(uuid.uuid4())
	task_list.append(new_task)
	save_task_list(task_list,args["path"])
	return "New task:\n{task}".format(
		task="\n".join(verbose_task(new_task)))

def verbose_list(task_list,args):
	out_lines = []
	for task in task_list:
		if task_incomplete(task):
			out_lines.extend(verbose_task(task))
	return "\n".join(out_lines)

def urgent_list(task_list,args):
	out_lines = []
	for task in task_list:
		if task_urgent(task):
			out_lines.extend(verbose_task(task))
	return "\n".join(out_lines)
	

def get_function_for_command(first_arg):
	valid_args = {
		"e":edit_task, # edit
		"n":new_task, # new
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
	arg_list = ['script','path','command','task_id']
	for num,arg in enumerate(arg_list):
		if len(args) > num:
			args_dict[arg] = args[num]
	return args_dict
