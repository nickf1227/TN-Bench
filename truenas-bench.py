import subprocess
import json
import os
import threading
import time
import argparse
import sys
import datetime

# ANSI color codes
COLORS = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
    "ENDC": "\033[0m",
}

def color_text(text, color_name):
    """Apply color to text if output is a terminal"""
    if sys.stdout.isatty() and color_name in COLORS:
        return f"{COLORS[color_name]}{text}{COLORS['ENDC']}"
    return text

def print_header(title):
    """Print a formatted header with separators"""
    separator = "#" * 60
    print()
    print(color_text(separator, "BLUE"))
    print(color_text(f"# {title.center(56)} #", "BOLD"))
    print(color_text(separator, "BLUE"))
    print()

def print_subheader(title):
    """Print a subheader with separators"""
    separator = "-" * 60
    print()
    print(color_text(separator, "CYAN"))
    print(color_text(f"| {title.center(56)} |", "BOLD"))
    print(color_text(separator, "CYAN"))
    print()

def print_section(title):
    """Print a section separator"""
    separator = "=" * 60
    print()
    print(color_text(separator, "GREEN"))
    print(color_text(f" {title} ", "BOLD"))
    print(color_text(separator, "GREEN"))
    print()

def print_warning(message):
    """Print a warning message"""
    print(color_text(f"! WARNING: {message}", "YELLOW"))

def print_error(message):
    """Print an error message"""
    print(color_text(f"! ERROR: {message}", "RED"))

def print_info(message):
    """Print an informational message"""
    print(color_text(f"* {message}", "CYAN"))

def print_success(message):
    """Print a success message"""
    print(color_text(f"✓ {message}", "GREEN"))

def print_bullet(message):
    """Print a bullet point"""
    print(color_text(f"• {message}", "ENDC"))

def get_user_confirmation():
    print_header("TN-Bench v1.10")
    print(color_text("TN-Bench is an OpenSource Software Script that uses standard tools to", "BOLD"))
    print(color_text("Benchmark your System and collect various statistical information via", "BOLD"))
    print(color_text("the TrueNAS API.", "BOLD"))
    print()

    print_info("TN-Bench will create a Dataset in each of your pools for testing purposes")
    print_info("that will consume 20 GiB of space for every thread in your system.")
    print()

    print_warning("This test will make your system EXTREMELY slow during its run.")
    print_warning("It is recommended to run this test when no other workloads are running.")
    print()

    print_info("ZFS ARC will impact your results. You can set zfs_arc_max to 1 to prevent ARC caching.")
    print_info("Setting it back to 0 restores default behavior but requires a system restart.")

    print_section("Confirmation")
    continue_benchmark = input(color_text("Would you like to continue? (yes/no): ", "BOLD"))
    if continue_benchmark.lower() != 'yes':
        print_info("Exiting TN-Bench.")
        exit(0)

def get_system_info():
    result = subprocess.run(['midclt', 'call', 'system.info'], capture_output=True, text=True)
    system_info = json.loads(result.stdout)
    return system_info

def print_system_info_table(system_info):
    print_subheader("System Information")
    fields = [
        ("Version", system_info.get("version", "N/A")),
        ("Load Average (1m)", system_info.get("loadavg", ["N/A", "N/A", "N/A"])[0]),
        ("Load Average (5m)", system_info.get("loadavg", ["N/A", "N/A", "N/A"])[1]),
        ("Load Average (15m)", system_info.get("loadavg", ["N/A", "N/A", "N/A"])[2]),
        ("Model", system_info.get("model", "N/A")),
        ("Cores", system_info.get("cores", "N/A")),
        ("Physical Cores", system_info.get("physical_cores", "N/A")),
        ("System Product", system_info.get("system_product", "N/A")),
        ("Physical Memory (GiB)", f"{system_info.get('physmem', 0) / (1024 ** 3):.2f}")
    ]

    max_field_length = max(len(field[0]) for field in fields)
    max_value_length = max(len(str(field[1])) for field in fields)

    # Print table header
    print(color_text(f"{'Field'.ljust(max_field_length)} | {'Value'.ljust(max_value_length)}", "BOLD"))
    print(color_text(f"{'-' * max_field_length}-+-{'-' * max_value_length}", "GREEN"))

    # Print table rows
    for field, value in fields:
        print(f"{color_text(field.ljust(max_field_length), 'CYAN')} | {str(value).ljust(max_value_length)}")

