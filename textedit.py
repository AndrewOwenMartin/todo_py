""" Returns text, optionally edited by a user.

Use this to populate a variable with some text (possibly empty), and then give
the user an opportunity to edit the text.

Args:
	skeleton_text: Text that will be in teh editor when it appears to the user.

Returns:
	A list of lines describing the file as saved by the user.

Raises:
	None
"""
import sys, tempfile, os
from subprocess import call

def read_from_editor(skeleton_text,suffix=".tmp"):
	EDITOR = os.environ.get('EDITOR','vim')

	initial_message = skeleton_text

	with tempfile.NamedTemporaryFile(suffix=suffix) as file:
		file.write(initial_message)
		file.flush()
		call([EDITOR, file.name])
		file.seek(0)
		file_lines = file.read()

	return file_lines
