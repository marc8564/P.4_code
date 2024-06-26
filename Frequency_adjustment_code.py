import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
from scipy import signal

def stft_m(wav_file, sample_rate=44100):
    rate, data = wav.read(wav_file)
    f, t, Zxx = signal.stft(data, fs=rate, noverlap=None, nperseg= 512)
    return Zxx

def compression_a(DFT_samples, DFT_list, move, a):
    samp = np.zeros_like(DFT_samples)
    for k in range(len(DFT_samples)):
        samp[int(np.floor(k*a))] = samp[int(np.floor(k*a))] + DFT_samples[k]
    for i in range(len(DFT_samples)):
        DFT_list[move[0] + i] = samp[i]
    return DFT_list

def freq_composition(DFT_list, move_, target_, c):

    for i in range(len(move_)):
        move = move_[i]
        target = target_[i]
        move_1 = list(DFT_list[move[0]: move[1]])
        N1 = move[1] - move[0]
        N2 = target[1] - target[0]

        if c[0] == 1:
            DFT_list = compression_a(move_1, DFT_list, move, c[2][i])
            move_1 = list(DFT_list[move[0]: move[1]])

        if c[1] == 1:
            for i in range(min(N1, N2)):
                DFT_list[target[0] + i] = DFT_list[target[0] + i] + move_1[i]
                if c[3] == 1:
                    DFT_list[move[0]+i] = 0

    return DFT_list


def STFT_adjustment(stft_matrix, move_stft_, target_stft_, c, sample_rate = 44100):
    N = int(len(stft_matrix)-1)
    for i in range(len(move_stft)):
        move_stft_[i][0] = int(np.floor(move_stft_[i][0] * N / (sample_rate)))
        move_stft_[i][1] = int(np.floor(move_stft_[i][1] * N / (sample_rate)))
        print(move_stft_)
        target_stft_[i][0] = int(np.floor(target_stft_[i][0] * N / (sample_rate)))
        target_stft_[i][1] = int(np.floor(target_stft_[i][1] * N / (sample_rate)))
    L = []
    transposed_matrix = stft_matrix.T
    for column in transposed_matrix:
        L.append(freq_composition(column, move_stft_, target_stft_,c))
    return np.array(L).T

def STFT_inverse(stft_matrix, dir_, sample_rate=44100):
    t, data = signal.istft(stft_matrix, sample_rate)
    data = data
    wav.write(dir_, sample_rate, np.int16(data))


# STFT range freq
move_stft = [[1000, 22050]]# Highest fq at 22050
target_stft = [[0, 1000]]# Highest fq at 22050

c = 0 # if c == 1 compression with a from move_stft[0] to fra move_stft[1]
c_1 = 1 # if c_1 == 1 then move is copied to target
c_2 = 0 # if c_2 == 1 then there is moved and not copied

a = [1]
c_ = [c, c_1, a, c_2]

STFT_inverse(STFT_adjustment(stft_m("dir_1"), move_stft, target_stft, c_), "dir_2")


db = np.array([-15, -15, -20, -22.5, -25, -28.75, -32.5, -36.25, -40, -42.5, -45, -47.5, -50, -53.75, -57.5, -61.25, -65, -66.875, -68.75, -70.625, -72.5, -74.375, -76.25, -78.125, -80, -79.375, -78.75, -78.125, -77.5, -76.875, -76.25, -75.625, -75])
def ap(lst):
    result_lst = []

    for i in range(len(lst) - 1):
        result_lst.append(lst[i])
        average = (lst[i] + lst[i+1]) / 2
        result_lst.append(average)

    result_lst.append(lst[-1])
    return np.array(result_lst)

def dbc(x):
    return abs(10**(x/20))

def h_n(H_k):
    N = len(H_k)
    a = (N-1)/2
    l = []
    for n in range(N):
        sum = 0
        for k in range(1,int((N-1)/2)):
            sum = sum + 2*H_k[k] * np.cos(2*np.pi*k*(n-a)/N)
        l.append(1/N * (sum + H_k[0]))
    return l

gain = dbc(np.append(ap(db), np.flip(ap(db))[:-1]))


def hearing_loss_sim(directory, sample_rate=44100):
    rate, data = wav.read(directory)
    filter_1 = h_n(gain)
    x = list(np.convolve(data, filter_1))
    x = 10*44100*[0] + x + 2*44100*[0]

    return np.int16(x)

wav.write("dir_3", rate=44100, data=hearing_loss_sim("dir_2"))
