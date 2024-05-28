import glob
import math
import numpy as np
from pathlib import Path
import soundfile as sf
import os

from transcribe_amazon import transcribe_amazon
from transcribe_google import transcribe_google

def gather_predictions(service, dataset_root, output_path, chunk_duration):
  subfolders = [f.path for f in os.scandir(dataset_root) if f.is_dir()]

  with open(output_path, "w") as output_file:
    for subfolder in subfolders:
      subsubfolders = [f.path for f in os.scandir(subfolder) if f.is_dir()]
      for subsubfolder in subsubfolders:
        flac_file_names = glob.glob(os.path.join(subsubfolder, "*.flac"))
        for flac_file_name in flac_file_names:
          file_id = Path(flac_file_name).stem
          print(file_id)
          audio_data, samplerate = sf.read(flac_file_name, dtype="int16")
          if service == "amazon":
            transcription_results = transcribe_amazon(audio_data, samplerate, chunk_duration)
          elif service == "google":
            transcription_results = transcribe_google(audio_data, samplerate, chunk_duration)
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
  OUTPUT_PATH = f"data/{service}_transcriptions.tsv"
  CHUNK_DURATION = 0.1

  gather_predictions(service, DATASET_ROOT, OUTPUT_PATH, CHUNK_DURATION)