def get_pool_info():
    result = subprocess.run(['midclt', 'call', 'pool.query'], capture_output=True, text=True)
    pool_info = json.loads(result.stdout)
    return pool_info

def print_pool_info_table(pool_info):
    for pool in pool_info:
        print_subheader("Pool Information")
        fields = [
            ("Name", pool.get("name", "N/A")),
            ("Path", pool.get("path", "N/A")),
            ("Status", pool.get("status", "N/A"))
        ]

        topology = pool.get("topology", {})
        data = topology.get("data", []) if topology else []

        vdev_count = len(data)
        disk_count = sum(len(vdev.get("children", [])) for vdev in data)

        fields.append(("VDEV Count", vdev_count))
        fields.append(("Disk Count", disk_count))

        max_field_length = max(len(field[0]) for field in fields)
        max_value_length = max(len(str(field[1])) for field in fields)

        # Print table header
        print(color_text(f"{'Field'.ljust(max_field_length)} | {'Value'.ljust(max_value_length)}", "BOLD"))
        print(color_text(f"{'-' * max_field_length}-+-{'-' * max_value_length}", "GREEN"))

        # Print table rows
        for field, value in fields:
            print(f"{color_text(field.ljust(max_field_length), 'CYAN')} | {str(value).ljust(max_value_length)}")

        # Print VDEV table
        print()
        print(color_text("VDEV Name  | Type           | Disk Count", "BOLD"))
        print(color_text("-----------+----------------+---------------", "GREEN"))

        for vdev in data:
            vdev_name = vdev.get("name", "N/A")
            vdev_type = vdev.get("type", "N/A")
            vdev_disk_count = len(vdev.get("children", []))
            print(f"{vdev_name.ljust(11)} | {vdev_type.ljust(14)} | {vdev_disk_count}")

def get_disk_info():
    result = subprocess.run(['midclt', 'call', 'disk.query'], capture_output=True, text=True)
    disk_info = json.loads(result.stdout)
    return disk_info

def get_pool_membership():
    result = subprocess.run(['midclt', 'call', 'pool.query'], capture_output=True, text=True)
    pool_info = json.loads(result.stdout)
    pool_membership = {}
    for pool in pool_info:
        topology = pool.get("topology", {})
        data = topology.get("data", []) if topology else []
        for vdev in data:
            for disk in vdev.get("children", []):
                pool_membership[disk["guid"]] = pool["name"]
    return pool_membership

def print_disk_info_table(disk_info, pool_membership):
    print_subheader("Disk Information")
    print_info("The TrueNAS API returns N/A for the Pool for boot devices and disks not in a pool.")

    fields = ["Name", "Model", "Serial", "ZFS GUID", "Pool", "Size (GiB)"]
    max_field_length = max(len(field) for field in fields)

    # Calculate max value length
    max_value_length = 0
    for disk in disk_info:
        for field in fields:
            value = str(disk.get(field.lower(), "N/A"))
            if len(value) > max_value_length:
                max_value_length = len(value)

    # Print table header
    print(color_text(f"{'Field'.ljust(max_field_length)} | {'Value'.ljust(max_value_length)}", "BOLD"))
    print(color_text(f"{'-' * max_field_length}-+-{'-' * max_value_length}", "GREEN"))

    # Print table rows
    for disk in disk_info:
        pool_name = pool_membership.get(disk.get("zfs_guid"), "N/A")
        size_gib = (disk.get("size", 0) or 0) / (1024 ** 3)
        values = [
            disk.get("name", "N/A"),
            disk.get("model", "N/A"),
            disk.get("serial", "N/A"),
            disk.get("zfs_guid", "N/A"),
            pool_name,
            f"{size_gib:.2f}"
        ]

        for i, (field, value) in enumerate(zip(fields, values)):
            field_text = color_text(field.ljust(max_field_length), "CYAN")
            print(f"{field_text} | {str(value).ljust(max_value_length)}")

        # Print separator between disks
        print(color_text(f"{'-' * max_field_length}-+-{'-' * max_value_length}", "GREEN"))

