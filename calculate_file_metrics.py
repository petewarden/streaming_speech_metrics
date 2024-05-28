import glob
import os
from pathlib import Path
import sys

from streaming_speech_metrics import calculate_wal_wsl_wer

if __name__ == '__main__':

  CHUNK_DURATION = 0.1
  dataset_root = sys.argv[1]
  pred_file_name = sys.argv[2]

  ref_timings_by_file = {}

  subfolders = [f.path for f in os.scandir(dataset_root) if f.is_dir()]
  for subfolder in subfolders:
    subsubfolders = [f.path for f in os.scandir(subfolder) if f.is_dir()]
    for subsubfolder in subsubfolders:
        align_file_names = glob.glob(os.path.join(subsubfolder, "*.alignment.txt"))
        for align_file_name in align_file_names:
          with open(align_file_name, "r") as align_file:
            for align_line in align_file.readlines():
              align_parts = align_line.split(" ")
              if len(align_parts) < 3:
                raise Exception(f"Bad alignment line: '{align_line}'")
              file_id = align_parts[0]
              reference_words_string = align_parts[1].strip("\"")
              timings_string = align_parts[2].strip("\"")
              reference_words = reference_words_string.lower().split(",")
              timings = list(map(lambda x: float(x), timings_string.split(",")))
              reference_timings = list(zip(reference_words, timings))
              ref_timings_by_file[file_id] = reference_timings

  wal_total = 0.0
  wsl_total = 0.0
  wer_total = 0.0
  total_duration = 0.0
  with open(pred_file_name, "r") as pred_file:
    prediction_timings = []
    previous_file_id = None
    for pred_line in pred_file.readlines():
      pred_parts = pred_line.split("\t")
      file_path = pred_parts[0]
      file_id = Path(file_path).stem
      pred_time = float(pred_parts[1])
      pred_sentence = pred_parts[2]
      if previous_file_id is not None and file_id != previous_file_id:
        reference_timings = ref_timings_by_file[previous_file_id]
        wal, wsl, wer = calculate_wal_wsl_wer(reference_timings, prediction_timings, CHUNK_DURATION)
        ref_end_time = reference_timings[-1][1]
        wal_total += wal * ref_end_time
        wsl_total += wsl * ref_end_time
        wer_total += wer * ref_end_time
        total_duration += ref_end_time
        prediction_timings = []
      previous_file_id = file_id
      prediction_timings.append((pred_sentence, pred_time))
    if previous_file_id is not None:
      reference_timings = ref_timings_by_file[previous_file_id]
      wal, wsl, wer = calculate_wal_wsl_wer(reference_timings, prediction_timings, CHUNK_DURATION)
      ref_end_time = reference_timings[-1][1]
      wal_total += wal * ref_end_time
      wsl_total += wsl * ref_end_time
      wer_total += wer * ref_end_time
      total_duration += ref_end_time

  mean_wal = wal_total / total_duration
  mean_wsl = wsl_total / total_duration
  mean_wer = wer_total / total_duration
  print(f"{pred_file_name}: WAL={mean_wal:0.2f}s, WSL={mean_wsl:0.2f}s, WER={mean_wer:0.2f}")