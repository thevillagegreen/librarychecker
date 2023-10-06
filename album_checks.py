import helper as h
import re

#============== UNIVERSAL CHECKS

# Folder has no contents
def empty_folder(contents):
  if not contents:
    return "Folder is empty"

# Folder name is longer than 100 char
def long_name(name):
  if len(name) > 180:
    return "Folder name too long"

def cover_missing(images):
  cover_found = False
  for img in images:
    if img["name"] in ['cover.jpg', 'cover.png']:
      cover_found = True
  if not cover_found:
    return "No cover found"

def cover_square(images):
  # Check only performed with proper cover
  if len(images) == 1 and images[0]["name"] in ['cover.jpg', 'cover.png']:
    if images[0]["size"][0] != images[0]["size"][1]:
      return "Cover not square"

def cover_size(images):
  # Check only performed with proper cover
  if len(images) == 1 and images[0]["name"] in ['cover.jpg', 'cover.png']:
    if images[0]["size"][0] > 10000 or images[0]["size"][1] > 10000:
      return "Cover too large"
    elif images[0]["size"][0] < 600 or images[0]["size"][1] < 600:
      return "Cover too small"

def cover_excess(images):
  if len(images) > 1:
    return "Too many images"

def folder_excess(folders):
  if len(folders) > 1:
    return "Too many folders"

def artwork_folder(folders):
  if len(folders) == 1 and folders[0]["name"] not in ["Artwork"]:
    return "Incorrect Artwork folder name"

def media_missing(media_type):
  if not media_type:
    return "This album has no media in folder name"

def audio_present(flac, non_flac):
  if not flac and not non_flac:
    return "This folder has no audio files"

def audio_mixed(flac, non_flac):
  if flac and non_flac:
    return "This folder has both flac and non-flac audio files"

def flac_mixed(flac):
  if flac:
    sr = flac[0]['sample_rate']
    ss = flac[0]['sample_size']
    for f in flac:
      if f['sample_rate'] != sr or f['sample_size'] != ss:
        return "This folder has mixed flac formats"

def tracks_continuous(flac, tracks):
  if flac and tracks:
    for disc in tracks:
        if disc: #TO DO: This does account for the first or last track missing
          range_list =list(range(min(disc), max(disc)+1))
          if range_list != sorted(disc):
            return "This album contains non-continuous tracks."
  
  elif flac and not tracks:
    return "This album is missing track/disc numbering information."

def flac_format(flac):
  pattern = re.compile(r'^\d{1,2}[-]\d{2,3}[.]', re.I)
  if flac:
    for f in flac:
      if not pattern.search(f['name']) or f['name'][:2].startswith("0"):
        return "This album is contains flac files with incorrect naming."

#============== CD CHECKS

#============== WEB CHECKS

#============== TAPE/VINYL CHECKS




def run(name, path):
  album_results_dict = {
    "total_checks_made": 0,
    "name": name,
    "path": path,
    "media_type": '',
    "fails": [],
    "no_fails": False
  }

  contents = h.try_dir(path)
  contents_dict = h.extract_album_contents(path)
  album_results_dict["media_type"] = h.find_folder_media_type(name)
  track_arr = h.populate_track_number_arr(contents_dict)

  album_results_dict["fails"].append(empty_folder(contents))
  album_results_dict["fails"].append(long_name(name))
  album_results_dict["fails"].append(cover_missing(contents_dict["images"]))
  album_results_dict["fails"].append(cover_square(contents_dict["images"]))
  album_results_dict["fails"].append(cover_size(contents_dict["images"]))
  album_results_dict["fails"].append(cover_excess(contents_dict["images"]))
  album_results_dict["fails"].append(folder_excess(contents_dict["folders"]))
  album_results_dict["fails"].append(artwork_folder(contents_dict["folders"]))
  album_results_dict["fails"].append(media_missing(album_results_dict["media_type"]))
  album_results_dict["fails"].append(audio_present(contents_dict["flac"], contents_dict["non_flac"]))
  album_results_dict["fails"].append(audio_mixed(contents_dict["flac"], contents_dict["non_flac"]))
  album_results_dict["fails"].append(flac_mixed(contents_dict["flac"]))
  album_results_dict["fails"].append(tracks_continuous(contents_dict["flac"], track_arr))
  album_results_dict["fails"].append(flac_format(contents_dict["flac"]))




  if all(x is None for x in album_results_dict["fails"]):
    album_results_dict["no_fails"] = True

  h.remove_nones(album_results_dict["fails"])

  return album_results_dict