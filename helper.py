import os, pathlib
from mutagen.flac import FLAC
from PIL import Image

audio_formats = ['.3gp', '.8svx', '.aa','.aac','.aax','.act','.aiff','.alac','.amr','.ape','.au','.awb','.cda','.dss','.dvf','.flac','.gsm','.iklax','.ivs','.m4a','.m4b','.m4p','.mmf','.mp3','.mpc','.msv','.nmf','.ogg','.oga','.mogg','.opus','.ra','.rm','.raw','.rf64','.sln','.tta','.voc','.vox','.wav','.webm','.wma','.wv']
image_formats = ['.jpg','.jpeg','.png','.gif','.webp','.tiff','.psd','.raw','.bmp','.heif',',indd','.svg','.ai','.eps']

def try_dir(path):
  try:
    return os.listdir(path)
  except:
    return []
  
def try_m_flac(obj, key):
  try:
    return int(obj[key][0])
  except:
    return ''

def perform_checks(func_arr):
  messages_arr = []
  for check in func_arr:
    val = check()
    if val:
      messages_arr.append(val.values())
  return messages_arr
          
def find_folder_media_type(name):
    mediaType = ''
    brackets = []
    for i, letter in enumerate(name):
      if letter == '[':
        brackets.append([i+1])

    for i, bracket in enumerate(brackets):
      end = find_nth(name, ']', i+1)
      brackets[i].append(end)
      extracted = name[brackets[i][0]:brackets[i][1]]

      if 'WEB' in extracted:
        mediaType = 'WEB'

      elif 'Vinyl' in extracted:
        mediaType = 'Vinyl'

      elif ('CD' in extracted or 'LOG' in extracted or 'SELF-RIP' in extracted):
        if 'CD' not in mediaType:
          mediaType = 'CD'
          # self.messages.append(Message("CheckCD", "Folder uses 'CD' as media type. Inspect contents", 1))
      elif 'Cassette' in extracted:
        mediaType = 'Cassette'

    return mediaType
        
def find_nth(string, substring, n):
  if (n == 1):
      return string.find(substring)
  else:
      return string.find(substring, find_nth(string, substring, n - 1) + 1)

def extract_album_contents(path):
  content = {
    'is_valid': False,
    'folders': [],
    'flac': [],
    'non_flac': [],
    'logs': [],
    'cues': [],
    'images': [],
    'other': [],
  }
  
  # catch if album path is a file
  album_arr = try_dir(path)
  if album_arr:
    for file in album_arr:
      content['is_valid'] = True
      # get extension
      ext = pathlib.Path(file).suffix.lower()
      # create variable for file path
      file_path = path + '/' + file
      
      # add folders to contents
      if ext == '':
        content['folders'].append({'file_type':'folder', 'name': file, 'path': file_path})
      
      # add flac files to contents
      elif ext == '.flac':
        m_flac = FLAC(file_path)
        content['flac'].append({
          'file_type':'flac',
          'name': file,
          'path': file_path,
          'sample_rate': FLAC(file_path).info.sample_rate,
          'sample_size': FLAC(file_path).info.bits_per_sample,
          'media_type': try_m_flac(m_flac, 'media'),
          'disc_number': try_m_flac(m_flac, 'discnumber'),
          'total_discs': try_m_flac(m_flac, 'totaldiscs'),
          'track_number': try_m_flac(m_flac, 'tracknumber'),
          'disc_total': try_m_flac(m_flac, 'disctotal'),
          'track_total': try_m_flac(m_flac, 'tracktotal'),
        }) 
      
      # add non-flac audio files to contents
      elif any(ext in s for s in audio_formats):
        content['non_flac'].append({
          'file_type':'flac',
          'name': file,
          'path': file_path,
          'ext': ext,
        })
      
      # add images to contents
      elif any(ext in s for s in image_formats):
        i = Image.open(file_path)
        content['images'].append({
          'file_type':'image',
          'name': file,
          'path': file_path,
          'ext': ext,
          'size': i.size
        })
      
      elif ext == '.log':
        content['logs'].append({
          'file_type':'log',
          'name': file,
          'path': file_path,
        })
        
      elif ext == '.cue':
        content['cues'].append({
          'file_type':'cue',
          'name': file,
          'path': file_path,
        })
      
      else:
        content['other'].append({
          'file_type':'other',
          'name': file,
          'path': file_path,
          'ext': ext
        })
        

        
  return content    
    
def populate_track_number_arr(contents):
  return_arr = []
  
  if contents['flac']:
    if contents['flac'][0]['disc_total']:
      for x in range(contents['flac'][0]['disc_total']):
          return_arr.append([])
          
      for file in contents['flac']:
        try:
          discNumber = int(file['disc_number'])
          return_arr[discNumber-1].append(file['track_number'])
        except:
          print(contents)
        
  
  return return_arr

def is_file(path):
  if not try_dir(path):
    return True
  else:
    return False

def remove_nones(arr):
  for item in arr[:]:
    if not item:
      arr.remove(item)
  return arr