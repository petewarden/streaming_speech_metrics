from jiwer import process_words

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

if __name__ == '__main__':
  reference = "How I wish I could calculate Pi"
  hypothesis = "How I wish I could calc"

  result = calculate_alignment(reference, hypothesis)
  print(result)