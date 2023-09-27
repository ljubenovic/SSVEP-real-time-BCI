import tkinter as tk
from tkinter import ttk

stop_eeg_thread = False

def get_session_details(refresh_rate):

    def on_option_selected(event):

        global num_of_freqs
        num_of_freqs = option_var1.get()
        return
    
    def submit():

        global subject_name
        global session_name
        global target_freqs
        global iteration_duration
        global n_harmonics

        subject_name = entry1.get()
        session_name = entry2.get()
        iteration_duration = float(entry3.get())
        n_harmonics = int(entry4.get())

        selected_indices = listbox1.curselection()
        """
        if len(selected_indices) != num_of_freqs:
            if num_of_freqs == 1:
                error_label.config(text="Select exactly 1 frequency!", fg="red")
            else:
                error_label.config(text="Select exactly {} frequencies!".format(num_of_freqs), fg="red")
            submit_button.config(state="normal")
            return"""

        target_freqs = [listbox1.get(ind) for ind in selected_indices]
        #error_label.config(text="")
        window.destroy()
        return

    window = tk.Tk()
    window.attributes("-topmost", True)
    window.title("Session details")
    window.geometry("800x600")
    label_font = ("Helvetica", 12)
    entry_font = ("Helvetica", 12)

    label0 = tk.Label(window, text="", width=20)
    label1 = tk.Label(window, text="Subject name:", font=label_font, width=20)
    entry1 = tk.Entry(window,font=entry_font, width=40)

    label2 = tk.Label(window, text="Session name:", font=label_font, width=20)
    entry2 = tk.Entry(window,font=entry_font, width=40)

    label3 = tk.Label(window, text="Number of frequencies:", font=label_font, width=20)
    
    num_of_freqs_options = [1, 2, 4, 6]
    option_var1 = tk.StringVar()
    option_menu1 = ttk.Combobox(window, textvariable=option_var1, values=num_of_freqs_options, width=20)
    option_menu1.bind("<<ComboboxSelected>>", on_option_selected)

    label4 = tk.Label(window, text="Select frequencies:", font=label_font, width=20)

    possible_freqs =  [refresh_rate/i for i in range(2, 11)]
    listbox1 = tk.Listbox(window, selectmode=tk.MULTIPLE, font=label_font)
    for i in range(len(possible_freqs)):
        listbox1.insert(tk.END, round(possible_freqs[i],2))

    label5 = tk.Label(window, text=" *do not select a frequency that is a multiple of any previously selected one", font=("Helvetica", 10))

    label6 = tk.Label(window, text="Iteration duration:", font=label_font, width=20)
    entry3 = tk.Entry(window,font=entry_font, width=40)
    label7 = tk.Label(window, text=" *in seconds", font=("Helvetica", 10), width=10)

    label8 = tk.Label(window, text="Number of harmonics:", font=label_font, width=20)
    entry4 = tk.Entry(window,font=entry_font, width=40)
    label9 = tk.Label(window, text=" *for CCA reference signals", font=("Helvetica", 10), width=20)

    label10 = tk.Label(window, text="", font=label_font, width=20)

    submit_button = tk.Button(window, text="Submit", command=submit, font=label_font, width=20)

    #error_label = tk.Label(window, text="", font=label_font, fg="red")

    label0.grid(row=0, column=0, sticky='w')
    label1.grid(row=1, column=0, sticky='w')
    entry1.grid(row=1, column=1)
    label2.grid(row=2, column=0, sticky='w')
    entry2.grid(row=2, column=1)
    label3.grid(row=3, column=0, sticky='w')
    option_menu1.grid(row=3, column=1, sticky='w')
    label4.grid(row=4, column=0, sticky='w')
    listbox1.grid(row=4, column=1, sticky='w')
    label5.grid(row=5, column=0, columnspan=2, sticky='w')
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
    return (subject_name, session_name, num_of_freqs, target_freqs, iteration_duration, n_harmonics)


def ssvep_stimulus(target_freqs, num_of_freqs):

    def toggle_color(frame, freq):

        if freq != 0:
            current_color = frame.cget("background")
            if current_color == "black":
                frame.configure(background="white")
            else:
                frame.configure(background="black")
            period = int((1/freq)*1000) # in ms
            frame.after(period, toggle_color, frame, freq)
        return

    def exit_app():

        global stop_eeg_thread
        stop_eeg_thread = True
        root.quit()
        return
    
    if int(num_of_freqs) == 1:
        target_freqs = [0, target_freqs, 0, 0, 0, 0]
    elif int(num_of_freqs) == 2:
        target_freqs = [0, target_freqs[0], 0, 0, target_freqs[1], 0]
    elif int(num_of_freqs) == 4:
        target_freqs = [target_freqs[0], 0.0, target_freqs[1], target_freqs[2], 0.0, target_freqs[3]]

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes("-topmost", True)
    root.configure(background='black')

    toolbar_frame = tk.Frame(root, background="black")
    toolbar_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")

    exit_button = tk.Button(toolbar_frame, text="Exit", command=exit_app)
    exit_button.pack(side="right", padx=10, pady=10)

    frames = []
    for i in range(2):
        for j in range(3):
            frame = tk.Frame(root, borderwidth=80, relief="solid", width=10, height=10, background="black")
            frame.grid(row=i+1, column=j, padx=10, pady=10, sticky="nsew")
            frames.append(frame)

            freq = target_freqs[i*3+j]            
            toggle_color(frame, freq)

    if target_freqs[0] != 0:
        label0 = tk.Label(root, text="{} Hz".format(target_freqs[0]), font=("Helvetica", 10), background="black", foreground="white")
        label0.grid(row=1, column=0)
    if target_freqs[1] != 0:
        label1 = tk.Label(root, text="{} Hz".format(target_freqs[1]), font=("Helvetica", 10), background="black", foreground="white")
        label1.grid(row=1, column=1)
    if target_freqs[2] != 0:
        label2 = tk.Label(root, text="{} Hz".format(target_freqs[2]), font=("Helvetica", 10), background="black", foreground="white")
        label2.grid(row=1, column=2)
    if target_freqs[3] != 0:
        label3 = tk.Label(root, text="{} Hz".format(target_freqs[3]), font=("Helvetica", 10), background="black", foreground="white")
        label3.grid(row=2, column=0)
    if target_freqs[4] != 0:
        label4 = tk.Label(root, text="{} Hz".format(target_freqs[4]), font=("Helvetica", 10), background="black", foreground="white")
        label4.grid(row=2, column=1)
    if target_freqs[5] != 0:
        label5 = tk.Label(root, text="{} Hz".format(target_freqs[5]), font=("Helvetica", 10), background="black", foreground="white")
        label5.grid(row=2, column=2)

    for i in range(2):
        root.grid_rowconfigure(i+1, weight=1)
    for j in range(3):
        root.grid_columnconfigure(j, weight=1)

    root.mainloop()
    return

