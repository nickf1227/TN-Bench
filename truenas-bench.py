import subprocess
import json
import os
import signal
import threading
import time
import argparse

def get_user_confirmation():
    print("\n###################################")
    print("#                                 #")
    print("#          TN-Bench v1.08         #")
    print("#          MONOLITHIC.            #")
    print("#                                 #")
    print("###################################")
    print("TN-Bench is an OpenSource Software Script that uses standard tools to Benchmark your System and collect various statistical information via the TrueNAS API.")
    print("\nTN-Bench will make a Dataset in each of your pools for the purposes of this testing that will consume 20 GiB of space for every thread in your system during its run.")
    print("\nAfter which time we will prompt you to delete the dataset which was created.")
    print("###################################")
    print("\nWARNING: This test will make your system EXTREMELY slow during its run. It is recommended to run this test when no other workloads are running.")
    print("\nNOTE: ZFS ARC will also be used and will impact your results. This may be undesirable in some circumstances, and the zfs_arc_max can be set to 1 (which means 1 byte) to prevent ARC from caching.")
    print("\nNOTE: Setting it back to 0 will restore the default behavior, but the system will need to be restarted!")
    print("###################################")
    continue_benchmark = input("\nWould you like to continue? (yes/no): ")
    if continue_benchmark.lower() != 'yes':
        print("Exiting TN-Bench.")
        exit(0)

def get_system_info():
    result = subprocess.run(['midclt', 'call', 'system.info'], capture_output=True, text=True)
    system_info = json.loads(result.stdout)
    return system_info

def print_system_info_table(system_info):
    print("\n### System Information ###")
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

    print(f"{'Field'.ljust(max_field_length)} | {'Value'.ljust(max_value_length)}")
    print(f"{'-' * max_field_length}-+-{'-' * max_value_length}")

    for field, value in fields:
        print(f"{field.ljust(max_field_length)} | {str(value).ljust(max_value_length)}")

def get_pool_info():
    result = subprocess.run(['midclt', 'call', 'pool.query'], capture_output=True, text=True)
    pool_info = json.loads(result.stdout)
    return pool_info

