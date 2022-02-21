#! /bin/python3

import psutil
import time

initial_cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
max_cpu_usage = initial_cpu_usage.copy()
print("CPU Usage -> \nInitial: ", initial_cpu_usage)

try:
  while True:
    curr_cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
    for i in range(len(max_cpu_usage)):
      max_cpu_usage[i] = max(max_cpu_usage[i], curr_cpu_usage[i]);
    print(f"Max: {max_cpu_usage}  Current: {curr_cpu_usage}", end='\r')
    time.sleep(5)
except KeyboardInterrupt:
  print("\n__________________________________________________________________")
  print(f"CPU Usage ->\n\tInitial: {initial_cpu_usage}\n\tMax: {max_cpu_usage}")
  per_increased = list(map(lambda x, y: round(x - y, 4) , max_cpu_usage, initial_cpu_usage))
  print(f"\t% Increased: {per_increased}")