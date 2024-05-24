#!/usr/bin/env bash -ex

cd data

wget "http://www.openslr.org/resources/12/test-clean.tar.gz"
tar xzf test-clean.tar.gz
rm -rf test-clean.tar.gz

wget "https://storage.googleapis.com/download.usefulsensors.com/datasets/LibriSpeech-Alignments.zip"
unzip -q LibriSpeech-Alignments.zip
rm -rf LibriSpeech-Alignments.zip

rm -rf unaligned.txt