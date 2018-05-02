import argparse
import subprocess
import shlex
import os
import shutil
import tempfile
import re
import threading
from Queue import Queue, Empty

FAILURES = [0]#, 5, 25, 50, 75, 95, 100]
AGENT_COUNTS = [3]#, 5, 10]
CMD = 'java -cp {runtime} goal.tools.Run "{mas}" -v --repeats {repeats} --timeout {timeout}'
BW4T_CMD = 'java -jar {bw4t} -gui false'
DEFAULT_RUNTIME = 'runtime.jar'
DEFAULT_BW4T = 'bw4t.jar'
DEFAULT_REPEATS = 1  # No repeats
DEFAULT_TIMEOUT = 300  # five minutes]


def enqueue_output(out, queue, stop_event):
    for line in iter(out.readline, b''):
        if stop_event.is_set():
            break
        queue.put(line)


def setup_nonblocking_read(output):
    q = Queue()
    t_stop = threading.Event()
    t = threading.Thread(target=enqueue_output, args=(output, q, t_stop))
    t.daemon = True  # thread dies with the program
    t.start()
    return q, t_stop


def non_block_readline(q):
    try:
        line = q.get_nowait()
    except Empty:
        return ''
    else:
        return line


def prepare_fail_chance(fail_chance, maslocation):
    mas_dir = os.path.dirname(maslocation)
    fail_file_loc = os.path.join(mas_dir, 'common/failure.pl')
    print 'LOCATIONS:', mas_dir, fail_file_loc
    with open(fail_file_loc, 'w+') as fail_file:
        fail_file.write('dropChance({0}).'.format(fail_chance))
        print 'TEST WRITE:', 'dropChance({0}).'.format(fail_chance)


def prepare_mas(maslocation, agent_count):
    mas_file = open(maslocation)
    mas_contents = mas_file.readlines()
    changed_mas = tempfile.NamedTemporaryFile(delete=False)
    replacement_count = 'agentcount = "%s"' % agent_count
    for line in mas_contents:
        if 'agentcount' in line:
            line = re.sub(r'agentcount ?= ?["\']\d+["\']', replacement_count, line)

        changed_mas.write(line)
    changed_mas.close()
    dest_name = os.path.join(os.path.dirname(maslocation),
                             os.path.basename(changed_mas.name) + '.mas2g')
    shutil.move(changed_mas.name, dest_name)
    return dest_name


def prepare_logfile(bw4t_logs):
    tries = 0
    log_file = None
    while log_file is None:
        tries += 1
        if tries > 10:
            print "Could not open log file after ten tries."
            break
        import time
        time.sleep(1)
        for listed_file in os.listdir(bw4t_logs):
            if listed_file.endswith(".log"):
                log_file = open(os.path.join(bw4t_logs, listed_file))
                print 'Found logfile:', listed_file
                break
    return log_file


def detect_early_stop(log_lines, agents, agent_count):
    for logline in log_lines:
        logline = logline.split()
        if logline[2] != 'action':
            break

        agent_name = logline[3]
        agent_action = logline[4]
        agent_data = agents.get(agent_name, ('', False))
        if agent_data[0] == agent_action:
            agents[agent_name] = (agent_action, True)
        elif 'collided' in agent_action:
            pass
        else:
            agents[agent_name] = (agent_action, False)
    # do stuff if all agents are repeating themselves.
    if len(agents) == agent_count and all([data[1] for data in agents.values()]):
        return True
    return False


def run(args):
    for maslocation in args.mas:
        for agent_count in AGENT_COUNTS:
            mas_name = os.path.basename(maslocation)
            masfile = prepare_mas(maslocation, agent_count)

            for fail_chance in FAILURES:
                print 'Doing run with {fail} chance of communication failure.'.format(fail=fail_chance)
                #prepare_fail_chance(fail_chance, masfile)

                bw4t_path = os.path.dirname(args.bw4t)
                bw4t_logs = bw4t_path.join('log')
                if os.path.exists(bw4t_logs):
                    shutil.rmtree(bw4t_path.join('log'))
                print 'Removed old logs if existing.'

                server = subprocess.Popen(shlex.split(BW4T_CMD.format(bw4t=args.bw4t)),
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                # Make sure the server has started properly
                while True:
                    line = server.stdout.readline()
                    if 'Launching the BW4T Server Graphical User Interface.' in line or \
                            'Launching the BW4T Server without a graphical user interface.' in line:
                        print 'Launched BW4T server.'
                        break

                client_command = CMD.format(runtime=args.runtime, repeats=args.repeats, mas=masfile,
                                            timeout=args.timeout)
                # This way I don't need to check for spaces and stuff that needs escaping.
                client = subprocess.Popen(shlex.split(client_command), stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)
                # Setup the goal log reading.
                #log_file = prepare_logfile(bw4t_logs)

                agents = {}
                # Process runtime data.
                print 'start processing'
                client_q, client_t = setup_nonblocking_read(client.stdout)
                server_q, server_t = setup_nonblocking_read(server.stdout)
                print 'setup client and server'
                while True:
                    line = non_block_readline(client_q)
                    serverlines = non_block_readline(server_q)
                    # Do stuff with the runtime output here.
                    # log_lines = log_file.readlines()  # Haven't made the runtime output useful yet.

                    # Do cycle detection, and nothing happens detection.
                    if args.repeats == 1 and detect_early_stop(log_lines, agents, agent_count):
                        print 'Stopped because of action cycles.'
                        break

                    # Detect the end of the run.
                    poll = client.poll()
                    if (line.startswith('ran for') and line.endswith('seconds.\n')) or poll is not None:
                        print 'Finished run'
                        break
                
                print 'Shutting down'
                client_t.set()
                server_t.set()
                client.terminate()
                server.terminate()
                client.wait()
                print 'shut down'  # shut down client server read threads.

                try:
                    os.renames(bw4t_logs, os.path.join(mas_name, '%d' % agent_count,
                                                       '%.2f' % (fail_chance / 100.0)))
                except OSError as e:
                    print 'error moving logs to %s' % os.path.join(mas_name, '%d' % agent_count,
                                                                   '%.2f' % (fail_chance / 100.0))
                    print e
                print 'Ran {mas} with the following failure chance: {chance}'.format(mas=mas_name,
                                                                                     chance=fail_chance)
            os.remove(masfile)
    print 'Finished doing runs.'


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
    parser.add_argument('mas', type=str, nargs='+',
                        help='The location for the MAS files to be run. '
                        'Multiple can be provided which will be run in sequence.')
    run(parser.parse_args())