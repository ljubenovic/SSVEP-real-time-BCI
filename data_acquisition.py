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


def acquire_eeg_data(board, fs, bandwidth, iteration_duration, eeg_chn, target_freqs, n_harmonics, corr_ratio_threshold, return_queue):

    raw_data = np.empty([15,0])
    cca_df = pd.DataFrame(columns=['frequency','Rmax','R_ratio','time'])
    f_detected_old = None
    
    board.start_stream()

    recording_start = time.strftime("%H:%M:%S", time.localtime())
    print("\nStreaming started at: ", recording_start, "\n")

    time.sleep(iteration_duration)
    board.get_board_data()  # getting rid of the first (iteration_duration) seconds of data which is usually noisy

    time.sleep(iteration_duration)

    R_ratio_arr = []

    while not gui.stop_eeg_thread:
        t1 = time.time()
        t = time.strftime("%H:%M:%S", time.localtime())
        print("NEW")
        r_data = np.array(board.get_board_data())
        #r_data_con = np.concar_data_old
        rdf = data_manipulation.format_data(r_data, eeg_chn, fs)
        df = data_manipulation.filter_data(rdf, fs, bandwidth)
        (f_detected,R_max,R_sec) = cca.ssvep_check_cca(df, fs, target_freqs, n_harmonics)
        R_ratio = R_sec/R_max
        R_ratio_arr.append(R_ratio)

        new_row = {'frequency': [f_detected], 'Rmax': [R_max],'R_ratio': [R_ratio],'time': [t]}
        new_row = pd.DataFrame(new_row)
        cca_df = pd.concat([cca_df, new_row], ignore_index=True)

        #if (R_ratio <= corr_ratio_threshold) and (f_detected == f_detected_old):
        #if (R_ratio <= corr_ratio_threshold):
        if True:
            print("SSVEP: {:.2f} Hz (Rmax = {:.2f}, Rsec/Rmax = {:.2f})".format(f_detected, R_max, R_ratio))

        f_detected_old = f_detected
        r_data_old = r_data
        raw_data = np.concatenate((raw_data, r_data), axis=1)
        
        t2 = time.time()
        elapsed_time = t2-t1
        remaining_time = max(0,iteration_duration-elapsed_time)
        time.sleep(remaining_time)

    board.stop_stream()
    board.release_session()

    recording_end = time.strftime("%H:%M:%S", time.localtime())
    print("\nStreaming ended at: ", recording_end)

    return_queue.put(([recording_start, recording_end], raw_data, cca_df, R_ratio_arr))
    return

