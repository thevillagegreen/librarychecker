import helper as h
import artist_checks as artist_checks
import album_checks as album_checks
import os

def run(library_path):
  print("Running checker...")
  print("Using path: " + library_path)
  results_dict = {
    "stats": {
      "total_checks_made":0,
      "total_fails":0,
      "score":0,
      "perfect_albums":0,
      "letter_count":0,
      "nonascii_letter_count":0,
      "artist_count":0,
      "album_count":0,
      "track_count":0,
      "log_count":0,
      "cue_count":0,
      "artwork_count":0,
      "image_count":0
    },
    "library": [],
    "artist": {},
  }

  artist_arr = []
  library_arr = h.try_dir(library_path)

  # parse through top of library, get all instances of non-ascii letter folders into the library arr
  for letter in library_arr:
    results_dict["stats"]["letter_count"] += 1
    # If letter is the "!ascii" which holds letter folder that are non-ascii
    if letter == "!ascii":
      notascii_path = library_path + "/!ascii"
      notascii_arr = h.try_dir(notascii_path)
      for notascii_letter in notascii_arr:
        results_dict["stats"]["nonascii_letter_count"] += 1
        library_arr.append("!ascii/"+ notascii_letter)
  
  library_arr.remove("!ascii")

  # populate artist arr from letter folders
  for letter in library_arr:
    letter_path = library_path + "/" + letter
    letter_arr = h.try_dir(letter_path)
    for artist in letter_arr:
      artist_arr.append({"name":artist, "path":letter_path+"/"+artist})
  
  for artist in artist_arr:
    results_dict["stats"]["artist_count"] += 1
    
    results_dict["artist"][artist["name"]] = {
      "name": artist["name"],
      "path": artist["path"],
      "albums": {},
      "fails": [],
      "no_fails": False
    }

    results_dict["artist"][artist["name"]]["fails"] = artist_checks.run(artist["name"], artist["path"])["fails"]
    
    if all(x is None for x in results_dict["artist"][artist["name"]]["fails"]):
      results_dict["artist"][artist["name"]]["no_fails"] = True

    album_arr = h.try_dir(artist["path"])
    
    for album in album_arr:
      if not os.path.isfile(artist["path"] + "/" + album):
        
        album_results_obj = album_checks.run(album, artist["path"] + "/" + album)

        results_dict["artist"][artist["name"]]["albums"][album] = album_results_obj
        
        
  
  for album in results_dict["artist"]["Ariel Pink"]["albums"]:
    print(results_dict["artist"]["Ariel Pink"]["albums"][album])

  return results_dict
