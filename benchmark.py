from datetime import datetime
import time
import subprocess
import re
import json
import os


FLAGS = '--os-username cc1718-group10 --os-password 6sXyXJ5iss --os-tenant-name cc1718-group10 --os-auth-url http://cloud.cit.tu-berlin.de:5000/v2.0/'
NUM_ITERATIONS = 5

def main():
    """Runs a bunch of benchmarks, parses the results with ugly regexes and stores the outcome in a json file"""
    print('Running benchmark')

    dt = datetime.now()
    base_path = os.path.dirname(os.path.realpath(__file__))

    list_measurements = []
    boot_measurements = []
    for i in range(NUM_ITERATIONS):
        print('Benchmark iteration {}/{}'.format(i+1, NUM_ITERATIONS))
        # List VMs
        list_start = time.time()
        subprocess.run('openstack server list {}'.format(FLAGS), shell=True)
        list_measurements.append(time.time() - list_start)
        # Boot a VM
        boot_start = time.time()
        subprocess.run('openstack server create --flavor "Cloud Computing" --image ubuntu-16.04 --nic net-id=cc-net --security-group default {} boot-benchmark'.format(FLAGS), shell=True)
        # List the VMs until boot-benchmark is 'ACTIVE' and get it's IP
        while True:
            list_result = subprocess.run('openstack server list {} | grep boot-benchmark'.format(FLAGS), stdout=subprocess.PIPE, shell=True).stdout.decode()
            print(list_result)
            if 'ACTIVE' in list_result:
                break
        ip = re.search('cc-net=.*? ', list_result).group().replace('cc-net=', '').strip()
        # Wait until VM is reachable via ping
        subprocess.run('while true; do ping -c1 {} > /dev/null && break; done'.format(ip), shell=True)
        boot_measurements.append(time.time() - boot_start)
        print('Able to reach {}!'.format(ip))
        # Shut down VM
        subprocess.run('openstack server delete {} boot-benchmark'.format(FLAGS), shell=True)
        # Wait 5 seconds before the next run
        time.sleep(5)

    print(list_measurements)
    print(boot_measurements)

    with open(os.path.join(base_path, 'measurements', '{:%d%H%M}.json'.format(dt)), 'w') as f:
        json.dump({
            'time': '{:%Y-%m-%dT%H:%M:00}'.format(dt),
            'list_measurements': sum(list_measurements) / len(list_measurements),
            'boot_measurements': sum(boot_measurements) / len(boot_measurements),
        }, f, indent=4)

    print('Finished benchmark')


if __name__ == "__main__":
    while True:
        start = time.time()
        main()
        end = time.time()
        time.sleep((3600 * 4) + start - end)
