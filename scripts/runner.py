import argparse
import subprocess
import shlex
import os
import shutil

FAILURES = [0, 5, 25, 50, 75, 95, 100]
CMD = 'java -cp {runtime} goal.tools.Run "{mas}" --repeats {repeats} --timeout {timeout} ' \
      '--dropchance {failure}'
BW4T_CMD = 'java -jar {bw4t}'
DEFAULT_RUNTIME = 'runtime.jar'
DEFAULT_BW4T = 'bw4t.jar'
DEFAULT_REPEATS = 1 # No repeats
DEFAULT_TIMEOUT = 300 # five minutes]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run BW4T.')
    parser.add_argument('--bw4t', type=str, default=DEFAULT_BW4T,
                        nargs=1, help='The location for the BW4T server.')
    parser.add_argument('--runtime', type=str, default=DEFAULT_RUNTIME,
                        nargs=1, help='The location for the GOAL runtime.')
    parser.add_argument('--repeats', type=int, default=DEFAULT_REPEATS, nargs=1,
                        help='How many times should each mas file be tested per com '
                             'failure mode.')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT,
                        help='What is the timeout per run.')
    parser.add_argument('mas', type=str, default=DEFAULT_RUNTIME, nargs='+',
                        help='The location for the MAS files to be run. '
                        'Multiple can be provided which will be run in sequence.')
    args = parser.parse_args()

    DEVNULL = open(os.devnull, 'wb')
    for masfile in args.mas:
        for fail_chance in FAILURES:
            bw4t_path = os.path.dirname(args.bw4t)
            bw4t_logs = bw4t_path.join('log')
            if os.path.exists(bw4t_logs):
                shutil.rmtree(bw4t_path.join('log'))

            server = subprocess.Popen(shlex.split(BW4T_CMD.format(bw4t=args.bw4t)), stdout=DEVNULL,
                                      stderr=subprocess.STDOUT)
            client_command = CMD.format(runtime=args.runtime, repeats=args.repeats, mas=masfile,
                                        timeout=args.timeout, failure=fail_chance)
            # This way I don't need to check for spaces and stuff that needs escaping.
            client = subprocess.Popen(shlex.split(client_command), stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
            while True:
                line = client.stdout.readline()
                # Do stuff with the runtime output here.
                poll = client.poll()
                if line.endswith('milliseconds to run jobs.') or poll == None:
                    print line, poll
                    break

            client.terminate()
            server.terminate()
            client.communicate()

            mas_name = os.path.basename(masfile)
            os.renames(bw4t_logs, os.path.join(mas_name, '%.2f' % (fail_chance/100.0)))
            print 'Ran {mas} with the following failure chance: {chance}'.format(mas=masfile,
                                                                                 chance=fail_chance)
    print 'Finished doing runs.'




