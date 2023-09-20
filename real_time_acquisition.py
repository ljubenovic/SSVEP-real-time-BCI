import time
import sys
import keyboard
import threading
import queue
import numpy as np
import pandas as pd
from brainflow.board_shim import BoardShim, BoardIds, BrainFlowInputParams
import data_manipulation
import cca


# Initialization of variables
fs = 200
refresh_rate = 60
serial_port = 'COM5'
#board_id = BoardIds.GANGLION_BOARD.value
board_id = BoardIds.SYNTHETIC_BOARD.value
EEG_CHN = {'O1': 0,'Oz': 1,'O2': 2,'POz': 3}

bandwidth = [5, 31]
iteration_duration = 2

# CCA parameters
target_freqs = np.array([refresh_rate/i for i in range(2, 11)]) # 6 Hz, 6.67 Hz, 7.5 Hz, 8.57 Hz, 10 Hz, 12 Hz, 15 Hz, 20 Hz, 30 Hz
n_harmonics = 1
corr_threshold = 0.1

# --- functions ---

def prepare_the_board(board_id, serial_port):

    params = BrainFlowInputParams()
    params.serial_port = serial_port
    board = BoardShim(board_id, params)
    eeg_chn = BoardShim.get_eeg_channels(board_id)
    board.prepare_session()
    return (board, eeg_chn)


def acquire_eeg_data(board, fs, bandwidth, iteration_duration, return_queue):

    raw_data = np.empty([15,0])
    cca_data = np.empty([2,0])
    f_detected_old = None
    max_corr = 0
    
    board.start_stream()

    t_start = time.time()
    recording_start = time.strftime("%H:%M:%S", time.localtime())
    print("\nStreaming started at: ", recording_start)

    time.sleep(iteration_duration)

    while not stop_eeg_thread:
        t1 = time.time()
        r_data = np.array(board.get_board_data())
        rdf = data_manipulation.format_data(r_data, eeg_chn, fs)
        df = data_manipulation.filter_data(rdf, fs, bandwidth)
        (f_detected, max_corr) = cca.ssvep_check_cca(df, fs, target_freqs, n_harmonics)

        if f_detected_old and (f_detected == f_detected_old) and (max_corr >= corr_threshold):
            print("SSVEP detected at {:.2f} Hz (correlation = {:.2f})".format(f_detected, max_corr))
            cca_data = np.concatenate((cca_data, np.array([f_detected, max_corr])), axis=1)
        f_detected_old = f_detected

        raw_data = np.concatenate((raw_data, r_data), axis=1)
        
        t2 = time.time()
        elapsed_time = t2-t1
        remaining_time = max(0,iteration_duration-elapsed_time)
        time.sleep(remaining_time)

    board.stop_stream()
    board.release_session()

    recording_end = time.strftime("%H:%M:%S", time.localtime())
    print("\nStreaming ended at: ", recording_end)
    t_end = time.time()

    return_queue.put(([recording_start, recording_end], raw_data, cca_data))
    return


def wait_for_enter():

    global stop_eeg_thread
    keyboard.wait("enter")
    stop_eeg_thread = True
    sys.stdin.flush()
    return


# --- main ---

subject_name = input("Enter subject name: ")
session_name = input("Enter session name: ")
path = r'recorded_data\{}'.format(subject_name)

(board, eeg_chn) = prepare_the_board(board_id, serial_port)
return_queue = queue.Queue()
stop_eeg_thread = False
eeg_thread = threading.Thread(target = acquire_eeg_data, args = (board, fs, bandwidth, iteration_duration, return_queue))
eeg_thread.start()

enter_thread = threading.Thread(target = wait_for_enter)
enter_thread.start()

eeg_thread.join()
(time_vars, raw_data, cca_data) = return_queue.get()

session_queue = queue.Queue()
session_queue.put()
cca_queue = queue.Queue()
cca_queue.put((target_freqs, n_harmonics, corr_threshold, cca_data))

data_manipulation.save_data(raw_data, fs, bandwidth, session_queue, cca_queue)

print('\nFINISHED\n')

