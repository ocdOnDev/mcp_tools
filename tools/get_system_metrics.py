"""Gets system metrics such as CPU, memory, and disk usage.

This tool retrieves key performance indicators from the host system,
including CPU load, memory usage, and disk space utilization.
"""

import psutil
from pydantic import BaseModel


class Output(BaseModel):
    cpu_percent: float
    mem_percent: float
    disk_percent: float


def execute() -> Output:
    return Output(
        cpu_percent=psutil.cpu_percent(interval=0.2),
        mem_percent=psutil.virtual_memory().percent,
        disk_percent=psutil.disk_usage("/").percent,
    )
