import numpy as np
from sklearn.cross_decomposition import CCA


def refernce_signals_one_freq(pts, target_freq, fs, n_harmonics = 1):
    
    t = np.arange(0, (pts/fs), step = 1.0/fs)
    reference_signals = []
    for i in range(n_harmonics):
        reference_signals.append(np.sin(np.pi*2*(i+1)*target_freq*t))
        reference_signals.append(np.cos(np.pi*2*(i+1)*target_freq*t))
    reference_signals = np.array(reference_signals)
    reference_signals = np.transpose(reference_signals)
    reference_signals = reference_signals[0:pts,:]
    return reference_signals


def get_reference_signals(pts, target_freqs, fs, n_harmonics = 1):

    reference_signals = np.empty((pts,2,len(target_freqs)))
    for i in range(len(target_freqs)):
        reference_signals[:,:,i] = refernce_signals_one_freq(pts, target_freqs[i], fs, n_harmonics)
    return reference_signals


def find_correlation(data, references, target_freqs):
    
    cca = CCA(n_components = 1)

    result = np.zeros(len(target_freqs))
    for f_ind in range(len(target_freqs)):
        ref = np.squeeze(references[:, :, f_ind])
        cca.fit(data,ref)
        data_c, ref_c = cca.transform(data,ref)
        corr_coef = np.corrcoef(data_c.T, ref_c.T)[0, 1]
        result[f_ind] = corr_coef
    return result


def cca_classify(data, references, target_freqs):

    result = find_correlation(data,references,target_freqs)
    ind_f = np.argmax(result)
    max_corr = result[ind_f]
    f = target_freqs[ind_f]
    return (f,max_corr)


def ssvep_check_cca(df, fs, target_freqs, n_harmonics = 1):

    pts = df.shape[0]
    keys = df.keys()
    data = df[keys[0:4]]
    data = df.to_numpy()
    reference_signals = get_reference_signals(pts, target_freqs, fs, n_harmonics)
    (f,max_corr) = cca_classify(data, reference_signals, target_freqs)
    return (f, max_corr)

