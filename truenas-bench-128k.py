import subprocess
import json
import os
import signal
import threading
import time

def get_user_confirmation():
    print("\n######################################")
    print("#                                      #")
    print("#          TN-Bench v1.06              #")
    print("#          128K MONOLITHIC.            #")  
    print("#                                      #")
    print("########################################")
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
        size_gib = disk.get("size", 0) / (1024 ** 3)
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
        "recordsize": "128K",  # Changed from "1M" to "128K"
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

def run_write_benchmark(threads, bytes_per_thread, block_size, file_prefix, dataset_path):
    print(f"Running DD write benchmark with {threads} threads...")
    speeds = []

    for run in range(2):  # Run the benchmark two times
        start_time = time.time()

        threads_list = []
        for i in range(threads):
            command = f"dd if=/dev/urandom of={dataset_path}/{file_prefix}{i}.dat bs={block_size} count={bytes_per_thread * 2} status=none"  # Double the size
            thread = threading.Thread(target=run_dd_command, args=(command,))
            thread.start()
            threads_list.append(thread)

        for thread in threads_list:
            thread.join()

        end_time = time.time()
        total_time_taken = end_time - start_time
        total_bytes = threads * bytes_per_thread * 2 * 1024 * 1024  # Total bytes = threads * bytes per thread (in bytes) * 2

        write_speed = total_bytes / 1024 / 1024 / total_time_taken  # Speed in MB/s
        speeds.append(write_speed)
        print(f"Run {run + 1} write speed: {write_speed:.2f} MB/s")

    average_write_speed = sum(speeds) / len(speeds)
    print(f"Average write speed: {average_write_speed:.2f} MB/s")
    return speeds[0], speeds[1], average_write_speed

def run_read_benchmark(threads, bytes_per_thread, block_size, file_prefix, dataset_path):
    print(f"Running DD read benchmark with {threads} threads...")
    speeds = []

    for run in range(2):  # Run the benchmark two times
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

    average_read_speed = sum(speeds) / len(speeds)
    print(f"Average read speed: {average_read_speed:.2f} MB/s")
    return speeds[0], speeds[1], average_read_speed

def run_benchmarks_for_pool(pool_name, cores, bytes_per_thread, block_size, file_prefix, dataset_path):
    # Escape spaces in the pool name
    escaped_pool_name = pool_name.replace(" ", "\\ ")
    thread_counts = [1, cores // 4, cores // 2, cores]
    results = []

    for threads in thread_counts:
        write_speed_1, write_speed_2, average_write_speed = run_write_benchmark(threads, bytes_per_thread, block_size, file_prefix, dataset_path)
        read_speed_1, read_speed_2, average_read_speed = run_read_benchmark(threads, bytes_per_thread, block_size, file_prefix, dataset_path)
        results.append((threads, write_speed_1, write_speed_2, average_write_speed, read_speed_1, read_speed_2, average_read_speed))

    print(f"\n###################################")
    print(f"#         DD Benchmark Results for Pool: {escaped_pool_name}    #")
    print("###################################")
    for threads, write_speed_1, write_speed_2, average_write_speed, read_speed_1, read_speed_2, average_read_speed in results:
        print(f"#    Threads: {threads}    #")
        print(f"#    128K Seq Write Run 1: {write_speed_1:.2f} MB/s     #")
        print(f"#    128K Seq Write Run 2: {write_speed_2:.2f} MB/s     #")
        print(f"#    128K Seq Write Avg: {average_write_speed:.2f} MB/s #")
        print(f"#    128K Seq Read Run 1: {read_speed_1:.2f} MB/s       #")
        print(f"#    128K Seq Read Run 2: {read_speed_2:.2f} MB/s       #")
        print(f"#    128K Seq Read Avg: {average_read_speed:.2f} MB/s   #")
        print("###################################")

def run_disk_read_benchmark(disk_info):
    print("Running disk read benchmark...")
    print("###################################")
    print("This benchmark tests the 4K sequential read performance of each disk in the system using dd. It is run 2 times for each disk and averaged.")
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
            for _ in range(2):  # Run 2 sequential times for each disk
                speed = run_dd_read_command(disk_name, read_size_gib)
                speeds.append(speed)  # Collect the speed value
            average_speed = sum(speeds) / len(speeds)
            results.append((disk_name, speeds[0], speeds[1], average_speed))  # Report both runs and the average speed in MB/s

    print("\n###################################")
    print("#         Disk Read Benchmark Results   #")
    print("###################################")
    for disk_name, speed1, speed2, average_speed in results:
        print(f"#    Disk: {disk_name}    #")
        print(f"#    Run 1: {speed1:.2f} MB/s     #")
        print(f"#    Run 2: {speed2:.2f} MB/s     #")
        print(f"#    Average: {average_speed:.2f} MB/s     #")
    print("###################################")

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

if __name__ == "__main__":
    get_user_confirmation()
    
    start_time = time.time()  # Start the timer

    system_info = get_system_info()
    print_system_info_table(system_info)
    
    pool_info = get_pool_info()
    print_pool_info_table(pool_info)

    disk_info = get_disk_info()
    pool_membership = get_pool_membership()
    print_disk_info_table(disk_info, pool_membership)

    cores = system_info.get("cores", 1)
    bytes_per_thread_series_1 = 20480 * 8  # Adjusted for 128K block size
    block_size_series_1 = "128K"  # Changed from "1M" to "128K"
    file_prefix_series_1 = "file_"

    print("\n###################################")
    print("#                                 #")
    print("#       DD Benchmark Starting     #")
    print("#                                 #")
    print("###################################")
    print(f"Using {cores} threads for the benchmark.\n")

    for pool in pool_info:
        pool_name = pool.get('name', 'N/A')
        print(f"\nCreating test dataset for pool: {pool_name}")
        dataset_name = f"{pool_name}/tn-bench"
        dataset_path = create_dataset(pool_name)
        if dataset_path:
            print(f"\nRunning benchmarks for pool: {pool_name}")
            run_benchmarks_for_pool(pool_name, cores, bytes_per_thread_series_1, block_size_series_1, file_prefix_series_1, dataset_path)
            cleanup(file_prefix_series_1, dataset_path)

    run_disk_read_benchmark(disk_info)

    end_time = time.time()  # End the timer
    total_time_taken = end_time - start_time
    total_time_taken_minutes = total_time_taken / 60

    print(f"\nTotal benchmark time: {total_time_taken_minutes:.2f} minutes")

    for pool in pool_info:
        pool_name = pool.get('name', 'N/A')
        dataset_name = f"{pool_name}/tn-bench"
        delete = input(f"Do you want to delete the testing dataset {dataset_name}? (yes/no): ")
        if delete.lower() == 'yes':
            delete_dataset(dataset_name)
            print(f"Dataset {dataset_name} deleted.")
        else:
            print(f"Dataset {dataset_name} not deleted.")
