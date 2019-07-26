# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:52:48 2019

@author: veberhar
"""

from tkinter import ttk, Tk, Button, Scrollbar, Label, Listbox, RIGHT, LEFT, TOP, BOTTOM, X, Y, END, BOTH
from tkinter.font import Font
import os
import Py_SQL as sql
import threading



WIDTH = 900
HEIGHT = 500

NULL_MESSAGE = 'no tags in field'
NULL_MESSAGE2 = 'error: no reader attached'



class GUI:
    def __init__(self, master):
        self.master = master
        
        self.running = False
        
        master.title("RFID Scan")
        
        master.geometry(str(WIDTH) + "x" + str(HEIGHT))
        
        self.label = Label(master, text='Scan items to get data', height=2, font=("Helvetica",16,"bold"))
        self.label.pack()
        
        self.btn_stop = Button(master, text="Stop", command=self.stop, height=3, font=("Helvetica",10), bg="red", fg="white").pack(side=BOTTOM, fill=X)
        self.btn_clear = Button(master, text="Clear", command=self.clear, height=3, font=("Helvetica",10), bg="grey", fg="white").pack(side=BOTTOM, fill=X)
        self.btn_start = Button(master, text="Start", command=self.start, height=3, font=("Helvetica",10), bg="green", fg="white").pack(side=BOTTOM, fill=X)
        
        self.scrollbar = Scrollbar(root)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        col_header = ('Linked?', 'RFID_Code', 'Serial', 'Description', 'Due date', 'Last scan', 'Location')
        self.txt = ttk.Treeview(root, yscrollcommand=self.scrollbar.set, columns=col_header, show='headings')
        self.txt.pack(side=TOP, fill=BOTH, expand=1)
        
        self.txt.column('Linked?', anchor='center')
        self.txt.column('Serial', anchor='center')
        self.txt.column('Description', anchor='center')
        self.txt.column('Due date', anchor='center')
        self.txt.column('Last scan', anchor='center')
        
        self.txt.bind('<ButtonRelease-1>', self.delete_item)
        
        for c in col_header:
            self.txt.heading(c, text=c.title())
            self.txt.column(c, width=Font().measure(c.title()))
            
        self.scrollbar.config(command=self.txt.yview)
        self.rfid_list = []
    

    def hex_to_dec(self, HEX):
        if len(HEX) > 0:
            try:
                #print('Found {} item(s)...'.format(len(HEX)))
                for x in HEX:
                    dec_head = int(x[2:9], 16)
                    dec_mid = int(x[9:15], 16)
                    dec_tail = int(x[15:], 16)
                    if dec_tail not in self.rfid_list:
                        self.rfid_list.append(dec_tail)
                        rfid_dec = '{}.{}.{}'.format(dec_head, dec_mid, dec_tail)
                        #print('{} --> {}\n'.format(x, rfid_dec))
                        sql_cursor = list(sql.run_query(rfid_dec))
                        #print("SQL_CURSOR CURRENT:", sql_cursor)
                        if sql_cursor == []:
                            self.ins_unlinked(rfid_dec)
                        else:
                            sql_cursor.insert(0, "LINKED")
                            self.ins_linked(sql_cursor)
                    else:
                        print("Duplicate RFID tag...")
            except ValueError:
                print("ERROR")

    
    def run(self):
        try:
            results = os.popen('skyetek.exe GetTags').read().strip()
            if results != NULL_MESSAGE and results != NULL_MESSAGE2:
                results = str(results).replace('tag: ', '')
                results = str(results).replace(' ISO 18000-6C Auto Detect', '')
                HEX = results.splitlines()
                #print("HEX = ", HEX)
                self.hex_to_dec(HEX)
        except KeyboardInterrupt:
            exit() 
    
    
    def start(self):
        if self.running:
            pass
        else:
            self.running = True
            self.start_threads()
            
    def stop(self):
        if self.running:
            self.running = False
        else:
            pass
                
    def start_threads(self):
        if self.running:
            try:
                t = threading.Thread(target=self.run)
                t.start()
                root.after(500, self.start_threads)
            except KeyboardInterrupt:
                exit()
                
    def clear(self):
        self.rfid_list.clear()
        self.txt.delete(*self.txt.get_children())
        
    
    def ins_linked(self, string):
        item = (str(string[0]), str(string[1][0]), str(string[1][1]), str(string[1][2]), str(string[1][3]), str(string[1][4]), str(string[1][5]))
        self.txt.insert('', END, values=item, tags=('item'))
        self.txt.tag_configure('item', background='#99e386',font=("Arial",8))
        
    def ins_unlinked(self, string):
        item = ('UNLINKED', string)
        self.txt.insert('', END, values=item, tags=('non_linked_item'))
        self.txt.tag_configure('non_linked_item', background='#ed7272',font=("Arial",8))
                               
    def delete_item(self, select_item):
        item = self.txt.focus()
        item_dic = self.txt.item(item)
        self.txt.delete(item)
        item_rfid = item_dic['values'][1]
        rfid_tail = int(item_rfid[11:])
        self.rfid_list.remove(rfid_tail)

if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.mainloop()

