# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 08:00:19 2018

@author: TopBadger
Supposed to be a supporting application for playing Dungeons&Dragons, or as I
call it Caves&Lizards. There are databases of enemies and spells in the
background that should be supplied with this source code. If they're not you're
basically fucked. I mean you can create a DB of your own but you would either
need to reproduce my formatting exactly or alter the code to fit your DB.

For now this is a console application. At a later point in time I would like
to make a nice GUI with buttons and fields and shit.

Functionalities:
    - Random en group generator based on:
        . Number of players
        . Player level
        . Output in a text file would be nice
    - Import tool to feed new data into the database
    - Spell allocation tool that suggests spells based on:
        . Player character level
        . Player magic level
        . Player character class
    - Random adventure generator based on:
        . Number of players
        . Player level
        . Current region the party is in
    - Battlefield generator
        . Sets the mood for a battle
        . Gives environment to use (both for party and for enemies)
        . Based on the region the party is in
"""

# -----------------------------------------------------------------------------
# Import stuff
# -----------------------------------------------------------------------------

import sqlite3
import os
import tempfile
import time
import webbrowser
import math
import pandas as pd
import tkinter as tk
from tkinter import font as tkfont
from sqlite3 import Error
from random import randint
from tkinter import ttk

# -----------------------------------------------------------------------------
# Global vars
# -----------------------------------------------------------------------------

workingFolder = r'C:\Users\apo\AppData\Local\Programs\Python\Python37-32\Scripts\Caves&Lizards'
targetFile = os.path.join(workingFolder, "dataStorage.db")
dataSource = os.path.join(workingFolder, "dataInput.xlsm")
welcomeMessageList = ["How's your day going?",
                      "Back again, are we?",
                      "Don't have any friends either, hm?",
                      "Nice to see you're doing well!",
                      "Not bored of my tool yet, eh?"]
regionList = ["woods",
              "desert",
              "castle",
              "Soviet Russia",
              "Syria",
              "cave",
              "the moon!"]

# -----------------------------------------------------------------------------
# Vars to tweak shit
# -----------------------------------------------------------------------------

expFactor = -0.05  # Factor for exponential function decay

# -----------------------------------------------------------------------------
# Start of actual code
# -----------------------------------------------------------------------------


# Gets data from an Excel file and pushes it to the database
def importData(sourceFile, dbFile, sheetToImport):
    conn = sqlite3.connect(dbFile)
    # read the source Excel into a dataFrame
    df = pd.read_excel(sourceFile,
                       sheetToImport)
    # throw the dataFrame into the DB
    df.to_sql(sheetToImport,
              conn,
              if_exists='replace')
    # close the connection to the DB
    conn.close()
# ----------------------------------------------------------------------


# Get data from the database (requires query to be supplied)
def fetchFromDB(conn, SQLquery):
    # Create a cursor
    cur = conn.cursor()
    # Run the command to fetch data based on the query
    cur.execute("SELECT DISTINCT " + SQLquery)
    # Create dummy List
    fetchedData = []
    # Fill List with columns titles of database
    fetchedData.append([tuple[0] for tuple in cur.description])
    # Get all the rows that fit the query
    rows = cur.fetchall()

    # Loop through rows that we just got from the DB
    for rowData in rows:
        # create a temporary List
        tempList = []
        # Loop through all items
        for singleItem in rowData:
            # Add item to temporary List
            tempList.append(singleItem)
        # Append it to the parent List
        fetchedData.append(tempList)
    return fetchedData
# ----------------------------------------------------------------------


# Check if a given List contains an item in a given Column
def listContains(listToSearch, listLevel, itemToSearch):
    # loop through all items in the List
    for item in listToSearch:
        # Check if item at given position matches the searched item
        if item[listLevel] == itemToSearch:
            return True
        else:
            return False
# ----------------------------------------------------------------------


# Generates a random en group based on user input
def generateEnemies(diffInput, levelInput):
    # Process user input
    if int(diffInput) == 1:
        difficulty = "Easy"
        mobLevelDivider = 0.5
        difficultyMultiplier = 1
        difficultyScaler = 0.1
    elif int(diffInput) == 2:
        difficulty = "Medium"
        mobLevelDivider = 0.6
        difficultyMultiplier = 1.05
        difficultyScaler = 0.15
    elif int(diffInput) == 3:
        difficulty = "Hard"
        mobLevelDivider = 0.7
        difficultyMultiplier = 1.1
        difficultyScaler = 0.2
    elif int(diffInput) == 4:
        difficulty = "Deadly"
        mobLevelDivider = 0.8
        difficultyMultiplier = 1.15
        difficultyScaler = 0.6
    else:
        difficulty = "Medium"
        mobLevelDivider = 0.6
        difficultyMultiplier = 1.05
        difficultyScaler = 0.15

    # Split level input to get a List for easier handling and map to int
    levelList = list(map(int, levelInput.split(",")))
    # Get number of items in list
    numPlayers = len(levelList)
    # Calculate average player level base value
    playerLevel = round(sum(levelList) / numPlayers * difficultyMultiplier)
    if numPlayers >= 4:
        # If there's more than 4 people, add sth on top to increase difficulty
        expTerm = math.exp(round(sum(levelList) / numPlayers) * expFactor)
        diffIncrease = numPlayers % 4 * difficultyScaler * expTerm
        playerLevel += playerLevel * diffIncrease

    # Round player level to nearest multiple of 0.125
    playerLevel -= playerLevel % 0.125

    # Create empty list to be filled
    chosenenList = []
    # Set top and bottom caps
    topCap = playerLevel
    lowCap = playerLevel*mobLevelDivider
    # Initialize number of tries as 0
    tries = 0

    # While challenge level of en group is below player levelavg, loop
    while sum(row[1] for row in chosenenList) < playerLevel:
        conn = sqlite3.connect(targetFile)
        # Query all enemies from the database that fit the criteria (correct
        # region and challenge level below players) Only get name and
        # challenge info though
        SQLstring = ("enName, enChallenge FROM enemies WHERE enChallenge BETWEEN '"
                     + str(lowCap)
                     + "' AND '"
                     + str(topCap)
                     + "'")
        enList = fetchFromDB(conn,
                             SQLstring)
        conn.close()
        # Dump first entry of freshly acquired list
        enList = enList[1:]
        # Get a new random en from the List
        randen = enList[randint(1, len(enList)) - 1]
        # Check if new en would go over boundaries
        curenLevel = sum(row[1] for row in chosenenList) + randen[1]
        if curenLevel <= playerLevel:
            # Add random en to the chosenList
            chosenenList.append(randen)
        # If it was tried three times to match an en into the remainder,
        # lower the level caps and reset the counter
        if tries > 3:
            tries = 0
            topCap = playerLevel - sum(row[1] for row in chosenenList)
            lowCap = topCap * mobLevelDivider
        else:
            tries += 1

    # Clear en list
    enList.clear()
    # Loop through all freshly randomly chosen enemies to get their details
    # and store those in a list
    for en in chosenenList:
        try:
            conn = sqlite3.connect(targetFile)
            SQLstring = "* FROM enemies WHERE enName = '" + en[0] + "'"
            enDetails = fetchFromDB(conn, SQLstring)
            conn.close()
        except Error as e:
            print("Error at: " + en[0])
            print(e)
        enList.append(enDetails[1])
    # Add titles to columns
    enList.insert(0, enDetails[0])

    # Delete the first entry of each row (index)
    for subList in enList:
        del subList[0]

    # Create temporary file name with timestamp
    filename = tempfile.gettempdir() + "randen_" + str(round(time.time()))
    # Open textfile for append
    f = open(filename, "a")
    # Add information about party to file (beginning)
    tempString = "Player levels: "
    for player in levelList:
        tempString += (str(player) + ", ")
    # Add info about calculated difficulty level
    tempString += ("\nAverage level for calculation: "
                   + str(playerLevel) + "\nChosen difficulty: "
                   + difficulty + "\n")
    # Add a visible divider
    tempString += "\n--------------------------------------------------\n"
    f.write(tempString)

    # If user does not want to return a file
    if not enFrame.returnFile == 0:
        # Write all the info about an en to the file (1 line per parameter)
        for subList in enList[1:]:
            counter = 0

            # Formatting if this spans multiline
            for item in subList:
                if len(enList[0][counter]) > 14:
                    f.write(enList[0][counter] + " \t")
                else:
                    f.write(enList[0][counter] + " \t\t")

                if str(item).find("\n") == -1:
                    f.write(str(item))
                else:
                    tempList = str(item).split("\n")
                    f.write(tempList[0])
                    for tempItem in tempList[1:]:
                        f.write("\n")
                        f.write("\t\t\t")
                        f.write(tempItem)
                f.write("\n")
                counter += 1

            f.write("\n")
            f.write("\n")

        # Open the file in an editor
        webbrowser.open(filename)

    return enList
# ----------------------------------------------------------------------


# Check what spells can be used by the player based on user input
def checkSpells():
    # Character class
    # Character level
    # magicLevel

    # Process input
    print("Nothing")
# ----------------------------------------------------------------------


# Generate a random adventure based on user input
def generateAdventure():
    # Experimental state warning
    # Region to generate for
    # Player levels

    # Process input
    print("Nothing")

# ----------------------------------------------------------------------
# Class definitions (not used in this version, kept it for later versions)
# ----------------------------------------------------------------------


class en:
    def __init__(self, name, type, alignment, armorClass, HP, speed, str,
                 dex, con, wis, cha, senses, challenge, savingThrows=None,
                 skills=None, vulnerabilities=None, damageResistance=None,
                 damageImmunity=None, conditionImmunity=None, languages=None,
                 traits=None, actions=None, legendaryActions=None):
        self.name = name
        self.type = type
        self.alignment = alignment
        self.armorClass = armorClass
        self.HP = HP
        self.speed = speed
        self.str = str
        self.dex = dex
        self.con = con
        self.wis = wis
        self.cha = cha
        self.savingThrows = savingThrows
        self.senses = senses
        self.skills = skills
        self.vulnerabilities = vulnerabilities
        self.damageResistance = damageResistance
        self.damageImmunity = damageImmunity
        self.conditionImmunity = conditionImmunity
        self.challenge = challenge
        self.languages = languages
        self.traits = traits
        self.actions = actions
        self.legendaryActions = legendaryActions
# ----------------------------------------------------------------------


class spell:
    def __init__(self, name, type, school, castingTime, range, duration,
                 components, classes, description, higherLevels):
        self.name = name
        self.type = type
        self.school = school
        self.castingTime = castingTime
        self.range = range
        self.duration = duration
        self.components = components
        self.classes = classes
        self.description = description
        self.higherLevels = higherLevels

# ----------------------------------------------------------------------
# GUI stuff
# ----------------------------------------------------------------------


class mainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (startPage, enFrame, spellFrame, advFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(startPage)
    # ------------------------------------------------------------------

    def showFrame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
# ----------------------------------------------------------------------


class startPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.titleFont = tkfont.Font(family='Helvetica',
                                     size=14,
                                     weight="bold",
                                     slant="italic")
        self.widgets(controller)

    def widgets(self, controller):
        # Create start frame (buttons)
        lbl = ttk.Label(self,
                        text="Welcome to the noice Caves & Lizards tool",
                        font=self.titleFont)
        lbl.grid(column=1,
                 columnspan=2,
                 row=1,
                 sticky='we')

        btn1 = ttk.Button(self,
                          text="Generate enemies",
                          command=lambda: controller.showFrame(enFrame))
        btn1.grid(column=1,
                  row=2,
                  sticky='we')

        btn2 = ttk.Button(self,
                          text="Check spells",
                          command=spellFrame)
        btn2.grid(column=2,
                  row=2,
                  sticky='we')

        btn3 = ttk.Button(self,
                          text="Generate adventure",
                          command=advFrame)
        btn3.grid(column=1,
                  row=3,
                  sticky='we')

        btn4 = ttk.Button(self,
                          text="Import to database",
                          command=importData)
        btn4.grid(column=2,
                  row=3,
                  sticky='we')

    # ------------------------------------------------------------------

    def showEnemyShit(self):
        self.window = enFrame(self)
        self.window.grid(row=0, column=10, rowspan=2)
# ----------------------------------------------------------------------


class enFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.widgets(controller)
    # ------------------------------------------------------------------

    def widgets(self, controller):
        # Create for later (supports auto-update)
        self.playerLevels = tk.StringVar()
        self.curDiffInt = tk.IntVar()
        self.curDiffStr = tk.StringVar()
        self.returnFile = tk.IntVar()
        self.playerLevels.set("")
        self.curDiffInt.set(2)

        # Create widgets
        lbl1 = ttk.Label(self,
                         text="Player levels:")
        lbl1.grid(column=1,
                  row=1,
                  sticky='e')

        plrLvl = ttk.Entry(self,
                           width=7,
                           textvariable=self.playerLevels)
        plrLvl.grid(column=2,
                    row=1,
                    sticky='we')

        lbl2 = ttk.Label(self,
                         text="Difficulty:")
        lbl2.grid(column=1,
                  row=2,
                  sticky='e')

        self.diffScale = ttk.Scale(self,
                                   from_=1,
                                   to=4,
                                   orient='horizontal',
                                   variable=self.curDiffInt,
                                   command=self.doScaleStuff)
        self.diffScale.grid(column=2,
                            row=2,
                            sticky='we')
        self.diffScale.set(2)

        lbl3 = ttk.Label(self,
                         textvariable=self.curDiffStr)
        lbl3.grid(column=2,
                  row=3,
                  sticky='we')

        checkbtn = ttk.Checkbutton(self,
                                   text="Return file",
                                   variable=self.returnFile)
        checkbtn.grid(column=3,
                      row=1,
                      sticky='w')
        checkbtn.state = False

        # Create buttons
        genBtn = ttk.Button(self,
                            text="Generate",
                            command=lambda: controller.showFrame(enFrameOut))
        genBtn.grid(column=3,
                    row=2,
                    sticky='w')

        backBtn = ttk.Button(self,
                             text="Back",
                             command=lambda: controller.showFrame(startPage))
        backBtn.grid(column=3,
                     row=3,
                     sticky='e')

        # Add nice padding to everything
        for child in self.winfo_children():
            child.grid_configure(padx=5,
                                 pady=5)

        # Set focus to first entry field
        plrLvl.focus()
# ----------------------------------------------------------------------

    def doScaleStuff(self, *args):
        value = self.diffScale.get()
        if int(value) != value:
            self.diffScale.set(round(value, 0))
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
# ---------------------------------------------------------------------


class enFrameOut(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        enOutRoot = tk.Toplevel()
        enOutRoot.title("Enemy output")

        enList = generateEnemies(enFrame.diffScale.get(), enFrame.plrLvl.get())

        backBtn = ttk.Button(enOutRoot,
                             text="Back",
                             command=enList.destroy())
        backBtn.grid(column=1,
                     row=1,
                     sticky='e')
        curColumn = 1
        curRow = 2
        for item in enList[0]:
            ttk.Label(enOutRoot, text=item[0]).grid(column=curColumn, row=curRow)
            curColumn += 1
            curRow += 1

            if curColumn > 3:
                curColumn = 1
# ----------------------------------------------------------------------


class spellFrame(tk.Frame):
    """

    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="red")
        self.parent = parent
        self.widgets(controller)
    # ------------------------------------------------------------------

    def widgets(self, controller):
        """

        """
# ----------------------------------------------------------------------


class advFrame(tk.Frame):
    """

    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="red")
        self.parent = parent
    # ------------------------------------------------------------------

    def widgets(self, controller):
        """

        """
# ----------------------------------------------------------------------


if __name__ == "__main__":
    app = mainWindow(None)
    app.title("Main frame")
    app.mainloop()
