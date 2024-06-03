from jiwer import process_words, wer

import math

from utils import reference_words_before, predicted_sentence_before

def calculate_alignment(reference, hypothesis):

  process_result = process_words(reference, hypothesis)

  ref_words = process_result.references[0]
  hyp_words = process_result.hypotheses[0]
  alignments = process_result.alignments[0]

  word_states = [None] * len(ref_words)
  for alignment in alignments:
    ref_start = alignment.ref_start_idx
    ref_end = alignment.ref_end_idx
    hyp_start = alignment.hyp_start_idx
    hyp_end = alignment.hyp_end_idx
    align_type = alignment.type
    for ref_idx in range(ref_start, ref_end):
      ref_word = ref_words[ref_idx]
      if align_type == "equal":
        word_states[ref_idx] = (ref_word, "correct", ref_word)
      elif align_type == "substitute":
        hyp_word = hyp_words[hyp_start]
        word_states[ref_idx] = (ref_word, "wrong", hyp_word)
      else:
        word_states[ref_idx] = (ref_word, "missing", None)

  return word_states

def calculate_wal_wsl_wer(reference_timings, prediction_timings, chunk_duration):

  transcript_duration = max(reference_timings[-1][1], prediction_timings[-1][1])
  last_chunk = int(math.ceil(transcript_duration / chunk_duration))

  prediction_stats = []
  for reference_timing in reference_timings:
    prediction_stats.append((None, None, None))

  for chunk_index in range(last_chunk):
    current_time = (chunk_index + 1) * chunk_duration
    reference = reference_words_before(reference_timings, current_time)
    if reference == "":
      continue
    hypothesis = predicted_sentence_before(prediction_timings, current_time)
    word_states = calculate_alignment(reference, hypothesis)
    for word_index, word_state in enumerate(word_states):
      previous_stats = prediction_stats[word_index]
      previous_word = previous_stats[0]
      previous_appearance = previous_stats[1]
      previous_stability = previous_stats[2]
      current_state = word_state[1]
      current_word = word_state[2]
      new_appearance = previous_appearance
      new_stability = previous_stability
      new_word = previous_word
      if previous_appearance is None and current_state != "missing":
        new_appearance = current_time
        new_stability = current_time
        new_word = current_word
      elif current_word != previous_word:
        new_stability = current_time
        new_word = current_word
      prediction_stats[word_index] = (new_word, new_appearance, new_stability)

  found_count = 0
  total_wal = 0.0
  total_wsl = 0.0
  for word_index, reference_timing in enumerate(reference_timings):
    stats = prediction_stats[word_index]
    reference_time = reference_timing[1]
    prediction_appearance = stats[1]
    prediction_stability = stats[2]
    if prediction_appearance is None:
      continue
    word_appearance_latency = prediction_appearance - reference_time
    word_stability_latency = prediction_stability - reference_time
    total_wal += word_appearance_latency
    total_wsl += word_stability_latency
    found_count += 1
  
  if found_count > 1:
    mean_wsl = total_wsl / found_count
    mean_wal = total_wal / found_count
  else:
    mean_wsl = 0.0
    mean_wal = 0.0

  mean_wer = wer(reference, hypothesis)
  
  return mean_wal, mean_wsl, mean_wer
  

if __name__ == '__main__':
  reference = "How I wish I could calculate Pi"
  hypothesis = "How I wish I could calc"

  result = calculate_alignment(reference, hypothesis)
  print(result)
  
  reference_timings = [('he', 0.62), ('hoped', 1.01), ('there', 1.13), ('would', 1.31),
                       ('be', 1.44), ('stew', 1.83), ('for', 1.99), ('dinner', 2.36), 
                       ('turnips', 3.07), ('and', 3.24), ('carrots', 3.77), ('and', 3.98), 
                       ('bruised', 4.38), ('potatoes', 5.05), ('and', 5.23), ('fat', 5.6), 
                       ('mutton', 6.02), ('pieces', 6.51), ('to', 6.63), ('be', 6.8), 
                       ('ladled', 7.25), ('out', 7.57), ('in', 7.68), ('thick', 8.15), 
                       ('peppered', 8.64), ('flour', 9.11), ('fattened', 9.56), 
                       ('sauce', 10.12)]

  prediction_timings = [
    ("he", 0.76),
    ("he hoped", 1.06),
    ("he hoped their", 1.30),
    ("he", 1.36),
    ("he", 1.42),
    ("he hoped", 1.66),
    ("he hoped", 1.90),
    ("he hoped", 1.96),
    ("he hoped there would be", 2.02),
    ("he hoped there would be", 2.14),
    ("he hoped there would be", 2.26),
    ("he hoped there would be stew", 2.56),
    ("he hoped there would be stew for", 2.74),
    ("he hoped there would be stew for dinner", 2.86),
    ("he hoped there would be stew for dinner", 3.04),
    ("he hoped there would be stew for dinner", 3.22),
    ("he hoped there would be stew for dinner", 3.34),
    ("he hoped there would be stew for dinner", 3.70),
    ("he hoped there would be stew for dinner", 3.76),
    ("he hoped there would be stew for dinner turnips", 3.82),
    ("he hoped there would be stew for dinner turnips and", 3.94),
    ("he hoped there would be stew for dinner turnips and carrots", 4.36),
    ("he hoped there would be stew for dinner turnips and carrots", 4.42),
    ("he hoped there would be stew for dinner turnips and carrots", 4.48),
    ("he hoped there would be stew for dinner turnips and carrots and", 4.54),
    ("he hoped there would be stew for dinner turnips and carrots and", 4.66),
    ("he hoped there would be stew for dinner turnips and carrots and", 4.90),
    ("he hoped there would be stew for dinner turnips and carrots and bruised", 5.08),
    ("he hoped there would be stew for dinner turnips and carrots and bruised", 5.26),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes", 5.50),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes", 5.62),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and", 5.86),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and", 6.10),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat", 6.22),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat", 6.34),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat", 6.40),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat", 6.64),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton", 6.82),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces", 7.00),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces", 7.18),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to", 7.24),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to", 7.36),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be", 7.42),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be", 7.48),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled", 7.96),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out", 8.08),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out", 8.14),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out", 8.56),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in", 8.68),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick", 8.74),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick", 8.80),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick", 9.16),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick peppered", 9.40),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick peppered", 9.52),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick peppered", 9.64),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick peppered", 9.76),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick peppered", 9.94),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick peppered", 10.06),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick peppered flower", 10.24),
    ("he hoped there would be stew for dinner turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick peppered flower fattened sauce", 10.39),
  ]
  chunk_duration = 0.1

  wal, wsl, wer = calculate_wal_wsl_wer(reference_timings, prediction_timings, chunk_duration)
  print(wal, wsl, wer)