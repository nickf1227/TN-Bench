# TN-Bench v1.06

TN-Bench is an OpenSource software script that benchmarks your system and collects various statistical information via the TrueNAS API. It creates a dataset in each of your pools during testing, consuming 10 GiB of space for each thread in your system.

## Features

- Collects system information using TrueNAS API.
- Benchmarks system performance using `dd` command.
- Provides detailed information about system, pools, and disks.
- Supports multiple pools.

### Running the Script

   ```
   git clone https://github.com/nickf1227/TN-Bench.git && cd TN-Bench && python3 truenas-bench.py
   ```
The script will display system and pool information, then prompt you to continue with the benchmarks. Follow the prompts to complete the benchmarking process.

### Benchmarking Process

- **Dataset Creation**: The script creates a temporary dataset in each pool. The dataset is created with a 1M Record Size with no Compression and sync=Disabled using `midclt call pool.dataset.create`
- **Pool Write Benchmark**: The script performs four runs of the write benchmark using `dd` with varying thread counts. We are using `/dev/urandom` as our input file, so CPU performance may be relevant. This is by design as `/dev/zero` is flawed for this purpoose, and CPU stress is expected in real-world use anyway. The data is written in 1M chunks to a dataset with a 1M record size. For each thread, 20G of data is written. This scales with the number of threads, so a system with 16 Threads would write 320G of data.
- **Pool Read Benchmark**: The script performs four runs of the read benchmark using `dd` with varying thread counts. We are using `/dev/null` as out output file, so RAM speed may be relevant. The data is read in 1M chunks from a dataset with a 1M record size. For each thread, the previously written 20G of data is read. This scales with the number of threads, so a system with 16 Threads would have read 320G of data.

**NOTE:** ZFS ARC will also be used and will impact your results. This may be undesirable in some circumstances, and the `zfs_arc_max` can be set to `1` (which means 1 byte) to prevent ARC from caching. Setting it back to `0` will restore the default behavior, but the system will need to be restarted!

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
#          TN-Bench v1.05         #
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
----------------------+---------------------------------------------
Version               | TrueNAS-SCALE-25.04.0-MASTER-20250110-005622
Load Average (1m)     | 0.06689453125                               
Load Average (5m)     | 0.142578125                                 
Load Average (15m)    | 0.15283203125                               
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

NOTE: The TrueNAS API will return N/A for the Pool for the boot device(s) as well as the disk name if the disk is not a member of a pool.
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
Name       | nvme3n1                   
Model      | INTEL SSDPE21D960GA       
Serial     | PHM2913000QM960CGN        
ZFS GUID   | 16221756077833732578      
Pool       | inferno                   
Size (GiB) | 894.25                    
-----------+---------------------------
-----------+---------------------------
Name       | nvme5n1                   
Model      | INTEL SSDPE21D960GA       
Serial     | PHM2913000YF960CGN        
ZFS GUID   | 8625327235819249102       
Pool       | inferno                   
Size (GiB) | 894.25                    
-----------+---------------------------
-----------+---------------------------
Name       | nvme2n1                   
Model      | INTEL SSDPE21D960GA       
Serial     | PHM2913000DC960CGN        
ZFS GUID   | 11750420763846093416      
Pool       | inferno                   
Size (GiB) | 894.25                    
-----------+---------------------------
-----------+---------------------------
Name       | nvme4n1                   
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
#                                 #
#       DD Benchmark Starting     #
#                                 #
###################################
Using 12 threads for the benchmark.


Creating test dataset for pool: inferno

Running benchmarks for pool: inferno
Running DD write benchmark with 1 threads...
Run 1 write speed: 411.17 MB/s
Run 2 write speed: 412.88 MB/s
Average write speed: 412.03 MB/s
Running DD read benchmark with 1 threads...
Run 1 read speed: 6762.11 MB/s
Run 2 read speed: 5073.43 MB/s
Average read speed: 5917.77 MB/s
Running DD write benchmark with 3 threads...
Run 1 write speed: 1195.91 MB/s
Run 2 write speed: 1193.22 MB/s
Average write speed: 1194.56 MB/s
Running DD read benchmark with 3 threads...
Run 1 read speed: 4146.25 MB/s
Run 2 read speed: 4161.19 MB/s
Average read speed: 4153.72 MB/s
Running DD write benchmark with 6 threads...
Run 1 write speed: 2060.54 MB/s
Run 2 write speed: 2058.62 MB/s
Average write speed: 2059.58 MB/s
Running DD read benchmark with 6 threads...
Run 1 read speed: 4209.25 MB/s
Run 2 read speed: 4212.84 MB/s
Average read speed: 4211.05 MB/s
Running DD write benchmark with 12 threads...
Run 1 write speed: 2353.74 MB/s
Run 2 write speed: 2184.07 MB/s
Average write speed: 2268.91 MB/s
Running DD read benchmark with 12 threads...
Run 1 read speed: 4191.27 MB/s
Run 2 read speed: 4199.91 MB/s
Average read speed: 4195.59 MB/s

