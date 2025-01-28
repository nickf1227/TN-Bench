# TN-Bench v1.06

TN-Bench is an OpenSource software script that benchmarks your system and collects various statistical information via the TrueNAS API. It creates a dataset in each of your pools during testing, consuming 20 GiB of space for each thread in your system.

## Features

- Collects system information using TrueNAS API.
- Benchmarks system performance using `dd` command.
- Provides detailed information about system, pools, and disks.
- Supports multiple pools.

### Running the Script with 1M block size

   ```
   git clone https://github.com/nickf1227/TN-Bench.git && cd TN-Bench && python3 truenas-bench.py
   ```
The script will display system and pool information, then prompt you to continue with the benchmarks. Follow the prompts to complete the benchmarking process.

### Running the Script with 128K block size

   ```
   git clone https://github.com/nickf1227/TN-Bench.git && cd TN-Bench && python3 truenas-bench-128k.py
   ```
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
#          TN-Bench v1.06         #
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
Version               | TrueNAS-SCALE-25.04.0-MASTER-20250118-155243
Load Average (1m)     | 0.26123046875                               
Load Average (5m)     | 0.22216796875                               
Load Average (15m)    | 0.185546875                                 
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
Dataset inferno/tn-bench created successfully.

Running benchmarks for pool: inferno
Running DD write benchmark with 1 threads...
Run 1 write speed: 410.96 MB/s
Run 2 write speed: 410.95 MB/s
Average write speed: 410.96 MB/s
Running DD read benchmark with 1 threads...
Run 1 read speed: 4204.60 MB/s
Run 2 read speed: 5508.72 MB/s
Average read speed: 4856.66 MB/s
Running DD write benchmark with 3 threads...
Run 1 write speed: 1179.53 MB/s
Run 2 write speed: 1165.82 MB/s
Average write speed: 1172.67 MB/s
Running DD read benchmark with 3 threads...
Run 1 read speed: 4260.03 MB/s
Run 2 read speed: 4275.41 MB/s
Average read speed: 4267.72 MB/s
Running DD write benchmark with 6 threads...
Run 1 write speed: 1971.18 MB/s
Run 2 write speed: 1936.90 MB/s
Average write speed: 1954.04 MB/s
Running DD read benchmark with 6 threads...
Run 1 read speed: 4237.76 MB/s
Run 2 read speed: 4240.26 MB/s
Average read speed: 4239.01 MB/s
Running DD write benchmark with 12 threads...
Run 1 write speed: 2049.01 MB/s
Run 2 write speed: 1940.13 MB/s
Average write speed: 1994.57 MB/s
Running DD read benchmark with 12 threads...
Run 1 read speed: 4087.74 MB/s
Run 2 read speed: 4092.10 MB/s
Average read speed: 4089.92 MB/s

###################################
#         DD Benchmark Results for Pool: inferno    #
###################################
#    Threads: 1    #
#    1M Seq Write Run 1: 410.96 MB/s     #
#    1M Seq Write Run 2: 410.95 MB/s     #
#    1M Seq Write Avg: 410.96 MB/s #
#    1M Seq Read Run 1: 4204.60 MB/s      #
#    1M Seq Read Run 2: 5508.72 MB/s      #
#    1M Seq Read Avg: 4856.66 MB/s  #
###################################
#    Threads: 3    #
#    1M Seq Write Run 1: 1179.53 MB/s     #
#    1M Seq Write Run 2: 1165.82 MB/s     #
#    1M Seq Write Avg: 1172.67 MB/s #
#    1M Seq Read Run 1: 4260.03 MB/s      #
#    1M Seq Read Run 2: 4275.41 MB/s      #
#    1M Seq Read Avg: 4267.72 MB/s  #
###################################
#    Threads: 6    #
#    1M Seq Write Run 1: 1971.18 MB/s     #
#    1M Seq Write Run 2: 1936.90 MB/s     #
#    1M Seq Write Avg: 1954.04 MB/s #
#    1M Seq Read Run 1: 4237.76 MB/s      #
#    1M Seq Read Run 2: 4240.26 MB/s      #
#    1M Seq Read Avg: 4239.01 MB/s  #
###################################
#    Threads: 12    #
#    1M Seq Write Run 1: 2049.01 MB/s     #
#    1M Seq Write Run 2: 1940.13 MB/s     #
#    1M Seq Write Avg: 1994.57 MB/s #
#    1M Seq Read Run 1: 4087.74 MB/s      #
#    1M Seq Read Run 2: 4092.10 MB/s      #
#    1M Seq Read Avg: 4089.92 MB/s  #
###################################
Cleaning up test files...
Running disk read benchmark...
###################################
This benchmark tests the 4K sequential read performance of each disk in the system using dd. It is run 2 times for each disk and averaged.
In order to work around ARC caching in systems with it still enabled, This benchmark reads data in the amount of total system RAM or the total size of the disk, whichever is smaller.
###################################
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
#    Run 1: 2017.87 MB/s     #
#    Run 2: 1924.79 MB/s     #
#    Average: 1971.33 MB/s     #
#    Disk: nvme3n1    #
#    Run 1: 2008.92 MB/s     #
#    Run 2: 1911.36 MB/s     #
#    Average: 1960.14 MB/s     #
#    Disk: nvme5n1    #
#    Run 1: 2044.10 MB/s     #
#    Run 2: 1944.96 MB/s     #
#    Average: 1994.53 MB/s     #
#    Disk: nvme2n1    #
#    Run 1: 2039.12 MB/s     #
#    Run 2: 1943.66 MB/s     #
#    Average: 1991.39 MB/s     #
#    Disk: nvme4n1    #
#    Run 1: 1927.49 MB/s     #
#    Run 2: 1828.96 MB/s     #
#    Average: 1878.23 MB/s     #
#    Disk: nvme1n1    #
#    Run 1: 2031.78 MB/s     #
#    Run 2: 1933.92 MB/s     #
#    Average: 1982.85 MB/s     #
###################################

Total benchmark time: 16.45 minutes
Do you want to delete the testing dataset inferno/tn-bench? (yes/no): yes
Deleting dataset: inferno/tn-bench
Dataset inferno/tn-bench deleted.
 
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or fixes.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
