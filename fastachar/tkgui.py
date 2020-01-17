from functools import partial
import os
from io import StringIO
from sys import platform

import tkinter as Tk
from tkinter import filedialog
import tkinter.ttk as ttk

import configparser

from . import fasta_logic, fasta_io, fasta_doc


CONFIG = dict(linux = dict(INIFILE = 'fastacharrc',
                           INIPATH = '.config/fastachar'),
              win32 = dict(INIFILE = 'fastachar.ini',
                           INIPATH ='.fastachar'))

class ConfigFastachar(object):
    ''' Class to contain the configuration of the Fastachar gui

    '''
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.load()
        
    def get_home(self):
        ''' Return the home directory

        Return
        ======
        
        home_dir: string

        '''
        if platform == 'linux':
            home_dir = os.getenv('HOME')
        elif platform == 'win32':
            home_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                    os.getenv('HOMEPATH'))
        else:
            raise OSError('Detected an unsupported OS.')
        return home_dir
    
    def get_path(self):
        ''' Return the full path to the configuration file.
        
        Returns
        -------
        path : string
        '''
        home_dir = self.get_home()
        path = os.path.join(home_dir,
                            CONFIG[platform]['INIPATH'])
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, 
                            CONFIG[platform]['INIFILE'])

    def set_defaults(self, section, **p):
        ''' Sets the default values for the configuration file
        
        '''
        if not self.config.has_section(section):
            self.config.add_section(section)
        if section == 'DEFAULT':
            try:
                wd = p['working_directory']
            except KeyError:
                wd = None
            default_cwd = wd or self.get_home()
            if not os.path.exists(default_cwd):
                default_cwd = os.getcwd()
            self.config.set('DEFAULT', 'working_directory', default_cwd)
        elif section == 'REGEX':
            self.config.set('REGEX', 'header_format','{ID} {SPECIES}')
            self.config.set('REGEX', 'id','[A-Za-z0-9\._]+')
            self.config.set('REGEX', 'species', '[A-Z][a-z ]+')
    
    def load(self):
        ''' Load and parse configuration file
        
        Upon calling this method, the configuration dictionary self.config gets
        populated.

        '''
        p = self.get_path()
        cfg_file = self.config.read(p)
        if not cfg_file:
            self.set_defaults()
        else:
            try:
                cwd = self.config.get('DEFAULT','working_directory')
            except configparser.NoSectionError:
                self.set_defaults('DEFAULT')
            else:
                if not os.path.exists(cwd):
                    self.set_defaults('DEFAULT')
            try:
                self.config.get('REGEX','id')
            except configparser.NoSectionError:
                self.set_defaults('REGEX')

    def save(self):
        ''' Save the the current configuration to file.

        This method writes self.config to file.
        '''
        p = self.get_path()
        with open(p, 'w') as fp:
            self.config.write(fp)

    
          
class Case(object):
    LIST_KWDS = "species setA setB".split()
    
    def __init__(self):
        self.clear()
        
    def clear(self):
        self.data = {}
        
    def populate(self, filename,
                 species,
                 setA,
                 setB,
                 operation,
                 regex_header_format,
                 regex_id,
                 regex_species):
        self.data = dict(filename=filename,
                         species=species,
                         setA=setA,
                         setB=setB,
                         operation=operation,
                         regex_header_format=regex_header_format,
                         regex_id=regex_id,
                         regex_species=regex_species)

    def parse_line(self, line):
        kwd, value = line.split("=")
        kwd=kwd.strip()
        value=value.strip()
        if kwd in Case.LIST_KWDS:
            value=[i.strip() for i in value.split(",")]
            value.sort()
        return kwd, value
    
    def load(self, filename):
        if not os.path.exists(filename):
            error = fasta.ERROR_FILE_NOT_FOUND
            arg = filename
            return error, arg
        # file exists, now open it.
        error = fasta_io.OK
        arg = ''
        lineno = 0
        with open(filename,'r') as fp:
            while True:
                line = fp.readline()
                lineno+=1
                if not line:
                    break
                try:
                    kwd, value = self.parse_line(line)
                except ValueError:
                    error = fasta_io.ERROR_CASE
                    arg = "{} (line no: {}".format(line, lineno)
                else:
                    self.data[kwd]=value
        return error, arg
    
    def save(self, filename):
        with open(filename,'w') as fp:
            fp.write("filename = {}\n".format(self.data['filename']))
            fp.write("species = {}\n".format(" , ".join(self.data['species'])))
            fp.write("setA = {}\n".format(" , ".join(self.data['setA'])))
            fp.write("setB = {}\n".format(" , ".join(self.data['setB'])))
            fp.write("operation = {}\n".format(self.data['operation']))
            fp.write("regex_header_format = {}\n".format(self.data['regex_header_format']))
            fp.write("regex_id = {}\n".format(self.data['regex_id']))
            fp.write("regex_species = {}\n".format(self.data['regex_species']))
        

