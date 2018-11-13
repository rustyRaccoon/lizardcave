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
    - Random enemy group generator based on:
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

#-----------------------------------------------------------------------------
# Import stuff
#-----------------------------------------------------------------------------

import sqlite3
import os
import tempfile
import time
import webbrowser
import math
import pandas as pd
import tkinter as tk
from sqlite3 import Error
from random import randint
from tkinter import ttk

#-----------------------------------------------------------------------------
# Global vars
#-----------------------------------------------------------------------------

workingFolder = 'C:\\Users\\apo\_LOCAL\Caves&Lizards'
targetFile = os.path.join(workingFolder,"dataStorage.db")
dataSource = os.path.join(workingFolder,"dataInput.xlsm")
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

#-----------------------------------------------------------------------------
# Vars to tweak shit
#-----------------------------------------------------------------------------

expFactor = -0.05 #Factor for exponential function decay

#-----------------------------------------------------------------------------
# Start of actual code
#-----------------------------------------------------------------------------

# Main function
def main():
    # Welcome the user
    welcomeMessage = welcomeMessageList[randint(0,len(welcomeMessageList)-1)]
    print("Welcome, dear user! " + welcomeMessage)

    # Main loop
    # Ask user what he wants to do
    while 1:
        print('\nWhat would you like to do next?')
        print('[1] Generate new enemy group')
        print('[2] Check available spells')
        print('[3] Generate new adventure (early access)')
        print('[4] Import new data to database (*.txt, *.xlsx)')
        print('[0] Exit')

        userInput = input()

        # Process user input
        # Exit command
        if userInput == '0':
            break
        # User wants to generate random enemy group
        elif userInput == '1':
            generateEnemies()
        # User wants to check out spells
        elif userInput == '2':
            checkSpells()
        # User wants to generate random adventure
        elif userInput == '3':
            generateAdventure()
        # User wants to import new data to the database
        elif userInput == '4':
            importData(dataSource,targetFile,"enemies")
            importData(dataSource,targetFile,"spells")
        # User entered bullshit
        else:
            print('Sorry, that is not a valid input. Try again brah...')

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

# Gets data from an Excel file and pushes it to the database
def importData(sourceFile, dbFile, sheetToImport):
    conn = sqlite3.connect(dbFile)
    # read the source Excel into a dataFrame
    df = pd.read_excel(sourceFile,sheetToImport)
    # throw the dataFrame into the DB
    df.to_sql(sheetToImport,conn,if_exists='replace')
    # close the connection to the DB
    conn.close()

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

#Clear the console
def clear():
    os.system('cls')

# Check if a given List contains an item in a given Column
def listContains(listToSearch,listLevel,itemToSearch):
    # loop through all items in the List
    for item in listToSearch:
        # Check if item at given position matches the searched item
        if item[listLevel] == itemToSearch:
            return True
        else:
            return False

# Generates a random enemy group based on user input
def generateEnemies():
    clear()
    print('Welcome to the enemy generator subroutine. It will help you to',
           'generate a new group of enemies suitable for your party and',
           'current area. Please provide some data first.\n')

    # Ask user how hard the challenge should be
    print("From 1-5 hard should the challenge be? [1 = Easy, 4 = Deadly]: ",end="")
    userInput = input()

    #Process user input
    if int(userInput) == 1:
        difficulty = "Easy"
        mobLevelDivider = 0.5
        difficultyMultiplier = 1
        difficultyScaler = 0.1
    elif int(userInput) == 2:
        difficulty = "Medium"
        mobLevelDivider = 0.6
        difficultyMultiplier = 1.05
        difficultyScaler = 0.15
    elif int(userInput) == 3:
        difficulty = "Hard"
        mobLevelDivider = 0.7
        difficultyMultiplier = 1.1
        difficultyScaler = 0.2
    elif int(userInput) == 4:
        difficulty = "Deadly"
        mobLevelDivider = 0.8
        difficultyMultiplier = 1.15
        difficultyScaler = 0.6
    else:
        print("You fucked up. Difficulty set to default values.")
        difficulty = "Medium"
        mobLevelDivider = 0.6
        difficultyMultiplier = 1.05
        difficultyScaler = 0.15

    # Ask for user for player levels
    print("Player level (10 max; separated by commas): ",end="")
    # Split answer to get a List for easier handling and map to int
    levelList = list(map(int,input().split(",")))
    # Get number of items in list
    numPlayers = len(levelList)
    # Calculate average player level base value
    playerLevel = round(sum(levelList)/numPlayers * difficultyMultiplier)
    if numPlayers >= 4:
        # If there's more than 4 people, add something on top to increase difficulty
        playerLevel += playerLevel * (numPlayers%4*difficultyScaler*math.exp(round(sum(levelList)/numPlayers)*expFactor))
        
    # Round player level to nearest multiple of 0.125
    playerLevel -= playerLevel%0.125
    
    # Create empty list to be filled
    chosenEnemyList = []
    # Set top and bottom caps
    topCap = playerLevel
    lowCap = playerLevel*mobLevelDivider
    # Initialize number of tries as 0
    tries = 0

    # While the challenge level of the enemy group is below the average player level, keep looping
    while sum(row[1] for row in chosenEnemyList) < playerLevel:
        conn = sqlite3.connect(targetFile)
        # Query all enemies from the database that fit the criteria (correct region and challenge level below players) Only get name and challenge info though
        enemyList = fetchFromDB(conn, "enemyName, enemyChallenge FROM enemies WHERE enemyChallenge BETWEEN '" + str(lowCap) + "' AND '" + str(topCap) + "'")
        conn.close()
        # Dump first entry of freshly acquired list
        enemyList = enemyList[1:]
        # Get a new random enemy from the List
        randEnemy = enemyList[randint(1,len(enemyList))-1]
        # Check if new enemy would go over boundaries
        if (sum(row[1] for row in chosenEnemyList) + randEnemy[1]) <= playerLevel:
            # Add random enemy to the chosenList
            chosenEnemyList.append(randEnemy)
        # If it was already tried three times to match an enemy into the remainder, lower the level caps and reset the counter
        if tries > 3:
            tries = 0
            topCap = playerLevel - sum(row[1] for row in chosenEnemyList)
            lowCap = topCap * mobLevelDivider
        else:
            tries += 1

    # Clear enemy list
    enemyList.clear()
    # Loop through all freshly randomly chosen enemies to get their details and store those in a list
    for enemy in chosenEnemyList:
        try:
            conn = sqlite3.connect(targetFile)
            enemyDetails = fetchFromDB(conn, "* FROM enemies WHERE enemyName = '" + enemy[0] + "'")
            conn.close()
        except Error as e:
            print("Error at: " + enemy[0])
        enemyList.append(enemyDetails[1])
    # Add titles to columns
    enemyList.insert(0,enemyDetails[0])

    #delete the first entry of each row (index)
    for subList in enemyList:
        del subList[0]

    # Create temporary file name with timestamp
    filename = tempfile.gettempdir() + "randEnemy_" + str(round(time.time()))
    # Open textfile for append
    f = open(filename,"a")
    # Add information about party to file (beginning)
    tempString = "Player levels: "
    for player in levelList:
        tempString += (str(player) + ", ")
    # Add info about calculated difficulty level
    tempString += ("\nAverage level for calculation: " + str(playerLevel) + "\nChosen difficulty: "+ difficulty + "\n")
    # Add a visible divider
    tempString += "\n---------------------------------------------------------------------------\n"
    f.write(tempString)


    # Write all the info about an enemy to the file (1 line per parameter)
    for subList in enemyList[1:]:
        counter = 0

        # Formatting if this spans multiline
        for item in subList:
            if len(enemyList[0][counter]) > 14:
                f.write(enemyList[0][counter] + " \t")
            else:
                f.write(enemyList[0][counter] + " \t\t")

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
            counter+=1

        f.write("\n")
        f.write("\n")

    # Open the file in an editor
    webbrowser.open(filename)

