from datetime import datetime
import time
import subprocess
import re
import json
import os


def main():
    """Runs a bunch of benchmarks, parses the results with ugly regexes and stores the outcome in a json file"""
    print('Running benchmark')

    dt = datetime.now()
    base_path = os.path.dirname(os.path.realpath(__file__))

    # Sequential write
    sequential_disk_write_output = subprocess.run('dd if=/dev/zero of=tempfile bs=1M count=1024 conv=fdatasync,notrunc',
                                                  stderr=subprocess.PIPE, shell=True).stderr.decode()
    sequential_disk_write = float(re.search(' s, \d*', sequential_disk_write_output).group().replace(' s, ', '').replace(' MB/s', ''))

    # Drop cache
    subprocess.run('echo 3 | sudo tee /proc/sys/vm/drop_caches', shell=True)

    # Sequential read
    sequential_disk_read_output = subprocess.run('dd if=tempfile of=/dev/null bs=1M count=1024',
                                                 stderr=subprocess.PIPE, shell=True).stderr.decode()
    sequential_disk_read = float(re.search(' s, \d*', sequential_disk_read_output).group().replace(' s, ', '').replace(' MB/s', ''))

    # Random read and write
    random_disk_output = subprocess.run('fio --rw=randrw --name=test --size=20M --direct=1 | grep "read\|write"',
                                        stdout=subprocess.PIPE, shell=True).stdout.decode()

    random_disk_read_output, random_disk_write_output, _, _ = random_disk_output.split('\n')
    random_disk_read = int(re.search('iops=\d*', random_disk_read_output).group().replace('iops=', ''))
    random_disk_write = int(re.search('iops=\d*', random_disk_write_output).group().replace('iops=', ''))

    # Disk clean up
    subprocess.run('rm tempfile test.0.0', shell=True)

    # Memory
    memory_output = subprocess.run([os.path.join(base_path, 'memsweep.sh')], stdout=subprocess.PIPE).stdout.decode()
    memory = float(re.search('seconds: .*', memory_output).group().replace('seconds: ', ''))

    # CPU
    cpu_output = subprocess.run([os.path.join(base_path, 'linpack.sh')], stdout=subprocess.PIPE).stdout.decode()
    cpu = float(re.search('result: .*', cpu_output).group().replace('result: ', '').replace(' KFLOPS', ''))

    with open(os.path.join(base_path, 'measurements', '{:%d%H%M}.json'.format(dt)), 'w') as f:
        json.dump({
            'time': '{:%Y-%m-%dT%H:%M:00}'.format(dt),
            'sequential_disk_read_mbs': sequential_disk_read,
            'sequential_disk_write_mbs': sequential_disk_write,
            'random_disk_read_iops': random_disk_read,
            'random_disk_write_iops': random_disk_write,
            'memory': memory,
            'cpu_kflops': cpu
        }, f, indent=4)

    print('Finished benchmark')


if __name__ == "__main__":
    for i in range(12):
        start = time.time()
        main()
        end = time.time()
        time.sleep((3600 * 4) + start - end)
