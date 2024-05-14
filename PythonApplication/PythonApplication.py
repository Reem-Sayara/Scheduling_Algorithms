import sys

class ProcessControlBlock:
    # Constructor method to initialize object attributes
    def __init__(self, process_id, Arrival_time, CPU_time): 
        self.process_id = process_id # Initialize process_id attribute with the value of process_id parameter
        self.Arrival_time = int(Arrival_time) # Convert Arrival_time parameter to integer and assign to Arrival_time attribute
        self.CPU_time = int(CPU_time) # Convert CPU_time parameter to integer and assign to CPU_time attribute
        self.time_left = int(CPU_time) # Set time_left attribute to the same value as CPU_time
        self.time_started = 0 # Initialize time_started attribute to 0
        self.Finish_time = 0 # Initialize Finish_time attribute to 0
        self.wait_time = 0 # Initialize wait_time attribute to 0
        self.TournAround_time = 0 # Initialize TournAround_time attribute to 0

def load_process_data(file_path):
    process_list = []  # Initialize an empty list to store process information
    
    with open(file_path, 'r') as file: # Open the file specified by file_path in read mode
        data_lines = file.readlines() # Read all lines from the file and store them as a list of strings
        Quantum_time= int(data_lines[0].strip()) # Extract and convert the first line (quantum time) to an integer
        Context_switch = int(data_lines[1].strip()) # Extract and convert the second line (context switch) to an integer
        
        for line in data_lines[2:]: # Iterate over each line starting from the third line
            details = line.strip().split(',') # Remove leading/trailing whitespace and split the line by comma
            process_list.append(ProcessControlBlock(details[0], details[1], details[2])) # Create a ProcessControlBlock object using the extracted details and add it to the process_list
    
    return process_list, Quantum_time, Context_switch # Return the list of process control blocks along with quantum time and context switch

def execute_fcfs(process_list, Context_switch):
    # Initialize variables
    timer = 0 # Initialize the timer to 0
    timeline = [] # Initialize an empty list to store the timeline of processes
    processing_time = 0 # Initialize the total processing time
    
    # Sort process_list based on Arrival_time
    process_list.sort(key=lambda x: x.Arrival_time)
    
    # Iterate through each process in the process list
    for proc in process_list:
        if timer < proc.Arrival_time: # If the timer is less than the arrival time of the process
            timer = proc.Arrival_time # Set the timer to the arrival time of the process
        if timeline: # If the timeline is not empty
            timer += Context_switch # Add context switch time to the timer
        proc.time_started = timer # Set the start time of the process to the current timer value
        timeline.append((proc.process_id, timer, timer + proc.CPU_time)) # Append process info to the timeline
        timer += proc.CPU_time # Increment timer by the CPU time of the current process
        proc.Finish_time = timer # Set the finish time of the process to the current timer value
        proc.wait_time = proc.time_started - proc.Arrival_time # Calculate the wait time of the process
        proc.TournAround_time = proc.Finish_time - proc.Arrival_time # Calculate the turnaround time of the process
        processing_time += proc.CPU_time # Add CPU Burst time of the current process to the total processing time
    
    utilization = (processing_time / timer) * 100 # Add CPU time of the current process to the total processing time
    
    return timeline, utilization

def execute_srt(process_list, Context_switch):
    # Initialize variables
    timer = 0 # Initialize the timer to 0
    timeline = [] # Initialize an empty list to store the timeline of processes
    pending_queue = [] # Initialize an empty list to store processes in the pending queue
    processing_time = 0 # Initialize the total processing time
    
    while process_list or pending_queue: # Continue loop until there are processes in the process list or pending_queue
        # Add processes from process_list to pending_queue if they have arrived by the current time
        pending_queue.extend([p for p in process_list if p.Arrival_time <= timer and p not in pending_queue])
        # Sort pending_queue based on remaining CPU time and arrival time
        pending_queue.sort(key=lambda x: (x.time_left, x.Arrival_time))
        # If pending_queue is empty, increment the timer and continue to the next iteration of the loop
        if not pending_queue:
            timer += 1
            continue
        # Get the current process from the front of the pending_queue
        current_process = pending_queue[0]
        # If there are processes in the timeline and the last process is different from the current process, add context switch time to the timer
        if timeline and timeline[-1][0] != current_process.process_id:
            timer += Context_switch
        # Remove the current process from the process_list
        process_list = [p for p in process_list if p != current_process]
        timer += 1 # Increment the timer by 1 unit
        current_process.time_left -= 1
        timeline.append((current_process.process_id, timer - 1, timer)) # Append process info to the timeline
        # If the remaining time of the current process is 0, it has finished execution
        if current_process.time_left == 0:
            # Calculate finish time, turnaround time, and wait time for the current process
            current_process.Finish_time = timer
            current_process.TournAround_time = current_process.Finish_time - current_process.Arrival_time
            current_process.wait_time = current_process.TournAround_time - current_process.CPU_time
            processing_time += current_process.CPU_time # Add CPU time of the current process to the total processing time
            pending_queue.pop(0) # Remove the current process from the pending_queue
            
    utilization = (processing_time / timer) * 100 # Calculate CPU utilization
    
    return timeline, utilization # Return the timeline and CPU utilization

