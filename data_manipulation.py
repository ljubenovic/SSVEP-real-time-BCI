import time
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import signal
import preprocessing_functions


EEG_CHN = {'O1': 0,'Oz': 1,'O2': 2,'POz': 3}
CHN_TO_POS = {v: k for k, v in EEG_CHN.items()}

def format_data(data, eeg_chn, fs):
    
    data = data[eeg_chn]
    data = data.transpose()
    df = pd.DataFrame(data, columns=['ch1', 'ch2', 'ch3', 'ch4'])
    t = np.arange(0, len(df['ch1'])/fs, 1/fs)
    t = [round(x, 3) for x in t]
    df['t'] = t[0:len(df['ch1'])]
    return  df


def filter_data(rdf, fs, bandwidth, plotting = False):

    df = rdf.copy()
    for i in range(4):
        df['ch{}'.format(i+1)] = preprocessing_functions.filter(df['ch{}'.format(i+1)], fs, bandwidth)
    t = df['t']

    if plotting:
        fig = plt.figure(figsize=(10, 6))
        gs = gridspec.GridSpec(4, 1)
        for i in range(4):
            ax = fig.add_subplot(gs[i, 0])
            ax.plot(t, df['ch{}'.format(i+1)], color='b')
            ax.set_ylabel('ch{}'.format(i+1))
            ax.set_xlabel('t [s]')
        plt.tight_layout()
        plt.show()
    return df


def psd(df, fs, bandwidth, plotting = False):

    data = df[['ch1', 'ch2', 'ch3', 'ch4']]
    (data_fft, f) = preprocessing_functions.signal_fft(data, fs)
    data_psd = data_fft**2
    data_psd = pd.DataFrame(data_psd, columns=['ch1', 'ch2', 'ch3', 'ch4'])
    data_psd['f'] = f

    if plotting:
        fig = plt.figure(figsize=(10, 6))
        gs = gridspec.GridSpec(2,2)
        for i in range(4):
            ax = fig.add_subplot(gs[i // 2, i % 2])
            ax.plot(f,data_psd['ch{}'.format(i+1)], color='b')
            ax.set_title(CHN_TO_POS[i])
            ax.set_xlabel('f [Hz]')
            ax.set_xlim(bandwidth)
        plt.tight_layout()
        plt.show()
    return  data_psd


def plot_spectrograms(df, fs, bandwidth):

    n_fft = 1024
    window_size = int(fs*0.1)
    overlap = int(window_size * 0.5)  # 50% overlap
    fig = plt.figure(figsize=(10, 6))
    gs = gridspec.GridSpec(2, 2)
    for i in range(4):
        ax = fig.add_subplot(gs[i // 2, i % 2])
        f, t, Sxx = signal.spectrogram(df['ch{}'.format(i+1)], nperseg = window_size, fs = fs, noverlap = overlap, nfft=n_fft)
        spectrogram_data = np.array(Sxx)
        im = ax.pcolormesh(t, f, spectrogram_data)
        ax.set_ylabel('f [Hz]')
        ax.set_xlabel('t [s]')
        ax.set_ylim(bandwidth)
        ax.set_title('Spectrogram of channel {}'.format(CHN_TO_POS[i]))
        fig.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.show()
    return


def save_data(raw_data, fs, bandwidth, session_queue, cca_queue):

    (subject_name, session_name, path, [recording_start, recording_end], eeg_chn, iteration_duration) = session_queue.get()
    (target_freqs, n_harmonics, corr_threshold, cca_df) = cca_queue.get()

    date = time.strftime('%Y-%m-%d')
    data_folder = path + '\{}\{}'.format(date, session_name)
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    rdf = format_data(raw_data, eeg_chn, fs)
    raw_data_path = data_folder + r'\raw_data.csv'
    rdf.to_csv(raw_data_path, index = False)

    df = filter_data(rdf, fs, bandwidth, plotting = False)
    data_path = data_folder + r'\data.csv'
    df.to_csv(data_path, index = False)

    data_psd = psd(df, fs, bandwidth, plotting = False)
    data_psd_path = data_folder + r'\data_psd.csv'
    data_psd.to_csv(data_psd_path, index=False)

    info_file = data_folder + r'\recording_info.txt'
    file = open(info_file,'w')
    file.write('Subject name: ' + subject_name + '\n')
    file.write('Session name: ' + session_name + '\n')
    file.write('Date: ' + date + '\n')
    file.write('Positions of EEG electrodes: '+ '\n')
    for i in range(4):
        file.write('\t'+ 'ch{}: '.format(i+1) + CHN_TO_POS[i]+ '\n')
    t = df['t'].iloc[df.shape[0] - 1]
    file.write("Recording time: {:.2f} s + first {} s of recording that haven't been considered\n".format(t, iteration_duration))
    file.write('\t'+'Recording started at: ' + recording_start + '\n')
    file.write('\t'+'Recording ended at: ' + recording_end + '\n')
    file.write('Duration of one loop iteration: {:.2f} s\n'.format(iteration_duration))
    file.write('Frequencies shown on screen: \n')
    file.write('\t'+'top: {} Hz'.format(target_freqs[1]))
    file.write('\t'+'left: {} Hz'.format(target_freqs[3]))
    file.write('\t'+'right: {} Hz'.format(target_freqs[0]))
    file.write('\t'+'bottom: {} Hz'.format(target_freqs[2]))
    file.write('Bandpass filter: [{}, {}] Hz\n'.format(bandwidth[0], bandwidth[1]))
    file.write('Number of harmonics in CCA reference signals: ' + str(n_harmonics) + '\n')
    file.write('Correlation threshold: ' + str(corr_threshold) + '\n')
    file.close()

    cca_data_path = data_folder + r'\cca_data.csv'
    if cca_df.shape[0] == 0:
        file = open(cca_data_path,'w')
        file.write('No SSVEP was detected in this session')
        file.close()
    else:
        cca_df.to_csv(cca_data_path, index=False)

    return

