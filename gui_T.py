import tkinter as tk
import time

from gui_functions import *

# get display refresh rate
refresh_rate = 60  #Hz
blink_fs = [15, 12, 60/7, 7.5]  #Hz
#blink_fs = [15, 15, 15, 15]  #Hz
frame_colors = ['black', 'black', 'black', 'black']

blink_time = 21
pause_time = 0.5
n_trials = 2
pause_between_trials = 1
session_name = 'synthetic'
# get current date
date = time.strftime('%Y-%m-%d')
# write parameters to txt file
info_path = r'data_collection\recorded_data\{}\{}\info.txt'.format(date, session_name)

# create folder with info_path if it doesn't exist
if not os.path.exists(os.path.dirname(info_path)):
    os.makedirs(os.path.dirname(info_path))
print(info_path)
with open(info_path, 'w') as f:
    # write current time in format: hour-minute-second in first line
    curr_time = time.strftime('%H-%M-%S')
    f.write(curr_time + '\n')
    # write refresh rate in second line
    f.write(f'Refresh rate: {refresh_rate}' + '\n')
    # write blinking frequencies in third line
    f.write(f'Blinking frequencies: {blink_fs}'+ '\n')
    # write blinking time in fourth line
    f.write(f'Blinking time: {blink_time}'+ '\n')
    # write pause time in fifth line
    f.write(f'Pause time: {pause_time}'+ '\n')
    # write number of trials in sixth line
    f.write(f'Number of trials: {n_trials}'+ '\n')
    # write pause between trials in seventh line
    f.write(f'Pause between trials: {pause_between_trials}'+ '\n')


# initialize gui
root = tk.Tk()
root.title('SSVEP Data Collection')
root.geometry('1920x1080')


# blinking frames dimenstions
w = 250
h = 200

# set color of the background
root.configure(bg='black')

stimulus_frame = tk.Frame(root, width=0.5*root.winfo_width(), height=0.5*root.winfo_height(), relief=tk.RAISED, bd=2, bg='black')
stimulus_frame.grid(row=0, column=0, padx=10, pady=10)

btn_frame = tk.Frame(root, width=0.25*root.winfo_width(), height=0.25*root.winfo_height(), relief=tk.RAISED, bd=2)
btn_frame.grid(row=0, column=1, padx=10, pady=10, sticky='n')


# 1st square
frame1 = tk.Frame(stimulus_frame, bg=frame_colors[0], width=w, height=h)
frame1.grid(row=0, column=0, padx=0.5*w, pady=0.5*h)
# 2nd square
frame2 = tk.Frame(stimulus_frame, bg=frame_colors[1], width=w, height=h)
frame2.grid(row=0, column=1, padx=0.5*w, pady=0.5*h)
# 3rd square
frame3 = tk.Frame(stimulus_frame, bg=frame_colors[2], width=w, height=h)
frame3.grid(row=1, column=0, padx=0.5*w, pady=0.5*h)
# 4th square
frame4 = tk.Frame(stimulus_frame, bg=frame_colors[3], width=w, height=h)
frame4.grid(row=1, column=1, padx=0.5*w, pady=0.5*h)

def main():
    frames = [frame1, frame2, frame3, frame4]
    start_recording(frames, blink_fs, blink_time, pause_time, n_trials, pause_between_trials, session_name, text_label)

# text label to show notifications
text_label = tk.Label(btn_frame, text='Text Label')
text_label.grid(row=0, column=0, columnspan=1, padx=10, pady=10)

# add button to start data collection
button = tk.Button(btn_frame, text='Start Data Collection', command=main)
button.grid(row=1, column=0, columnspan=1,  padx=10, pady=10)

# add button to exit gui
button = tk.Button(btn_frame, text='Stop Data Collection', command=root.destroy)
button.grid(row=1, column=1, columnspan=1, padx=10, pady=10)

# run gui
root.mainloop()