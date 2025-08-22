import psutil
import requests
import socket
import time
from datetime import datetime
import pytz

# Configuration
API_ENDPOINT = "http://localhost:8000/api/processes/"
INTERVAL = 2 # Seconds between data collections

def get_process_info():
    processes = []
    hostname = socket.gethostname()
    timestamp = datetime.now(pytz.UTC).isoformat(timespec='microseconds')

    for proc in psutil.process_iter(['pid', 'name', 'ppid', 'cpu_percent', 'memory_info', 'io_counters']):

        try:
            name = proc.info['name'] or 'Unknown'
            parent_pid = int(proc.info['ppid'] or 0)
            cpu_percent = float(proc.info['cpu_percent'] if proc.info['cpu_percent'] is not None else 0.0)
            if cpu_percent > 100.0 * psutil.cpu_count():
                cpu_percent = 0.0
            memory_usage = float(proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0.0)

            # Disk I/O (bytes read/written per second)
            disk_io = proc.io_counters() if proc.info.get('io_counters') else None
            disk_usage = (disk_io.read_bytes + disk_io.write_bytes) / 1024 / 1024 if disk_io else 0.0  # MB/s

            # Network I/O (bytes sent/received per second)
            # Note: psutil.net_io_counters() is per-interface, not per-process, so this is a placeholder
            net_usage = 0.0  # Mbps (requires additional logic)

            if name.strip() == '':
                print(f"Skipping process with blank name: PID={proc.info['pid']}")
                continue

            if parent_pid == proc.info['pid']:
                print(f"Warning: Process PID={proc.info['pid']} has itself as parent, setting parent_pid to 0")
                parent_pid = 0

            proc_info = {
                'hostname': str(hostname),
                'timestamp': timestamp,
                'pid': int(proc.info['pid']),
                'name': str(name),
                'parent_pid': parent_pid,
                'cpu_percent': cpu_percent,
                'memory_usage': memory_usage,
                'disk_usage': disk_usage,
                'net_usage': net_usage,
            }
            processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error processing process PID={proc.info.get('pid', 'unknown')}: {e}")
            try:
                proc_info = {
                    'hostname': str(hostname),
                    'timestamp': timestamp,
                    'pid': int(proc.info['pid']),
                    'name': 'Unknown (Access Denied)',
                    'parent_pid': int(proc.info['ppid'] or 0),
                    'cpu_percent': 0.0,
                    'memory_usage': 0.0,
                    'disk_usage': 0.0,
                    'net_usage': 0.0,
                }
                processes.append(proc_info)
            except Exception as e2:
                print(f"Failed to include minimal process info for PID={proc.info.get('pid', 'unknown')}: {e2}")
        except ValueError as e:
            print(f"ValueError for process PID={proc.info.get('pid', 'unknown')}: {e}")
            continue
    print(f"Collected {len(processes)} processes")
    return processes

def send_data(processes):
    try:
        print(f"Sending {len(processes)} processes: First process: {processes[:1]}")
        response = requests.post(API_ENDPOINT, json=processes)
        if response.status_code == 201:
            print(f"Data sent successfully at {datetime.now(pytz.UTC)}")
        else:
            print(f"Failed to send data: {response.status_code}")
            print(f"Response content: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending data: {e}")

def main():
    print("Starting process monitoring agent...")
    while True:
        processes = get_process_info()
        if processes:
            send_data(processes)
        else:
            print("No valid processes to send.")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()