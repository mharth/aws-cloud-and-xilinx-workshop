import logging
import sys
import time
import glob
import subprocess
import os
import json
import greengrasssdk
import datetime
from threading import Timer


# Setup logging to stdout
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


client = greengrasssdk.client('iot-data')


# This is where the video inference results are stored
# Assume there is only 1 folder with suffix `-aws-cloud-and-xilinx-workshop`
bucket = glob.glob1('/home/xilinx', '*-aws-cloud-and-xilinx-workshop')[0]
sync_folder_path = os.path.join("/home/xilinx", bucket)
download_path = "/home/xilinx/download"
topic = "/unit_controller/video_inference"
parameters = 'parameters.txt'

def run_pydeephi_yolo():
    num_seconds = 5
    threshold = 2

    payload = {'message': 'starting video inference'}
    client.publish(topic=topic, payload=json.dumps(payload))


    if os.path.isfile(os.path.join(download_path, parameters)):
        with open(os.path.join(download_path, parameters)) as f:
            num_seconds = int(f.readline())
            threshold = int(f.readline())
    logger.info("Running subprocess in {}".format(sync_folder_path))
    logger.info("Parameter number of seconds: {}".format(num_seconds))
    logger.info("Parameter threshold: {}".format(threshold))

    ret = subprocess.check_call(
            'cd {0} && PYTHONPATH=/usr/lib/python3.6 '
            '/usr/local/bin/pydeephi_yolo.py {1} {2}'.format(
            sync_folder_path, num_seconds, threshold), shell=True)
    logger.info("{}".format(ret))

    # wait long enough time for application to finish
    time.sleep(num_seconds)
    time.sleep(3)

    payload = {'message': 'ended video inference'}
    client.publish(topic=topic, payload=json.dumps(payload))
    return

while (1):
    run_pydeephi_yolo()
    time.sleep(1)

def lambda_handler(event, context):
    return