###################################
#         DD Benchmark Results for Pool: inferno    #
###################################
#    Threads: 1    #
#    1M Seq Write Run 1: 411.17 MB/s     #
#    1M Seq Write Run 2: 412.88 MB/s     #
#    1M Seq Write Avg: 412.03 MB/s #
#    1M Seq Read Run 1: 6762.11 MB/s      #
#    1M Seq Read Run 2: 5073.43 MB/s      #
#    1M Seq Read Avg: 5917.77 MB/s  #
###################################
#    Threads: 3    #
#    1M Seq Write Run 1: 1195.91 MB/s     #
#    1M Seq Write Run 2: 1193.22 MB/s     #
#    1M Seq Write Avg: 1194.56 MB/s #
#    1M Seq Read Run 1: 4146.25 MB/s      #
#    1M Seq Read Run 2: 4161.19 MB/s      #
#    1M Seq Read Avg: 4153.72 MB/s  #
###################################
#    Threads: 6    #
#    1M Seq Write Run 1: 2060.54 MB/s     #
#    1M Seq Write Run 2: 2058.62 MB/s     #
#    1M Seq Write Avg: 2059.58 MB/s #
#    1M Seq Read Run 1: 4209.25 MB/s      #
#    1M Seq Read Run 2: 4212.84 MB/s      #
#    1M Seq Read Avg: 4211.05 MB/s  #
###################################
#    Threads: 12    #
#    1M Seq Write Run 1: 2353.74 MB/s     #
#    1M Seq Write Run 2: 2184.07 MB/s     #
#    1M Seq Write Avg: 2268.91 MB/s #
#    1M Seq Read Run 1: 4191.27 MB/s      #
#    1M Seq Read Run 2: 4199.91 MB/s      #
#    1M Seq Read Avg: 4195.59 MB/s  #
###################################
Cleaning up test files...
Running disk read benchmark...
This benchmark tests the 4K sequential read performance of each disk in the system using dd. It is run 2 times for each disk and averaged.
In order to work around ARC caching in systems with it still enabled, This benchmark reads data in the amount of total system RAM or the total size of the disk, whichever is smaller.
Testing disk: nvme0n1
Testing disk: nvme0n1
Testing disk: nvme3n1
Testing disk: nvme3n1
Testing disk: nvme5n1
Testing disk: nvme5n1
Testing disk: nvme2n1
Testing disk: nvme2n1
Testing disk: nvme4n1
Testing disk: nvme4n1
Testing disk: nvme1n1
Testing disk: nvme1n1

###################################
#         Disk Read Benchmark Results   #
###################################
#    Disk: nvme0n1    #
#    Run 1: 2032.08 MB/s     #
#    Run 2: 1825.83 MB/s     #
#    Average: 1928.95 MB/s     #
#    Disk: nvme3n1    #
#    Run 1: 1964.28 MB/s     #
#    Run 2: 1939.57 MB/s     #
#    Average: 1951.93 MB/s     #
#    Disk: nvme5n1    #
#    Run 1: 1908.79 MB/s     #
#    Run 2: 1948.96 MB/s     #
#    Average: 1928.88 MB/s     #
#    Disk: nvme2n1    #
#    Run 1: 1947.48 MB/s     #
#    Run 2: 1762.31 MB/s     #
#    Average: 1854.90 MB/s     #
#    Disk: nvme4n1    #
#    Run 1: 1829.80 MB/s     #
#    Run 2: 1787.41 MB/s     #
#    Average: 1808.60 MB/s     #
#    Disk: nvme1n1    #
#    Run 1: 1836.51 MB/s     #
#    Run 2: 1879.80 MB/s     #
#    Average: 1858.16 MB/s     #
###################################

Total benchmark time: 15.88 minutes
 
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or fixes.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
