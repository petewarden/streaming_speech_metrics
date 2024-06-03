import math
import os
import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont

from utils import ref_timings_for_file_id, reference_words_before, pred_timings_for_file_id, predicted_sentence_before

WIDTH = 1280
HEIGHT = 960
CHAR_WIDTH = 50
FPS = 30
FRAME_DURATION = (1.0 / FPS)

FONT_TTF_PATH = "data/FreeMono.ttf"
LARGE_FONT_SIZE = 40
LARGE_FONT_LINE_SPACING = 40
SMALL_FONT_SIZE = 20

def draw_large_text(d, x, y, text, color=(255, 255, 255)):
  for line in textwrap.wrap(text.strip(), width=CHAR_WIDTH):
    d.text((x, y), line, font=large_font, fill=color)
    y += LARGE_FONT_LINE_SPACING

if __name__ == '__main__':

  if len(sys.argv) < 2:
    raise Exception("Need to pass in a file id as the first argument")

  file_id = sys.argv[1]
  if len(sys.argv) < 3:
    output_root = "/tmp"
  else:
    output_root = sys.argv[2]

  ref_timings = ref_timings_for_file_id(file_id)
  assert ref_timings is not None

  pred_timings = pred_timings_for_file_id(file_id)
  
  large_font = ImageFont.truetype(FONT_TTF_PATH, LARGE_FONT_SIZE)
  small_font = ImageFont.truetype(FONT_TTF_PATH, SMALL_FONT_SIZE)

  duration = ref_timings[-1][1] + 0.25
  frame_count = int(math.ceil(duration / FRAME_DURATION))
  for frame in range(frame_count):
    time = frame * FRAME_DURATION

    ref_sentence = reference_words_before(ref_timings, time)

    txt = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))

    d = ImageDraw.Draw(txt)

    draw_large_text(d, 10, 40, ref_sentence)

    x = 10
    y = 180
    for service_name in pred_timings.keys():
      display_service_name = service_name[0].upper() + service_name[1:] + ":"
      service_timings = pred_timings[service_name]
      d.text((x, y), display_service_name, font=small_font, fill=(128, 255, 128))
      y += 30
      service_text = predicted_sentence_before(service_timings, time)
      draw_large_text(d, x, y, service_text)
      y += LARGE_FONT_LINE_SPACING * 4

    output_file_name = f"{file_id}_{frame:04d}.png"
    output_path = os.path.join(output_root, output_file_name)
    txt.save(output_path)
