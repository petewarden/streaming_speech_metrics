# Streaming Speech Metrics

Python library for analyzing the latency and accuracy of streaming speech to text systems


`python calculate_file_metrics.py data/LibriSpeech/test-clean data/amazon_transcriptions.tsv`

`data/amazon_transcriptions.tsv: WAL=1.42s, WSL=1.47s, WER=0.05 (4.63%)`

`python calculate_file_metrics.py data/LibriSpeech/test-clean data/google_transcriptions.tsv`

`data/google_transcriptions.tsv: WAL=1.52s, WSL=1.60s, WER=0.07 (6.77%)`

sudo apt install -y git
curl https://pyenv.run | bash
echo 'export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc

sudo apt-get update
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev zip
pyenv install 3.10.14
pyenv global 3.10.14
python -m pip install aiofile amazon_transcribe google-cloud-speech whisper numpy soundfile stt torch
git clone https://github.com/petewarden/streaming_speech_metrics
cd streaming_speech_metrics
./download_datasets.sh
python gather_predictions.py coqui