def create_dataset(pool_name):
    # Escape spaces in the pool name
    escaped_pool_name = pool_name.replace(" ", "\\ ")
    dataset_name = f"{escaped_pool_name}/tn-bench"
    dataset_config = {
        "name": dataset_name,
        "recordsize": "1M",
        "compression": "OFF",
        "sync": "DISABLED"
    }

    # Check if the dataset already exists
    result = subprocess.run(['midclt', 'call', 'pool.dataset.query'], capture_output=True, text=True)
    if result.returncode != 0:
        print_error(f"Error querying datasets: {result.stderr}")
        return None

    existing_datasets = json.loads(result.stdout)
    dataset_exists = any(ds['name'] == dataset_name for ds in existing_datasets)

    if not dataset_exists:
        result = subprocess.run(['midclt', 'call', 'pool.dataset.create', json.dumps(dataset_config)], capture_output=True, text=True)
        if result.returncode != 0:
            print_error(f"Error creating dataset {dataset_name}: {result.stderr}")
            return None
        print_success(f"Created temporary dataset: {dataset_name}")

        # Fetch the updated dataset information
        result = subprocess.run(['midclt', 'call', 'pool.dataset.query'], capture_output=True, text=True)
        if result.returncode != 0:
            print_error(f"Error querying datasets after creation: {result.stderr}")
            return None
        existing_datasets = json.loads(result.stdout)

    # Return the mountpoint of the dataset
    for ds in existing_datasets:
        if ds['name'] == dataset_name:
            print_success(f"Dataset {dataset_name} created successfully.")
            return ds['mountpoint']

    print_error(f"Dataset {dataset_name} was not found after creation.")
    return None

def run_dd_command(command):
    subprocess.run(command, shell=True)

def run_write_benchmark(threads, bytes_per_thread, block_size, file_prefix, dataset_path, iterations=2):
    print_info(f"Running DD write benchmark with {threads} threads...")
    speeds = []

    for run in range(iterations):
        start_time = time.time()

        threads_list = []
        for i in range(threads):
            command = f"dd if=/dev/urandom of={dataset_path}/{file_prefix}{i}.dat bs={block_size} count={bytes_per_thread} status=none"
            thread = threading.Thread(target=run_dd_command, args=(command,))
            thread.start()
            threads_list.append(thread)

        for thread in threads_list:
            thread.join()

        end_time = time.time()
        total_time_taken = end_time - start_time
        total_bytes = threads * bytes_per_thread * 1024 * 1024
        write_speed = total_bytes / 1024 / 1024 / total_time_taken
        speeds.append(write_speed)
        print_info(f"Run {run + 1} write speed: {color_text(f'{write_speed:.2f} MB/s', 'YELLOW')}")

    average_write_speed = sum(speeds) / len(speeds) if speeds else 0
    print_success(f"Average write speed: {color_text(f'{average_write_speed:.2f} MB/s', 'GREEN')}")
    return speeds, average_write_speed

def run_read_benchmark(threads, bytes_per_thread, block_size, file_prefix, dataset_path, iterations=2):
    print_info(f"Running DD read benchmark with {threads} threads...")
    speeds = []

    for run in range(iterations):
        start_time = time.time()

        threads_list = []
        for i in range(threads):
            command = f"dd if={dataset_path}/{file_prefix}{i}.dat of=/dev/null bs={block_size} count={bytes_per_thread * 2} status=none"
            thread = threading.Thread(target=run_dd_command, args=(command,))
            thread.start()
            threads_list.append(thread)

        for thread in threads_list:
            thread.join()

        end_time = time.time()
        total_time_taken = end_time - start_time
        total_bytes = threads * bytes_per_thread * 2 * 1024 * 1024
        read_speed = total_bytes / 1024 / 1024 / total_time_taken
        speeds.append(read_speed)
        print_info(f"Run {run + 1} read speed: {color_text(f'{read_speed:.2f} MB/s', 'YELLOW')}")

    average_read_speed = sum(speeds) / len(speeds) if speeds else 0
    print_success(f"Average read speed: {color_text(f'{average_read_speed:.2f} MB/s', 'GREEN')}")
    return speeds, average_read_speed

