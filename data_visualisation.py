import data_manipulation
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

fs = 200
path = r'recorded_data\Nemanja\2023-09-27\6_frekv_proba_3'

df = pd.read_csv(path + r'\data.csv')
df = df.iloc[int(2*fs):]
fig = plt.figure(figsize=(10, 6))
gs = gridspec.GridSpec(2,2)
for i in range(4):
    ax = fig.add_subplot(gs[i // 2, i % 2])
    ax.plot(df['t'], df['ch{}'.format(i+1)], color='b')
    ax.set_xlabel('t [s]')
    ax.set_title(data_manipulation.CHN_TO_POS[i])
    ax.set_xlim([2, 10])
plt.tight_layout()
plt.show()

data_manipulation.psd(df, fs, [5,31], True)
data_manipulation.plot_spectrograms(df, fs, [5, 31])