def print_pool_info_table(pool_info):
    for pool in pool_info:
        print("\n### Pool Information ###")
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

        print(f"{'Field'.ljust(max_field_length)} | {'Value'.ljust(max_value_length)}")
        print(f"{'-' * max_field_length}-+-{'-' * max_value_length}")

        for field, value in fields:
            print(f"{field.ljust(max_field_length)} | {str(value).ljust(max_value_length)}")

        print("\nVDEV Name  | Type           | Disk Count")
        print("-----------+----------------+---------------")

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
    print("\n### Disk Information ###")
    print("###################################")
    print("\nNOTE: The TrueNAS API will return N/A for the Pool for the boot device(s) as well as any disk is not a member of a pool.")
    print("###################################")
    fields = ["Name", "Model", "Serial", "ZFS GUID", "Pool", "Size (GiB)"]
    max_field_length = max(len(field) for field in fields)
    max_value_length = max(len(str(disk.get(field.lower(), "N/A"))) for disk in disk_info for field in fields)

    print(f"{'Field'.ljust(max_field_length)} | {'Value'.ljust(max_value_length)}")
    print(f"{'-' * max_field_length}-+-{'-' * max_value_length}")

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
        for field, value in zip(fields, values):
            print(f"{field.ljust(max_field_length)} | {str(value).ljust(max_value_length)}")
        print(f"{'-' * max_field_length}-+-{'-' * max_value_length}")
        print(f"{'-' * max_field_length}-+-{'-' * max_value_length}")

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
        print(f"Error querying datasets: {result.stderr}")
        return None

    existing_datasets = json.loads(result.stdout)
    dataset_exists = any(ds['name'] == dataset_name for ds in existing_datasets)

    if not dataset_exists:
        result = subprocess.run(['midclt', 'call', 'pool.dataset.create', json.dumps(dataset_config)], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error creating dataset {dataset_name}: {result.stderr}")
            return None
        print(f"Created temporary dataset: {dataset_name}")

        # Fetch the updated dataset information
        result = subprocess.run(['midclt', 'call', 'pool.dataset.query'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error querying datasets after creation: {result.stderr}")
            return None
        existing_datasets = json.loads(result.stdout)

    # Return the mountpoint of the dataset
    for ds in existing_datasets:
        if ds['name'] == dataset_name:
            print(f"Dataset {dataset_name} created successfully.")
            return ds['mountpoint']
    
    print(f"Dataset {dataset_name} was not found after creation.")
    return None

def run_dd_command(command):
    subprocess.run(command, shell=True)

def run_write_benchmark(threads, bytes_per_thread, block_size, file_prefix, dataset_path, iterations=2):
    print(f"Running DD write benchmark with {threads} threads...")
    speeds = []

    for run in range(iterations):  # Run the benchmark specified number of times
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
        total_bytes = threads * bytes_per_thread * 1024 * 1024  # Total bytes = threads * bytes per thread (in bytes)

        write_speed = total_bytes / 1024 / 1024 / total_time_taken  # Speed in MB/s
        speeds.append(write_speed)
        print(f"Run {run + 1} write speed: {write_speed:.2f} MB/s")

    average_write_speed = sum(speeds) / len(speeds) if speeds else 0
    print(f"Average write speed: {average_write_speed:.2f} MB/s")
    return speeds, average_write_speed

def run_read_benchmark(threads, bytes_per_thread, block_size, file_prefix, dataset_path, iterations=2):
    print(f"Running DD read benchmark with {threads} threads...")
    speeds = []

    for run in range(iterations):  # Run the benchmark specified number of times
        start_time = time.time()

        threads_list = []
        for i in range(threads):
            command = f"dd if={dataset_path}/{file_prefix}{i}.dat of=/dev/null bs={block_size} count={bytes_per_thread * 2} status=none"  # Double the size
            thread = threading.Thread(target=run_dd_command, args=(command,))
            thread.start()
            threads_list.append(thread)

        for thread in threads_list:
            thread.join()

        end_time = time.time()
        total_time_taken = end_time - start_time
        total_bytes = threads * bytes_per_thread * 2 * 1024 * 1024  # Total bytes = threads * bytes per thread (in bytes) * 2

        read_speed = total_bytes / 1024 / 1024 / total_time_taken  # Speed in MB/s
        speeds.append(read_speed)
        print(f"Run {run + 1} read speed: {read_speed:.2f} MB/s")

    average_read_speed = sum(speeds) / len(speeds) if speeds else 0
    print(f"Average read speed: {average_read_speed:.2f} MB/s")
    return speeds, average_read_speed

def run_benchmarks_for_pool(pool_name, cores, bytes_per_thread, block_size, file_prefix, dataset_path, iterations=2):
    # Escape spaces in the pool name
    escaped_pool_name = pool_name.replace(" ", "\\ ")
    thread_counts = [1, cores // 4, cores // 2, cores]
    results = []

    for threads in thread_counts:
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

    print(f"\n###################################")
    print(f"#         DD Benchmark Results for Pool: {escaped_pool_name}    #")
    print("###################################")
    for result in results:
        print(f"#    Threads: {result['threads']}    #")
        for i, speed in enumerate(result['write_speeds']):
            print(f"#    1M Seq Write Run {i+1}: {speed:.2f} MB/s     #")
        print(f"#    1M Seq Write Avg: {result['average_write_speed']:.2f} MB/s #")
        for i, speed in enumerate(result['read_speeds']):
            print(f"#    1M Seq Read Run {i+1}: {speed:.2f} MB/s      #")
        print(f"#    1M Seq Read Avg: {result['average_read_speed']:.2f} MB/s  #")
        print("###################################")
    
    return results

def run_disk_read_benchmark(disk_info, system_info, iterations=2):
    print("Running disk read benchmark...")
    print("###################################")
    print("This benchmark tests the 4K sequential read performance of each disk in the system using dd.")
    print(f"It is run {iterations} time(s) for each disk and averaged.")
    print("In order to work around ARC caching in systems with it still enabled, This benchmark reads data in the amount of total system RAM or the total size of the disk, whichever is smaller.")
    print("###################################")
    results = []

    def run_dd_read_command(disk_name, read_size_gib):
        print(f"Testing disk: {disk_name}")
        command = f"dd if=/dev/{disk_name} of=/dev/null bs=4K count={int(read_size_gib * 1024 * 1024 // 4)} status=none"  # Read size in 4 KiB blocks
        start_time = time.time()
        subprocess.run(command, shell=True)
        end_time = time.time()
        total_time_taken = end_time - start_time
        total_bytes = read_size_gib * 1024 * 1024 * 1024  # Total bytes = read size in GiB
        read_speed = total_bytes / 1024 / 1024 / total_time_taken  # Speed in MB/s
        return read_speed

    system_ram_gib = system_info.get('physmem', 0) / (1024 ** 3)  # System RAM in GiB

    for disk in disk_info:
        disk_name = disk.get("name", "N/A")
        disk_size_gib = disk.get("size", 0) / (1024 ** 3)  # Disk size in GiB
        read_size_gib = min(system_ram_gib, disk_size_gib)  # Read the smaller of system RAM or disk size

        if disk_name != "N/A":
            speeds = []
            for run_num in range(iterations):  # Run specified number of times
                print(f"Running disk read test on {disk_name} (run {run_num+1})...")
                speed = run_dd_read_command(disk_name, read_size_gib)
                speeds.append(speed)
                print(f"Disk {disk_name} run {run_num+1}: {speed:.2f} MB/s")
            average_speed = sum(speeds) / len(speeds) if speeds else 0
            results.append({
                "disk": disk_name,
                "speeds": speeds,
                "average_speed": average_speed,
                "iterations": iterations
            })

    print("\n###################################")
    print("#         Disk Read Benchmark Results   #")
    print("###################################")
    for result in results:
        print(f"#    Disk: {result['disk']}    #")
        for i, speed in enumerate(result['speeds']):
            print(f"#    Run {i+1}: {speed:.2f} MB/s     #")
        print(f"#    Average: {result['average_speed']:.2f} MB/s     #")
    print("###################################")
    
    return results

def cleanup(file_prefix, dataset_path):
    print("Cleaning up test files...")
    # Escape spaces in the dataset path
    escaped_dataset_path = dataset_path.replace(" ", "\\ ")
    for file in os.listdir(escaped_dataset_path):
        if file.startswith(file_prefix) and file.endswith('.dat'):
            os.remove(os.path.join(escaped_dataset_path, file))

def delete_dataset(dataset_name):
    # Escape spaces in the dataset name
    escaped_dataset_name = dataset_name.replace(" ", "\\ ")
    print(f"Deleting dataset: {escaped_dataset_name}")
    subprocess.run(['midclt', 'call', 'pool.dataset.delete', json.dumps({"id": escaped_dataset_name, "recursive": False, "force": False})], capture_output=True, text=True)

def get_dataset_available_bytes(pool_name):
    dataset_name = f"{pool_name}/tn-bench"
    result = subprocess.run(['midclt', 'call', 'pool.dataset.query'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error querying datasets: {result.stderr}")
        return 0
    try:
        datasets = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to parse dataset query result.")
        return 0
    for ds in datasets:
        if ds.get('name') == dataset_name:
            available_info = ds.get('available', {})
            # Use 'parsed' value if available (exact bytes)
            parsed_bytes = available_info.get('parsed')
            if parsed_bytes is not None:
                return parsed_bytes
            # Fallback to parsing 'value' string (e.g., "3.07T")
            value_str = available_info.get('value', '0')
            try:
                # Extract numeric part and unit
                unit = value_str[-1] if value_str[-1] in {'T', 'G', 'M', 'K', 'B'} else 'B'
                numeric_part = value_str[:-1] if unit != 'B' else value_str
                numeric_value = float(numeric_part)
                # Convert to bytes based on unit
                unit_multipliers = {
                    'T': 1024 ** 4,
                    'G': 1024 ** 3,
                    'M': 1024 ** 2,
                    'K': 1024,
                    'B': 1
                }
                return int(numeric_value * unit_multipliers[unit])
            except (ValueError, KeyError):
                print(f"Invalid value for available bytes: {value_str}")
                return 0
    print(f"Dataset {dataset_name} not found.")
    return 0

def save_results_to_json(results, output_path):
    """Save benchmark results to a JSON file"""
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"\nBenchmark results saved to: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"Error saving results to JSON: {str(e)}")

def select_pools_to_test(pool_info):
    """Prompt user to select which pools to benchmark"""
    print("\n###################################")
    print("#     Pool Selection for Testing   #")
    print("###################################")
    print("Available pools:")
    for i, pool in enumerate(pool_info):
        print(f"{i+1}. {pool['name']}")
    
    print("\nYou can:")
    print("1. Enter specific pool numbers (comma separated)")
    print("2. Type 'all' to test all pools")
    print("3. Type 'none' to skip pool testing")
    
    while True:
        selection = input("\nEnter your choice [all]: ").strip()
        if not selection:
            return pool_info  # Default to all
        
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
                    print(f"Warning: Index {idx+1} is out of range. Skipping.")
            return selected_pools
        except ValueError:
            print("Invalid input. Please enter pool numbers (e.g., '1,3'), 'all', or 'none'.")

def ask_about_disk_benchmark():
    """Prompt user whether to run disk benchmark"""
    print("\n###################################")
    print("#    Individual Disk Benchmark    #")
    print("###################################")
    response = input("Do you want to run the individual disk read benchmark? (yes/no) [yes]: ").strip().lower()
    if response in ['', 'y', 'yes']:
        return True
    elif response in ['n', 'no']:
        print("Skipping individual disk benchmark.")
        return False
    else:
        print("Invalid input. Defaulting to yes.")
        return True

def ask_iteration_count(benchmark_type):
    """Ask user how many iterations to run for a benchmark"""
    print("\n###################################")
    print(f"#    {benchmark_type} Benchmark Iterations    #")
    print("###################################")
    print("How many times should we run each test? (More iterations provide more consistent results but take longer)")
    print("1. Run each test once (faster)")
    print("2. Run each test twice (default, more accurate)")
    
    while True:
        response = input("\nEnter iteration count (1 or 2) [2]: ").strip()
        if not response:
            return 2
        
        try:
            count = int(response)
            if count in [1, 2]:
                return count
            print("Please enter 1 or 2")
        except ValueError:
            print("Invalid input. Please enter 1 or 2")

def ask_zfs_iterations():
    """Ask user how many iterations to run for ZFS benchmarks"""
    return ask_iteration_count("ZFS Pool")

def ask_disk_iterations():
    """Ask user how many iterations to run for disk benchmarks"""
    return ask_iteration_count("Individual Disk")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='TN-Bench System Benchmark')
    parser.add_argument('--output', type=str, default='./tn_bench_results.json',
                        help='Path to output JSON file (default: ./tn_bench_results.json)')
    args = parser.parse_args()

    # Initialize results dictionary
    benchmark_results = {
        "system_info": {},
        "pools": [],
        "disk_benchmark": [],
        "total_benchmark_time_minutes": 0,
        "benchmark_config": {
            "selected_pools": [],
            "disk_benchmark_run": False,
            "zfs_iterations": 2,
            "disk_iterations": 2
        }
    }

    get_user_confirmation()
    
    start_time = time.time()

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
    
    # Ask about ZFS iterations if pools selected
    zfs_iterations = 2
    if selected_pools:
        zfs_iterations = ask_zfs_iterations()
    benchmark_results["benchmark_config"]["zfs_iterations"] = zfs_iterations
    
    # Ask about disk benchmark
    run_disk_bench = ask_about_disk_benchmark()
    benchmark_results["benchmark_config"]["disk_benchmark_run"] = run_disk_bench
    
    # Ask about disk iterations if benchmark requested
    disk_iterations = 2
    if run_disk_bench:
        disk_iterations = ask_disk_iterations()
    benchmark_results["benchmark_config"]["disk_iterations"] = disk_iterations

    cores = system_info.get("cores", 1)
    bytes_per_thread_series_1 = 10240  # 10 GiB per thread (1M * 10240)
    block_size_series_1 = "1M"
    file_prefix_series_1 = "file_"

    print("\n###################################")
    print("#       DD Benchmark Starting     #")
    print("###################################")
    print(f"Using {cores} threads for the benchmark.")
    print(f"ZFS tests will run {zfs_iterations} time(s) per configuration")
    if run_disk_bench:
        print(f"Disk tests will run {disk_iterations} time(s) per disk")
    print()

    # Run benchmarks for each selected pool
    for pool in selected_pools:
        pool_name = pool.get('name', 'N/A')
        print(f"\nCreating test dataset for pool: {pool_name}")
        dataset_name = f"{pool_name}/tn-bench"
        dataset_path = create_dataset(pool_name)
        if dataset_path:
            # Check available space
            available_bytes = get_dataset_available_bytes(pool_name)
            required_bytes = 20 * cores * (1024 ** 3)  # 20 GiB per thread * cores
            
            # Convert to GiB for display
            available_gib = available_bytes / (1024 ** 3)
            required_gib = 20 * cores
            
            print(f"\n=== Space Verification ===")
            print(f"Available space: {available_gib:.2f} GiB")
            print(f"Space required:  {required_gib:.2f} GiB (20 GiB/thread × {cores} threads)")
            
            if available_bytes < required_bytes:
                print(f"\n WARNING: Insufficient space in dataset {pool_name}/tn-bench")
                print(f"Minimum required: {required_gib} GiB")
                print(f"Available:        {available_gib:.2f} GiB")
                proceed = input("\nProceeding may cause benchmark failures. Continue anyway? (yes/no): ")
                if proceed.lower() != 'yes':
                    print(f"Skipping benchmarks for pool {pool_name}")
                    delete_dataset(f"{pool_name}/tn-bench")
                    continue

            print(f"\n Sufficient space available - proceeding with benchmarks...")
            
            print(f"\nRunning benchmarks for pool: {pool_name}")
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

    end_time = time.time()
    total_time_taken = end_time - start_time
    total_time_taken_minutes = total_time_taken / 60
    benchmark_results["total_benchmark_time_minutes"] = total_time_taken_minutes
    print(f"\nTotal benchmark time: {total_time_taken_minutes:.2f} minutes")

    # Cleanup datasets for selected pools
    for pool in selected_pools:
        pool_name = pool.get('name', 'N/A')
        dataset_name = f"{pool_name}/tn-bench"
        delete = input(f"Do you want to delete the testing dataset {dataset_name}? (yes/no): ")
        if delete.lower() == 'yes':
            delete_dataset(dataset_name)
            print(f"Dataset {dataset_name} deleted.")
        else:
            print(f"Dataset {dataset_name} not deleted.")

    # Save results to JSON
    save_results_to_json(benchmark_results, args.output)
