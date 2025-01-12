# TN-Bench v1.02

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
- **Pool Write Benchmark**: The script performs four runs of the write benchmark using `dd` with varying thread counts. We are using `/dev/urandom` as our input file, so CPU performance may be relevant. This is by design as `/dev/zero` is flawed for this purpoose, and CPU stress is expected in real-world use anyway. The data is written in 1M chunks to a dataset with a 1M record size. For each thread, 10G of data is written. This scales with the number of threads, so a system with 16 Threads would write 160G of data.
- **Pool Read Benchmark**: The script performs four runs of the read benchmark using `dd` with varying thread counts. We are using `/dev/null` as out output file, so RAM speed may be relevant. The data is read in 1M chunks from a dataset with a 1M record size. For each thread, the previously written 10G of data is read. This scales with the number of threads, so a system with 16 Threads would have read 160G of data.

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
#          TN-Bench v1.01         #
#          MONOLITHIC.            #
#                                 #
###################################
TN-Bench is an OpenSource Software Script that uses standard tools to Benchmark your System and collect various statistical information via the TrueNAS API.

TN-Bench will make a Dataset in each of your pools for the purposes of this testing that will consume 10 GiB of space for every thread in your system during its run.

After which time we will prompt you to delete the dataset which was created.

Would you like to continue? (yes/no): yes

### System Information ###
Field                 | Value                                       
----------------------+---------------------------------------------
Version               | TrueNAS-SCALE-25.04.0-MASTER-20250110-005622
Load Average (1m)     | 0.26953125                                  
Load Average (5m)     | 0.18798828125                               
Load Average (15m)    | 0.1328125                                   
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
Field    | Value                     
---------+---------------------------
Name     | nvme0n1                   
Model    | INTEL SSDPE21D960GA       
Serial   | PHM29081000X960CGN        
ZFS GUID | 212601209224793468        
Pool     | inferno                   
---------+---------------------------
---------+---------------------------
Name     | nvme3n1                   
Model    | INTEL SSDPE21D960GA       
Serial   | PHM2913000QM960CGN        
ZFS GUID | 16221756077833732578      
Pool     | inferno                   
---------+---------------------------
---------+---------------------------
Name     | nvme5n1                   
Model    | INTEL SSDPE21D960GA       
Serial   | PHM2913000YF960CGN        
ZFS GUID | 8625327235819249102       
Pool     | inferno                   
---------+---------------------------
---------+---------------------------
Name     | nvme2n1                   
Model    | INTEL SSDPE21D960GA       
Serial   | PHM2913000DC960CGN        
ZFS GUID | 11750420763846093416      
Pool     | inferno                   
---------+---------------------------
---------+---------------------------
Name     | nvme4n1                   
Model    | SAMSUNG MZVL2512HCJQ-00BL7
Serial   | S64KNX2T216015            
ZFS GUID | None                      
Pool     | N/A                       
---------+---------------------------
---------+---------------------------
Name     | nvme1n1                   
Model    | INTEL SSDPE21D960GA       
Serial   | PHM2908101QG960CGN        
ZFS GUID | 10743034860780890768      
Pool     | inferno                   
---------+---------------------------
---------+---------------------------

###################################
#                                 #
#       DD Benchmark Starting     #
#                                 #
###################################
Using 12 threads for the benchmark.


Creating test dataset for pool: inferno

Running benchmarks for pool: inferno
Running DD write benchmark with 1 threads...
Run 1 write speed: 409.71 MB/s
Run 2 write speed: 411.04 MB/s
Run 3 write speed: 410.87 MB/s
Run 4 write speed: 412.42 MB/s
Average write speed: 411.01 MB/s
Running DD read benchmark with 1 threads...
Run 1 read speed: 8152.66 MB/s
Run 2 read speed: 8317.79 MB/s
Run 3 read speed: 8226.39 MB/s
Run 4 read speed: 8017.75 MB/s
Average read speed: 8178.65 MB/s
Running DD write benchmark with 3 threads...
Run 1 write speed: 1182.07 MB/s
Run 2 write speed: 1188.16 MB/s
Run 3 write speed: 1191.31 MB/s
Run 4 write speed: 1190.17 MB/s
Average write speed: 1187.93 MB/s
Running DD read benchmark with 3 threads...
Run 1 read speed: 4181.71 MB/s
Run 2 read speed: 4229.10 MB/s
Run 3 read speed: 4213.72 MB/s
Run 4 read speed: 4220.44 MB/s
Average read speed: 4211.24 MB/s
Running DD write benchmark with 6 threads...
Run 1 write speed: 2043.38 MB/s
Run 2 write speed: 2036.34 MB/s
Run 3 write speed: 2036.05 MB/s
Run 4 write speed: 2015.42 MB/s
Average write speed: 2032.80 MB/s
Running DD read benchmark with 6 threads...
Run 1 read speed: 4156.96 MB/s
Run 2 read speed: 4166.86 MB/s
Run 3 read speed: 4167.39 MB/s
Run 4 read speed: 4171.87 MB/s
Average read speed: 4165.77 MB/s
Running DD write benchmark with 12 threads...
Run 1 write speed: 2425.96 MB/s
Run 2 write speed: 2154.59 MB/s
Run 3 write speed: 2128.10 MB/s
Run 4 write speed: 2116.66 MB/s
Average write speed: 2206.33 MB/s
Running DD read benchmark with 12 threads...
Run 1 read speed: 4107.46 MB/s
Run 2 read speed: 4111.38 MB/s
Run 3 read speed: 4107.17 MB/s
Run 4 read speed: 4109.34 MB/s
Average read speed: 4108.84 MB/s

