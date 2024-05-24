import glob
import math
import numpy as np
import soundfile as sf
import os

from google.cloud import speech

def transcribe_google(audio_data, samplerate, chunk_duration):
  """Streams transcription of the given audio file."""

  client = speech.SpeechClient()

  chunk_size = chunk_duration * samplerate
  chunk_count = int(math.ceil(audio_data.shape[0] / chunk_size))
  stream = np.array_split(audio_data, chunk_count)

  requests = list(
    speech.StreamingRecognizeRequest(audio_content=chunk.tobytes()) for chunk in stream
  )

  config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=samplerate,
    language_code="en-US",
  )

  streaming_config = speech.StreamingRecognitionConfig(
    config=config, interim_results=True
  )

  # streaming_recognize returns a generator.
  responses = client.streaming_recognize(
    config=streaming_config,
    requests=requests,
  )

  output_list = []
  for response in responses:
    result = response.results[0]
    end_time = result.result_end_time.ToSeconds() + (result.result_end_time.ToMilliseconds() / 1000.0)
    alternatives = result.alternatives
    output_list.append((alternatives[0].transcript.lower(), end_time))

  return output_list

def gather_predictions(service, dataset_root, output_path, chunk_duration):
  subfolders = [f.path for f in os.scandir(dataset_root) if f.is_dir()]

  with open(output_path, "w") as output_file:
    for subfolder in subfolders:
      subsubfolders = [f.path for f in os.scandir(subfolder) if f.is_dir()]
      for subsubfolder in subsubfolders:
        flac_file_names = glob.glob(os.path.join(subsubfolder, "*.flac"))
        for flac_file_name in flac_file_names:
          print(flac_file_name)
          audio_data, samplerate = sf.read(flac_file_name, dtype="int16")
          if service == "google":
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