def run_benchmarks_for_pool(pool_name, cores, bytes_per_thread, block_size, file_prefix, dataset_path, iterations=2):
    escaped_pool_name = pool_name.replace(" ", "\\ ")
    thread_counts = [1, cores // 4, cores // 2, cores]
    results = []

    for threads in thread_counts:
        print_section(f"Testing Pool: {escaped_pool_name} - Threads: {threads}")
        write_speeds, average_write_speed = run_write_benchmark(
            threads, bytes_per_thread, block_size, file_prefix, dataset_path, iterations
        )
        read_speeds, average_read_speed = run_read_benchmark(
            threads, bytes_per_thread, block_size, file_prefix, dataset_path, iterations
        )
        results.append({
            "threads": threads,
            "write_speeds": write_speeds,
            "average_write_speed": average_write_speed,
            "read_speeds": read_speeds,
            "average_read_speed": average_read_speed,
            "iterations": iterations
        })

    print_header(f"DD Benchmark Results for Pool: {escaped_pool_name}")
    for result in results:
        print_subheader(f"Threads: {result['threads']}")

        # Extract values to avoid nested f-string issues
        write_speeds = result['write_speeds']
        avg_write = result['average_write_speed']
        read_speeds = result['read_speeds']
        avg_read = result['average_read_speed']

        for i, speed in enumerate(write_speeds):
            print_bullet(f"1M Seq Write Run {i+1}: {color_text(f'{speed:.2f} MB/s', 'YELLOW')}")
        print_bullet(f"1M Seq Write Avg: {color_text(f'{avg_write:.2f} MB/s', 'GREEN')}")

        for i, speed in enumerate(read_speeds):
            print_bullet(f"1M Seq Read Run {i+1}: {color_text(f'{speed:.2f} MB/s', 'YELLOW')}")
        print_bullet(f"1M Seq Read Avg: {color_text(f'{avg_read:.2f} MB/s', 'GREEN')}")

    return results

def run_disk_read_benchmark(disk_info, system_info, iterations=2):
    print_header("Disk Read Benchmark")
    print_info("This benchmark tests the 4K sequential read performance of each disk")
    print_info("To work around ARC caching, reads data = min(system RAM, disk size)")

    results = []

    def run_dd_read_command(disk_name, read_size_gib):
        print_info(f"Testing disk: {disk_name}")
        command = f"dd if=/dev/{disk_name} of=/dev/null bs=4K count={int(read_size_gib * 1024 * 1024 // 4)} status=none"
        start_time = time.time()
        subprocess.run(command, shell=True)
        end_time = time.time()
        total_time_taken = end_time - start_time
        total_bytes = read_size_gib * 1024 * 1024 * 1024
        read_speed = total_bytes / 1024 / 1024 / total_time_taken
        return read_speed

    system_ram_gib = system_info.get('physmem', 0) / (1024 ** 3)

    for disk in disk_info:
        disk_name = disk.get("name", "N/A")
        disk_size_gib = disk.get("size", 0) / (1024 ** 3)
        read_size_gib = min(system_ram_gib, disk_size_gib)

        if disk_name != "N/A":
            speeds = []
            print_section(f"Testing Disk: {disk_name}")
            for run_num in range(iterations):
                speed = run_dd_read_command(disk_name, read_size_gib)
                speeds.append(speed)
                print_info(f"Run {run_num+1}: {color_text(f'{speed:.2f} MB/s', 'YELLOW')}")
            average_speed = sum(speeds) / len(speeds) if speeds else 0
            print_success(f"Average: {color_text(f'{average_speed:.2f} MB/s', 'GREEN')}")
            results.append({
                "disk": disk_name,
                "speeds": speeds,
                "average_speed": average_speed,
                "iterations": iterations
            })

    print_header("Disk Read Benchmark Results")
    for result in results:
        print_subheader(f"Disk: {result['disk']}")

        # Extract values to avoid nested f-string issues
        speeds = result['speeds']
        avg_speed = result['average_speed']

        for i, speed in enumerate(speeds):
            print_bullet(f"Run {i+1}: {color_text(f'{speed:.2f} MB/s', 'YELLOW')}")
        print_bullet(f"Average: {color_text(f'{avg_speed:.2f} MB/s', 'GREEN')}")

    return results

def cleanup(file_prefix, dataset_path):
    print_info("Cleaning up test files...")
    escaped_dataset_path = dataset_path.replace(" ", "\\ ")
    for file in os.listdir(escaped_dataset_path):
        if file.startswith(file_prefix) and file.endswith('.dat'):
            os.remove(os.path.join(escaped_dataset_path, file))

def delete_dataset(dataset_name):
    escaped_dataset_name = dataset_name.replace(" ", "\\ ")
    print_info(f"Deleting dataset: {escaped_dataset_name}")
    subprocess.run(['midclt', 'call', 'pool.dataset.delete', json.dumps({"id": escaped_dataset_name, "recursive": False, "force": False})], capture_output=True, text=True)

def get_dataset_available_bytes(pool_name):
    dataset_name = f"{pool_name}/tn-bench"
    result = subprocess.run(['midclt', 'call', 'pool.dataset.query'], capture_output=True, text=True)
    if result.returncode != 0:
        print_error(f"Error querying datasets: {result.stderr}")
        return 0
    try:
        datasets = json.loads(result.stdout)
    except json.JSONDecodeError:
        print_error("Failed to parse dataset query result.")
        return 0
    for ds in datasets:
        if ds.get('name') == dataset_name:
            available_info = ds.get('available', {})
            parsed_bytes = available_info.get('parsed')
            if parsed_bytes is not None:
                return parsed_bytes
            value_str = available_info.get('value', '0')
            try:
                unit = value_str[-1] if value_str[-1] in {'T', 'G', 'M', 'K', 'B'} else 'B'
                numeric_part = value_str[:-1] if unit != 'B' else value_str
                numeric_value = float(numeric_part)
                unit_multipliers = {
                    'T': 1024 ** 4,
                    'G': 1024 ** 3,
                    'M': 1024 ** 2,
                    'K': 1024,
                    'B': 1
                }
                return int(numeric_value * unit_multipliers[unit])
            except (ValueError, KeyError):
                print_error(f"Invalid value for available bytes: {value_str}")
                return 0
    print_error(f"Dataset {dataset_name} not found.")
    return 0

def save_results_to_json(results, output_path):
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)
        print_success(f"Benchmark results saved to: {os.path.abspath(output_path)}")
    except Exception as e:
        print_error(f"Error saving results to JSON: {str(e)}")

