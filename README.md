# TN-Bench v1.00

TN-Bench is an OpenSource software script that benchmarks your system and collects various statistical information via the TrueNAS API. It creates a dataset in each of your pools during testing, consuming 10 GiB of space for each thread in your system.

## Features

- Collects system information using TrueNAS API.
- Benchmarks system performance using `dd` command.
- Provides detailed information about system, pools, and disks.
- Supports multi-threaded read and write benchmarks.


### Running the Script

   ```
   git clone https://github.com/nickf1227/TN-Bench.git && cd TN-Bench && python3 truenas-bench.py
   ```
The script will display system and pool information, then prompt you to continue with the benchmarks. Follow the prompts to complete the benchmarking process.

### Benchmarking Process

- **Dataset Creation**: The script creates a temporary dataset in each pool.
- **Write Benchmark**: The script performs four runs of the write benchmark using `dd` with varying thread counts.
- **Read Benchmark**: The script performs four runs of the read benchmark using `dd` with varying thread counts.
- **Results**: The script displays the results for each run and the average speed.

### Cleanup

After the benchmarking is complete, the script prompts you to delete the datasets created during the process.

## Example Output

```
###################################
#                                 #
#          TN-Bench v1.00         #
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
Load Average (1m)     | 0.22607421875                               
Load Average (5m)     | 1.54833984375                               
Load Average (15m)    | 2.447265625                                 
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
Run 1 write speed: 411.39 MB/s
Run 2 write speed: 412.18 MB/s
Run 3 write speed: 412.35 MB/s
Run 4 write speed: 411.94 MB/s
Average write speed: 411.96 MB/s
Running DD read benchmark with 1 threads...
Run 1 read speed: 8226.72 MB/s
Run 2 read speed: 8015.52 MB/s
Run 3 read speed: 8290.26 MB/s
Run 4 read speed: 8097.91 MB/s
Average read speed: 8157.61 MB/s
Running DD write benchmark with 3 threads...
Run 1 write speed: 1146.18 MB/s
Run 2 write speed: 1188.32 MB/s
Run 3 write speed: 1187.90 MB/s
Run 4 write speed: 1184.87 MB/s
Average write speed: 1176.82 MB/s
Running DD read benchmark with 3 threads...
Run 1 read speed: 4173.55 MB/s
Run 2 read speed: 4227.74 MB/s
Run 3 read speed: 4220.36 MB/s
Run 4 read speed: 4222.56 MB/s
Average read speed: 4211.05 MB/s
Running DD write benchmark with 6 threads...
Run 1 write speed: 2055.52 MB/s
Run 2 write speed: 2050.54 MB/s
Run 3 write speed: 2041.28 MB/s
Run 4 write speed: 2045.12 MB/s
Average write speed: 2048.12 MB/s
Running DD read benchmark with 6 threads...
Run 1 read speed: 4136.48 MB/s
Run 2 read speed: 4149.05 MB/s
Run 3 read speed: 4142.20 MB/s
Run 4 read speed: 4138.69 MB/s
Average read speed: 4141.60 MB/s
Running DD write benchmark with 12 threads...
Run 1 write speed: 2399.55 MB/s
Run 2 write speed: 2143.21 MB/s
Run 3 write speed: 2107.37 MB/s
Run 4 write speed: 2095.10 MB/s
Average write speed: 2186.31 MB/s
Running DD read benchmark with 12 threads...
Run 1 read speed: 4117.50 MB/s
Run 2 read speed: 4115.39 MB/s
Run 3 read speed: 4112.43 MB/s
Run 4 read speed: 4126.08 MB/s
Average read speed: 4117.85 MB/s

###################################
#         DD Benchmark Results for Pool: inferno    #
###################################
#    Threads: 1    #
#    1M Seq Write Run 1: 411.39 MB/s     #
#    1M Seq Write Run 2: 412.18 MB/s     #
#    1M Seq Write Run 3: 412.35 MB/s     #
#    1M Seq Write Run 4: 411.94 MB/s     #
#    1M Seq Write Avg: 411.96 MB/s #
#    1M Seq Read Run 1: 8226.72 MB/s      #
#    1M Seq Read Run 2: 8015.52 MB/s      #
#    1M Seq Read Run 3: 8290.26 MB/s      #
#    1M Seq Read Run 4: 8097.91 MB/s      #
#    1M Seq Read Avg: 8157.61 MB/s  #
###################################
#    Threads: 3    #
#    1M Seq Write Run 1: 1146.18 MB/s     #
#    1M Seq Write Run 2: 1188.32 MB/s     #
#    1M Seq Write Run 3: 1187.90 MB/s     #
#    1M Seq Write Run 4: 1184.87 MB/s     #
#    1M Seq Write Avg: 1176.82 MB/s #
#    1M Seq Read Run 1: 4173.55 MB/s      #
#    1M Seq Read Run 2: 4227.74 MB/s      #
#    1M Seq Read Run 3: 4220.36 MB/s      #
#    1M Seq Read Run 4: 4222.56 MB/s      #
#    1M Seq Read Avg: 4211.05 MB/s  #
###################################
#    Threads: 6    #
#    1M Seq Write Run 1: 2055.52 MB/s     #
#    1M Seq Write Run 2: 2050.54 MB/s     #
#    1M Seq Write Run 3: 2041.28 MB/s     #
#    1M Seq Write Run 4: 2045.12 MB/s     #
#    1M Seq Write Avg: 2048.12 MB/s #
#    1M Seq Read Run 1: 4136.48 MB/s      #
#    1M Seq Read Run 2: 4149.05 MB/s      #
#    1M Seq Read Run 3: 4142.20 MB/s      #
#    1M Seq Read Run 4: 4138.69 MB/s      #
#    1M Seq Read Avg: 4141.60 MB/s  #
###################################
#    Threads: 12    #
#    1M Seq Write Run 1: 2399.55 MB/s     #
#    1M Seq Write Run 2: 2143.21 MB/s     #
#    1M Seq Write Run 3: 2107.37 MB/s     #
#    1M Seq Write Run 4: 2095.10 MB/s     #
#    1M Seq Write Avg: 2186.31 MB/s #
#    1M Seq Read Run 1: 4117.50 MB/s      #
#    1M Seq Read Run 2: 4115.39 MB/s      #
#    1M Seq Read Run 3: 4112.43 MB/s      #
#    1M Seq Read Run 4: 4126.08 MB/s      #
#    1M Seq Read Avg: 4117.85 MB/s  #
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
#    Run 1: 2009.14 MB/s     #
#    Run 2: 2680.08 MB/s     #
#    Run 3: 3970.21 MB/s     #
#    Run 4: 3964.53 MB/s     #
#    Average: 3155.99 MB/s     #
#    Disk: nvme3n1    #
#    Run 1: 1978.65 MB/s     #
#    Run 2: 2072.62 MB/s     #
#    Run 3: 3974.11 MB/s     #
#    Run 4: 3975.83 MB/s     #
#    Average: 3000.30 MB/s     #
#    Disk: nvme5n1    #
#    Run 1: 1944.16 MB/s     #
#    Run 2: 2715.57 MB/s     #
#    Run 3: 3968.82 MB/s     #
#    Run 4: 3970.32 MB/s     #
#    Average: 3149.72 MB/s     #
#    Disk: nvme2n1    #
#    Run 1: 1783.78 MB/s     #
#    Run 2: 1734.97 MB/s     #
#    Run 3: 3961.26 MB/s     #
#    Run 4: 3976.13 MB/s     #
#    Average: 2864.04 MB/s     #
#    Disk: nvme4n1    #
#    Run 1: 1927.84 MB/s     #
#    Run 2: 1876.39 MB/s     #
#    Run 3: 3964.16 MB/s     #
#    Run 4: 3970.86 MB/s     #
#    Average: 2934.81 MB/s     #
#    Disk: nvme1n1    #
#    Run 1: 1976.26 MB/s     #
#    Run 2: 1917.99 MB/s     #
#    Run 3: 3954.96 MB/s     #
#    Run 4: 3960.59 MB/s     #
#    Average: 2952.45 MB/s     #
###################################

Total benchmark time: 14.26 minutes
Do you want to delete the testing dataset inferno/tn-bench? (yes/no): 
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or fixes.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
