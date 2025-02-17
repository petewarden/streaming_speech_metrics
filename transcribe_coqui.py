#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import argparse
import json
import math
import shlex
import subprocess
import sys
import wave
from timeit import default_timer as timer

import numpy as np
from stt import Model, version

try:
    from shlex import quote
except ImportError:
    from pipes import quote

# Downloaded in download_data.sh.
COQUI_MODEL_PATH = "data/cache/large-model.tflite"
COQUI_SCORER_PATH = "data/cache/large-vocabulary.scorer"

coqui_model = None

def transcribe_coqui(audio_data, samplerate, chunk_duration, _):
  global coqui_model
  if coqui_model is None:
    coqui_model = Model(COQUI_MODEL_PATH)
    coqui_model.enableExternalScorer(COQUI_SCORER_PATH)

  chunk_size = chunk_duration * samplerate
  chunk_count = int(math.ceil(audio_data.shape[0] / chunk_size))
  chunks = np.array_split(audio_data, chunk_count)

  output_list = []
  stream = coqui_model.createStream()
  previous_results = ""
  for chunk_index, chunk in enumerate(chunks):
    end_time = chunk_index * chunk_duration + (chunk.shape[0] / samplerate) 
    stream.feedAudioContent(chunk)
    intermediate_results = stream.intermediateDecode()
    if intermediate_results == previous_results:
      continue
    output_list.append((intermediate_results, end_time))
    previous_results = intermediate_results

  output_list.append((coqui_model.stt(audio_data), end_time))
  return output_list

if __name__ == "__main__":
    main()
