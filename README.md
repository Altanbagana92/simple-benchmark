# Openstack list and boot benchmark

## Results
#### Openstack server list
![Sequential Disk](img/list.png)

#### Openstack boot VM
![Random Disk](img/boot.png)

## Setup
On the Openstack VM
```
sudo apt-get update
sudo apt-get install openstack
python3 benchmark.py
```

To get the data
```
scp -i C:\.ssh\ccg10.pem ubuntu@10.200.2.172:simple-benchmark-master/measurements/* measurements\
```

Run the notebook