###################################
#         DD Benchmark Results for Pool: inferno    #
###################################
#    Threads: 1    #
#    1M Seq Write Run 1: 409.71 MB/s     #
#    1M Seq Write Run 2: 411.04 MB/s     #
#    1M Seq Write Run 3: 410.87 MB/s     #
#    1M Seq Write Run 4: 412.42 MB/s     #
#    1M Seq Write Avg: 411.01 MB/s #
#    1M Seq Read Run 1: 8152.66 MB/s      #
#    1M Seq Read Run 2: 8317.79 MB/s      #
#    1M Seq Read Run 3: 8226.39 MB/s      #
#    1M Seq Read Run 4: 8017.75 MB/s      #
#    1M Seq Read Avg: 8178.65 MB/s  #
###################################
#    Threads: 3    #
#    1M Seq Write Run 1: 1182.07 MB/s     #
#    1M Seq Write Run 2: 1188.16 MB/s     #
#    1M Seq Write Run 3: 1191.31 MB/s     #
#    1M Seq Write Run 4: 1190.17 MB/s     #
#    1M Seq Write Avg: 1187.93 MB/s #
#    1M Seq Read Run 1: 4181.71 MB/s      #
#    1M Seq Read Run 2: 4229.10 MB/s      #
#    1M Seq Read Run 3: 4213.72 MB/s      #
#    1M Seq Read Run 4: 4220.44 MB/s      #
#    1M Seq Read Avg: 4211.24 MB/s  #
###################################
#    Threads: 6    #
#    1M Seq Write Run 1: 2043.38 MB/s     #
#    1M Seq Write Run 2: 2036.34 MB/s     #
#    1M Seq Write Run 3: 2036.05 MB/s     #
#    1M Seq Write Run 4: 2015.42 MB/s     #
#    1M Seq Write Avg: 2032.80 MB/s #
#    1M Seq Read Run 1: 4156.96 MB/s      #
#    1M Seq Read Run 2: 4166.86 MB/s      #
#    1M Seq Read Run 3: 4167.39 MB/s      #
#    1M Seq Read Run 4: 4171.87 MB/s      #
#    1M Seq Read Avg: 4165.77 MB/s  #
###################################
#    Threads: 12    #
#    1M Seq Write Run 1: 2425.96 MB/s     #
#    1M Seq Write Run 2: 2154.59 MB/s     #
#    1M Seq Write Run 3: 2128.10 MB/s     #
#    1M Seq Write Run 4: 2116.66 MB/s     #
#    1M Seq Write Avg: 2206.33 MB/s #
#    1M Seq Read Run 1: 4107.46 MB/s      #
#    1M Seq Read Run 2: 4111.38 MB/s      #
#    1M Seq Read Run 3: 4107.17 MB/s      #
#    1M Seq Read Run 4: 4109.34 MB/s      #
#    1M Seq Read Avg: 4108.84 MB/s  #
###################################
Cleaning up test files...
Running disk read benchmark...
This benchmark tests the 4K sequential read performance of each disk in the system using dd. It is run 4 times for each disk and averaged.
This benchmark is useful for comparing disks within the same pool, to identify potential issues and bottlenecks.
Testing disk: nvme0n1
Testing disk: nvme0n1
Testing disk: nvme0n1
Testing disk: nvme0n1
Testing disk: nvme3n1
Testing disk: nvme3n1
Testing disk: nvme3n1
Testing disk: nvme3n1
Testing disk: nvme5n1
Testing disk: nvme5n1
Testing disk: nvme5n1
Testing disk: nvme5n1
Testing disk: nvme2n1
Testing disk: nvme2n1
Testing disk: nvme2n1
Testing disk: nvme2n1
Testing disk: nvme4n1
Testing disk: nvme4n1
Testing disk: nvme4n1
Testing disk: nvme4n1
Testing disk: nvme1n1
Testing disk: nvme1n1
Testing disk: nvme1n1
Testing disk: nvme1n1

###################################
#         Disk Read Benchmark Results   #
###################################
#    Disk: nvme0n1    #
#    Run 1: 2026.97 MB/s     #
#    Run 2: 1959.99 MB/s     #
#    Run 3: 1960.39 MB/s     #
#    Run 4: 1960.94 MB/s     #
#    Average: 1977.07 MB/s     #
#    Disk: nvme3n1    #
#    Run 1: 2029.23 MB/s     #
#    Run 2: 1961.14 MB/s     #
#    Run 3: 1956.62 MB/s     #
#    Run 4: 1959.65 MB/s     #
#    Average: 1976.66 MB/s     #
#    Disk: nvme5n1    #
#    Run 1: 2034.83 MB/s     #
#    Run 2: 1968.09 MB/s     #
#    Run 3: 1965.92 MB/s     #
#    Run 4: 1967.62 MB/s     #
#    Average: 1984.12 MB/s     #
#    Disk: nvme2n1    #
#    Run 1: 2022.89 MB/s     #
#    Run 2: 1960.77 MB/s     #
#    Run 3: 1960.92 MB/s     #
#    Run 4: 1960.54 MB/s     #
#    Average: 1976.28 MB/s     #
#    Disk: nvme4n1    #
#    Run 1: 1836.50 MB/s     #
#    Run 2: 1791.16 MB/s     #
#    Run 3: 1790.46 MB/s     #
#    Run 4: 1788.25 MB/s     #
#    Average: 1801.59 MB/s     #
#    Disk: nvme1n1    #
#    Run 1: 2114.62 MB/s     #
#    Run 2: 2039.22 MB/s     #
#    Run 3: 2038.66 MB/s     #
#    Run 4: 2038.23 MB/s     #
#    Average: 2057.68 MB/s     #
###################################

Total benchmark time: 23.15 minutes
Do you want to delete the testing dataset inferno/tn-bench? (yes/no): 
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or fixes.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
