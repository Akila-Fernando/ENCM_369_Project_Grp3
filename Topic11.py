import matplotlib.pyplot as plt

# Gantt Chart Plotter
def plot_gantt_chart(processes, title):
    fig, ax = plt.subplots(figsize=(10, 2))
    y = 0
    colors = ['tab:blue', 'tab:orange']

    for idx, p in enumerate(processes):
        color = colors[idx % len(colors)] 
        ax.broken_barh([(p['start'], p['burst'])], (y, 1), facecolors=color)
        ax.text(p['start'] + p['burst'] / 2, y + 0.5, p['id'], ha='center', va='center', color='white')
    ax.set_ylim(0, 1)
    ax.set_xlim(0, max(p['start'] + p['burst'] for p in processes))
    ax.set_xlabel('Time')
    ax.set_yticks([])
    ax.set_title(title)
    plt.tight_layout()
    plt.show()

# Scheduling Simulations
def get_all_algorithms_gantt_data():
    all_data = {}

    # FCFS
    processes_fcfs = [{'id': f'P{i+1}', 'arrival': i % 4, 'burst': (i * 3) % 10 + 1} for i in range(13)]
    time = 0
    for p in processes_fcfs:
        p['start'] = max(time, p['arrival'])
        time = p['start'] + p['burst']
    all_data["FCFS"] = processes_fcfs

    # SJF Non-preemptive
    processes_sjf = [{'id': f'P{i+1}', 'arrival': i % 4, 'burst': (13 - i) % 10 + 1} for i in range(13)]
    time = 0
    completed = []
    ready_queue = []
    while len(completed) < len(processes_sjf):
        ready_queue.extend([p for p in processes_sjf if p not in completed and p['arrival'] <= time and p not in ready_queue])
        if ready_queue:
            ready_queue.sort(key=lambda x: x['burst'])
            p = ready_queue.pop(0)
            p['start'] = time
            time += p['burst']
            completed.append(p)
        else:
            time += 1
    all_data["SJF"] = completed

    # Round Robin
    rr_processes = [{'id': f'P{i+1}', 'arrival': i % 3, 'burst': (i * 2) % 9 + 1} for i in range(13)]
    quantum = 3
    remaining = {p['id']: p['burst'] for p in rr_processes}
    arrival_map = {p['id']: p['arrival'] for p in rr_processes}
    time = 0
    queue = [p['id'] for p in rr_processes if p['arrival'] <= time]
    gantt = []
    visited = set(queue)
    while remaining:
        if not queue:
            time += 1
            for p in rr_processes:
                if p['arrival'] <= time and p['id'] in remaining and p['id'] not in visited:
                    queue.append(p['id'])
                    visited.add(p['id'])
            continue
        pid = queue.pop(0)
        bt = min(quantum, remaining[pid])
        start_time = time
        time += bt
        gantt.append({'id': pid, 'start': start_time, 'burst': bt})
        remaining[pid] -= bt
        if remaining[pid] == 0:
            del remaining[pid]
        for p in rr_processes:
            if p['arrival'] <= time and p['id'] in remaining and p['id'] not in visited:
                queue.append(p['id'])
                visited.add(p['id'])
        if pid in remaining:
            queue.append(pid)
    all_data["Round Robin"] = gantt

    # Priority Scheduling
    processes_priority = [{'id': f'P{i+1}', 'burst': (i * 4) % 10 + 1, 'priority': (i * 7) % 10 + 1} for i in range(13)]
    processes_priority.sort(key=lambda x: x['priority'])
    time = 0
    for p in processes_priority:
        p['start'] = time
        time += p['burst']
    all_data["Priority"] = processes_priority

    return all_data

# Compute waiting and turnaround time

def compute_wait_turnaround(processes, is_fragmented=False):
    result = {}
    completion = {}
    arrival = {}
    burst = {}
    if is_fragmented:
        for p in processes:
            if p['id'] not in arrival:
                arrival[p['id']] = 0
                burst[p['id']] = 0
            burst[p['id']] += p['burst']
            completion[p['id']] = p['start'] + p['burst']
        for pid in burst:
            turnaround = completion[pid] - arrival[pid]
            waiting = turnaround - burst[pid]
            result[pid] = (waiting, turnaround)
    else:
        for p in processes:
            arrival[p['id']] = p.get('arrival', 0)
            bt = p['burst']
            st = p['start']
            waiting = st - arrival[p['id']]
            turnaround = bt + waiting
            result[p['id']] = (waiting, turnaround)
    return result

# Run all
all_scheduling_data = get_all_algorithms_gantt_data()
metrics = {}
for sched_type, process_list in all_scheduling_data.items():
    is_frag = (sched_type == "Round Robin")
    metrics[sched_type] = compute_wait_turnaround(process_list, is_fragmented=is_frag)
    plot_gantt_chart(process_list, sched_type)

# Plot waiting vs turnaround comparison
fig, ax = plt.subplots(figsize=(10, 6))
for sched_type, data in metrics.items():
    waiting_times = [data[pid][0] for pid in data]
    turnaround_times = [data[pid][1] for pid in data]
    ax.plot(waiting_times, turnaround_times, marker='o', label=sched_type)

ax.set_xlabel("Waiting Time")
ax.set_ylabel("Turnaround Time")
ax.set_title("Waiting Time vs Turnaround Time for Scheduling Algorithms")
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()