def select_pools_to_test(pool_info):
    print_header("Pool Selection")
    print_info("Available pools:")
    for i, pool in enumerate(pool_info):
        print_bullet(f"{i+1}. {pool['name']}")

    print_info("Options:")
    print_bullet("1. Enter specific pool numbers (comma separated)")
    print_bullet("2. Type 'all' to test all pools")
    print_bullet("3. Type 'none' to skip pool testing")

    while True:
        selection = input(color_text("\nEnter your choice [all]: ", "BOLD")).strip()
        if not selection:
            return pool_info

        if selection.lower() == 'all':
            return pool_info

        if selection.lower() == 'none':
            return []

        try:
            selected_indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
            selected_pools = []
            for idx in selected_indices:
                if 0 <= idx < len(pool_info):
                    selected_pools.append(pool_info[idx])
                else:
                    print_warning(f"Index {idx+1} is out of range. Skipping.")
            return selected_pools
        except ValueError:
            print_error("Invalid input. Please enter pool numbers (e.g., '1,3'), 'all', or 'none'.")

def ask_about_disk_benchmark():
    print_header("Individual Disk Benchmark")
    response = input(color_text("Run individual disk read benchmark? (yes/no) [yes]: ", "BOLD")).strip().lower()
    if response in ['', 'y', 'yes']:
        return True
    elif response in ['n', 'no']:
        print_info("Skipping individual disk benchmark.")
        return False
    else:
        print_warning("Invalid input. Defaulting to yes.")
        return True

def ask_iteration_count(benchmark_type):
    print_header(f"{benchmark_type} Benchmark Iterations")
    print_info("How many times should we run each test?")
    print_bullet("1. Run each test once (faster)")
    print_bullet("2. Run each test twice (default, more accurate)")

    while True:
        response = input(color_text("\nEnter iteration count (1 or 2) [2]: ", "BOLD")).strip()
        if not response:
            return 2

        try:
            count = int(response)
            if count in [1, 2]:
                return count
            print_error("Please enter 1 or 2")
        except ValueError:
            print_error("Invalid input. Please enter 1 or 2")

def ask_zfs_iterations():
    return ask_iteration_count("ZFS Pool")

def ask_disk_iterations():
    return ask_iteration_count("Individual Disk")

