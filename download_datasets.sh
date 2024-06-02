#!/bin/bash -ex

cd data

wget "http://www.openslr.org/resources/12/test-clean.tar.gz"
tar xzf test-clean.tar.gz
rm -rf test-clean.tar.gz

wget "https://storage.googleapis.com/download.usefulsensors.com/datasets/LibriSpeech-Alignments.zip"
unzip -q LibriSpeech-Alignments.zip
rm -rf LibriSpeech-Alignments.zip

rm -rf unaligned.txt

mkdir -p cache
curl -L https://github.com/coqui-ai/STT-models/releases/download/english/coqui/v1.0.0-large-vocab/model.tflite -o cache/large-model.tflite
curl -L https://github.com/coqui-ai/STT-models/releases/download/english%2Fcoqui%2Fv1.0.0-large-vocab/large_vocabulary.scorer -o cache/large-vocabulary.scorer
