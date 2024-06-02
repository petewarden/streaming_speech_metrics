from google.cloud import speech

def transcribe_google(audio_data, samplerate, chunk_duration, _):
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
  prefix = ""
  for response in responses:
    result = response.results[0]
    end_time = result.result_end_time.ToMilliseconds() / 1000.0
    alternatives = result.alternatives
    prediction = alternatives[0].transcript.lower()
    output_list.append((prefix + prediction, end_time))
    if result.is_final:
      prefix += prediction + " "

  return output_list

if __name__ == '__main__':
  import math
  import numpy as np
  import soundfile as sf

  chunk_duration = 0.1
  flac_file_name = "data/LibriSpeech/test-clean/61/70970/61-70970-0040.flac"
  audio_data, samplerate = sf.read(flac_file_name, dtype="int16")
  transcription_results = transcribe_google(audio_data, samplerate, chunk_duration, None)
  print(transcription_results)