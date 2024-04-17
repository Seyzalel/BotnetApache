#!/bin/bash

while true; do
    python app.py https://agrcbt.unicard.pt/ &
    PID=$!
    # Dorme por um período aleatório entre 7 a 10 segundos
    sleep $((7 + RANDOM % 4))
    kill $PID
done
