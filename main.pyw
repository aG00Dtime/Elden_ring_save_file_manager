import os.path
import shutil
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from datetime import datetime
from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import *


root = os.path.abspath(os.curdir)


def get_time():
    now = datetime.now()
    date_string = now.strftime("[%d-%m-%Y]")
    time_string = now.strftime("[%H-%M-%S-%p]")
    return date_string, time_string


def window_pos(w, h):
    """Takes width and height of a window as arguments and returns a tkinter geometry string that centers the window
    on the screen , usage e.g. geometry(window_pos(500,500))"""
    # dummy window to get screen size
    dummy = Tk()

    # hide window
    dummy.withdraw()
    # get the screen width and height
    x = (dummy.winfo_screenwidth() / 2) - (w / 2)
    y = (dummy.winfo_screenheight() / 2) - (h / 2)

    # destroy window
    dummy.destroy()

    # return str
    return "%dx%d+%d+%d" % (w, h, x, y)


class Window(tk.Tk):

    def __init__(self):
        super(Window, self).__init__()

        # string var
        self.working_dir = StringVar()
        self.backup_state = StringVar()
        self.restore_state = StringVar()

        # window settings
        self.title("Elden Ring Save File Manager")
        self.resizable(False, False)
        self.geometry(window_pos(520, 320))

        # check for save file loc
        if os.path.exists('save_file_location.txt'):
            with open('save_file_location.txt', 'r') as file:
                path_to_save = file.readline()
                if "EldenRing" in os.path.basename(os.path.normpath(path_to_save)):
                    self.working_dir.set(path_to_save)

        else:
            self.working_dir.set("No directory set")

        if os.path.exists('last_backup.txt'):
            with open('last_backup.txt', 'r') as file:
                last_backup = file.readline()
                if last_backup:
                    self.backup_state.set(f'''{last_backup}''')
                    # print(os.path.basename(os.path.normpath(path_to_save)))
        else:
            self.backup_state.set("No backups made yet")

        # buttons & labels

        # directory selection button
        Label(self, width=200, textvariable=self.working_dir).grid(row=0, column=1, rowspan=2, padx=(10, 0),
                                                                   pady=(20, 0))
        Button(self, text="Select save directory", command=self.get_dir, width=25).grid(
            row=0, column=0, rowspan=2,
            pady=(20, 0), padx=(10, 0))

        # backup button
        # custom backup name
        Label(self, width=25, text="Custom backup name -->").grid(row=2, column=0,
                                                                  rowspan=2,
                                                                  pady=(20, 0),
                                                                  padx=(10, 0), sticky=W)
        self.backup_name = Entry(self, width=50)
        self.backup_name.grid(row=2, column=1,
                              rowspan=2,
                              pady=(20, 0),
                              padx=(10, 0), sticky=W)

        Button(self, text="backup current save file", width=25, command=self.backup_file_to_zip).grid(row=4, column=0,
                                                                                                      rowspan=2,
                                                                                                      pady=(20, 0),
                                                                                                      padx=(10, 0))
        Label(self, width=200, textvariable=self.backup_state).grid(row=4, column=1, rowspan=2, padx=(10, 0),
                                                                    pady=(20, 0))

        # restore save
        Button(self, text="Restore previous save file", width=25, command=self.restore_file_from_zip).grid(row=6,
                                                                                                           column=0,
                                                                                                           rowspan=2,
                                                                                                           pady=(20, 0),
                                                                                                           padx=(10, 0))
        Label(self, width=200, textvariable=self.restore_state).grid(row=6, column=1, rowspan=2, padx=(10, 0),
                                                                     pady=(20, 0))

        # log area
        self.log = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=80, height=8)
        self.log.grid(row=8, column=0, columnspan=2, sticky=W, pady=10, padx=10)
        self.log.config(font='arial 8 ',state=DISABLED)

        self.mainloop()

    # select save file dir
    def get_dir(self):

        save_file_dir = fd.askdirectory(title="Navigate to appdata/roaming and select the elden ring folder...")
        if not save_file_dir:
            self.log.insert('end', f'''No folder selected... \n''')
            return
        self.working_dir.set(save_file_dir)
        # check if path is correct
        if "EldenRing" not in os.path.basename(os.path.normpath(save_file_dir)) and "EldenRing" not in os.path.basename(
                os.path.normpath(self.working_dir.get())):

            user_retry = mb.askretrycancel(title="Incorrect folder!",
                                           message='''Incorrect folder selected,Please choose the "EldenRing" folder''')
            if not user_retry:
                self.destroy()
            else:
                self.get_dir()

        else:
            with open('save_file_location.txt', 'w') as file:
                file.write(save_file_dir)

    # save file to zip
    def backup_file_to_zip(self):
        custom_name = self.backup_name.get().replace(" ", "_")
        files_dir = self.working_dir.get()

        date = get_time()

        file_name = f'''ER-Save-{date[0]}-{date[1]}'''

        if custom_name:
            file_name = f'''ER-Save-[{custom_name}]-{date[0]}-{date[1]}'''

        # make zip
        make_zip = shutil.make_archive(os.path.join(root, "saves", file_name), 'zip', files_dir)

        # clear entry box
        self.backup_name.delete(0, 'end')

        with open('last_backup.txt', 'w') as file:
            file.write(f'''Last backup : {file_name}''')

        if make_zip:
            self.backup_state.set(f'''Saved as {file_name}''')

            self.update_log(f'''Backup Created as {file_name} \n''')

    # restore save
    def restore_file_from_zip(self):

        save_to_restore = fd.askopenfilename(initialdir=os.path.join(root, 'saves'),
                                             title="Select save file to restore...")
        restore_path = self.working_dir.get()

        if not save_to_restore:
            self.update_log(f'''No file selected...''')

            return

        # backup previous save file just in case
        self.update_log(f'''Backing up previous save just in case...''')
        self.backup_file_to_zip()

        # restore save file
        shutil.unpack_archive(save_to_restore, restore_path, 'zip')
        self.update_log(f'''Restored : {save_to_restore}''')
        self.restore_state.set(f'''Restored : {os.path.basename(os.path.normpath(save_to_restore))}''')

    # update log
    def update_log(self, message):

        cur_date, cur_time = get_time()

        self.log.config(state=NORMAL)
        self.log.insert('end', f'''{cur_time}: {message} \n''')
        self.log.see('end')
        self.log.config(state=DISABLED)


if __name__ == '__main__':
    win = Window()
