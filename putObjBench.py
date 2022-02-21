#! /bin/python3

import os
import subprocess
import shlex
import json
from multiprocessing.pool import ThreadPool as Pool

# rgw user/instance info
ACCESS_KEY = "XPAXFYP1JALDA7GBX2M5"
SECRET_KEY = "EH0OC2m2XIlf28UyJaibJxGMGAuN0GiCpnwd2M1U"
ENDPOINT = "http://localhost:8000"

# test configuration
NUM_WORKERS = 3
NUM_ITER_PER_WORKER = 2
OBJ_SIZE = "1Mb"
# TOTAL_NUM_OPERATIONS = NUM_SAMPLE_PER_ITER * NUM_ITER_PER_WORKER * NUM_WORKERS
NUM_SAMPLE_PER_ITER = 10

pwd = os.getcwd()

def merge_reports(report1, report2):
    if not report1:
        return report2
    if not report2:
        return report1
    for i in range(0,2):
        # report1["Parameters"]["label"] += f", " + report2["Parameters"]["label"]

        report1["Tests"][i]["Duration Avg"] = \
            (report1["Tests"][i]["Duration Avg"] + report2["Tests"][i]["Duration Avg"] ) / 2

        report1["Tests"][i]["Duration Max"] = max(
            report1["Tests"][i]["Duration Max"],
            report2["Tests"][i]["Duration Max"]
        )

        report1["Tests"][i]["Duration Min"] = min(
            report1["Tests"][i]["Duration Min"],
            report2["Tests"][i]["Duration Min"]
        )

        report1["Tests"][i]["Errors Count"] += report2["Tests"][i]["Errors Count"]

        report1["Tests"][i]["RPS"] = \
            (report1["Tests"][i]["RPS"] + report2["Tests"][i]["RPS"] ) / 2

        report1["Tests"][i]["Total Duration (s)"] += \
            report2["Tests"][i]["Total Duration (s)"]

        report1["Tests"][i]["Total Requests Count"] += \
            report2["Tests"][i]["Total Requests Count"]

        report1["Tests"][i]["Total Transferred (MB)"] = \
            (report1["Tests"][i]["Total Transferred (MB)"] +
             report2["Tests"][i]["Total Transferred (MB)"] ) / 2

        report1["Tests"][i]["Ttfb Avg"] = \
            (report1["Tests"][i]["Ttfb Avg"] +
             report2["Tests"][i]["Ttfb Avg"] ) / 2

        report1["Tests"][i]["Ttfb Max"] = max(
            report1["Tests"][i]["Ttfb Max"],
            report2["Tests"][i]["Ttfb Max"]
        )

        report1["Tests"][i]["Ttfb Min"] = min(
            report1["Tests"][i]["Ttfb Min"],
            report2["Tests"][i]["Ttfb Min"]
        )
    return report1


def worker(worker_num):
    try:
        dir_path = os.path.join(pwd, f"worker_{worker_num}")
        os.makedirs(dir_path, mode = 0o777, exist_ok=True)
        bucket_prefix = f"bench-bkt-{worker_num}"
        final_report = {}
        for iteration in range(1, NUM_ITER_PER_WORKER+1):
            bucket_name = f"{bucket_prefix}-{iteration}"
            cmd = (f"{pwd}/s3bench -accessKey={ACCESS_KEY} -accessSecret={SECRET_KEY}"
                   f" -bucket={bucket_name} -endpoint={ENDPOINT} -numClients=1"
                   f" -numSamples={NUM_SAMPLE_PER_ITER} -objectSize={OBJ_SIZE}"
                   f" --region=default -o={dir_path}/report -t=json")
            print("Executing the Command: ", cmd, "\n")
            s3bench_cmd = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                                                                         stderr=subprocess.PIPE)
            _, stderr = s3bench_cmd.communicate()
            if stderr.decode():
                print("stderr: ", stderr)
            else:
                with open(f"{dir_path}/report", "r") as report_file:
                    report = report_file.readline()
                    report = json.loads(report)
                    # print(report["Tests"][0])
                    final_report = merge_reports(final_report, report)
                    os.remove(f"{pwd}/s3bench-{report['Parameters']['label']}.log")
        # print(final_report)
        with open(f"{dir_path}/final_report", 'w') as f:
            f.write(json.dumps(final_report))
        # write the final report to file
    except Exception as e:
        print(e)

pool = Pool(NUM_WORKERS)

for i in range(1,NUM_WORKERS+1):
    pool.apply_async(worker, (i,))

pool.close()
pool.join()

avg_report = {}
for i in range(1,NUM_WORKERS+1):
    file_path = os.path.join(pwd, f"worker_{i}", "final_report")
    # print(file_path)
    with open(file_path, 'r') as f:
        curr_report = f.readline()
        curr_report = json.loads(curr_report)
        avg_report = merge_reports(avg_report, curr_report)
print(f"Average Report from {NUM_WORKERS} workers:\n",
      json.dumps(avg_report, sort_keys=False, indent=4))
