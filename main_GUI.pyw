import tkinter as Tk
from tkinter import ttk
from tkinter import font as tkfont

def generateEnemies():
    print("none")
########################################################################
class enemyFrame(Tk.Toplevel):
    #----------------------------------------------------------------------
    def __init__(self, original):
        self.originalFrame = original
        Tk.Toplevel.__init__(self)
        self.title("Enemy frame")
        
        # Create for later (supports auto-update)
        self.playerLevels = Tk.StringVar()
        self.playerLevels.set("")
        self.curDiffInt = Tk.IntVar()
        self.curDiffInt.set(2)
        self.curDiffStr = Tk.StringVar()
        self.returnFile = Tk.IntVar()

        # Create entry boxes
        plrLvl = ttk.Entry(self, width=7, textvariable=self.playerLevels)
        plrLvl.grid(column = 2, row = 1, sticky = 'we')

        # Create labels
        ttk.Label(self, text="Player levels:").grid(column = 1, row = 1, sticky = 'e')
        ttk.Label(self, text="Difficulty:").grid(column = 1, row = 2, sticky = 'e')
        ttk.Label(self, textvariable=self.curDiffStr).grid(column = 2, row = 3, sticky = 'we')

        # Create buttons
        ttk.Button(self, text="Generate", command = generateEnemies).grid(column = 3, row = 3, sticky='w')
        ttk.Button(self, text = "Back", command = self.onClose).grid(column = 3, row = 4, sticky = 'e')

        # Create slider
        self.diffScale = ttk.Scale(self, from_=1, to=4, orient = 'horizontal', variable = self.curDiffInt, command = self.doScaleStuff)
        self.diffScale.grid(column = 2, row = 2, sticky='we')
        self.diffScale.set(2)

        # Create checkboxes
        checkbtn = ttk.Checkbutton(self, text = "Return file", variable = self.returnFile)
        checkbtn.grid(column = 2, row = 4, sticky = 'w')
        checkbtn.state = False

        # Add nice padding to everything
        for child in self.winfo_children():child.grid_configure(padx=5, pady=5)

        # Set focus to first entry field
        plrLvl.focus()
    
    #----------------------------------------------------------------------
    def onClose(self):
        self.destroy()
        self.originalFrame.show()
    
    #----------------------------------------------------------------------
    def doScaleStuff(self, *args):
        value = self.diffScale.get()
        if int(value) != value:
            self.diffScale.set(round(value,0))
        if value == 1:
            self.curDiffStr.set("Easy")
        elif value == 2:
            self.curDiffStr.set("Medium")
        elif value == 3:
            self.curDiffStr.set("Hard")
        elif value == 4:
            self.curDiffStr.set("Deadly")
        else:
            self.curDiffStr.set("Medium")
        
########################################################################
class spellFrame(Tk.Toplevel):
    #----------------------------------------------------------------------
    def __init__(self):
        Tk.Toplevel.__init__(self)
        self.title("otherFrame")

########################################################################
class adventureFrame(Tk.Toplevel):
    #----------------------------------------------------------------------
    def __init__(self):
        Tk.Toplevel.__init__(self)
        self.title("otherFrame")

########################################################################
class MyApp(object):
    #----------------------------------------------------------------------
    def __init__(self, parent):
        self.root = parent
        self.root.title("Main frame")
        self.frame = Tk.Frame(parent)
        self.frame.pack()

        # Create start frame
        # Create buttons
        lbl = ttk.Label(self.frame, text="Welcome to the noice Caves & Lizards tool", font=titleFont)
        lbl.pack()
        btn1 = ttk.Button(self.frame, text="Generate enemies",command=self.openEnemyFrame)
        btn1.pack()
        btn2 = ttk.Button(self.frame, text="Check spells",command=self.openSpellFrame)
        btn2.pack()
        btn3 = ttk.Button(self.frame, text="Generate adventure",command=self.openAdventureFrame)
        btn3.pack()
        btn4 = ttk.Button(self.frame, text="Quit",command=self.closeAll)
        btn4.pack(side = "bottom")

    #----------------------------------------------------------------------
    def hide(self):
        """"""
        self.root.withdraw()

    #----------------------------------------------------------------------
    def openEnemyFrame(self):
        """"""
        self.hide()
        subFrame = enemyFrame(self)

    #----------------------------------------------------------------------
    def openSpellFrame(self):
        """"""
        self.hide()
        subFrame = spellFrame(self)

    #----------------------------------------------------------------------
    def openAdventureFrame(self):
        """"""
        self.hide()
        subFrame = adventureFrame(self)

    #----------------------------------------------------------------------
    def onCloseOtherFrame(self, otherFrame):
        """"""
        otherFrame.destroy()
        self.show()

    #----------------------------------------------------------------------
    def show(self):
        """"""
        self.root.update()
        self.root.deiconify()

    def closeAll(self):
        root.destroy()
        root.quit()

#----------------------------------------------------------------------
if __name__ == "__main__":
    root = Tk.Tk()
    titleFont = tkfont.Font(family='Helvetica', size=14, weight="bold", slant="italic")
    app = MyApp(root)
    root.mainloop()
