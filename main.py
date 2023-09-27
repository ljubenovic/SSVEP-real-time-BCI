import threading
import queue
from brainflow.board_shim import BoardIds
import data_acquisition
import gui
import data_manipulation


# Initialization of variables
fs = 200
refresh_rate = 60     # possible frequencies: 6 Hz, 6.67 Hz, 7.5 Hz, 8.57 Hz, 10 Hz, 12 Hz, 15 Hz, 20 Hz, 30 Hz
serial_port = 'COM5'
board_id = BoardIds.GANGLION_BOARD.value
EEG_CHN = {'O1': 0,'Oz': 1,'O2': 2,'POz': 3}

# CCA parameters
corr_threshold = 0.4

# --- main ---

(subject_name, session_name, num_of_freqs, target_freqs, iteration_duration, n_harmonics) = gui.get_session_details(refresh_rate)

path = r'recorded_data\{}'.format(subject_name)
bandwidth = [min(target_freqs)-1, max(target_freqs)+1]

(board, eeg_chn) = data_acquisition.prepare_the_board(board_id, serial_port)

return_queue = queue.Queue()
eeg_thread = threading.Thread(target = data_acquisition.acquire_eeg_data, args = (board, fs, bandwidth, iteration_duration, eeg_chn, target_freqs, n_harmonics, corr_threshold, return_queue))
eeg_thread.start()

enter_thread = threading.Thread(target = gui.ssvep_stimulus, args = (target_freqs, num_of_freqs))
enter_thread.start()

eeg_thread.join()
(time_vars, raw_data, cca_df) = return_queue.get()

session_queue = queue.Queue()
session_queue.put((subject_name, session_name, path, time_vars, eeg_chn, iteration_duration))
cca_queue = queue.Queue()
cca_queue.put((target_freqs, n_harmonics, corr_threshold, cca_df))

data_manipulation.save_data(raw_data, fs, bandwidth, session_queue, cca_queue)

print('\nFINISHED\n')

