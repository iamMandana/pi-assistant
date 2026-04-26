import os
import shutil
from datetime import datetime


def get_time_date():
    # Returns current system time and date in a readable format
    now = datetime.now()
    return now.strftime("%A, %d %B %Y | %H:%M")


def system_health():
    try:
        # Read CPU temperature
        temp = os.popen("vcgencmd measure_temp").read().strip()

        # Get disk usage statistics for root filesystem
        total, used, free = shutil.disk_usage("/")

        # Convert free space to GB
        free_gb = free // (2**30)

        # Combine temperature and storage info into a single response
        return f"{temp}, {free_gb}GB free space"
    except:
        return "Unable to read system health"
