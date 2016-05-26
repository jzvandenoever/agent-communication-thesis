from collections import defaultdict
import datetime
import os
from os.path import isdir, join


def to_time(time_string):
    hours, minutes, smaller = time_string.split(':', 2)
    seconds, milisecs = smaller.split(',', 1)
    return datetime.datetime(year=1900, month=1, day=1,
        hour=int(hours), minute=int(minutes), second=int(seconds), microsecond=int(milisecs)*1000)


if __name__ == "__main__":
    path = os.getcwd()
    log_sets = [f for f in os.listdir(path) if isdir(join(path, f))]
    log_set_stats = defaultdict(dict)

    for log_set in log_sets:
        failure, _, correction = log_set.partition(' ')
        correction = not bool(correction)
        set_path = join(path, log_set)
        log_dirs = [f for f in os.listdir(set_path) if isdir(join(set_path, f))]
        for log_dir in log_dirs:
            list_of_logfiles = [f for f in os.listdir(join(set_path, log_dir)) if f[-1].isdigit()]
            list_of_logfiles.sort(cmp=lambda x, y: cmp(int(x.rsplit('.', 1)[-1]), int(y.rsplit('.', 1)[-1])), reverse=True)

            cur_summaries = {'amount': 0, 'run_time': [], 'good_drops': [], 'wrong_drops': [], 'rooms_entered': [], 'idletime': []}
            log_set_stats[log_dir][(failure, correction)] = cur_summaries
            for logfile in list_of_logfiles:
                last_index = 0
                with open(join(set_path, log_dir, logfile)) as logtext:
                    start_time = end_time = None
                    summary = [None, {}, {}, {}]
                    for line in logtext:
                        parts = line.split()
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
                            print set_path, log_dir, logfile, line
                        #if end_time and parts[2] in ('action', 'Bot'):
                        #    print set_path, log_dir, logfile, parts

                    # if len(summary[1]) > 0:
                    if end_time is not None:
                        cur_summaries['amount'] += 1
                        run_time = end_time - start_time
                        if run_time < datetime.timedelta():
                            raise ValueError('crossed date.')
                        cur_summaries['run_time'].append(run_time.total_seconds())
                        for i in range(1, len(summary)):
                            if not summary[i]:
                                continue
                            cur_summaries['good_drops'].append(int(summary[i]['gooddrops']))
                            cur_summaries['wrong_drops'].append(int(summary[i]['wrongdrops']))
                            cur_summaries['rooms_entered'].append(int(summary[i]['nroomsentered']))
                            cur_summaries['idletime'].append(float(summary[i]['idletime']))

    # print as csv log_set_stats
    csv_file = open('data.csv', 'w')
    csv_file.write('agent, com_failure, correction, run_time, idletime, good_drops, wrong_drops, rooms_entered\n')
    for agent in log_set_stats:
        for conditions in log_set_stats[agent]:
            stat_sets = log_set_stats[agent][conditions]
            assert len(stat_sets['idletime']) == len(stat_sets['good_drops']) == len(stat_sets['good_drops']) == \
                   len(stat_sets['wrong_drops']) == len(stat_sets['rooms_entered'])
            stats = zip(stat_sets['idletime'], stat_sets['good_drops'], stat_sets['wrong_drops'],
                        stat_sets['rooms_entered'])
            #repeat runtime to match the bot specific stats.
            stat_sets['run_time'] = [i for i in stat_sets['run_time'] for _ in xrange(3)]
            stats = zip(stat_sets['run_time'], stats)
            for stat in stats:
                csv_file.write('%s, %s, %s, %s, %s, %s, %s, %s\n' % (agent, conditions[0], conditions[1], stat[0],
                                                           stat[1][0], stat[1][1], stat[1][2], stat[1][3]))