# ================ VERSIONED SCHEMA FUNCTIONS =================
def restructure_to_v1(benchmark_results, start_iso, end_iso, total_time_taken_minutes):
    """Convert raw results to versioned schema v1.0"""
    # Build pool membership map
    pool_membership = {}
    for pool in benchmark_results["pools"]:
        topology = pool.get("topology", {})
        data_vdevs = topology.get("data", []) if topology else []
        for vdev in data_vdevs:
            children = vdev.get("children", [])
            for child in children:
                if isinstance(child, dict) and "guid" in child:
                    pool_membership[child["guid"]] = pool["name"]

    # Build the new structured output
    new_output = {
        "schema_version": "1.0",
        "metadata": {
            "start_timestamp": start_iso,
            "end_timestamp": end_iso,
            "duration_minutes": total_time_taken_minutes,
            "benchmark_config": benchmark_results.get("benchmark_config", {})
        },
        "system": {
            "os_version": benchmark_results["system_info"].get("version"),
            "load_average_1m": benchmark_results["system_info"].get("loadavg", [None, None, None])[0],
            "load_average_5m": benchmark_results["system_info"].get("loadavg", [None, None, None])[1],
            "load_average_15m": benchmark_results["system_info"].get("loadavg", [None, None, None])[2],
            "cpu_model": benchmark_results["system_info"].get("model"),
            "logical_cores": benchmark_results["system_info"].get("cores"),
            "physical_cores": benchmark_results["system_info"].get("physical_cores"),
            "system_product": benchmark_results["system_info"].get("system_product"),
            "memory_gib": benchmark_results["system_info"].get("physmem", 0) / (1024**3)
        },
        "pools": [],
        "disks": []
    }

    # Process pools
    for pool in benchmark_results["pools"]:
        vdevs = []
        topology = pool.get("topology", {})
        data_vdevs = topology.get("data", []) if topology else []
        for vdev in data_vdevs:
            vdevs.append({
                "name": vdev.get("name"),
                "type": vdev.get("type"),
                "disk_count": len(vdev.get("children", []))
            })

        pool_entry = {
            "name": pool.get("name"),
            "path": pool.get("path"),
            "status": pool.get("status"),
            "vdevs": vdevs
        }

        # Add benchmark results if available
        if "benchmark_results" in pool:
            pool_entry["benchmark"] = pool["benchmark_results"]
        else:
            pool_entry["benchmark"] = None

        new_output["pools"].append(pool_entry)

    # Process disks
    for disk in benchmark_results["disks"]:
        disk_entry = {
            "name": disk.get("name"),
            "model": disk.get("model"),
            "serial": disk.get("serial"),
            "zfs_guid": disk.get("zfs_guid"),
            "pool": pool_membership.get(disk.get("zfs_guid"), None),
            "size_gib": (disk.get("size", 0) or 0) / (1024**3)
        }

        # Add disk benchmark results if available
        disk_bench = None
        if "disk_benchmark" in benchmark_results:
            for d in benchmark_results["disk_benchmark"]:
                if d["disk"] == disk.get("name"):
                    disk_bench = {
                        "speeds": d["speeds"],
                        "average_speed": d["average_speed"],
                        "iterations": d["iterations"]
                    }
                    break
        disk_entry["benchmark"] = disk_bench

        new_output["disks"].append(disk_entry)

    return new_output

