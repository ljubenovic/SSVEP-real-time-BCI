import time
import numpy as np
import pandas as pd
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import data_manipulation
import cca
import gui


def prepare_the_board(board_id, serial_port):

    params = BrainFlowInputParams()
    params.serial_port = serial_port
    board = BoardShim(board_id, params)
    eeg_chn = BoardShim.get_eeg_channels(board_id)
    board.prepare_session()
    return (board, eeg_chn)


def acquire_eeg_data(board, fs, bandwidth, iteration_duration, eeg_chn, target_freqs, n_harmonics, corr_threshold, return_queue):

    raw_data = np.empty([15,0])
    cca_df = pd.DataFrame(columns=['frequency', 'correlation', 'time'])
    f_detected_old = None
    max_corr = 0
    
    board.start_stream()

    recording_start = time.strftime("%H:%M:%S", time.localtime())
    print("\nStreaming started at: ", recording_start, "\n")

    time.sleep(2)
    board.get_board_data()  # getting rid of the first 2 seconds of data which is usually noisy

    time.sleep(iteration_duration)

    while not gui.stop_eeg_thread:
        t1 = time.time()
        t = time.strftime("%H:%M:%S", time.localtime())
        r_data = np.array(board.get_board_data())
        rdf = data_manipulation.format_data(r_data, eeg_chn, fs)
        df = data_manipulation.filter_data(rdf, fs, bandwidth)
        (f_detected, max_corr) = cca.ssvep_check_cca(df, fs, target_freqs, n_harmonics)

        if (f_detected_old and (max_corr >= corr_threshold)) or (f_detected_old and (f_detected == f_detected_old)):
            print("SSVEP detected at {:.2f} Hz (correlation = {:.2f}) at {}".format(f_detected, max_corr, t))
            new_row = {'frequency': [f_detected], 'correlation': [max_corr], 'time': [t]}
            new_row = pd.DataFrame(new_row)
            cca_df = pd.concat([cca_df, new_row], ignore_index=True)
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

    return_queue.put(([recording_start, recording_end], raw_data, cca_df))
    return

