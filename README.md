# tn-bench v1.07

##  tn-bench is an OpenSource software script that benchmarks your system and collects various statistical information via the TrueNAS API. It creates a dataset in each of your pools during testing, consuming 20 GiB of space for each thread in your system.

## Features

- Collects system information using TrueNAS API.
- Benchmarks system performance using `dd` command.
- Provides detailed information about system, pools, and disks.
- Supports multiple pools.
- Space validation


### Running the Script with 1M block size

   ```
   git clone -b monolithic-version-1.07 https://github.com/nickf1227/TN-Bench.git && cd TN-Bench && python3 truenas-bench.py
   ```


NOTE: `/dev/urandom` generates inherently uncompressible data, the the value of the compression options above is minimal in the current form.

The script will display system and pool information, then prompt you to continue with the benchmarks. Follow the prompts to complete the benchmarking process.


### Benchmarking Process

- **Dataset Creation**: The script creates a temporary dataset in each pool. The dataset is created with a 1M Record Size with no Compression and sync=Disabled using `midclt call pool.dataset.create`
- **Pool Write Benchmark**: The script performs four runs of the write benchmark using `dd` with varying thread counts. We are using `/dev/urandom` as our input file, so CPU performance may be relevant. This is by design as `/dev/zero` is flawed for this purpoose, and CPU stress is expected in real-world use anyway. The data is written in 1M chunks to a dataset with a 1M record size. For each thread, 20G of data is written. This scales with the number of threads, so a system with 16 Threads would write 320G of data.
- **Pool Read Benchmark**: The script performs four runs of the read benchmark using `dd` with varying thread counts. We are using `/dev/null` as out output file, so RAM speed may be relevant. The data is read in 1M chunks from a dataset with a 1M record size. For each thread, the previously written 20G of data is read. This scales with the number of threads, so a system with 16 Threads would have read 320G of data.

**NOTE:** ZFS ARC will also be used and will impact your results. This may be undesirable in some circumstances, and the `zfs_arc_max` can be set to `1` (which means 1 byte) to prevent ARC from caching. Setting it back to `0` will restore the default behavior, but the system will need to be restarted!

I have tested several permutations of file sizes on a dozen systems with varying amount of storage types, space, and RAM. Eventually settled on the current behavior for several reasons. Primarily, I wanted to reduce the impact of, but not REMOVE the ZFS ARC, since in a real world scenario, you would be leveraging the benefits of ARC caching. However, in order to avoid insanely unrealistic results, I needed to use file sizes that saturate the ARC completely. I believe this gives us the best data possible. 


Example of `arcstat -f time,hit%,dh%,ph%,mh% 10` running while the benchmark is running.
<img src="https://github.com/user-attachments/assets/4bdeea59-c88c-46b1-b17a-939594c4eda1" width="50%" />


- **Disk Benchmark**: The script performs four runs of the read benchmark using `dd` with varying thread counts. Calculated based on the size of your RAM and the disks, data already on each disk is read in 4K chunks to `/dev/null` , making this a 4K sequential read test. 4K was chosen because `ashift=12` for all recent ZFS pools created in TrueNAS. The reads are so large to try and avoid ARC caching. Run-to-run variance is still expected, particularly on SSDs, as the data ends up inside of internal caches. For this reason, it is run 4 times and averaged.
  
- **Results**: The script displays the results for each run and the average speed. This should give you an idea of the impacts of various thread-counts (as a synthetic representation of client-counts) and the ZFS ARC caching mechanism. 

**NOTE:** The script's run duration is dependant on the number of threads in your system as well as the number of disks in your system. Small all-flash systems may complete this benchmark in 25 minutes, while larger systems with spinning hardrives may take several hours. The script will not stop other I/O activity on a production system, but will severely limit performance. This benchmark is best run on a system with no other workload. This will give you the best outcome in terms of the accuracy of the data, in addition to not creating angry users.
### Cleanup

After the benchmarking is complete, the script prompts you to delete the datasets created during the process.

## Example Output