# Check what spells can be used by the player based on user input
def checkSpells():
    clear()
    print('Welcome to the spell organizer subroutine. It will help you and',
          'your party to find suitable spells for their level, class and',
          'knowledge. Please provide some data to get started.\n')

# Ask for user input and assign it to variables
    print("Character class: ",end="")
    charClass = input()
    print("Character level: ",end="")
    charLevel = input()
    print("Magic level: ",end="")
    magicLevel = input()

    # Process input

# Generate a random adventure based on user input
def generateAdventure():
    clear()
    print('WARNING! THIS FEATURE IS HIGHLY EXPERIMENTAL!\n\n')
    print('Welcome to the super tight adventure generator (S.T.A.G.) which',
          'will help you to make a really nice adventure for your party.',
          'Damn straight, brosef, this will knock your socks off.')

    # Ask user for region to generate for
    print("Region to generate in (for a list enter 'list'):",end="")
    targetRegion = input()
    # If user wants to see the list of regions, show him and keep asking until he provides viable input
    while targetRegion == 'list':
        for region in regionList:
            print("+ " + region)
        print("Region to generate for: ",end="")
        targetRegion = input()
    print("Number of players: ",end="")
    numPlayers = input()
    print("Average player level: ",end="")
    playerLevel = input()

    # Process input

#-----------------------------------------------------------------------------
# Class definitions (classes not used in this version, kept it for later versions)
#-----------------------------------------------------------------------------

class enemy:
    def __init__(self, name, type, alignment, armorClass, HP, speed, str, dex, con, wis, cha, senses, challenge, savingThrows=None, skills=None, vulnerabilities=None, damageResistance=None, damageImmunity=None, conditionImmunity=None, languages=None, traits=None, actions=None, legendaryActions=None):
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

class spell:
    def __init__(self, name, type, school, castingTime, range, duration, components, classes, description, higherLevels):
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

#-----------------------------------------------------------------------------
# GUI stuff
#-----------------------------------------------------------------------------

# Create root woop woop
root = tk.Tk()
root.title("Caves & Lizards toolkit")

# Create main frame that houses everything else
mainframe = ttk.Frame(root, padding="5")
mainframe.grid(column=0, row=0, sticky='nwes')
# If main window is resized, expand frame to take up the extra space
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Create for later (supports auto-update)
playerLevels = tk.StringVar()

# Create entry boxes
playerLevels = ttk.Entry(mainframe, width=7, textvariable=playerLevels)
playerLevels.grid(column=2, row=1, sticky='we')

# Create labels
ttk.Label(mainframe, text="Player levels:").grid(column=1, row=1, sticky='e')
ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky='e')
ttk.Label(mainframe, text="meters").grid(column=2, row=2, sticky='w')

# Create buttons
ttk.Button(mainframe, text="Generate", command=generateEnemies).grid(column=2, row=3, sticky='w')

# Create slider
difficultySlider = ttk.Scale(mainframe, from_=1, to=5, orient = 'horizontal', value = 2)
difficultySlider.grid(column = 1, row = 3, sticky='we')
#difficultySlider.set(2)

# Add nice padding to everything
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# Set focus to first entry field
playerLevels.focus()
# Bind enemy generating function to Enter key
root.bind('<Return>', generateEnemies)
    
# Start event loop
root.mainloop()
