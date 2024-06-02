import glob
import math
import numpy as np
from pathlib import Path
import soundfile as sf
import os

from transcribe_amazon import transcribe_amazon
from transcribe_google import transcribe_google
from transcribe_whisper import transcribe_whisper

def gather_alignments(subsubfolder):
  align_file_names = glob.glob(os.path.join(subsubfolder, "*.alignment.txt"))
  ref_timings_by_file = {}
  for align_file_name in align_file_names:
    with open(align_file_name, "r") as align_file:
      for align_line in align_file.readlines():
        align_parts = align_line.split(" ")
        assert len(align_parts) >= 3
        file_id = align_parts[0]
        reference_words_string = align_parts[1].strip("\"")
        timings_string = align_parts[2].strip("\"")
        reference_words = reference_words_string.lower().split(",")
        timings = list(map(lambda x: float(x), timings_string.split(",")))
        reference_timings = list(zip(reference_words, timings))
        ref_timings_by_file[file_id] = reference_timings
  return ref_timings_by_file

def gather_predictions(service, dataset_root, output_path, chunk_duration):
  subfolders = [f.path for f in os.scandir(dataset_root) if f.is_dir()]

  with open(output_path, "w") as output_file:
    for subfolder in subfolders:
      subsubfolders = [f.path for f in os.scandir(subfolder) if f.is_dir()]
      for subsubfolder in subsubfolders:
        ref_timings_by_file = gather_alignments(subsubfolder)
        flac_file_names = glob.glob(os.path.join(subsubfolder, "*.flac"))
        for flac_file_name in flac_file_names:
          file_id = Path(flac_file_name).stem
          print(file_id)
          audio_data, samplerate = sf.read(flac_file_name, dtype="int16")
          ref_timings = ref_timings_by_file[file_id]
          if service == "amazon":
            transcription_results = transcribe_amazon(audio_data, samplerate, chunk_duration, ref_timings)
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