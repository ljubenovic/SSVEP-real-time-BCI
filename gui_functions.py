
import tkinter as tk
from threading import Thread
from queue import Queue

from brainflow.board_shim import BoardShim, BoardIds, BrainFlowInputParams
from brainflow.data_filter import DataFilter

import os
import pandas as pd
import math as m
import time
import numpy as np

frame_colors = ['black', 'black', 'black', 'black']


def initialize_board(port):
    params = BrainFlowInputParams()
    params.serial_port = port
    #board_id = BoardIds.GANGLION_BOARD.value
    board_id = BoardIds.SYNTHETIC_BOARD.value
    board = BoardShim(board_id, params)
    return board

def board_recording(board, recording_time, n_samples):
    board_id = BoardIds.GANGLION_BOARD.value
    #board_id = BoardIds.SYNTHETIC_BOARD.value
    board.start_stream(n_samples)
    time.sleep(recording_time)
    # data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    data = board.get_board_data()  # get all data and remove it from internal buffer
    board.stop_stream()
    board.release_session()
    eeg_chn = BoardShim.get_eeg_channels(board_id)
    timestamps_chn = BoardShim.get_timestamp_channel(board_id)
    return data[eeg_chn+[timestamps_chn]]

# function to make squere blink
def blink(frame, blink_freq, blink_time, j):    
    n_repeats = int(blink_time*blink_freq)
    for i in range(n_repeats):
        frame.config(bg='white')
        time.sleep(1/(2*blink_freq))
        frame.config(bg=frame_colors[j])
        time.sleep(1/(2*blink_freq))

    # interval = 1 / (2 * blink_freq)
    # start_time = time.time()
    
    # for _ in range(n_repeats):
    #     elapsed_time = time.time() - start_time
        
    #     # Check if it's time to toggle the rectangle
    #     if elapsed_time >= interval:
    #         print('blink')
    #         frame.config(bg=frame_colors[j] if frame.cget('bg') == 'white' else frame_colors[j])
    #         start_time = time.time()
    #     frame.update()


def blink_frames(frames, freqs, blink_time):
    # create thread for each frame
    
    threads = []
    for i, frame in enumerate(frames):
        t = Thread(target=blink, args=(frame, freqs[i], blink_time, i))
        threads.append(t)
    # start all threads
    for t in threads:
        t.start() 


def blink_all(frames, freqs, blink_time, pause_time, n_trials, pause_between_trials, q1, q2, q3, text_label):
    #try:

    for trial_num in range(n_trials):
        q3.put(trial_num)
        text_label.config(text=f'Trial {trial_num+1} of {n_trials}')

        for i, frame in enumerate(frames):
            q1.put(i)
            q2.get()
            #print(f'Frame{i+1} start', time.time())
            text_label.config(text=f'Recording data from squere {i+1}')
            frame.config(highlightbackground='red', highlightthickness=3)
            # 1st version
            blink(frame, freqs[i], blink_time, i)
            ############
            # 2nd version
            #blink_frames(frames, freqs, blink_time) 
            #time.sleep(blink_time)       
            ############                
            frame.config(highlightbackground='black', highlightthickness=0)
            text_label.config(text=f'Pause for {pause_time} seconds')
            #print(f'Frame{i+1} end', time.time())
            time.sleep(pause_time)
    
        text_label.config(text=f'Pause between trials for {pause_between_trials} seconds')
        time.sleep(pause_between_trials)
    return
    #except:
        #return

def record_data(q1, q2, q3, freqs, text_label, recording_time, session_path, n_trials, n_samples):
    board = initialize_board('COM7')
    curr_time = time.strftime('%H-%M-%S')
    #try:
    while True:
        df = pd.DataFrame(columns=['blink_freq', 'ch1', 'ch2', 'ch3', 'ch4', 'timestamp'])
        trial_num = q3.get()
        #print(trial_num)
        while True:
            # pandas dataframe with columns: blink_freq, ch1, ch2, ch3, ch4
            data = q1.get()
            text_label.config(text=f'Prepare to record data from squere {data+1}')
            # prepare recording
            board.prepare_session()
            # recoring is ready, send signal to blink and start recording
            q2.put(1)
            recorded_data = board_recording(board, recording_time, n_samples).transpose()
            recorded_data = np.concatenate((np.full(shape=(recorded_data.shape[0], 1), fill_value=freqs[data]), recorded_data), axis=1)
            # create dataframe with recorded data
            curr_df = pd.DataFrame(recorded_data, columns=['blink_freq', 'ch1', 'ch2', 'ch3', 'ch4', 'timestamp'])
            # add recorded data to dataframe with pandas.concat
            df = pd.concat([df, curr_df], ignore_index=True)
            if data == 3:
                # save dataframe to csv file
                # create folder for current time if it doesn't exist
                time_path = f'{session_path}\\{curr_time}'
                if not os.path.exists(time_path):
                    os.mkdir(time_path)
                df.to_csv(f'{time_path}\\trial_{trial_num}.csv')
                break

        if trial_num == n_trials-1:
            text_label.config(text=f'Data collection is finished')
            return
    #except:
        #return

def start_recording(frames, freqs, blink_time, pause_time, n_trials, pause_between_trials, session_name, text_label):
    fs = 200  #Hz
    n_samples = int(blink_time*fs)
    # create folder for current date if it doesn't exist
    date = time.strftime('%Y-%m-%d')
    # create folder for current date if it doesn't exist
    date_path = f'data_collection\\recorded_data\\{date}'
    if not os.path.exists(date_path):
        os.mkdir(date_path)
    # create folder for current session if it doesn't exist
    session_path = f'{date_path}\\{session_name}'
    if not os.path.exists(session_path):
        os.mkdir(session_path)


    #for i in range(n_trials):
    q1 = Queue()
    q2 = Queue()
    q3 = Queue()
    # create thread
    blink_thread = Thread(target=blink_all, args=(frames, freqs, blink_time, pause_time, n_trials, pause_between_trials, q1, q2, q3, text_label))
    # second thread to record data
    record_thread = Thread(target=record_data, args=(q1, q2, q3, freqs, text_label, blink_time, session_path, n_trials, n_samples))
    # start both threads
    record_thread.start()
    blink_thread.start()