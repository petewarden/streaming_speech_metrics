import glob
import math
import numpy as np
import soundfile as sf
import os

from transcribe_amazon import transcribe_amazon
from transcribe_coqui import transcribe_coqui
from transcribe_google import transcribe_google
from transcribe_whisper import transcribe_whisper
from utils import gather_alignments, file_id_from_flac_file_name

def gather_predictions(service, dataset_root, output_path, chunk_duration):
  subfolders = [f.path for f in os.scandir(dataset_root) if f.is_dir()]

  with open(output_path, "w") as output_file:
    for subfolder in subfolders:
      subsubfolders = [f.path for f in os.scandir(subfolder) if f.is_dir()]
      for subsubfolder in subsubfolders:
        ref_timings_by_file = gather_alignments(subsubfolder)
        flac_file_names = glob.glob(os.path.join(subsubfolder, "*.flac"))
        for flac_file_name in flac_file_names:
          file_id = file_id_from_flac_file_name(flac_file_name)
          print(file_id)
          audio_data, samplerate = sf.read(flac_file_name, dtype="int16")
          ref_timings = ref_timings_by_file[file_id]
          if service == "amazon":
            transcription_results = transcribe_amazon(audio_data, samplerate, chunk_duration, ref_timings)
          elif service == "coqui":
            transcription_results = transcribe_coqui(audio_data, samplerate, chunk_duration, ref_timings)
          elif service == "google":
            transcription_results = transcribe_google(audio_data, samplerate, chunk_duration, ref_timings)
          elif service == "whisper":
            transcription_results = transcribe_whisper(audio_data, samplerate, chunk_duration, ref_timings)
          else:
            raise Exception(f"Unknown service {service}")
          for entry in transcription_results:
            sentence = entry[0]
            time = entry[1]
            output_file.write(f"{flac_file_name}\t{time: 0.2f}\t{sentence}\n")

if __name__ == '__main__':
  import sys
  
  service = sys.argv[1]
  DATASET_ROOT = "data/LibriSpeech/test-clean"
  OUTPUT_PATH = f"data/transcriptions/{service}.tsv"
  CHUNK_DURATION = 0.1

  gather_predictions(service, DATASET_ROOT, OUTPUT_PATH, CHUNK_DURATION)