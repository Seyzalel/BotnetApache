#!/bin/bash

# Define o tempo total de execução para cada script antes de ser reiniciado.
TOTAL_TIME=10
# Define o tempo de sobreposição em segundos (tempo antes do término do script atual para iniciar um novo).
OVERLAP_TIME=4

while true; do
    # Inicia o script Python passando a URL como argumento em segundo plano.
    python app.py https://agrcbt.unicard.pt/ &
    PID=$!

    # Aguarda o tempo total menos o tempo de sobreposição.
    sleep $((TOTAL_TIME - OVERLAP_TIME))

    # Inicia uma nova instância do script antes de terminar o processo anterior.
    python app.py https://agrcbt.unicard.pt/ &

    # Aguarda o tempo de sobreposição antes de matar o processo anterior.
    sleep $OVERLAP_TIME

    # Mata o processo anterior.
    kill $PID
done
