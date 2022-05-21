import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from assetkey import assetkey
from assetkey import assetkey_r
import sys
import tools
import os
import time
import shutil
import numpy as np
sys.path.append("\\".join(os.getcwd().split("\\")[:-1]))
import HkLib.HoLib as HoLib

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometry("1200x782")
        self.parent.resizable(False, False)
        self.parent.title("SwagEdit") 
        self.parent.iconbitmap(default=resource_path("icon.ico"))

        s=ttk.Style()

        s.configure('Treeview', rowheight=18)

        self.tree = ttk.Treeview(self.parent, height=42)
        self.tree["columns"] = ("Name", "AssetType", "AssetID", "Total Size")
        self.tree.column("#0", anchor=tk.W, width=100)
        self.tree.column("Name", anchor=tk.W, width=550)
        self.tree.column("AssetType", anchor=tk.W, width=120)
        self.tree.column("AssetID", anchor=tk.CENTER, width=120)
        self.tree.column("Total Size", anchor=tk.CENTER, width=80)

        self.tree.heading("#0", text="Tree")
        self.tree.heading("Name", text="Name")
        self.tree.heading("AssetType", text="AssetType")
        self.tree.heading("AssetID", text="AssetID")
        self.tree.heading("Total Size", text="Total Size")
        #self.tree.bind("<Button-1>", self.disableEvent)
        self.tree.place(x=0, y=0)

        self.vsb = ttk.Scrollbar(self.parent, orient="vertical", command=self.tree.yview)
        self.vsb.place(x=973, y=0, height=782)

        self.tree.configure(yscrollcommand=self.vsb.set)

        self.options = ttk.LabelFrame(self.parent, text="Options")
        self.options.place(x=1000, y=0,height=773,width=190)


        self.export_button = tk.Button(self.options, text="Export", height=1, width=19, command=self.export)
        self.export_button.place(x=21, y=40)

        self.import_button = tk.Button(self.options, text="Import", height=1, width=19, command=self.import_)
        self.import_button.place(x=21, y=70)
        
        self.exportall_button = tk.Button(self.options, text="Export all", height=1, width=19, command=self.export_all)
        self.exportall_button.place(x=21, y=10)

        self.copy_button = tk.Button(self.options, text="Copy ID to clipboard", height=1, width=19, command=self.save_clip)
        self.copy_button.place(x=21, y=120)


        self.typeselection = tk.StringVar(self.options)
        self.typeselection.set([*assetkey_r.keys()][0])
        self.type_menu = ttk.Combobox(self.options, textvariable=self.typeselection, width=18)
        self.type_menu["values"] = [*assetkey_r.keys()]
        self.type_menu['state'] = 'readonly'
        self.type_menu.place(x=19, y=170)

        self.name_entry = tk.Entry(self.options, width=20)
        self.name_entry.place(x=21, y=200)

        self.newasset_button = tk.Button(self.options, text="New asset", height=1, width=19, command=self.new_asset)
        self.newasset_button.place(x=21, y=230)

        self.dupeasset_button = tk.Button(self.options, text="Duplicate asset", height=1, width=19, command=self.dupe_asset)
        self.dupeasset_button.place(x=21, y=260)

        self.delasset_button = tk.Button(self.options, text="Remove asset", height=1, width=19, command=self.delete_asset)
        self.delasset_button.place(x=21, y=290)

        self.menu = tk.Menu(self.parent)
        self.parent.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff="off")
        self.menu.add_cascade(label="File", menu=self.file_menu)
        
        self.file_menu.add_command(label="Open...", command=self.ask_directory)
        self.file_menu.add_command(label="Build...", command=self.save)
        self.file_menu.add_command(label="Build new...", command=self.save_as)
        self.file_menu.add_command(label="Quit", command=self.quit) 


        self.search_entry = tk.Entry(self.options, width=20)
        self.search_entry.place(x=21, y=555)

        self.search_id = tk.Button(self.options, text="Search for ID...", height=1, width=19, command=self.search_id)
        self.search_id.place(x=21, y=585)

        self.search_id_within = tk.Button(self.options, text="Search for Reference...", height=1, width=19, command=self.search_reference)
        self.search_id_within.place(x=21, y=615)

        self.search_names = tk.Button(self.options, text="Search for Name...", height=1, width=19, command=self.search_name)
        self.search_names.place(x=21, y=645)

        self.clear = tk.Button(self.options, text="Reset", height=1, width=19, command=self.reset_search)
        self.clear.place(x=21, y=700)


        self.archive = None
        self.detached_items = []

    def dupe_asset(self):
        if self.archive == None:
            return

        curr_item = self.tree.focus()
        if self.tree.item(curr_item)["text"] != "[Entry]":
            return

        li = self.tree.item(curr_item)["tags"][0]
        ti = self.tree.item(curr_item)["tags"][1]
        ai = self.tree.item(curr_item)["tags"][2]

        new_id = self.generate_id()
        name = self.archive.mast.sections[0].layers[li].sublayer.tables[ti].assets[ai].name
        new_type = self.archive.mast.sections[0].layers[li].sublayer.tables[ti].assets[ai].assettype
        data = self.archive.mast.sections[0].layers[li].sublayer.tables[ti].assets[ai].data
        
        ai = len(self.archive.mast.sections[0].layers[li].sublayer.tables[ti].assets)

        self.archive.NewAsset(li, ti, new_id, new_type, name, data)

        asset = self.archive.mast.sections[0].layers[li].sublayer.tables[ti].assets[-1]

        try: self.tree.insert(parent=f"{str(li).zfill(4)}{str(ti).zfill(4)}", index="end", iid=f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}", text="[Entry]", values=(name, assetkey[int.from_bytes(asset.assettype, self.archive.endian)], asset.assetid.hex(), tools.NumToBytecount(asset.length_padding)), tags=(li, ti, ai))
        except: self.tree.insert(parent=f"{str(li).zfill(4)}{str(ti).zfill(4)}", index="end", iid=f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}", text="[Entry]", values=(name, hex(int.from_bytes(asset.assettype, self.archive.endian)), asset.assetid.hex(), tools.NumToBytecount(asset.length_padding)), tags=(li, ti, ai))
    
    def generate_id(self):
        allids = []
        for layer in self.archive.mast.sections[0].layers:
            if layer.sublayer_magic == "PSLD":
                continue
            for table in layer.sublayer.tables:
                for asset in table.assets:
                    allids.append(asset.assetid)

        new_id = 0
        while (not new_id in allids) and (new_id == 0):
            new_id = np.random.bytes(0x08)

        return new_id

    def new_asset(self):
        if self.archive == None:
            return

        curr_item = self.tree.focus()
        if self.tree.item(curr_item)["text"].split(" ")[-1] != "[Table]":
            return

        li = self.tree.item(curr_item)["tags"][0]
        ti = self.tree.item(curr_item)["tags"][1]
        ai = len(self.archive.mast.sections[0].layers[li].sublayer.tables[ti].assets)

        new_id = self.generate_id()
        name = self.name_entry.get().replace("\\", "").replace("/", "")
        new_type = assetkey_r[self.typeselection.get()].to_bytes(4, self.archive.endian)

        temp_directory = (str(tk.filedialog.askopenfilename()))
        if temp_directory == "":
            return
        directory = temp_directory

        with open(directory, "rb") as file:
            data = file.read()

        self.archive.NewAsset(li, ti, new_id, new_type, name, data)

        asset = self.archive.mast.sections[0].layers[li].sublayer.tables[ti].assets[-1]

        try: self.tree.insert(parent=f"{str(li).zfill(4)}{str(ti).zfill(4)}", index="end", iid=f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}", text="[Entry]", values=(name, assetkey[int.from_bytes(asset.assettype, self.archive.endian)], asset.assetid.hex(), tools.NumToBytecount(asset.length_padding)), tags=(li, ti, ai))
        except: self.tree.insert(parent=f"{str(li).zfill(4)}{str(ti).zfill(4)}", index="end", iid=f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}", text="[Entry]", values=(name, hex(int.from_bytes(asset.assettype, self.archive.endian)), asset.assetid.hex(), tools.NumToBytecount(asset.length_padding)), tags=(li, ti, ai))
    
    def delete_asset(self):
        if self.archive == None:
            return

        curr_item = self.tree.focus()
        if self.tree.item(curr_item)["text"] != "[Entry]":
            return

        li = self.tree.item(curr_item)["tags"][0]
        ti = self.tree.item(curr_item)["tags"][1]
        ai = self.tree.item(curr_item)["tags"][2]
        
        self.archive.mast.sections[0].layers[li].sublayer.tables[ti].assets.pop(ai)
        
        self.tree.delete(f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}")
        
        self.unhide()
        self.update_tree()

    def save_clip(self):
        if self.archive == None:
            return

        curr_item = self.tree.focus()
        if self.tree.item(curr_item)["text"] != "[Entry]":
            return

        self.parent.clipboard_clear()
        self.parent.clipboard_append(self.tree.item(curr_item)["values"][2])

    def search_reference(self):
        if self.archive == None:
            return
            
        try:
            to_search = bytes.fromhex(self.search_entry.get().lower())
        except:
            return

        self.reset_search()

        items_remove = []
        for li, layer in enumerate(self.archive.mast.sections[0].layers):
            if layer.sublayer_magic == "PSLD": continue
            for ti, table in enumerate(layer.sublayer.tables):
                for ai, asset in enumerate(table.assets):
                    if to_search in asset.data:
                        items_remove.append(f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}")
        
        if items_remove == []: return

        self.hide_except(items_remove)

    def export_all(self):
        if self.archive == None:
            return

        curr_dir = filedialog.askdirectory()
        if curr_dir == "":
            return
        if os.path.exists(f"{curr_dir}\{self.archive.game}"):
            shutil.rmtree(f"{curr_dir}\{self.archive.game}")
        os.mkdir(f"{curr_dir}\{self.archive.game}")
        directory = f"{curr_dir}\{self.archive.game}"
        
        for li, layer in enumerate(self.archive.mast.sections[0].layers):
            if layer.type == "PD  ":
                continue
            typename = layer.type.replace(" ", "")
            os.mkdir(f"{directory}\{typename} [{li}]")
            for ti, table in enumerate(layer.sublayer.tables):
                os.mkdir(f"{directory}\{typename} [{li}]\{ti}")
                for asset in table.assets:
                    try:
                        if not os.path.exists(f"{directory}\{typename} [{li}]\{ti}\{assetkey[int.from_bytes(asset.assettype, self.archive.endian)]}"):
                            os.mkdir(f"{directory}\{typename} [{li}]\{ti}\{assetkey[int.from_bytes(asset.assettype, self.archive.endian)]}")
                            
                    except:
                        if not os.path.exists(f"{directory}\{typename} [{li}]\{ti}\{hex(int.from_bytes(asset.assettype, self.archive.endian))}"):
                            os.mkdir(f"{directory}\{typename} [{li}]\{ti}\{hex(int.from_bytes(asset.assettype, self.archive.endian))}")
                        

        for li, layer in enumerate(self.archive.mast.sections[0].layers):
            if layer.type == "PD  ":
                continue
            typename = layer.type.replace(" ", "")
            for ti, table in enumerate(layer.sublayer.tables):
                for asset in table.assets:
                    name = asset.name.replace("/","")
                    try:
                        with open(f"{directory}\{typename} [{li}]\{ti}\{assetkey[int.from_bytes(asset.assettype, self.archive.endian)]}\{name} [{asset.assetid.hex()}].dat", "wb+") as file:
                            file.write(asset.data)
                    except:
                        with open(f"{directory}\{typename} [{li}]\{ti}\{hex(int.from_bytes(asset.assettype, self.archive.endian))}\{name} [{asset.assetid.hex()}].dat", "wb+") as file:
                            file.write(asset.data)

    def reset_search(self):
        self.unhide()
        self.search_entry.delete(0,"end")
        self.search_entry.insert(0, "")

    def search_id(self):
        if self.archive == None:
            return

        try:
            to_search = self.search_entry.get().replace(" ", "").lower()
        except:
            return
        
        self.reset_search()


        for li, layer in enumerate(self.archive.mast.sections[0].layers):
            if layer.sublayer_magic == "PSLD": continue
            for ti, table in enumerate(layer.sublayer.tables):
                for ai, asset in enumerate(table.assets):
                    if asset.assetid.hex() == to_search:
                        self.tree.selection_set(f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}")
                        self.tree.focus(f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}")
                        self.hide_except((f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}"))

    def search_name(self):
        if self.archive == None:
            return
            
        try:
            to_search = self.search_entry.get().lower()
        except:
            return

        self.reset_search()

        items_remove = []
        for li, layer in enumerate(self.archive.mast.sections[0].layers):
            if layer.sublayer_magic == "PSLD": continue
            for ti, table in enumerate(layer.sublayer.tables):
                for ai, asset in enumerate(table.assets):
                    if to_search in asset.name.lower():
                        items_remove.append(f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}")
        
        if items_remove == []: return

        self.hide_except(items_remove)

    def hide_except(self, item):
        
        for layer in self.tree.get_children():
            for table in self.tree.get_children(layer):
                for asset in self.tree.get_children(table):
                    if not asset in item:
                        self.tree.detach(asset)
                        self.detached_items.append(asset)

    def unhide(self):       
        for i in self.detached_items:
            self.tree.reattach(i,f"{i[:4]}{i[4:8]}",index=int(i[8:16], 10))
        self.detached_items.clear()

    def import_(self):
        if self.archive == None:
            return

        curr_item = self.tree.focus()
        if self.tree.item(curr_item)["text"] != "[Entry]":
            return

        temp_directory = (str(tk.filedialog.askopenfilename()))
        if temp_directory == "":
            return
        directory = temp_directory

        tags = self.tree.item(curr_item)["tags"]

        with open(directory, "rb") as file:
            self.archive.mast.sections[0].layers[tags[0]].sublayer.tables[tags[1]].assets[tags[2]].data = file.read()

    def export(self):
        if self.archive == None:
            return

        curr_item = self.tree.focus()
        if self.tree.item(curr_item)["text"] != "[Entry]":
            return
        
        tags = self.tree.item(curr_item)["tags"]
        asset = self.archive.mast.sections[0].layers[tags[0]].sublayer.tables[tags[1]].assets[tags[2]]

        directory = filedialog.askdirectory() + f"\{asset.name} [{asset.assetid.hex()}].dat"
        if directory == "":
            return

        with open(directory, "wb+") as file:
            file.write(asset.data)

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())

        for li, layer in enumerate(self.archive.mast.sections[0].layers):
            if layer.sublayer_magic == "PSLD": continue
            self.tree.insert(parent=f"", index="end", iid=f"{str(li).zfill(4)}", text=f"{layer.type} [Layer]", values=("", "", "", tools.NumToBytecount(layer.data_length)))

            for ti, table in enumerate(layer.sublayer.tables):
                self.tree.insert(parent=f"{str(li).zfill(4)}", index="end", iid=f"{str(li).zfill(4)}{str(ti).zfill(4)}", text=f"{ti} [Table]", values=("", "", "", tools.NumToBytecount(table.data_length+table.dir_length)), tags=(li, ti))

                for ai, asset in enumerate(table.assets):
                    try: self.tree.insert(parent=f"{str(li).zfill(4)}{str(ti).zfill(4)}", index="end", iid=f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}", text="[Entry]", values=(asset.name, assetkey[int.from_bytes(asset.assettype, self.archive.endian)], asset.assetid.hex(), tools.NumToBytecount(asset.length_padding)), tags=(li, ti, ai))
                    except: self.tree.insert(parent=f"{str(li).zfill(4)}{str(ti).zfill(4)}", index="end", iid=f"{str(li).zfill(4)}{str(ti).zfill(4)}{str(ai).zfill(8)}", text="[Entry]", values=(asset.name, hex(int.from_bytes(asset.assettype, self.archive.endian)), asset.assetid.hex(), tools.NumToBytecount(asset.length_padding)), tags=(li, ti, ai))
    
    def save_as(self):
        if self.archive == None:
            return

        curr_dir = filedialog.asksaveasfile(mode='wb', defaultextension=".ho")
        if curr_dir == None:
            return

        self.archive.compiler = "HkLib:HoLib.hkOArchive.SaveAs"

        starttime = time.time()
        self.archive.Update()
        updatetime = time.time()
        self.archive.SaveAs(curr_dir)
        savetime = time.time()

        delta_u = round((updatetime-starttime)*1000)/1000
        delta_s = round((savetime-updatetime)*1000)/1000
        delta_t = round((savetime-starttime)*1000)/1000

        tk.messagebox.showinfo('Success!', f"Update: {delta_u}s\nBuild: {delta_s}s\nTotal: {delta_t}s")

    def save(self):
        if self.archive == None:
            return

        starttime = time.time()
        self.archive.Update()
        updatetime = time.time()
        self.archive.Save()
        savetime = time.time()

        delta_u = round((updatetime-starttime)*1000)/1000
        delta_s = round((savetime-updatetime)*1000)/1000
        delta_t = round((savetime-starttime)*1000)/1000

        tk.messagebox.showinfo('Success!', f"Update: {delta_u}s\nBuild: {delta_s}s\nTotal: {delta_t}s")

    def ask_directory(self):
        temp_directory = (str(tk.filedialog.askopenfilename(filetypes=[("hkO Archives", "*.ho")])))
        if temp_directory == "":
            return

        self.current_directory = temp_directory

        self.parent.title(f"SwagEdit - [{self.current_directory}]")

        starttime = time.time()
        self.archive = HoLib.hkOArchive(self.current_directory)
        opentime = time.time()

        delta_t = round((opentime-starttime)*1000)/1000
        
        tk.messagebox.showinfo('[General Package Information]', f"Compilation Date: {self.archive.date}\nPlatform: {self.archive.platform}\nGame: {self.archive.game}\nUsername: {self.archive.username}\nCompiler: {self.archive.compiler}\nHash: {self.archive.hash}\nEndiannes: {self.archive.endian}\n\nDuration: {delta_t}s")

        self.archive.username = "swagedit_autobuild"
        self.archive.compiler = "HkLib:HoLib.hkOArchive.Save"

        self.unhide()
        self.update_tree()
        
        



if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()