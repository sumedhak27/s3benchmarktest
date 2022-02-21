#! /bin/python3

import psutil
import time
import json

ini_mem_usage = psutil.virtual_memory()[2]
ini_cpu_usage = psutil.cpu_percent(interval=5, percpu=True)
print("Initial Readings\t│\t", end="")
print("Memory: ", ini_mem_usage, "\t│\tCPU: ", ini_cpu_usage)
max_mem_usage = ini_mem_usage
max_cpu_usage = ini_cpu_usage.copy()

print("------------------------------------------------",
      "-----------------------------------------------------")
try:
  while True:
    cur_mem_usage = psutil.virtual_memory()[2]
    max_mem_usage = max(max_mem_usage, cur_mem_usage)

    cur_cpu_usage = psutil.cpu_percent(interval=5, percpu=True)
    for i in range(len(max_cpu_usage)):
      max_cpu_usage[i] = max(max_cpu_usage[i], cur_cpu_usage[i])

    print("Current Readings\t│\tMemory: ", cur_mem_usage, "\t│\tCPU: ", cur_cpu_usage, "\t", end="\r")
except KeyboardInterrupt:
  per_cpu_incr = list(map(lambda x, y: round(x - y, 4) , max_cpu_usage, ini_cpu_usage))
  print("\n------------------------------------------------",
        "-----------------------------------------------------")
  print("Max % Reached\t│\t", end="")
  print("Memory: ", max_mem_usage, "\t│\t", end="")
  print("CPU: ", max_cpu_usage)
  print("------------------------------------------------",
        "-----------------------------------------------------")
  print("Max % Change\t│\t", end="")
  print("Memory: ", round(max_mem_usage-ini_mem_usage, 4), "\t│\t", end="")
  print("CPU: ", per_cpu_incr)
  with open("./resource_usage", 'w') as f:
    f.write(json.dumps({"Memory Usage": {
                "Initial": ini_mem_usage,
                "Peak": max_mem_usage,
                "Max % Change": round(max_mem_usage-ini_mem_usage, 4)
             },
            "CPU Usage": {
                "Initial": ini_cpu_usage,
                "Peak": max_cpu_usage,
                "Max % Change": per_cpu_incr   
            }
          }))
