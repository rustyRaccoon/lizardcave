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
import sqlite3, os, tempfile, time, pandas as pd
from sqlite3 import Error
from random import randint

#-----------------------------------------------------------------------------
# Global vars
#-----------------------------------------------------------------------------
workingFolder = 'C:\\Users\\apo\_LOCAL\Caves&Lizards'                           # Global variables
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
              "the moon!"]

#-----------------------------------------------------------------------------
# Vars to tweak shit
#-----------------------------------------------------------------------------
damageMultiplier = 1.2
damageModifier = 0.8

#-----------------------------------------------------------------------------
# Start of actual code
#-----------------------------------------------------------------------------
def main():                                                                     
    print("--# Caves & Lizards toolkit #--\n")                                  # Welcome code
    
    welcomeMessage = welcomeMessageList[randint(0,len(welcomeMessageList)-1)]
    print("Welcome, dear user! " + welcomeMessage)
                                                                                # Main loop
    while 1:                                                                    # Ask user what he wants to do
        print('\nWhat would you like to do next?')
        print('[1] Generate new enemy group')
        print('[2] Check available spells')
        print('[3] Generate new adventure (early access)')
        print('[4] Import new data to database (*.txt, *.xlsx)')
        print('[0] Exit')
                
        userInput = input()                                                     # Process user input
        
        if userInput == '0':                                                    # Exit command
            break
        elif userInput == '1':                                                  # User wants to generate random enemy group
            generateEnemies()
        elif userInput == '2':                                                  #User wants to check out spells
            checkSpells()
        elif userInput == '3':                                                  # User wants to generate random adventure
            generateAdventure()
        elif userInput == '4':                                                  # User wants to import new data to the database
            importData(dataSource,targetFile,"enemies")
            importData(dataSource,targetFile,"spells")
        else:                                                                   # User entered bullshit
            print('Sorry, that is not a valid input. Try again brah...')

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------
def importData(sourceFile, dbFile, sheetToImport):
    conn = sqlite3.connect(dbFile)                                              # create connection to the DB
    df = pd.read_excel(sourceFile,sheetToImport)                                # read the source Excel into a dataFrame
    df.to_sql(sheetToImport,conn,if_exists='replace')                           # throw the dataFrame into the DB
    conn.close()                                                                # close the connection to the DB

def createConnection(dbFile): # return connection object or None
    try:
        conn = sqlite3.connect(dbFile)
        return conn
    except Error as e:
        print("You fucked up dawg, the database could not be found. How? Why?\n" + e)
    return None


def createTable(conn, SQLstring): # SQLstring should be the table name with all parameters in parentheses (add NOT NULL if forced parameter), e.g. tableName(id integer PRIMARY KEY, parameter1 type1, parameter2 type2 NOT NULL)
    try:
        c = conn.cursor()                                                       # Create a cursor
        c.execute("CREATE TABLE IF NOT EXISTS " + SQLstring)                    # Create new table if it does not exist yet
    except Error as e:
        print("Oh man, another error? Jeez, wtf are you even doing?\n" + e)

def fetchFromDB(conn, SQLquery): # Get data from the database (requires query to be supplied)
    cur = conn.cursor()                                                         # Create a cursor
    cur.execute("SELECT DISTINCT " + SQLquery)                                  # Run the command to fetch data based on the query   
    
    fetchedData = []                                                            # Create dummy List
    fetchedData.append([tuple[0] for tuple in cur.description])                 # Fill List with columns titles of database
    rows = cur.fetchall()                                                       # Get all the rows that fit the query
       
    for rowData in rows:                                                        # Loop through rows
        tempList = []                                                           # create a temporary List
        for singleItem in rowData:                                              # Loop through all items
            tempList.append(singleItem)                                         # Add item to temporary List        
        fetchedData.append(tempList)                                            # Append it to the parent List
    return fetchedData                                                          # Return parent List

def clear(): #Clear the console
    os.system('cls')

def listContains(listToSearch,listLevel,itemToSearch): # Check if a given List contains an item in a given Column
    for item in listToSearch:                                                   # loop through all items in the List
        if item[listLevel] == itemToSearch:                                     # Check if item at given position matches the searched item
            return True
        else:
            return False
        
def generateEnemies(): # Generates a random enemy group based on user input
    clear()                                                                     # Clear console
    print('Welcome to the enemy generator subroutine. It will help you to',
           'generate a new group of enemies suitable for your party and', 
           'current area. Please provide some data first.\n')
    
    print("Player level (10 max; separated by commas): ",end="")                        
    userInput = input()                                                         # Ask for user input to base the generation on
    levelList = userInput.split(",")                                            # Split answer to get a List for easier handling
    levelList = list(map(int,levelList))                                        # Change type to ints
    numPlayers = len(levelList)                                                 # Get number of items in list    
    if numPlayers <= 4:
        playerLevel = round(sum(levelList)/numPlayers * damageMultiplier)       # Calculate average player level (does not account for parties greater 10 people)
    else:
        playerLevel = round(sum(levelList)/numPlayers * damageMultiplier * (numPlayers%4*damageModifier)) # Calculate average player level (does not account for parties greater 10 people)
        
    fetchedEnemyList = fetchFromDB(createConnection(targetFile), "enemyName, enemyChallenge FROM enemies WHERE enemyChallenge BETWEEN '" + str(playerLevel/2) + "' AND '" + str(playerLevel) + "'") # Query all enemies from the database that fit the criteria (correct region and challenge level below players)
    chosenEnemyList = []                                                        # Create empty list
    
    while sum(row[1] for row in chosenEnemyList) < playerLevel:                 # While the challenge level of the enemy group is below the average player level, keep looping
        chosenEnemyList.append(fetchedEnemyList[randint(1,len(fetchedEnemyList))-1]) # Get a new random enemy from the List and add him to the chosenList
    
    detailList = []
    for enemy in chosenEnemyList:
        enemyDetails = fetchFromDB(createConnection(targetFile), "* FROM enemies WHERE enemyName = '" + enemy[0] + "'")
        detailList.append(enemyDetails[1])
    detailList.insert(0,enemyDetails[0])
    
    f = open(tempfile.gettempdir() + "randEnemy_" + str(round(time.time())),"a")     # Write the outcome to the console or whatever. Maybe better to open a textfile and dump that shit there
    
    for enemy in detailList:
        for item in detailList:
            f.write(item)
        f.write("\n")
    
def checkSpells(): # Check what spells can be used by the player based on user input
    clear()                                                                     # Clear console
    print('Welcome to the spell organizer subroutine. It will help you and',
          'your party to find suitable spells for their level, class and',
          'knowledge. Please provide some data to get started.\n')
    
    print("Character class: ",end="")                                           # Ask for user input and assign it to variables
    charClass = input()
    print("Character level: ",end="")
    charLevel = input()
    print("Magic level: ",end="")
    magicLevel = input()
    
                                                                                # Process input
    
def generateAdventure(): # Generate a random adventure based on user input
    clear()                                                                     # Clear console
    print('WARNING! THIS FEATURE IS HIGHLY EXPERIMENTAL!\n\n')
    print('Welcome to the super tight adventure generator (S.T.A.G.) which',
          'will help you to make a really nice adventure for your party.',
          'Damn straight, brosef, this will knock your socks off.')
    
    print("Region to generate in (for a list enter 'list'):",end="")            # Ask user for input and assign to variables
    targetRegion = input()
    while targetRegion == 'list':                                               # If user wants to see the list of regions, show him
        for region in regionList:
            print("+ " + region)
        print("Region to generate for: ",end="")                                # Keep asking until he enters a valid region    
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

# Call main function to start program
main()
