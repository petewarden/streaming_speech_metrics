# Streaming Speech Metrics

Python library for analyzing the latency and accuracy of streaming speech to text systems


`python calculate_file_metrics.py data/LibriSpeech/test-clean data/amazon_transcriptions.tsv`

`data/amazon_transcriptions.tsv: WAL=1.42s, WSL=1.47s, WER=0.05 (4.63%)`

`python calculate_file_metrics.py data/LibriSpeech/test-clean data/google_transcriptions.tsv`

`data/google_transcriptions.tsv: WAL=1.52s, WSL=1.60s, WER=0.07 (6.77%)`