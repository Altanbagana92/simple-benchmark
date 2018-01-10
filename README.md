# Openstack list and boot benchmark

## Results
#### Openstack server list
![Sequential Disk](img/seq_disk.png)

#### Openstack boot VM
![Random Disk](img/rnd_disk.png)

## Setup
On the Openstack VM
```
sudo apt-get update
sudo apt-get install openstack
```

To get the data
```
scp -i C:\.ssh\ccg10.pem ubuntu@10.200.2.172:simple-benchmark-master/measurements/* measurements\
```

Run the notebook