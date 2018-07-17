from collections import defaultdict
import datetime
import os
import os.path as path
import sys

from scipy.stats import ks_2samp


def to_time(time_string):
    hours, minutes, smaller = time_string.split(':', 2)
    seconds, milisecs = smaller.split(',', 1)
    return datetime.datetime(year=1900, month=1, day=1,
                             hour=int(hours), minute=int(minutes), second=int(seconds),
                             microsecond=int(milisecs) * 1000)


def process_log_files(log_file_path):
    list_of_logfiles = [f for f in os.listdir(log_file_path) if path.isfile(path.join(log_file_path, f))]

    cur_summary = {'amount': 0, 'run_time': [], 'good_drops': [], 'wrong_drops': [], 'rooms_entered': [],
                     'idletime': []}
    missing_end_time_count = 0
    long_runtime_count = 0
    for logfile in list_of_logfiles:
        last_index = 0
        with open(path.join(log_file_path, logfile)) as logtext:
            start_time = end_time = None
            summary = [None, {}, {}, {}]
            # It seems sometimes the run shuts down before anything was done. This generally happens before all rooms
            # got listed in the run.
            debug_room_def_count = 0
            # Process each line in the log file.
            for line in logtext:
                parts = line.split()

                if 'room' in parts:
                    debug_room_def_count +=1

                if parts[-1] == 'sequence':
                    start_time = to_time(parts[0])

                if 'finish' in parts and 'sequence' in parts:
                    end_time = to_time(parts[0])

                if 'agentsummary' in line:
                    if 'robot' in line:
                        index = last_index
                    else:
                        last_index = index = int(parts[3][4:])

                    type, value = parts[-2:]
                    summary[index][type] = value

                if not end_time and 'total time is' in line:
                    if float(parts[5]) < 1000:
                        missing_end_time_count += 1
                        if debug_room_def_count == 9:
                            print ('Warning no end time found.', log_file_path, logfile, line)

            # If we have a complete run we process the log summary.
            if end_time is not None:
                cur_summary['amount'] += 1
                run_time = end_time - start_time
                # Check if the runtime is negative so we detect day changes and correct for it.
                if run_time < datetime.timedelta():
                    end_time += datetime.timedelta(days=1)
                    run_time = end_time - start_time
                if run_time > datetime.timedelta(seconds=200):
                    long_runtime_count += 1
                cur_summary['run_time'].append(run_time.total_seconds())
                runtimes.append(run_time.total_seconds())
                for i in range(1, len(summary)):
                    if not summary[i]:
                        continue
                    cur_summary['good_drops'].append(int(summary[i]['gooddrops']))
                    cur_summary['wrong_drops'].append(int(summary[i]['wrongdrops']))
                    cur_summary['rooms_entered'].append(int(summary[i]['nroomsentered']))
                    cur_summary['idletime'].append(float(summary[i]['idletime']))
    return cur_summary, missing_end_time_count, long_runtime_count


def process_summaries(agent_summaries, reference_agent):
    """Reference is the agent name that we are using as reference. We are assuming this to be an agent with all maps,
    done by 1 agent, with no communication failure."""
    reference_summaries = agent_summaries.pop(reference_agent)
    # Map reference dict to skip the static agent_count 1 and failure_chance 0.00
    for map_dir in reference_summaries.keys():
        reference_summaries[map_dir] = reference_summaries[map_dir]['1']['0.00']

    # Do comparisons.
    for agent, agent_summary in agent_summaries.items():
        for map, map_summary in agent_summary.items():
            for agent_count, agent_count_summary in map_summary.items():
                for failure, failure_summary in agent_count_summary.items():
                    ks_test_result = ks_2samp(reference_summaries[map]['run_time'], failure_summary['run_time'])
                    print('KS Test result for', agent, map, agent_count, failure, 'resulting in', ks_test_result)


if __name__ == "__main__":
    log_dir = os.getcwd()
    agent_directories = [f for f in os.listdir(log_dir) if path.isdir(path.join(log_dir, f))]
    print('AGENT DIRS!', agent_directories)
    log_set_stats = defaultdict(dict)
    missing_end_time_count = 0
    runtimes = []
    long_runtime_count = defaultdict(int)
    agent_summaries = dict()

    for agent_dir in agent_directories:
        agent_path = path.join(log_dir, agent_dir)
        map_directories = [f for f in os.listdir(agent_path) if path.isdir(path.join(agent_path, f))]
        map_summaries = dict()
        for map_dir in map_directories:
            map_path = path.join(agent_path, map_dir)
            count_directories = [f for f in os.listdir(map_path) if path.isdir(path.join(map_path, f))]
            count_summaries = dict()
            for count_dir in count_directories:
                count_path = path.join(map_path, count_dir)
                failure_directories = [f for f in os.listdir(count_path) if path.isdir(path.join(count_path, f))]
                failure_summaries = dict()
                for failure_dir in failure_directories:
                    failure_path = path.join(count_path, failure_dir)
                    log_summary, log_missing_endtime_count, log_long_runtime_count = process_log_files(failure_path)
                    failure_summaries[failure_dir] = log_summary
                    missing_end_time_count += log_missing_endtime_count
                    long_runtime_count[failure_path] = log_long_runtime_count
                # Populate the count summaries after processing all the failure logs
                count_summaries[count_dir] = failure_summaries
            # Populate the map summaries after processing all the count logs
            map_summaries[map_dir] = count_summaries
        # Populate the agent summaries after processing all the map logs
        agent_summaries[agent_dir] = map_summaries

        print('FINISHED AGENT', agent_dir)
        print('This many runs failed:', missing_end_time_count)
        import statistics

        print('Average Runtime:', sum(runtimes) / len(runtimes), 'Median runtime:', statistics.median(runtimes),
              'Higest Runtime:', max(runtimes), '10 highest runtimes:', sorted(runtimes)[-10:])
        print('long runtime counts', long_runtime_count)
        missing_end_time_count = 0
        runtimes = []
        long_runtime_count = defaultdict(int)
        print(
        '==========================================================================================================')

    if len(sys.argv) > 1:
        process_summaries(agent_summaries, sys.argv[1])