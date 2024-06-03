import glob
import os
from pathlib import Path

DEFAULT_ROOT = "data/LibriSpeech/test-clean"

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

def file_id_from_flac_file_name(flac_file_name):
  file_id = Path(flac_file_name).stem
  return file_id

def flac_file_name_from_file_id(file_id, root=DEFAULT_ROOT):
  id_parts = file_id.split("-")
  assert len(id_parts) == 3
  file_name = file_id + ".flac"
  return os.path.join(root, id_parts[0], id_parts[1], file_name)

def alignment_file_name_from_file_id(file_id, root=DEFAULT_ROOT):
  id_parts = file_id.split("-")
  assert len(id_parts) == 3
  file_name =  id_parts[0] + "-" + id_parts[1] + ".alignment.txt"
  return os.path.join(root, id_parts[0], id_parts[1], file_name)

def ref_timings_for_file_id(file_id, root=DEFAULT_ROOT):
  result = None
  align_file_name = alignment_file_name_from_file_id(file_id, root)
  with open(align_file_name, "r") as align_file:
    for align_line in align_file.readlines():
      align_parts = align_line.split(" ")
      if len(align_parts) < 3:
        raise Exception(f"Bad alignment line: '{align_line}'")
      current_file_id = align_parts[0]
      if current_file_id != file_id:
        continue
      reference_words_string = align_parts[1].strip("\"")
      timings_string = align_parts[2].strip("\"")
      reference_words = reference_words_string.lower().split(",")
      timings = list(map(lambda x: float(x), timings_string.split(",")))
      result = list(zip(reference_words, timings))
  return result

def reference_words_before(reference_timings, time_cutoff):
  result = []
  for word, word_end_time in reference_timings:
    if word_end_time > time_cutoff:
      break
    result.append(word)
  return " ".join(result)

def predicted_sentence_before(prediction_timings, time_cutoff):
  result = ""
  for sentence, word_end_time in prediction_timings:
    if word_end_time > time_cutoff:
      break
    result = sentence
  return result

def pred_timings_for_file_id(file_id, root="data/transcriptions"):
  result = {}
  pred_file_names = glob.glob(os.path.join(root, "*.tsv"))
  for pred_file_name in pred_file_names:
    service_name = Path(pred_file_name).stem
    with open(pred_file_name, "r") as pred_file:
      prediction_timings = []
      for pred_line in pred_file.readlines():
        pred_parts = pred_line.split("\t")
        file_path = pred_parts[0]
        current_file_id = Path(file_path).stem
        if current_file_id != file_id:
          continue
        pred_time = float(pred_parts[1])
        pred_sentence = pred_parts[2]
        prediction_timings.append((pred_sentence, pred_time))
    result[service_name] = prediction_timings
  return result  
  