import gui
import data_acquisition
import data_manipulation
import cca
import threading
import time
import random
import numpy as np
import tkinter as tk
import queue
from brainflow.board_shim import BoardIds
import pandas as pd

stop_eeg_thread = False

def arrow(n_runs, n_trials, trial_freqs, target_freqs, reaction_time, task_time, rest_time, return_queue):

    raw_data = np.empty([15,0])
    cca_df = pd.DataFrame(columns=['detected_frequency','expected_frequency','hit','Rmax','R_ratio','time'])
    
    board.start_stream()

    recording_start = time.strftime("%H:%M:%S", time.localtime())
    print("\nStreaming started at: ", recording_start, "\n")

    time.sleep(2)
    board.get_board_data()  # getting rid of the first 2 seconds of data which is usually noisy

    R_ratio_arr = []
    successful_detection = []

    for i in range(n_runs):
        print('\nRun {}'.format(i+1))
        if stop_eeg_thread:
            break

        for j in range(n_trials):
            print('\nTrial {}'.format(j+1))
            if stop_eeg_thread:
                break

            if trial_freqs[j] == target_freqs[0]:
                global arrow_right
                arrow_image = arrow_right
            elif trial_freqs[j] == target_freqs[1]:
                global arrow_top
                arrow_image = arrow_top
            elif trial_freqs[j] == target_freqs[2]:
                global arrow_bottom
                arrow_image = arrow_bottom
            elif trial_freqs[j] == target_freqs[3]:
                global arrow_left
                arrow_image = arrow_left
            else:
                global black
                arrow_image = black

            global arrow_label
            arrow_label.configure(image=arrow_image)

            time.sleep(reaction_time)
            board.get_board_data()

            time.sleep(task_time)
            t1 = time.time()
            t = time.strftime("%H:%M:%S", time.localtime())
            r_data = np.array(board.get_board_data())

            rdf = data_manipulation.format_data(r_data, eeg_chn, fs)
            df = data_manipulation.filter_data(rdf, fs, bandwidth)
            (f_detected,R_max,R_sec) = cca.ssvep_check_cca(df, fs, target_freqs, n_harmonics)
            R_ratio = R_sec/R_max
            R_ratio_arr.append(R_ratio)
            successful_detection.append(f_detected == trial_freqs[j])

            print("SSVEP: {:.2f} Hz (Rmax = {:.2f}, Rsec/Rmax = {:.2f})".format(f_detected, R_max, R_ratio))
            new_row = {'detected_frequency': [f_detected], 'expected_frequency': [trial_freqs[j]], 'hit': [f_detected == trial_freqs[j]] , 'Rmax': [R_max],'R_ratio': [R_ratio],'time': [t]}
            new_row = pd.DataFrame(new_row)
            cca_df = pd.concat([cca_df, new_row], ignore_index=True)

            raw_data = np.concatenate((raw_data, r_data), axis=1)

            time.sleep(rest_time)
        

    board.stop_stream()
    board.release_session()

    recording_end = time.strftime("%H:%M:%S", time.localtime())
    print("\nStreaming ended at: ", recording_end)
        
    return_queue.put(([recording_start, recording_end], raw_data, cca_df, R_ratio_arr))    

    return

fs = 200
refresh_rate = 60
serial_port = 'COM5'
board_id = BoardIds.GANGLION_BOARD.value
EEG_CHN = {'O1': 0,'Oz': 1,'O2': 2,'POz': 3}

target_freqs = [60/9, 60/8, 60/7, 60/6]
possible_freqs = target_freqs
bandwidth = [2,30]

(subject_name, session_name, iteration_duration, n_harmonics) = gui.get_session_details()

path = r'recorded_data\{}'.format(subject_name)

(board, eeg_chn) = data_acquisition.prepare_the_board(board_id, serial_port)

n_runs = 5
n_trials = 25

trial_duration = 3.5
reaction_time = 0.5
task_time = trial_duration - reaction_time

rest_time = 2

target_freqs = [60/9, 60/8, 60/7, 60/6]

freqs = target_freqs + [0]
trial_freqs = []
for i in range(n_trials):
    trial_freqs.append(random.choice(freqs))

print(trial_freqs)

