from datetime import datetime
import subprocess
import re
import json


def main():
    """Runs a bunch of benchmarks, parses the results with ugly regexes and stores the outcome in a json file"""

    dt = datetime.now()

    # Sequential write
    sequential_disk_write_output = subprocess.run('dd if=/dev/zero of=tempfile bs=1M count=1024 conv=fdatasync,notrunc',
                                                  stderr=subprocess.PIPE, shell=True).stderr.decode()
    sequential_disk_write = float(re.search(' s, \d*', sequential_disk_write_output).group().replace(' s, ', '').replace(' MB/s', ''))

    # Drop cache
    subprocess.run('echo 3 | sudo tee /proc/sys/vm/drop_caches', shell=True)

    # Sequential read
    sequential_disk_read_output = subprocess.run('dd if=tempfile of=/dev/null bs=1M count=1024',
                                                 stderr=subprocess.PIPE, shell=True).stderr.decode()
    sequential_disk_read = float(re.search(' s, \d*', sequential_disk_read_output).group().replace(' s, ', ''.replace(' MB/s', ''))

    # Random read and write
    random_disk_output = subprocess.run('fio --rw=randrw --name=test --size=20M --direct=1 | grep "read\|write"',
                                        stdout=subprocess.PIPE, shell=True).stdout.decode()
    random_disk_read_output, random_disk_write_output, _, _ = random_disk_output.split('\n')
    random_disk_read = int(re.search('iops=\d*', random_disk_read_output).group().replace('iops=', ''))
    random_disk_write = int(re.search('iops=\d*', random_disk_write_output).group().replace('iops=', ''))

    # Memory
    memory_output = subprocess.run(['./memsweep.sh'], stdout=subprocess.PIPE).stdout.decode()
    memory = float(re.search('seconds: .*', memory_output).group().replace('seconds: ', ''))

    # CPU
    cpu_output = subprocess.run(['./linpack.sh'], stdout=subprocess.PIPE).stdout.decode()
    cpu = float(re.search('result: .*', cpu_output).group().replace('result: ', '').replace(' KFLOPS', ''))

    with open('measurements/{:%d-%H}.json'.format(dt), 'w') as f:
        json.dump({
            'time': '{:%Y-%m-%dT%H:%M:00}'.format(dt),
            'sequential_disk_read_mbs': sequential_disk_read,
            'sequential_disk_write_mbs': sequential_disk_write,
            'random_disk_read_iops': random_disk_read,
            'random_disk_write_iops': random_disk_write,
            'memory': memory,
            'cpu_kflops': cpu
        }, f, indent=4)


if __name__ == "__main__":
    main()
