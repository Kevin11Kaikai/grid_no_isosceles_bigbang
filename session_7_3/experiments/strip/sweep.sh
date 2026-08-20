#!/bin/bash
export OMP_NUM_THREADS=4
for k in 1 2 3 4; do
  for n in $(seq 1 40); do
    if [ $((k*n)) -le 512 ]; then
      r=$(./solveA $k $n 0 --nosym 2>/dev/null | grep '^DONE' | awk '{print $4}')
      echo "$k $n $r"
    fi
  done
done