def toggle_color(frame, freq):

        if freq != 0:
            current_color = frame.cget("background")
            if current_color == "black":
                frame.configure(background="white")
            else:
                frame.configure(background="black")
            period = int((1/freq)*1000) # in ms
            frame.after(period, toggle_color, frame, freq)
        return

def exit_app():

    global stop_eeg_thread
    stop_eeg_thread = True
    root.quit()
    return

root = tk.Tk()
root.attributes('-fullscreen', True)
root.attributes("-topmost", True)
root.configure(background='black')

n_frames_x = 9
n_frames_y = 5

toolbar_frame = tk.Frame(root, background="black")
toolbar_frame.grid(row=0, column=0, columnspan=n_frames_x, sticky="nsew")

exit_button = tk.Button(toolbar_frame, text="Exit", command=exit_app)
exit_button.pack(side="right", padx=10, pady=10)

freqs = np.zeros([n_frames_y, n_frames_x])
middle_x = n_frames_x // 2 + 1
middle_y = n_frames_y // 2 + 1

freqs[0, middle_x - 1] = target_freqs[1]
freqs[middle_y - 1, 0] = target_freqs[3]
freqs[middle_y - 1, n_frames_x - 1] = target_freqs[0]
freqs[n_frames_y - 1, middle_x - 1] = target_freqs[2]

frames = []
for i in range(n_frames_y):
    for j in range(n_frames_x):
        frame = tk.Frame(root, borderwidth=10, relief="solid",background="black")
        frame.grid(row=i+1, column=j, padx=10, pady=10, sticky="nsew")
        frames.append(frame)

        freq = freqs[i,j] 
        toggle_color(frame, freq)
        if i == middle_y - 1 and j == middle_x - 1:
            central_frame = frame
            arrow_label = tk.Label(central_frame, image=None, background="black")
            arrow_label.grid(row = middle_y - 1, column = middle_x - 1)

arrow_top = tk.PhotoImage(file = "arrow_top_s.png")
arrow_bottom = tk.PhotoImage(file = "arrow_bottom_s.png")
arrow_left = tk.PhotoImage(file = "arrow_left_s.png")
arrow_right = tk.PhotoImage(file = "arrow_right_s.png")
black = tk.PhotoImage(file = "black.png")

for i in range(n_frames_y):
    root.grid_rowconfigure(i+1, weight=1)
for j in range(n_frames_x):
    root.grid_columnconfigure(j, weight=1)

return_queue = queue.Queue()
eeg_and_arrow_thread = threading.Thread(target = arrow, args = (n_runs, n_trials, trial_freqs, target_freqs, reaction_time, task_time, rest_time, return_queue))
eeg_and_arrow_thread.start()

root.mainloop()

eeg_and_arrow_thread.join()

(time_vars, raw_data, cca_df, R_ratio_arr) = return_queue.get()

session_queue = queue.Queue()
session_queue.put((subject_name, session_name, path, time_vars, eeg_chn, iteration_duration))
cca_queue = queue.Queue()
cca_queue.put((target_freqs, n_harmonics, 1, cca_df, R_ratio_arr))

cca_df_1 = cca_df[cca_df['hit'] == 1]
cca_df_0 = cca_df[cca_df['hit'] == 0]

mean_R_ratio_1 = cca_df_1['R_ratio'].mean()
mean_R_ratio_0 = cca_df_0['R_ratio'].mean()
max_R_ratio_1 = cca_df_1['R_ratio'].max()
max_R_ratio_0 = cca_df_0['R_ratio'].max()
min_R_ratio_1 = cca_df_1['R_ratio'].min()
min_R_ratio_0 = cca_df_0['R_ratio'].min()

print('mean_R_ratio_1: {:.4f}'.format(mean_R_ratio_1))
print('mean_R_ratio_0: {:.4f}'.format(mean_R_ratio_0))
print('max_R_ratio_1: {:.4}'.format(max_R_ratio_1))
print('max_R_ratio_0: {:.4f}'.format(max_R_ratio_0))
print('min_R_ratio_1: {:.4f}'.format(min_R_ratio_1))
print('min_R_ratio_0: {:.4f}'.format(min_R_ratio_0))

data_manipulation.save_data(raw_data, fs, bandwidth, session_queue, cca_queue)

print('\nFINISHED\n')


