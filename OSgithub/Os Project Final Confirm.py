import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import copy

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.waiting_time = 0
        self.turnaround_time = 0

# FCFS Scheduling
def fcfs_scheduling(processes):
    processes.sort(key=lambda x: x.arrival_time)
    current_time = 0
    gantt_chart = []
    for process in processes:
        start_time = max(current_time, process.arrival_time)
        gantt_chart.append((process.pid, start_time, start_time + process.burst_time))
        process.waiting_time = start_time - process.arrival_time
        process.turnaround_time = process.waiting_time + process.burst_time
        current_time = start_time + process.burst_time
    return processes, gantt_chart

# Round Robin Scheduling
def round_robin_scheduling(processes, quantum):
    queue = sorted(copy.deepcopy(processes), key=lambda x: x.arrival_time)
    current_time = 0
    gantt_chart = []
    ready_queue = []
    process_map = {p.pid: p for p in processes}
    while queue or ready_queue:
        if not ready_queue and queue:
            current_time = max(current_time, queue[0].arrival_time)
        while queue and queue[0].arrival_time <= current_time:
            ready_queue.append(queue.pop(0))
        if ready_queue:
            process = ready_queue.pop(0)
            execute_time = min(process.remaining_time, quantum)
            gantt_chart.append((process.pid, current_time, current_time + execute_time))
            process.remaining_time -= execute_time
            current_time += execute_time
            if process.remaining_time > 0:
                while queue and queue[0].arrival_time <= current_time:
                    ready_queue.append(queue.pop(0))
                ready_queue.append(process)
            else:
                original = process_map[process.pid]
                original.turnaround_time = current_time - original.arrival_time
                original.waiting_time = original.turnaround_time - original.burst_time
    return list(process_map.values()), gantt_chart

# SJF Scheduling (Non-preemptive)
def sjf_scheduling(processes):
    processes = copy.deepcopy(processes)
    completed = []
    gantt_chart = []
    current_time = 0
    while processes:
        available = [p for p in processes if p.arrival_time <= current_time]
        if available:
            process = min(available, key=lambda p: p.burst_time)
        else:
            current_time = min(processes, key=lambda p: p.arrival_time).arrival_time
            continue
        start_time = current_time
        end_time = start_time + process.burst_time
        gantt_chart.append((process.pid, start_time, end_time))
        process.waiting_time = start_time - process.arrival_time
        process.turnaround_time = process.waiting_time + process.burst_time
        current_time = end_time
        completed.append(process)
        processes.remove(process)
    return completed, gantt_chart

# Priority Scheduling
def priority_scheduling(processes):
    processes.sort(key=lambda x: (x.arrival_time, x.priority))
    current_time = 0
    gantt_chart = []
    for process in processes:
        start_time = max(current_time, process.arrival_time)
        gantt_chart.append((process.pid, start_time, start_time + process.burst_time))
        process.waiting_time = start_time - process.arrival_time
        process.turnaround_time = process.waiting_time + process.burst_time
        current_time = start_time + process.burst_time
    return processes, gantt_chart

# Draw Gantt Chart
def draw_gantt_chart(gantt_chart):
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = plt.cm.get_cmap('tab20', len(gantt_chart))
    for idx, (process_id, start, end) in enumerate(gantt_chart):
        ax.barh(y=0, width=end - start, left=start, height=0.5, align='center', edgecolor='black', color=colors(idx))
        ax.text((start + end) / 2, 0, f"P{process_id}", ha='center', va='center', color='white')
    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_title("Gantt Chart")
    plt.tight_layout()
    plt.show()