# ================ MAIN EXECUTION =================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TN-Bench System Benchmark')
    parser.add_argument('--output', type=str, default='./tn_bench_results.json',
                        help='Path to output JSON file (default: ./tn_bench_results.json)')
    args = parser.parse_args()

    # Record exact start time for metadata
    start_time = time.time()
    start_iso = datetime.datetime.fromtimestamp(start_time).isoformat()

    # Initialize results container
    benchmark_results = {
        "system_info": {},
        "pools": [],
        "disks": [],
        "benchmark_config": {
            "selected_pools": [],
            "disk_benchmark_run": False,
            "zfs_iterations": 2,
            "disk_iterations": 2
        }
    }

    get_user_confirmation()

    # Collect system information
    system_info = get_system_info()
    benchmark_results["system_info"] = system_info
    print_system_info_table(system_info)

    # Collect pool information
    pool_info = get_pool_info()
    benchmark_results["pools"] = pool_info
    print_pool_info_table(pool_info)

    # Collect disk information
    disk_info = get_disk_info()
    pool_membership = get_pool_membership()
    benchmark_results["disks"] = disk_info
    print_disk_info_table(disk_info, pool_membership)

    # Ask user which pools to test
    selected_pools = select_pools_to_test(pool_info)
    benchmark_results["benchmark_config"]["selected_pools"] = [p['name'] for p in selected_pools]

    # Ask about ZFS iterations
    zfs_iterations = 2
    if selected_pools:
        zfs_iterations = ask_zfs_iterations()
    benchmark_results["benchmark_config"]["zfs_iterations"] = zfs_iterations

    # Ask about disk benchmark
    run_disk_bench = ask_about_disk_benchmark()
    benchmark_results["benchmark_config"]["disk_benchmark_run"] = run_disk_bench

    # Ask about disk iterations
    disk_iterations = 2
    if run_disk_bench:
        disk_iterations = ask_disk_iterations()
    benchmark_results["benchmark_config"]["disk_iterations"] = disk_iterations

    cores = system_info.get("cores", 1)
    bytes_per_thread_series_1 = 10240
    block_size_series_1 = "1M"
    file_prefix_series_1 = "file_"

    print_header("DD Benchmark Starting")
    print_info(f"Using {cores} threads for the benchmark.")
    print_info(f"ZFS tests will run {zfs_iterations} time(s) per configuration")
    if run_disk_bench:
        print_info(f"Disk tests will run {disk_iterations} time(s) per disk")

    # Run benchmarks for each selected pool
    for pool in selected_pools:
        pool_name = pool.get('name', 'N/A')
        print_header(f"Testing Pool: {pool_name}")
        print_info(f"Creating test dataset for pool: {pool_name}")
        dataset_name = f"{pool_name}/tn-bench"
        dataset_path = create_dataset(pool_name)
        if dataset_path:
            # Check available space
            available_bytes = get_dataset_available_bytes(pool_name)
            required_bytes = 20 * cores * (1024 ** 3)
            available_gib = available_bytes / (1024 ** 3)
            required_gib = 20 * cores

            print_section("Space Verification")
            print_info(f"Available space: {available_gib:.2f} GiB")
            print_info(f"Space required:  {required_gib:.2f} GiB (20 GiB/thread × {cores} threads)")

            if available_bytes < required_bytes:
                print_warning(f"Insufficient space in dataset {pool_name}/tn-bench")
                print_warning(f"Minimum required: {required_gib} GiB")
                print_warning(f"Available:        {available_gib:.2f} GiB")
                proceed = input(color_text("\nProceed anyway? (yes/no): ", "BOLD")).lower()
                if proceed != 'yes':
                    print_info(f"Skipping benchmarks for pool {pool_name}")
                    delete_dataset(f"{pool_name}/tn-bench")
                    continue

            print_success("Sufficient space available - proceeding with benchmarks")

            pool_results = run_benchmarks_for_pool(
                pool_name, cores, bytes_per_thread_series_1,
                block_size_series_1, file_prefix_series_1, dataset_path,
                iterations=zfs_iterations
            )

            # Store pool benchmark results
            for pool_entry in benchmark_results["pools"]:
                if pool_entry["name"] == pool_name:
                    pool_entry["benchmark_results"] = pool_results

            cleanup(file_prefix_series_1, dataset_path)

    # Run disk benchmark if requested
    if run_disk_bench:
        disk_bench_results = run_disk_read_benchmark(disk_info, system_info, iterations=disk_iterations)
        benchmark_results["disk_benchmark"] = disk_bench_results

    # Record end time and duration
    end_time = time.time()
    total_time_taken = end_time - start_time
    total_time_taken_minutes = total_time_taken / 60
    end_iso = datetime.datetime.fromtimestamp(end_time).isoformat()

    print_header("Benchmark Complete")
    print_success(f"Total benchmark time: {total_time_taken_minutes:.2f} minutes")

    # Convert to versioned schema
    v1_results = restructure_to_v1(
        benchmark_results,
        start_iso,
        end_iso,
        total_time_taken_minutes
    )

    # Cleanup datasets
    for pool in selected_pools:
        pool_name = pool.get('name', 'N/A')
        dataset_name = f"{pool_name}/tn-bench"
        delete = input(color_text(f"\nDelete testing dataset {dataset_name}? (yes/no): ", "BOLD")).lower()
        if delete == 'yes':
            delete_dataset(dataset_name)
            print_success(f"Dataset {dataset_name} deleted.")
        else:
            print_info(f"Dataset {dataset_name} not deleted.")

    # Save results to JSON
    save_results_to_json(v1_results, args.output)