class Gui():
    def __init__(self):
        self.root = Tk.Tk()
        self.root.wm_title('Fastachar')
        self.config = ConfigFastachar()
        self.cwd = self.getcwd()
        self.alignment = fasta_io.Alignment()
        try:
            self.alignment.set_fasta_hdr_fmt(self.config.config['REGEX']['header_format'],
                                             self.config.config['REGEX']['id'],
                                             self.config.config['REGEX']['species'])
        except KeyError:
            pass # use default setting
        self.case = Case()
        self.reportxls = fasta_io.ReportXLS()

    def getcwd(self):
        cwd = self.config.config['DEFAULT']['working_directory']
        return cwd

    def setcwd(self,cwd):
        self.config.config['DEFAULT']['working_directory'] = cwd

    def cb_open_fasta_file_for_hdr(self, parent, regexs):
        self.fasta_file = filedialog.askopenfilename(defaultextension=".fas",
                                                     filetypes=[('fasta files', '.fas'), ('all files', '.*')],
                                                     initialdir=self.cwd,
                                                     #initialfile,
                                                     multiple=False,
                                                     #message,
                                                     parent=parent,
                                                     title="Open fasta file")
        lines=[]
        if self.fasta_file:
            with open(self.fasta_file, 'r') as fp:
                while True:
                    l = fp.readline()
                    if l and l.strip().startswith('>'):
                        s = "{}".format(l.rstrip())
                        lines.append(s)
                    if not l:
                        break
        if lines:
            error_free = True
            pattern_dict, regex_dict = self.alignment.generate_regex_dict(*[i.get() for i in regexs])
            ID_strings = []
            species_strings = []
            na='---'
            for line in lines:
                try:
                    IDspecies, species = self.alignment.parse_hdr(line, pattern_dict=pattern_dict, regex_dict=regex_dict)
                except ValueError:
                    ID_strings.append(na)
                    species_strings.append(na)
                    error_free = False
                else:
                    ID_strings.append(IDspecies)
                    species_strings.append(species)

            max_length = max([len(i) for i in lines])
            max_length_id = max([len(i) for i in ID_strings])
            max_length_species = max([len(i) for i in species_strings])
            fmt_str = "{:%ds} -> {:%ds} |  {:%ds}"%(max_length, max_length_id, max_length_species)
            parsed_lines = [fmt_str.format("Header", "ID", "Species")]
            parsed_lines+=["-"*len(parsed_lines[0])]
            parsed_lines += [fmt_str.format(s1, s2, s3) for s1, s2, s3 in zip(lines, ID_strings, species_strings)]
            self.cb_open_text_window(parsed_lines)
            if not error_free:
                self.fasta_file = None
        else:
            self.fasta_file = None

        
    def cb_set_regex(self):
        self.fasta_file = None
        cnf = dict(ipadx=10, ipady=10, padx=10, pady=0)
        cnfsticky = dict(sticky=Tk.N+Tk.E+Tk.S+Tk.W)
        toplevel = Tk.Toplevel()
        frame = Tk.Frame(toplevel)
        Tk.Label(frame, text="Header format: ").grid(row=0, column=0, **cnf)
        Tk.Label(frame, text="Regex ID: ").grid(row=1, column=0, **cnf)
        Tk.Label(frame, text="Regex SPECIES: ").grid(row=2, column=0, **cnf)
        v = []
        for i, k in enumerate("HEADER ID SPECIES".split()):
            v.append(Tk.StringVar())
            v[i].set(self.alignment.pattern_dict[k])
            Tk.Entry(frame, textvariable=v[i]).grid(row=i, column=1, **cnf)
        bottom_frame = Tk.Frame(toplevel)

        bt = Tk.Button(bottom_frame, text="OK", command=partial(self.cb_close_regex, toplevel, v))
        bt_cancel = Tk.Button(bottom_frame, text="Cancel", command=toplevel.destroy)
        bt_open = Tk.Button(bottom_frame, text="Preview file",
                            command=partial(self.cb_open_fasta_file_for_hdr, toplevel, v))
        help_lines = fasta_doc.REGEX_HELP_TEXT.split("\n")
        bt_help = Tk.Button(bottom_frame, text="Help",
                            command=partial(self.cb_open_text_window, help_lines))
        bt.pack(side=Tk.LEFT)
        bt_cancel.pack(side=Tk.LEFT)
        bt_open.pack(side=Tk.LEFT)
        bt_help.pack(side=Tk.RIGHT)
        #
        frame.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1, **cnf)
        bottom_frame.pack(side=Tk.BOTTOM, **cnf)
        toplevel.focus_force()

    def cb_close_regex(self,window, v):
        # update the regular expressions used in the alignment.
        self.alignment.set_fasta_hdr_fmt(*[_v.get() for _v in v])
        self.config.config['REGEX']['header_format'] = v[0].get()
        self.config.config['REGEX']['id'] = v[1].get()
        self.config.config['REGEX']['species'] = v[2].get()
        if self.fasta_file:
            self._open_fasta_file()
        window.destroy()
        
    def cb_open_text_window(self, lines):
        toplevel = Tk.Toplevel()
        frame = Tk.Frame(toplevel)
        frame.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        sb_report = Tk.Scrollbar(frame, orient=Tk.VERTICAL)
        sb_report.pack(side=Tk.RIGHT, fill=Tk.Y)
        report = Tk.Text(frame, state=Tk.DISABLED,
                         padx=10, pady=10, yscrollcommand=sb_report.set)
        report.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)
        sb_report.config(command=report.yview)
        bt = Tk.Button(toplevel, text="Close", command=toplevel.destroy)
        bt.pack(side=Tk.BOTTOM)
        report.config(state=Tk.NORMAL)
        for line in lines:
            report.insert(Tk.END, "{}\n".format(line))
        report.config(state=Tk.DISABLED)
        toplevel.focus_force()
        
    def about_window(self):
        toplevel = Tk.Toplevel()
        label1 = Tk.Label(toplevel, text=fasta_doc.ABOUT_TEXT, height=0, width=100,
                          justify=Tk.LEFT)
        label1.pack()
        label2 = Tk.Label(toplevel, text=fasta_doc.DISCLAIMER, height=0, width=100,
                          justify=Tk.LEFT)
        label2.pack()
        bt = Tk.Button(toplevel, text="Close", command=toplevel.destroy)
        bt.pack()
        toplevel.focus_force()

    def error_window(self, err_code, arg = ''):
        toplevel = Tk.Toplevel()
        if arg:
            text = " : ".join([fasta_doc.ERRORS[err_code], arg])
        else:
            text = fasta_doc.ERRORS[err_code]
        label1 = Tk.Label(toplevel, text=text,
                          height=0, width=80, padx=10, pady=10,
                          justify=Tk.LEFT)
        label1.pack()
        bt = Tk.Button(toplevel, text="Close", padx=10, pady=10,
                       command=toplevel.destroy)
        bt.pack()
        toplevel.focus_force()


    def help_window(self):
        toplevel = Tk.Toplevel()
        frame = Tk.Frame(toplevel)
        frame.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        sb_report = Tk.Scrollbar(frame, orient=Tk.VERTICAL)
        sb_report.pack(side=Tk.RIGHT, fill=Tk.Y)
        report = Tk.Text(frame, state=Tk.DISABLED,
                         padx=10, pady=10, yscrollcommand=sb_report.set)
        report.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)
        sb_report.config(command=report.yview)
        bt = Tk.Button(toplevel, text="Close", command=toplevel.destroy)
        bt.pack(side=Tk.BOTTOM)
        report.config(state=Tk.NORMAL)
        for line in fasta_doc.HELP_TEXT.split("\n"):
            report.insert(Tk.END, "{}\n".format(line))
        report.config(state=Tk.DISABLED)
        toplevel.focus_force()


    def create_menu(self):
        menubar = Tk.Menu(self.root)
        # create a pulldown menu, and add it to the menu bar
        filemenu = Tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open fasta file", command=self.cb_open_fasta_file)
        filemenu.add_command(label="Open fasta file /w preview", command=self.cb_set_regex)
        filemenu.add_command(label="Open case file", command=self.cb_open_case_file)
        filemenu.add_command(label="Save case file", command=self.cb_save_case_file)

        filemenu.add_separator()
        filemenu.add_command(label="Set working directory", command=self.cb_set_working_dir)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        #
        menubar.add_cascade(label="File", menu=filemenu)
        # create more pulldown menus
        helpmenu = Tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.cb_about)
        helpmenu.add_command(label="Help", command=self.cb_help)
        menubar.add_cascade(label="Help",  menu=helpmenu)
        outputmenu = Tk.Menu(menubar, tearoff=0)
        outputmenu.add_command(label="Save report (txt)", command=self.cb_save_report)
        outputmenu.add_command(label="Save report (xls)", command=self.cb_save_report_xls)
        menubar.add_cascade(label="Output", menu=outputmenu)
        # display the menu
        self.root.config(menu=menubar)

    def create_layout(self):
        root = self.root
        for i in range(3):
            Tk.Grid.columnconfigure(root, i, weight=1)
        Tk.Grid.rowconfigure(root, 1, weight=1)
        Tk.Grid.rowconfigure(root, 4, weight=1)
            
        cnf = dict(ipadx=10, ipady=10, padx=10, pady=0)
        cnfsticky = dict(sticky=Tk.N+Tk.E+Tk.S+Tk.W)
        Tk.Label(root, text="Unselected Species").grid(row=0, column=0, **cnf)
        Tk.Label(root, text="Selected species list A").grid(row=0, column=1, **cnf)
        Tk.Label(root, text="Selected species list B").grid(row=0, column=2, **cnf)
        # the list boxes
        #     define scrollbars
        frame_sequences=Tk.Frame()
        frame_A=Tk.Frame()
        frame_B=Tk.Frame()
        frame_sequences.grid(row=1, column=0, **cnf, **cnfsticky)
        frame_A.grid(row=1, column=1, **cnf, **cnfsticky)
        frame_B.grid(row=1, column=2, **cnf, **cnfsticky)

        frame_sequences.grid_rowconfigure(0,weight=1)
        frame_sequences.grid_columnconfigure(0,weight=1)
        frame_A.grid_rowconfigure(0,weight=1)
        frame_A.grid_columnconfigure(0,weight=1)
        frame_B.grid_rowconfigure(0,weight=1)
        frame_B.grid_columnconfigure(0,weight=1)
        
        # configure the frames with grid, so that the scrollbars can be placed easily.

        # the scrollbars:    
        sb_sequences = Tk.Scrollbar(frame_sequences, orient=Tk.VERTICAL)
        sb_A = Tk.Scrollbar(frame_A, orient=Tk.VERTICAL)
        sb_B = Tk.Scrollbar(frame_B, orient=Tk.VERTICAL)
        sb_hor_sequences = Tk.Scrollbar(frame_sequences, orient=Tk.HORIZONTAL)
        sb_hor_A = Tk.Scrollbar(frame_A, orient=Tk.HORIZONTAL)
        sb_hor_B = Tk.Scrollbar(frame_B, orient=Tk.HORIZONTAL)

        sb_sequences.grid(column=1, row=0, **cnfsticky)
        sb_A.grid(column=1, row=0, **cnfsticky)
        sb_B.grid(column=1, row=0, **cnfsticky)
        sb_hor_sequences.grid(row=1, column=0, **cnfsticky)
        sb_hor_A.grid(row=1, column=0, **cnfsticky)
        sb_hor_B.grid(row=1, column=0, **cnfsticky)
        #     define listboxes with scrollbar attached
        cnf_lb=dict(selectmode=Tk.EXTENDED)
        self.lb_sequences=Tk.Listbox(frame_sequences,
                                     xscrollcommand=sb_hor_sequences.set,
                                     yscrollcommand=sb_sequences.set,
                                     **cnf_lb)
        self.lb_A=Tk.Listbox(frame_A,
                             xscrollcommand=sb_hor_A.set,
                             yscrollcommand=sb_A.set,
                             **cnf_lb)
        self.lb_B=Tk.Listbox(frame_B,
                             xscrollcommand=sb_hor_B.set,
                             yscrollcommand=sb_B.set,
                             **cnf_lb)
        #     connect the xview and yview to the scrollbars
        sb_sequences.config(command=self.lb_sequences.yview)
        sb_A.config(command=self.lb_A.yview)
        sb_B.config(command=self.lb_B.yview)
        sb_hor_sequences.config(command=self.lb_sequences.xview)
        sb_hor_A.config(command=self.lb_A.xview)
        sb_hor_B.config(command=self.lb_B.xview)
        #     place the listboxes
        self.lb_sequences.grid(column=0, row=0, **cnfsticky)
        self.lb_A.grid(column=0, row=0, **cnfsticky)
        self.lb_B.grid(column=0, row=0, **cnfsticky)
        self.data=dict()
        self.data[self.lb_sequences]=[]
        self.data[self.lb_A]=[]
        self.data[self.lb_B]=[]
        
        # operation label and operation radio buttons
        Tk.Label(root, text="Operation").grid(row=2, column=0, **cnf)
        frame = Tk.Frame(root)
        frame.grid(row=3, column=0, **cnf)
        self.operation_method = Tk.IntVar()
        self.operation_method.set(1)
        Tk.Radiobutton(frame, text="Determine MDCs for species list A",
                       variable=self.operation_method, value=1).pack(anchor=Tk.W)
        Tk.Radiobutton(frame, text="Determine non-unique characters for species list A",
                       variable=self.operation_method, value=2).pack(anchor=Tk.W)

        bt_run = Tk.Button(root, text="Process", command=self.cb_run)
        bt_run.grid(row=3, column=1, **cnf)

        bt_clr = Tk.Button(root, text="Clear output", command=self.cb_clr)
        bt_clr.grid(row=3, column=2, **cnf)

        frame_report = Tk.Frame(pady=10)
        frame_report.grid(row=4, column=0, columnspan=3,
                          sticky=Tk.W+Tk.E+Tk.N+Tk.S, padx=10,pady=10)
        frame_report.grid_rowconfigure(0, weight=1)
        frame_report.grid_columnconfigure(0, weight=1)
        
        sb_report = Tk.Scrollbar(frame_report, orient=Tk.VERTICAL)
        sb_hor_report = Tk.Scrollbar(frame_report, orient=Tk.HORIZONTAL)
        sb_report.grid(column=1, row=0, **cnfsticky)
        sb_hor_report.grid(column=0, row=1, **cnfsticky)
        self.report = Tk.Text(frame_report, state=Tk.DISABLED,
                              wrap=None,
                              yscrollcommand=sb_report.set,
                              xscrollcommand=sb_hor_report.set)
        self.report.grid(column=0, row=0, **cnfsticky)
        sb_report.config(command=self.report.yview)
        sb_hor_report.config(command=self.report.xview)

    def create_bindings(self):
        self.dragging=False
        self.lb_sequences.bind("<B3-Motion>", self.cb_b1_motion_lb)
        self.lb_sequences.bind("<ButtonRelease-3>", self.cb_b1_release_lb)
        self.lb_A.bind("<B3-Motion>", self.cb_b1_motion_lb)
        self.lb_A.bind("<ButtonRelease-3>", self.cb_b1_release_lb)
        self.lb_B.bind("<B3-Motion>", self.cb_b1_motion_lb)
        self.lb_B.bind("<ButtonRelease-3>", self.cb_b1_release_lb)


    def cb_b1_motion_lb(self, event):
        self.dragging=True
        
    def cb_b1_release_lb(self, event):
        if self.dragging:
            s = self.release_in_listbox(event)
            if s and s!=event.widget:
                self.move_items(event.widget, s)
        self.dragging=False
        
        
    def move_items(self, lb_from, lb_to):
        items = list(lb_from.curselection())
        items.reverse()
        for i in items:
            lb_from.delete(i)
            s=self.data[lb_from].pop(i)
            self.data[lb_to].append(s)
            self.data[lb_to].sort()
            j=self.data[lb_to].index(s)
            lb_to.insert(j,s)
            
        
    def release_in_listbox(self, event):
        lbs=[self.lb_sequences, self.lb_A, self.lb_B]
        x = event.x_root
        y = event.y_root
        s=0
        for lb in lbs:
            x0 = lb.winfo_rootx()
            y0 = lb.winfo_rooty()
            dx = lb.winfo_width()
            dy = lb.winfo_height()
            if x>=x0 and x<=x0+dx and y>=y0 and y<=y0+dy:
                s = lb
        return s
            
    
        
    def populate_list_with_items(self, items, lb, delete_all=True):
        if delete_all:
            lb.delete(0,Tk.END)
        for item in items:
            lb.insert(Tk.END, item)
        
    def cb_open_fasta_file(self):
        self.fasta_file = filedialog.askopenfilename(defaultextension=".fas",
                                                     filetypes=[('fasta files', '.fas'), ('all files', '.*')],
                                                     initialdir=self.cwd,
                                                     #initialfile,
                                                     multiple=False,
                                                     #message,
                                                     parent=self.root,
                                                     title="Open fasta file")
        self._open_fasta_file()
        
    def _open_fasta_file(self):
        r,arg = self.open_fasta_file()
        if r != fasta_io.OK:
            if arg:
                arg += " (%s)"%(self.fasta_file)
            else:
                arg = self.fasta_file
            self.error_window(r, arg=arg)
            
    def cb_open_case_file(self):
        case_file = filedialog.askopenfilename(defaultextension=".fc",
                                               filetypes=[('case files', '.fc'), ('all files', '.*')],
                                               initialdir=self.cwd,
                                               #initialfile,
                                               multiple=False,
                                               #message,
                                               parent=self.root,
                                               title="Open case file")
        if case_file:
            r, arg = self.open_case_file(case_file)
            if r != fasta_io.OK:
                self.error_window(r, arg=case_file)
        # else ignore silently

        
    def open_fasta_file(self):
        error = fasta_io.OK
        arg = ''
        if self.fasta_file:
            error, arg = self.alignment.load(self.fasta_file)
            if error == fasta_io.OK:
                try:
                    species = self.alignment.get_species_list()
                except:
                    error = fasta_io.ERROR_FILE_INVALID
                    arg = ''
                else:
                    species.sort()
                    self.data[self.lb_sequences] = species
                    self.data[self.lb_A] = []
                    self.data[self.lb_B] = []
                    self.populate_list_with_items(species, self.lb_sequences, delete_all=True)
                    self.populate_list_with_items([], self.lb_A, delete_all=True)
                    self.populate_list_with_items([], self.lb_B, delete_all=True)
        return error, arg
    
    def open_case_file(self, case_file):
        error = fasta_io.OK
        arg=''
        if case_file:
            error, arg = self.case.load(case_file)
            if error == fasta_io.OK:
                self.fasta_file = self.case.data['filename']

                regex_header_format = self.case.data['regex_header_format']
                regex_id = self.case.data['regex_id']
                regex_species = self.case.data['regex_species']
                self.alignment.set_fasta_hdr_fmt(regex_header_format, regex_id, regex_species)
                
                error, arg = self.alignment.load(self.fasta_file)
                if error == fasta_io.OK:
                    self.data[self.lb_sequences] = self.case.data["species"]
                    self.populate_list_with_items(self.case.data["species"],
                                                  self.lb_sequences, delete_all=True)
                    self.data[self.lb_A] = self.case.data["setA"]
                    self.populate_list_with_items(self.case.data["setA"],
                                                  self.lb_A, delete_all=True)
                    self.data[self.lb_B] = self.case.data["setB"]
                    self.populate_list_with_items(self.case.data["setB"],
                                                  self.lb_B, delete_all=True)
                    self.operation_method.set(self.case.data["operation"])

        return error, arg

    def cb_set_working_dir(self):
        self.cwd = filedialog.askdirectory(initialdir=self.cwd) or self.cwd
        self.setcwd(self.cwd)
        
    def cb_save_case_file(self):
        error = fasta_io.OK
        if self.case.data:
            case_file = filedialog.asksaveasfilename(defaultextension=".fc",
                                                     filetypes=[('case files', '.fc'), ('all files', '.*')],
                                                     initialdir=self.cwd,
                                                     #initialfile,
                                                     #message,
                                                     parent=self.root,
                                                     title="Save case file")
            if case_file:
                try:
                    self.case.save(case_file)
                except IOError:
                    error = fasta_io.ERROR_IO
                    arg = case_file
            else:
                return # cancel clicked. Ignore silently.    
        else:
            error = fasta_io.ERROR_NO_CASE_DATA
            arg = ''
        if error != fasta_io.OK:
            self.error_window(error, arg)
            
    def cb_about(self):
        self.about_window()
        
    def cb_help(self):
        self.help_window()
    
    def cb_save_report(self):
        error = fasta_io.OK
        out_file = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[('text files', '.txt'), ('all files', '.*')],
                                                initialdir=self.cwd,
                                                #initialfile,
                                                #message,
                                                parent=self.root,
                                                title="Save output")
        if not out_file:
            return # Cancel clicked, ignore silently
        try:
            with open(out_file,'w') as fp:
                fp.write(self.report.get(1., Tk.END))
        except FileNotFoundError:
            error = fasta_io.ERROR_FILE_NOT_FOUND
            arg = out_file
        except IOError:
            error = fasta_io.ERROR_IO
            arg = out_file
        except:
            error = fasta_io.ERROR_UNKNOWN
            arg = out_file
        if error != fasta_io.OK:
            self.error_window(error, arg)

    def cb_save_report_xls(self):
        error = fasta_io.OK
        out_file = filedialog.asksaveasfilename(defaultextension=".xls",
                                                filetypes=[('xls files', '.xls'), ('all files', '.*')],
                                                initialdir=self.cwd,
                                                #initialfile,
                                                #message,
                                                parent=self.root,
                                                title="Save output as xls")
        if not out_file:
            return # Cancel clicked, ignore silently
        self.reportxls.save(out_file)
        try:
            self.reportxls.save(out_file)
        except FileNotFoundError:
            error = fasta_io.ERROR_FILE_NOT_FOUND
            arg = out_file
        except IOError:
            error = fasta_io.ERROR_IO
            arg = out_file
        except:
            error = fasta_io.ERROR_UNKNOWN
            arg = out_file
        if error != fasta_io.OK:
            self.error_window(error, arg)

            
        
    def cb_clr(self):
        self.report.config(state=Tk.NORMAL)
        self.report.delete(1.0,Tk.END)
        self.report.config(state=Tk.DISABLED)
        self.reportxls.clear()
        
    def cb_run(self):
        operation = self.operation_method.get()
        set_A = self.alignment.select_sequences_from_list(self.data[self.lb_A])
        set_B = self.alignment.select_sequences_from_list(self.data[self.lb_B])
        if (operation==1 and (len(set_A)==0 or len(set_B)==0)) or \
           (operation==2 and len(set_A)==0):
            return
        self.case.clear()
        try:
            self.case.populate(self.fasta_file,
                               self.data[self.lb_sequences],
                               self.data[self.lb_A],
                               self.data[self.lb_B],
                               operation,
                               self.alignment.pattern_dict['HEADER'],
                               self.alignment.pattern_dict['ID'],
                               self.alignment.pattern_dict['SPECIES'])
        except AttributeError:
            return
        memofile = StringIO()
        report = fasta_io.Report(self.fasta_file, output_filename=memofile, reportxls = self.reportxls)

        logic = fasta_logic.SequenceLogic()
        
        if operation == 1:
            result = logic.compare_sets(set_A, set_B)
            report.report_header(set_A, set_B)
            report.report_uniq_characters("List A", set_A, set_B, result)
            report.report_footer()
            self.report.config(state=Tk.NORMAL)
            self.report.insert(Tk.END, memofile.getvalue())
            self.report.config(state=Tk.DISABLED)
        elif operation == 2:
            result = logic.differences_within_set(set_A)
            report.report_header(set_A, [])
            report.report_differences_in_set("List A", set_A, result)
            report.report_footer()
            self.report.config(state=Tk.NORMAL)
            self.report.insert(Tk.END, memofile.getvalue())
            self.report.config(state=Tk.DISABLED)


def main():
    gui = Gui()
    gui.create_menu()
    gui.create_layout()
    gui.create_bindings()
    Tk.mainloop()
    gui.config.save()
    return 0



def test():
    print("hello world")
