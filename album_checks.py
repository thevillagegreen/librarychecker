import helper as h
import re, os, sys
from subprocess import *

#============== UNIVERSAL CHECKS

# Folder has no contents
def empty_folder(contents):
  if not contents:
    return "AlbumEmpty"

# Folder name is longer than 100 char
def long_name(name):
  if len(name) > 180:
    return "AlbumNameLong"

def cover_missing(images):
  cover_found = False
  for img in images:
    if img["name"] in ['cover.jpg', 'cover.png']:
      cover_found = True
  if not cover_found:
    return "AlbumNoCover"

def cover_square(images):
  # Check only performed with proper cover
  if len(images) == 1 and images[0]["name"] in ['cover.jpg', 'cover.png']:
    if images[0]["size"][0] != images[0]["size"][1]:
      return "AlbumCoverShape"

def cover_size(images):
  # Check only performed with proper cover
  if len(images) == 1 and images[0]["name"] in ['cover.jpg', 'cover.png']:
    if images[0]["size"][0] > 10000 or images[0]["size"][1] > 10000:
      return "AlbumCoverLarge"
    elif images[0]["size"][0] < 600 or images[0]["size"][1] < 600:
      return "AlbumCoverSmall"

def cover_excess(images):
  if len(images) > 1:
    return "AlbumManyImages"

def folder_excess(folders):
  if len(folders) > 1:
    return "AlbumManyFolders"

def artwork_folder(folders):
  if len(folders) == 1 and folders[0]["name"] not in ["Artwork"]:
    return "AlbumArtworkName"

def media_missing(media_type):
  if not media_type:
    return "AlbumNoMedia"

def audio_present(flac, non_flac):
  if not flac and not non_flac:
    return "AlbumNoAudio"

def audio_mixed(flac, non_flac):
  if flac and non_flac:
    return "AlbumMixedAudio"

def flac_mixed(flac):
  if flac:
    sr = flac[0]['sample_rate']
    ss = flac[0]['sample_size']
    for f in flac:
      if f['sample_rate'] != sr or f['sample_size'] != ss:
        return "AlbumMixedFlac"

def tracks_continuous(flac, tracks):
  if flac and tracks:
    for disc in tracks:
        if disc: #TO DO: This does account for the first or last track missing
          range_list =list(range(min(disc), max(disc)+1))
          if range_list != sorted(disc):
            return "AlbumNoncon"
  
  elif flac and not tracks:
    return "AlbumNoInfo"

def flac_format(flac):
  pattern = re.compile(r'^\d{1,2}[-]\d{2,3}[.]', re.I)
  if flac:
    for f in flac:
      if not pattern.search(f['name']) or f['name'][:2].startswith("0"):
        return "AlbumFlacName"

def flac_dupes(flac):
  if flac:
    for f in flac:
      if '(1)' in f["name"] or '(2)' in f["name"]:
        return "AlbumFlacDupes"

def flac_embeds(flac):
  if flac:
    for f in flac:
      if f["pictures"]:
        return "AlbumFlacEmbed"

# check if there are different versions, are they labeled
# check that non flac have quality info

#============== CD CHECKS
def CD_logs(name, logs):
  if logs:
    if "CD-Unchecked" in name:
      perfect_logs = True
      for log in logs:
        logrun = Popen("logchecker analyze \""+  log["path"] + "\" | head -4 | tail -1", shell=True, stdout=PIPE).communicate()[0]
        try:
          score = int(''.join(filter(str.isdigit, logrun.decode("utf-8").rstrip())))
          if score < 100:
            perfect_logs = False
        except:
          return "AlbumCDError"

        
        
      if perfect_logs:
        return "AlbumCDPerfect"
      else:
        return "AlbumCDNotPerfect"

  else:
    return "AlbumCDNoLogs"

def CD_cues(cues):
  if not cues:
    return "AlbumCDNoCues"

def CD_counts(contents_dict, tracks):
  if contents_dict["logs"] and contents_dict["cues"]:
    if contents_dict["flac"]:
      if len(tracks) != len(contents_dict["logs"]) or len(tracks) != len(contents_dict["cues"]):
        return "AlbumCDMissing"

def CD_names(contents_dict):
  bad_names =  False
  if contents_dict["logs"] and contents_dict["cues"]:
    for log in contents_dict["logs"]:
      if log["name"][0:2] != 'CD' or not log["name"][2:len(log["name"])-4].isnumeric():
        bad_names = True
    for cue in contents_dict["cues"]:
      if cue["name"][0:2] != 'CD' or not cue["name"][2:len(cue["name"])-4].isnumeric():
        bad_names = True
  if bad_names:
    return "AlbumCDNames"

  # Todo: check m3u
  # if there's a CD and Web version


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
  album_results_dict["fails"].append(flac_dupes(contents_dict["flac"]))
  album_results_dict["fails"].append(flac_embeds(contents_dict["flac"]))

  if album_results_dict["media_type"] == "CD":
    album_results_dict["fails"].append(CD_logs(name, contents_dict["logs"]))
    album_results_dict["fails"].append(CD_cues(contents_dict["cues"]))
    album_results_dict["fails"].append(CD_counts(contents_dict, track_arr))
    album_results_dict["fails"].append(CD_names(contents_dict))




  if all(x is None for x in album_results_dict["fails"]):
    album_results_dict["no_fails"] = True


  h.remove_nones(album_results_dict["fails"])
  
  for idx, fail in enumerate(album_results_dict["fails"]):
    if h.check_exceptions(album_results_dict["name"], fail):
      print(album_results_dict["name"])
      del album_results_dict["fails"][idx]

  for idx, fail in enumerate(album_results_dict["fails"]):
    new_value = h.fail_to_string(fail)
    album_results_dict["fails"][idx] = new_value

  

    

    
       

  return album_results_dict