```

###################################
#                                 #
#          TN-Bench v1.07         #
#          MONOLITHIC.            #
#                                 #
###################################
TN-Bench is an OpenSource Software Script that uses standard tools to Benchmark your System and collect various statistical information via the TrueNAS API.

TN-Bench will make a Dataset in each of your pools for the purposes of this testing that will consume 20 GiB of space for every thread in your system during its run.

After which time we will prompt you to delete the dataset which was created.
###################################

WARNING: This test will make your system EXTREMELY slow during its run. It is recommended to run this test when no other workloads are running.

NOTE: ZFS ARC will also be used and will impact your results. This may be undesirable in some circumstances, and the zfs_arc_max can be set to 1 (which means 1 byte) to prevent ARC from caching.

NOTE: Setting it back to 0 will restore the default behavior, but the system will need to be restarted!
###################################

Would you like to continue? (yes/no): yes

### System Information ###
Field                 | Value
----------------------+---------------------------------------
Version               | 25.04.0
Load Average (1m)     | 0.1220703125
Load Average (5m)     | 0.2275390625
Load Average (15m)    | 0.25244140625
Model                 | AMD Ryzen 5 5600G with Radeon Graphics
Cores                 | 12
Physical Cores        | 6
System Product        | X570 AORUS ELITE
Physical Memory (GiB) | 30.75

### Pool Information ###
Field      | Value
-----------+-------------
Name       | inferno
Path       | /mnt/inferno
Status     | ONLINE
VDEV Count | 1
Disk Count | 5

VDEV Name  | Type           | Disk Count
-----------+----------------+---------------
raidz1-0    | RAIDZ1         | 5

### Disk Information ###
###################################

NOTE: The TrueNAS API will return N/A for the Pool for the boot device(s) as well as any disk is not a member of a pool.
###################################
Field      | Value
-----------+---------------------------
Name       | nvme0n1
Model      | INTEL SSDPE21D960GA
Serial     | PHM29081000X960CGN
ZFS GUID   | 212601209224793468
Pool       | inferno
Size (GiB) | 894.25
-----------+---------------------------
-----------+---------------------------
Name       | nvme2n1
Model      | INTEL SSDPE21D960GA
Serial     | PHM2913000QM960CGN
ZFS GUID   | 16221756077833732578
Pool       | inferno
Size (GiB) | 894.25
-----------+---------------------------
-----------+---------------------------
Name       | nvme4n1
Model      | INTEL SSDPE21D960GA
Serial     | PHM2913000YF960CGN
ZFS GUID   | 8625327235819249102
Pool       | inferno
Size (GiB) | 894.25
-----------+---------------------------
-----------+---------------------------
Name       | nvme5n1
Model      | INTEL SSDPE21D960GA
Serial     | PHM2913000DC960CGN
ZFS GUID   | 11750420763846093416
Pool       | inferno
Size (GiB) | 894.25
-----------+---------------------------
-----------+---------------------------
Name       | nvme3n1
Model      | SAMSUNG MZVL2512HCJQ-00BL7
Serial     | S64KNX2T216015
ZFS GUID   | None
Pool       | N/A
Size (GiB) | 476.94
-----------+---------------------------
-----------+---------------------------
Name       | nvme1n1
Model      | INTEL SSDPE21D960GA
Serial     | PHM2908101QG960CGN
ZFS GUID   | 10743034860780890768
Pool       | inferno
Size (GiB) | 894.25
-----------+---------------------------
-----------+---------------------------

###################################
#       DD Benchmark Starting     #
###################################
Using 12 threads for the benchmark.


Creating test dataset for pool: inferno
Created temporary dataset: inferno/tn-bench
Dataset inferno/tn-bench created successfully.

=== Space Verification ===
Available space: 765.37 GiB
Space required:  240.00 GiB (20 GiB/thread × 12 threads)

 Sufficient space available - proceeding with benchmarks...

###################################
#                                 #
#       DD Benchmark Starting     #
#                                 #
###################################
Using 12 threads for the benchmark.


Creating test dataset for pool: inferno
Dataset inferno/tn-bench created successfully.

Running benchmarks for pool: inferno
Running DD write benchmark with 1 threads...
Run 1 write speed: 408.21 MB/s
Run 2 write speed: 404.35 MB/s
Average write speed: 406.28 MB/s
Running DD read benchmark with 1 threads...
Run 1 read speed: 10529.35 MB/s
Run 2 read speed: 14742.91 MB/s
Average read speed: 12636.13 MB/s
Running DD write benchmark with 3 threads...
Run 1 write speed: 1145.73 MB/s
Run 2 write speed: 1141.83 MB/s
Average write speed: 1143.78 MB/s
Running DD read benchmark with 3 threads...
Run 1 read speed: 8261.30 MB/s
Run 2 read speed: 8395.17 MB/s
Average read speed: 8328.24 MB/s
Running DD write benchmark with 6 threads...
Run 1 write speed: 1838.74 MB/s
Run 2 write speed: 1846.15 MB/s
Average write speed: 1842.44 MB/s
Running DD read benchmark with 6 threads...
Run 1 read speed: 8424.02 MB/s
Run 2 read speed: 8464.73 MB/s
Average read speed: 8444.38 MB/s
Running DD write benchmark with 12 threads...
Run 1 write speed: 2217.72 MB/s
Run 2 write speed: 2247.58 MB/s
Average write speed: 2232.65 MB/s
Running DD read benchmark with 12 threads...
Run 1 read speed: 8469.45 MB/s
Run 2 read speed: 8508.80 MB/s
Average read speed: 8489.13 MB/s

###################################
#         DD Benchmark Results for Pool: inferno    #
###################################
#    Threads: 1    #
#    1M Seq Write Run 1: 408.21 MB/s     #
#    1M Seq Write Run 2: 404.35 MB/s     #
#    1M Seq Write Avg: 406.28 MB/s #
#    1M Seq Read Run 1: 10529.35 MB/s      #
#    1M Seq Read Run 2: 14742.91 MB/s      #
#    1M Seq Read Avg: 12636.13 MB/s  #
###################################
#    Threads: 3    #
#    1M Seq Write Run 1: 1145.73 MB/s     #
#    1M Seq Write Run 2: 1141.83 MB/s     #
#    1M Seq Write Avg: 1143.78 MB/s #
#    1M Seq Read Run 1: 8261.30 MB/s      #
#    1M Seq Read Run 2: 8395.17 MB/s      #
#    1M Seq Read Avg: 8328.24 MB/s  #
###################################
#    Threads: 6    #
#    1M Seq Write Run 1: 1838.74 MB/s     #
#    1M Seq Write Run 2: 1846.15 MB/s     #
#    1M Seq Write Avg: 1842.44 MB/s #
#    1M Seq Read Run 1: 8424.02 MB/s      #
#    1M Seq Read Run 2: 8464.73 MB/s      #
#    1M Seq Read Avg: 8444.38 MB/s  #
###################################
#    Threads: 12    #
#    1M Seq Write Run 1: 2217.72 MB/s     #
#    1M Seq Write Run 2: 2247.58 MB/s     #
#    1M Seq Write Avg: 2232.65 MB/s #
#    1M Seq Read Run 1: 8469.45 MB/s      #
#    1M Seq Read Run 2: 8508.80 MB/s      #
#    1M Seq Read Avg: 8489.13 MB/s  #
###################################
Cleaning up test files...
Running disk read benchmark...
###################################
This benchmark tests the 4K sequential read performance of each disk in the system using dd. It is run 2 times for each disk and averaged.
In order to work around ARC caching in systems with it still enabled, This benchmark reads data in the amount of total system RAM or the total size of the disk, whichever is smaller.
###################################
Testing disk: nvme0n1
Testing disk: nvme0n1
Testing disk: nvme2n1
Testing disk: nvme2n1
Testing disk: nvme4n1
Testing disk: nvme4n1
Testing disk: nvme5n1
Testing disk: nvme5n1
Testing disk: nvme3n1
Testing disk: nvme3n1
Testing disk: nvme1n1
Testing disk: nvme1n1

###################################
#         Disk Read Benchmark Results   #
###################################
#    Disk: nvme0n1    #
#    Run 1: 1735.62 MB/s     #
#    Run 2: 1543.09 MB/s     #
#    Average: 1639.36 MB/s     #
#    Disk: nvme2n1    #
#    Run 1: 1526.69 MB/s     #
#    Run 2: 1432.16 MB/s     #
#    Average: 1479.42 MB/s     #
#    Disk: nvme4n1    #
#    Run 1: 1523.02 MB/s     #
#    Run 2: 1412.82 MB/s     #
#    Average: 1467.92 MB/s     #
#    Disk: nvme5n1    #
#    Run 1: 1523.86 MB/s     #
#    Run 2: 1463.96 MB/s     #
#    Average: 1493.91 MB/s     #
#    Disk: nvme3n1    #
#    Run 1: 1533.71 MB/s     #
#    Run 2: 1482.33 MB/s     #
#    Average: 1508.02 MB/s     #
#    Disk: nvme1n1    #
#    Run 1: 1624.40 MB/s     #
#    Run 2: 1547.07 MB/s     #
#    Average: 1585.73 MB/s     #
###################################

Total benchmark time: 10.62 minutes
 
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or fixes.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
