#!/bin/bash
VENV=/home/yay/apps/nora/backend/.venv
PY=$VENV/bin/python
LOG=/tmp/nora_pip.log
echo "=== START $(date) ===" > $LOG
$PY -m pip install --upgrade pip >> $LOG 2>&1
echo "--- pip rc=$? ---" >> $LOG
# fastembed (ONNX, ringan) + chromadb + openai. NO torch.
$PY -m pip install fastembed chromadb openai >> $LOG 2>&1
echo "--- install rc=$? ---" >> $LOG
$PY -c "import fastembed, chromadb, openai; print('VERIFY fastembed', fastembed.__version__, '| chromadb', chromadb.__version__, '| openai', openai.__version__)" >> $LOG 2>&1
echo "=== DONE $(date) ===" >> $LOG
