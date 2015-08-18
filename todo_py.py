#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import os
import textedit
import uuid


def load_tasks(task_list_file_name):
	with open(task_list_file_name,'r') as file:
		task_list_data = file.read()

	task_list = json.loads(task_list_data)
	for task in task_list:
		if not u"id" in task:
			task[u"id"] = str(uuid.uuid4())
		if not u"note" in task:
			task[u"note"] = u""
	return task_list

complete_statuses = [
	u"done",
	u"abandoned"
]

urgent_statuses = [
	u"[Bloody Urgent]",
	u"[Urgent]"
]

default_status = u"not done"

dt_format_str = u"%d/%m/%Y - %H:%M:%S"

def get_now_datetime():
	return datetime.datetime.now()

def get_now_date():
	return datetime.date.today()

def datetime_to_dt_str(dt):
	return dt.strftime(dt_format_str)

def dt_str_to_datetime(dt_str):
	return datetime.datetime.strptime(dt_str,dt_format_str)

task_template = (u""
u"{{\n"
u"	\"name\": \"\",\n"
u"	\"detail\": [\n"
u"		\"\"\n"
u"	],\n"
u"	\"status\": \"not done\",\n"
u"	\"note\": \"\",\n"
u"	\"hide\": \"{now}\"\n"
u"}}\n").format(
	now = datetime_to_dt_str(get_now_date()))

def get_field(task,field):
	if field in task:
		return task[field]
	else:
		raise KeyError(u"Task {task_id} missing a \"{field}\" field".format(
			task_id=task[u"id"][:8],
			field=field))

def task_hide(task):
	# Hide task returns true if the task has a hide field, and the hide field
	# encodes a time later (greater) than now.
	return (
		u"hide" in task
		and dt_str_to_datetime(task[u"hide"]) > get_now_datetime())

def task_incomplete(task):
	return (
		not u"status" in task
		or task[u"status"] not in complete_statuses)

def task_urgent(task):
	return (
		not u"status" in task
		or any((x in task[u"status"] for x in urgent_statuses)))

def quick_list(task_list):
	out_lines = []
	for task in task_list:
		if task_incomplete(task) and not task_hide(task):
			task_id = task[u"id"]
			task_info = [get_field(task,u"name")]
			#name = get_field(task,u"name")
			status = get_field(task,u"status")
			if not status == default_status:
				task_info.append(status)

			out_lines.append(
				u"{task_id}: {task_info}".format(
					task_id=task_id[:8],
					task_info=u" - ".join(task_info))
			)
	return u"\n".join(out_lines)

def verbose_task(task):
	out_lines = []
	name = get_field(task,u"name")
	task_id = task[u"id"]
	out_lines.append(u"{name}".format(
		task_id=task_id[:8],
		name=name))
	detail = get_field(task,u"detail")
	for detail_line in detail:
		out_lines.append(u"\t{detail_line}".format(
			detail_line=detail_line))
	other_fields = [x for x in task.keys() if x not in [
		u"name",
		u"detail",
		u"status"]]
	other_fields.sort()
	for field_name in other_fields:
		out_lines.append(u"\t{field_name}: {field_value}".format(
			field_name=field_name,
			field_value=task[field_name]))
	status = u"\tStatus: {status}\n".format(
		status=get_field(task,u"status"))
	out_lines.append(status)
	return out_lines

# def ordered_json_task(task):
# 	out_lines = []
# 	top_fields = [u"id",u"name",u"detail",u"status",u"note"]
# 	for field in top_fields:
# 		if field in task:
# 			out_lines.append(u"\"{field}\u": \"{value}\u"".format(
# 				field=field,
# 				value=task[field]))
# 	other_fields = [x for x in task.keys() if x not in top_fields]
# 	for field in other_fields:
# 		out_lines.append(u"\"{field}\": \"{value}\"u".format(
# 			field=field,
# 			value=task[field]))
#
# 	return u"{\n" + u"\n".join(out_lines) + u"\n}"


def get_task_by_id(task_list,task_id):
	for task in task_list:
		if task[u"id"].startswith(task_id):
			return task
	return None

def get_task_index_by_id(task_list,task_id):
	for num,task in enumerate(task_list):
		if task[u"id"].startswith(task_id):
			return num
	return None

def verbose_task_from_list(task_list,args):
	if u"task_id" in args:
		task_id = args[u"task_id"]
		task = get_task_by_id(task_list,task_id)
		if task:
			return u"\n".join(verbose_task(task))
	return None

def get_empty_task():
	#with open(os.path.join(u"templates",u"task_template.json"),u"r") as file:
	#	task_template = file.read()
	#empty_task = json.loads(task_template[:-2]) # remove trailing comma
	empty_task = {
		u"name":u"",
		u"detail":[u""],
		u"status":u"not done",
		u"note":u"",
		u"id":str(uuid.uuid4())
	}
	return empty_task

def editor_task(original_text):
	valid_json = False
	text_to_edit = original_text
	while not valid_json:
		edited_task_text = textedit.read_from_editor(
			text_to_edit,
			suffix=u".json")
		try:
			edited_task = json.loads(edited_task_text)
			valid_json = True
		except ValueError:
			valid_json = False
			text_to_edit = original_text + u"\n==========\n" + edited_task_text
	return edited_task


def edit_task(task_list,args):
	task_to_edit_index = get_task_index_by_id(task_list,args[u"task_id"])
	if task_to_edit_index is None:
		return u"Not a recognised task \"{id}\"".format(id=args[u"task_id"])
	else:
		task_to_edit = task_list[task_to_edit_index]
		task_list[task_to_edit_index] = editor_task(
			json.dumps(
				task_to_edit,
				sort_keys=True,
				indent=2,
				separators=(u",", u": ")))

		#task_list[task_to_edit_index][u"note"] += u" edited"
		save_task_list(task_list,args[u"path"])
		return u"Updated task:\n{task}".format(
			task=u"\n".join(verbose_task(task_list[task_to_edit_index])))


def save_task_list(task_list,path):
	with open(path,u"w") as file:
		file.write(json.dumps(
			task_list,
			sort_keys=True,
			indent=2,
			separators=(u",", u": ")))

def new_task(task_list,args):

	new_task = editor_task(task_template)

	#new_task_text = textedit.read_from_editor(
	#	task_template,suffix=u".json")
	#new_task = json.loads(new_task_text)
	new_task[u"id"] = str(uuid.uuid4())
	task_list.append(new_task)
	save_task_list(task_list,args[u"path"])
	return u"New task:\n{task}".format(
		task=u"\n".join(verbose_task(new_task)))

def verbose_list(task_list,args):
	out_lines = []
	for task in task_list:
		if task_incomplete(task):
			out_lines.extend(verbose_task(task))
	return u"\n".join(out_lines)

def urgent_list(task_list,args):
	out_lines = []
	for task in task_list:
		if task_urgent(task):
			out_lines.extend(verbose_task(task))
	return u"\n".join(out_lines)
	

def get_function_for_command(first_arg):
	valid_args = {
		u"e":edit_task, # edit
		u"n":new_task, # new
		u"s":verbose_task_from_list, # show
		u"u":urgent_list, # urgent
		u"v":verbose_list, # verbose
	}

	if first_arg in valid_args:
		return valid_args[first_arg]
	else:
		return None

def args_to_dict(args):
	args_dict = {}
	arg_list = [u"script",u"path",u"command",u"task_id"]
	for num,arg in enumerate(arg_list):
		if len(args) > num:
			args_dict[arg] = args[num]
	return args_dict
