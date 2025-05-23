#!/bin/bash

# ポート5000を使ってるプロセスをkill
PORT=5000
while lsof -ti tcp:$PORT >/dev/null; do
  PID=$(lsof -ti tcp:$PORT)
  echo "Port $PORT is still in use by PID $PID. Killing..."
  kill -9 $PID
  sleep 1
done

# 仮想環境をアクティベート
source .venv/bin/activate

# Flaskアプリ起動
python app.py