def execute_rr(process_list, Quantum_time, Context_switch):
    # Initialize variables
    timer = 0 # Initialize the timer to 0
    timeline = [] # Initialize an empty list to store the timeline of processes
    process_queue = [] # Initialize an empty list to store processes in the queue
    processing_time = 0 # Initialize the total processing time
    
    # Loop until there are processes in the process_list or the process_queue
    while process_list or process_queue:
        # Add processes from the process_list to the process_queue if their arrival time is less than or equal to the current timer
        process_queue.extend([p for p in process_list if p.Arrival_time <= timer and p not in process_queue])
        # If the process_queue is empty, increment the timer and continue
        if not process_queue:
            timer += 1
            continue
        # Get the current process from the end of the process_queue
        current_process = process_queue.pop(-1)
        # If the timeline is not empty and the last process in the timeline is not the same as the current process, add context switch time to the timer
        if timeline and timeline[-1][0] != current_process.process_id:
            timer += Context_switch
        # Calculate execution time for the current process (minimum of remaining time and quantum time)
        exec_time = min(current_process.time_left, Quantum_time)
        # Append process info to the timeline
        timeline.append((current_process.process_id, timer, timer + exec_time))
        timer += exec_time # Increment timer by the execution time
        current_process.time_left -= exec_time # Update the remaining time of the current process
        # If the current process still has remaining time, add it back to the process_queue
        if current_process.time_left > 0:
            process_queue.append(current_process)
        else: # If the current process has finished, calculate its finish time, turnaround time, and wait time
            current_process.Finish_time = timer
            current_process.TournAround_time = current_process.Finish_time - current_process.Arrival_time
            current_process.wait_time = current_process.TournAround_time - current_process.CPU_time
            processing_time += current_process.CPU_time
        # Remove the current process from the process_list
        process_list = [p for p in process_list if p != current_process]
        
    utilization = (processing_time / timer) * 100 # Calculate CPU utilization
    
    return timeline, utilization # Return the timeline and CPU utilization

def display_timeline(timeline):
    print("Gantt Chart:")
    for proc_id, start, end in timeline:
        print(f"{proc_id}[{start}-{end}] ", end="")
    print()

def display_performance(process_list, utilization):
    for proc in process_list:
        print(f"Process {proc.process_id}, Finish Time: {proc.Finish_time}, Waiting Time: {proc.wait_time}, Turnaround Time: {proc.TournAround_time}")
    print(f"CPU Utilization: {utilization:.2f}%")

if __name__ == "__main__":
    # Prompt user to input file path for process data
    file_path = input("Enter the file path for process data: ")
    process_list, Quantum_time, Context_switch = load_process_data(file_path) # Load process data from the file

    # Loop for menu selection
    while True:
        # Menu for algorithm selection
        print("\nSelect a scheduling algorithm:")
        print("1. First-Come, First-Served (FCFS)")
        print("2. Shortest Remaining Time (SRT)")
        print("3. Round Robin (RR)")
        print("4. Exit")

        choice = input("Enter your choice (1, 2, 3, or 4): ")

        if choice == "1":
            print("\nFCFS Simulation:")
            fcfs_list = [ProcessControlBlock(p.process_id, p.Arrival_time, p.CPU_time) for p in process_list] 
            fcfs_timeline, fcfs_utilization = execute_fcfs(fcfs_list, Context_switch)
            display_timeline(fcfs_timeline)
            display_performance(fcfs_list, fcfs_utilization)
        elif choice == "2":
            print("\nSRT Simulation:")
            srt_list = [ProcessControlBlock(p.process_id, p.Arrival_time, p.CPU_time) for p in process_list]
            srt_timeline, srt_utilization = execute_srt(srt_list, Context_switch)
            display_timeline(srt_timeline)
            display_performance(srt_list, srt_utilization)
        elif choice == "3":
            print("\nRR Simulation:")
            rr_list = [ProcessControlBlock(p.process_id, p.Arrival_time, p.CPU_time) for p in process_list]
            rr_timeline, rr_utilization = execute_rr(rr_list, Quantum_time, Context_switch)
            display_timeline(rr_timeline)
            display_performance(rr_list, rr_utilization)
        elif choice == "4":
            print("Exiting the program.")
            break  # Exit the loop and end the program
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


