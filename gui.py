import tkinter as tk
from tkinter import ttk


def get_session_details():

    def on_option_selected(event):

        global num_of_freqs
        num_of_freqs = option_var1.get()
        return
    
    
    def submit():

        global subject_name
        global session_name
        global target_freqs

        subject_name = entry1.get()
        session_name = entry2.get()

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
    window.title("Session details")
    window.geometry("800x600")
    label_font = ("Helvetica", 12)
    entry_font = ("Helvetica", 12)

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

    refresh_rate = 60
    possible_freqs =  [refresh_rate/i for i in range(2, 11)]    # 6 Hz, 6.67 Hz, 7.5 Hz, 8.57 Hz, 10 Hz, 12 Hz, 15 Hz, 20 Hz, 30 Hz
    listbox1 = tk.Listbox(window, selectmode=tk.MULTIPLE, font=label_font)
    for i in range(len(possible_freqs)):
        listbox1.insert(tk.END, round(possible_freqs[i],2))


    submit_button = tk.Button(window, text="Submit", command=submit, font=label_font, width=20)

    error_label = tk.Label(window, text="", font=label_font, fg="red")

    """
    window.columnconfigure(0, weight=5)
    window.columnconfigure(1, weight=5)
    window.columnconfigure(2, weight=5) 
    window.columnconfigure(3, weight=5)
    window.columnconfigure(4, weight=5)
    window.rowconfigure(0, weight=1)
    window.rowconfigure(1, weight=1)
    window.rowconfigure(2, weight=1)
    window.rowconfigure(3, weight=1)
    window.rowconfigure(4, weight=1)"""

    label1.grid(row=0, column=0, sticky='w')
    entry1.grid(row=0, column=1)
    label2.grid(row=1, column=0, sticky='w')
    entry2.grid(row=1, column=1)
    label3.grid(row=2, column=0, sticky='w')
    option_menu1.grid(row=2, column=1)
    label4.grid(row=6, column=0, sticky='w')
    listbox1.grid(row=6, column=1)
    submit_button.grid(row=7, column=0, columnspan=2, pady=10)
    error_label.grid(row=8, column=0, columnspan=2, pady=10)

    window.mainloop()
    return (subject_name, session_name, num_of_freqs, target_freqs)

