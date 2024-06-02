import asyncio
import math
import numpy as np
import string

# This example uses aiofile for asynchronous file reads.
# It's not a dependency of the project but can be installed
# with `pip install aiofile`.
import aiofile

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from amazon_transcribe.utils import apply_realtime_delay

REGION = "us-west-2"
LANGUAGE = "en-US"

class TranscriptionEventHandler(TranscriptResultStreamHandler):
  async def handle_transcript_event(self, transcript_event: TranscriptEvent):
    results = transcript_event.transcript.results
    if len(results) == 0:
      return
    result = results[0]
    alt = result.alternatives[0]
    normalized_partial = alt.transcript.translate(str.maketrans('', '', string.punctuation)).lower()
    normalized_full = self.prefix + normalized_partial
    self.output_list.append((normalized_full, result.end_time))
    if not result.is_partial:
      self.prefix += normalized_partial + " "


async def transcribe_amazon_async(audio_data, samplerate, chunk_duration):
  client = TranscribeStreamingClient(region=REGION)

  stream = await client.start_stream_transcription(
      language_code=LANGUAGE,
      media_sample_rate_hz=samplerate,
      media_encoding="pcm",
  )

  chunk_size = chunk_duration * samplerate
  chunk_count = int(math.ceil(audio_data.shape[0] / chunk_size))
  audio_chunks = np.array_split(audio_data, chunk_count)

  async def write_chunks():
    for chunk in audio_chunks:
      await stream.input_stream.send_audio_event(audio_chunk=chunk.data.tobytes())
    await stream.input_stream.end_stream()

  handler = TranscriptionEventHandler(stream.output_stream)
  handler.output_list = []
  handler.prefix = ""
  await asyncio.gather(write_chunks(), handler.handle_events())
  
  return handler.output_list

def transcribe_amazon(audio_data, samplerate, chunk_duration, _):
  return asyncio.run(transcribe_amazon_async(audio_data, samplerate, chunk_duration))

if __name__ == '__main__':
  import math
  import numpy as np
  import soundfile as sf

  chunk_duration = 0.1
  flac_file_name = "data/LibriSpeech/test-clean/61/70970/61-70970-0040.flac"
  audio_data, samplerate = sf.read(flac_file_name, dtype="int16")
  transcription_results = transcribe_amazon(audio_data, samplerate, chunk_duration, None)
  print(transcription_results)