import math
import numpy as np
import string
import torch
import whisper
import itertools

WHISPER_MODEL_NAME = "small.en"
WHISPER_MODEL_ROOT = "~/.cache/whisper"
whisper_model = None
whisper_device = None

def split_list(lst, val):
  return [list(group) for k, 
    group in
    itertools.groupby(lst, lambda x: x[0]==val) if not k]

def transcribe_whisper(audio_data, samplerate, chunk_duration, ref_timings):
  global whisper_model
  global whisper_device
  if whisper_model is None:
    whisper_device = ("cuda" if torch.cuda.is_available() else "cpu")
    whisper_model = whisper.load_model(WHISPER_MODEL_NAME, download_root=WHISPER_MODEL_ROOT).to(whisper_device)

  output_list = []
  timing_chunks = split_list(ref_timings, "")
  for timing_chunk in timing_chunks:
    end_time = timing_chunk[-1][1]
    end_sample = int(math.floor(end_time * samplerate))
    chunk_audio = audio_data[:end_sample]
    torch_data = torch.from_numpy(np.frombuffer(chunk_audio, np.int16).flatten().astype(np.float32) / 32768.0)
    result = whisper_model.transcribe(torch_data,language='english',suppress_tokens="")
    predicted_text = result["text"].translate(str.maketrans('', '', string.punctuation)).lower().strip()
    output_list.append((predicted_text, end_time))

  return output_list