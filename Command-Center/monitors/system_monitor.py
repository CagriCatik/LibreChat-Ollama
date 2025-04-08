# system_monitor.py

import GPUtil
from psutil import cpu_percent, virtual_memory

def get_cpu_usage():
    return cpu_percent(interval=0.1)

def get_memory_usage():
    return virtual_memory().percent

def get_gpu_usage():
    gpus = GPUtil.getGPUs()
    gpu_data = []
    if gpus:
        for i, gpu in enumerate(gpus):
            gpu_data.append({
                "index": i,
                "load": gpu.load * 100,
                "memory_used": gpu.memoryUsed
            })
    return gpu_data
