import helper as h

def empty_folder(contents):
  if not contents:
    return "Folder is empty"

def long_name(name):
  if len(name) > 180:
    return "Folder name too long"

def non_folder_contents(path, contents):
  non_folder = False
  for item in contents:
    if h.is_file(path + "/" + item):
      non_folder = True

  if non_folder:
    return "Folder contains file"

def run(artist, path):
  artist_results_dict = {
    "total_checks_made": 0,
    "fails": []
  }

  contents = h.try_dir(path)

  artist_results_dict["fails"].append(empty_folder(contents))
  artist_results_dict["fails"].append(long_name(artist))
  artist_results_dict["fails"].append(non_folder_contents(path, contents))



  return artist_results_dict