# Execute Scheduling
def execute_scheduling():
    try:
        processes = []
        for row in process_rows:
            pid = int(row[0].get())
            arrival_time = int(row[1].get())
            burst_time = int(row[2].get())
            priority = int(row[3].get()) if priority_shown else 0
            processes.append(Process(pid, arrival_time, burst_time, priority))

        selected_algorithm = algorithm_var.get()
        if selected_algorithm == "FCFS":
            result, gantt_chart = fcfs_scheduling(processes)
        elif selected_algorithm == "Round Robin":
            if not quantum_entry.get().isdigit():
                messagebox.showerror("Error", "Please enter a valid time quantum.")
                return
            quantum = int(quantum_entry.get())
            result, gantt_chart = round_robin_scheduling(processes, quantum)
        elif selected_algorithm == "Priority Scheduling":
            result, gantt_chart = priority_scheduling(processes)
        elif selected_algorithm == "SJF":
            result, gantt_chart = sjf_scheduling(processes)
        else:
            messagebox.showerror("Error", "Please select a scheduling algorithm")
            return

        for item in table.get_children():
            table.delete(item)

        total_waiting = 0
        total_turnaround = 0

        for process in result:
            table.insert("", "end", values=(process.pid, process.waiting_time, process.turnaround_time))
            total_waiting += process.waiting_time
            total_turnaround += process.turnaround_time

        avg_waiting = total_waiting / len(result)
        avg_turnaround = total_turnaround / len(result)

        avg_label.config(text=f"Average Waiting Time: {avg_waiting:.2f}, Turnaround Time: {avg_turnaround:.2f}")
        draw_gantt_chart(gantt_chart)
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values for all fields.")

# Update UI elements visibility based on selected algorithm
def update_priority_visibility(event=None):
    global priority_shown
    algorithm = algorithm_var.get()

    # Show/hide priority column
    priority_shown = algorithm == "Priority Scheduling"
    for row in process_rows:
        if priority_shown:
            row[3].grid()
        else:
            row[3].grid_remove()

    # Show/hide quantum entry
    if algorithm == "Round Robin":
        quantum_label.grid()
        quantum_entry.grid()
    else:
        quantum_label.grid_remove()
        quantum_entry.grid_remove()

# Add Process Row
def add_process_row():
    row_index = len(process_rows) + 1
    row_entries = []
    for col in range(4):
        entry = tk.Entry(frame)
        entry.grid(row=row_index, column=col, padx=5, pady=5)
        if col == 3 and not priority_shown:
            entry.grid_remove()
        row_entries.append(entry)
    process_rows.append(row_entries)

# GUI Setup
root = tk.Tk()
root.title("CPU Scheduling Simulator")

priority_shown = False

# Algorithm Selection
tk.Label(root, text="Select Scheduling Algorithm:").grid(row=0, column=0, padx=5, pady=5)
algorithm_var = tk.StringVar()
algorithm_dropdown = ttk.Combobox(root, textvariable=algorithm_var, values=["FCFS", "Round Robin", "Priority Scheduling", "SJF"])
algorithm_dropdown.grid(row=0, column=1, padx=5, pady=5)
algorithm_dropdown.bind("<<ComboboxSelected>>", update_priority_visibility)

# Quantum Input
quantum_label = tk.Label(root, text="Time Quantum (For Round Robin):")
quantum_entry = tk.Entry(root)
quantum_label.grid(row=1, column=0, padx=5, pady=5)
quantum_entry.grid(row=1, column=1, padx=5, pady=5)
quantum_label.grid_remove()
quantum_entry.grid_remove()

# Process Table
frame = tk.Frame(root)
frame.grid(row=2, column=0, columnspan=2)
for i, label in enumerate(["PID", "Arrival Time", "Burst Time", "Priority"]):
    tk.Label(frame, text=label).grid(row=0, column=i)

process_rows = []

# Add Process Button
add_process_button = tk.Button(root, text="Add Process", command=add_process_row)
add_process_button.grid(row=3, column=0, padx=5, pady=5)

# Execute Button
execute_button = tk.Button(root, text="Execute Scheduling", command=execute_scheduling)
execute_button.grid(row=3, column=1, padx=5, pady=5)

# Result Table
table = ttk.Treeview(root, columns=("PID", "Waiting Time", "Turnaround Time"), show="headings")
table.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
for col in ["PID", "Waiting Time", "Turnaround Time"]:
    table.heading(col, text=col)

# Average Time Label
avg_label = tk.Label(root, text="")
avg_label.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()