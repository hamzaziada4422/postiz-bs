#!/bin/bash
# One-time setup in a fresh session: TTS packages and voice models.
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q kokoro-onnx soundfile numpy
mkdir -p models
[ -f models/kokoro-v1.0.onnx ] || curl -sSL -o models/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f models/voices-v1.0.bin ] || curl -sSL -o models/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
echo setup done
