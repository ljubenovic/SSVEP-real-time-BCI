import pandas as pd
import numpy as np
import data_manipulation
import cca

fs = 200
refresh_rate = 60

path = r'recorded_data\Anastasija\2023-09-20\7_5Hz_8_57Hz_10Hz_12Hz_2s'
iteration_duration = 2
target_freqs = [15.0, 12.0, 10.0, 8.57, 7.5, 6.67]
possible_freqs =  [refresh_rate/i for i in range(2, 11)]

rdf = pd.read_csv(path + r'\raw_data.csv')
df = pd.read_csv(path + r'\data.csv')
psd_df = pd.read_csv(path + r'\data_psd.csv')

t = [i/fs for i in range(df.shape[0])]

t_int = int(t[-1])
t_int = t_int - t_int % iteration_duration

file = open(path + r'\analysis.txt','w')
file.write('Possible frequencies: {}\n'.format(possible_freqs))
file.write('Target frequencies: {}\n'.format(target_freqs))
file.write('Recording started at: 12:10:56\n')
file.write('Iteration duration: {} s\n'.format(iteration_duration))
file.write('\n')

data = df.iloc[:,0:4].values

for i in range(int(t_int/iteration_duration)):
    ind_0 =int(fs*iteration_duration*i)
    ind_1 = int(fs*iteration_duration*(i+1))
    data_sliced = data[ind_0:ind_1,:]
    df_sliced = pd.DataFrame(data_sliced, columns = ['ch1', 'ch2', 'ch3', 'ch4'])
    
    data_manipulation.psd(df_sliced, fs, [5,31], True)
    (f,R_max,R_sec) = cca.ssvep_check_cca(df_sliced, fs, possible_freqs, 1)
    str = 'Iteration: {}, f: {} Hz, R_max: {}, R_sec: {}, R_sec/R_max = {}'.format(i, f, R_max, R_sec, R_sec/R_max)
    print(str)
    file.write(str + '\n')

file.close()

