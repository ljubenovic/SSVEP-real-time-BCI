import tkinter as tk
from PIL import Image, ImageTk
import numpy as np

stop_eeg_thread = False

def get_session_details():

    """def on_option_selected(event):

        global num_of_freqs
        num_of_freqs = option_var1.get()
        return"""
    
    def submit():

        global subject_name
        global session_name
        #global target_freqs
        global iteration_duration
        global n_harmonics

        subject_name = entry1.get()
        session_name = entry2.get()
        iteration_duration = float(entry3.get())
        n_harmonics = int(entry4.get())
        #selected_indices = listbox1.curselection()
        #target_freqs = [listbox1.get(ind) for ind in selected_indices]
        
        window.destroy()
        return

    window = tk.Tk()
    window.attributes("-topmost", True)
    window.title("Session details")
    window.geometry("800x200")
    label_font = ("Helvetica", 12)
    entry_font = ("Helvetica", 12)

    label0 = tk.Label(window, text="", width=20)
    label1 = tk.Label(window, text="Subject name:", font=label_font, width=20)
    entry1 = tk.Entry(window,font=entry_font, width=40)

    label2 = tk.Label(window, text="Session name:", font=label_font, width=20)
    entry2 = tk.Entry(window,font=entry_font, width=40)

    #label3 = tk.Label(window, text="Number of frequencies:", font=label_font, width=20)
    
    #num_of_freqs_options = [1, 2, 4, 6]
    """num_of_freqs_options = [1, 2, 4]
    option_var1 = tk.StringVar()
    option_menu1 = ttk.Combobox(window, textvariable=option_var1, values=num_of_freqs_options, width=20)
    option_menu1.bind("<<ComboboxSelected>>", on_option_selected)"""

    #label4 = tk.Label(window, text="Select frequencies:", font=label_font, width=20)
    """possible_freqs =  [refresh_rate/i for i in range(2, 11)]
    listbox1 = tk.Listbox(window, selectmode=tk.MULTIPLE, font=label_font)
    for i in range(len(possible_freqs)):
        listbox1.insert(tk.END, round(possible_freqs[i],2))"""
    #label5 = tk.Label(window, text=" *do not select a frequency that is a multiple of any previously selected one", font=("Helvetica", 10))

    label6 = tk.Label(window, text="Iteration duration:", font=label_font, width=20)
    entry3 = tk.Entry(window,font=entry_font, width=40)
    label7 = tk.Label(window, text=" *in seconds", font=("Helvetica", 10), width=10)

    label8 = tk.Label(window, text="Number of harmonics:", font=label_font, width=20)
    entry4 = tk.Entry(window,font=entry_font, width=40)
    label9 = tk.Label(window, text=" *for CCA reference signals", font=("Helvetica", 10), width=20)

    label10 = tk.Label(window, text="", font=label_font, width=20)

    submit_button = tk.Button(window, text="Submit", command=submit, font=label_font, width=20)

    label0.grid(row=0, column=0, sticky='w')
    label1.grid(row=1, column=0, sticky='w')
    entry1.grid(row=1, column=1)
    label2.grid(row=2, column=0, sticky='w')
    entry2.grid(row=2, column=1)
    #label3.grid(row=3, column=0, sticky='w')
    #option_menu1.grid(row=3, column=1, sticky='w')
    #label4.grid(row=4, column=0, sticky='w')
    #listbox1.grid(row=4, column=1, sticky='w')
    #label5.grid(row=5, column=0, columnspan=2, sticky='w')
    label6.grid(row=6, column=0, sticky='w')
    entry3.grid(row=6, column=1)
    label7.grid(row=6, column=2, sticky='w')
    label8.grid(row=7, column=0, sticky='w')
    entry4.grid(row=7, column=1)
    label9.grid(row=7, column=2, sticky='w')
    label10.grid(row=8, column=0, sticky='w')
    submit_button.grid(row=9, column=1, sticky='w')
    #error_label.grid(row=9, column=1, columnspan=2, pady=10)
    
    window.mainloop()
    return (subject_name, session_name, iteration_duration, n_harmonics)


def ssvep_stimulus(target_freqs, x_dim, y_dim):
    
    def show_image(background_label, freq):
        #background_label.config(bg="black")
        background_label.config(image=photo)
        period = int((1/freq)*1000) # in ms
        root.after(period, hide_image, background_label, freq)  

    def hide_image(background_label, freq):
        #background_label.config(bg="white")
        background_label.config(image=black_photo)
        period = int((1/freq)*1000) # in ms
        root.after(period, show_image, background_label, freq)

    def exit_app():
        global stop_eeg_thread
        stop_eeg_thread = True
        root.quit()
        return

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes("-topmost", True)
    root.configure(background='black')

    n_frames_x = x_dim
    n_frames_y = y_dim

    toolbar_frame = tk.Frame(root, background="black")
    toolbar_frame.grid(row=0, column=0, columnspan=n_frames_x, sticky="nsew")

    exit_button = tk.Button(toolbar_frame, text="Exit", command=exit_app)
    exit_button.pack(side="right", padx=10, pady=10)

    freqs = np.zeros([n_frames_y, n_frames_x])
    middle_x = n_frames_x // 2 + 1
    middle_y = n_frames_y // 2 + 1

    if len(target_freqs) == 1:
        freqs[0, middle_x - 1] = target_freqs[0]
    elif len(target_freqs) == 4 and x_dim*y_dim >= 4:
        freqs[0, middle_x - 1] = target_freqs[1]
        freqs[middle_y - 1, 0] = target_freqs[3]
        freqs[middle_y - 1, n_frames_x - 1] = target_freqs[0]
        freqs[n_frames_y - 1, middle_x - 1] = target_freqs[2]

    image = Image.open("images\A.png")
    black_image = Image.open("images\Black.png")
    photo = ImageTk.PhotoImage(image)
    black_photo = ImageTk.PhotoImage(black_image)

    frames = []
    for i in range(n_frames_y):
        for j in range(n_frames_x):
            frame = tk.Frame(root, borderwidth=10, relief="solid",background="black")
            frame.grid(row=i+1, column=j, padx=10, pady=10, sticky="nsew")
            frames.append(frame)

            freq = freqs[i,j]

            if freq != 0:
                background_label = tk.Label(frame)
                background_label.config(bg="black")
                background_label.place(relwidth=1, relheight=1)
                show_image(background_label,freq)
            else:
                frame.configure(bg="black")

    global central_frame
    central_frame = frames[(middle_y - 1) * n_frames_x + middle_x - 1]

    for i in range(n_frames_y):
        root.grid_rowconfigure(i+1, weight=1)
    for j in range(n_frames_x):
        root.grid_columnconfigure(j, weight=1)

    root.mainloop()
    return 

