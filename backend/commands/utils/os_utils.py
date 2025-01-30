import os
from .constants import commands_output_path

debug_should_log = False

def ensure_dir(dir_name: str) -> None:
  output_dir = os.path.join(os.path.dirname(__file__), dir_name)
  if (debug_should_log): print(output_dir)
  os.makedirs(output_dir, exist_ok=True)


def ensure_file(file_name: str, output_dir: str = commands_output_path) -> None:
  if (debug_should_log): print(output_dir)
  os.makedirs(output_dir, exist_ok=True)

  output_file = os.path.join(output_dir, file_name)
  if (debug_should_log): print(output_file)
  return output_file
