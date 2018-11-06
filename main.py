# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 08:00:19 2018

@author: APO
Supposed to be a supporting application for playing Dungeons&Dragons, or as I
call it Caves&Lizards. There are databases of enemies and spells in the
background.

Functionalities should be in separate tabs.

Functionalities:
    - Random enemy group generator based on:
        . Number of players
        . Player level
        . Current region the party is in
    - Import tool to feed new data into the database
    - Spell allocation tool that suggests spells based on:
        . Player character level
        . Player magic level
        . Player character class
    - Random adventure generator based on:
        . Number of players
        . Player level
        . Current region the party is in
"""

import sqlite3, os, pandas as pd
from sqlite3 import Error
from random import randint

# Global variables
workingFolder = 'C:\\Users\\apo\_LOCAL\Caves&Lizards'
targetFile = os.path.join(workingFolder,"dataStorage.db")
dataSource = os.path.join(workingFolder,"dataInput.xlsm")
welcomeMessageList = ["How's your day going?",
                      "Back again, are we?",
                      "Don't have any friends either, hm?",
                      "Nice to see you're doing well!",
                      "Not bored of my tool yet, eh?"]

# Welcome code
def main():
    print("--# Caves & Lizards toolkit #--\n")
    
    welcomeMessage = welcomeMessageList[randint(0,len(welcomeMessageList)-1)]
    print("Welcome, dear user! " + welcomeMessage)
    
    # Main loop
    while 1:
        # Ask user what he wants to do
        print('\nWhat would you like to do next?')
        print('[1] Generate new enemy group')
        print('[2] Check available spells')
        print('[3] Generate new adventure (early access)')
        print('[4] Import new data to database (*.txt, *.xlsx)')
        print('[0] Exit')
        
        # Process user input
        userInput = input()
        
        if userInput == '0':
            break
        elif userInput == '1':
            generateEnemies()
        elif userInput == '2':
            checkSpells()
        elif userInput == '3':
            generateAdventure()
        elif userInput == '4':
            importData(dataSource,targetFile,"enemies")
            importData(dataSource,targetFile,"spells")
        else:
            print('Sorry, that is not a valid input. Try again brah...')

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------
def importData(sourceFile, dbFile, sheetToImport):
    # create connection to the DB
    conn = sqlite3.connect(dbFile)
    # read the source Excel into a dataFrame
    df = pd.read_excel(sourceFile,sheetToImport)
    # throw the dataFrame into the DB
    df.to_sql(sheetToImport,conn,if_exists='replace')
    # close the connection to the DB
    conn.close()

def createConnection(dbFile):
    # return connection object or None
    try:
        conn = sqlite3.connect(dbFile)
        return conn
    except Error as e:
        print("You fucked up dawg, the database could not be found. How? Why?\n" + e)
    return None

# SQLstring should be the table name with all parameters in parentheses (add
# NOT NULL if forced parameter), e.g. tableName(id integer PRIMARY KEY,
# parameter1 type1, parameter2 type2 NOT NULL)
def createTable(conn, SQLstring):
    try:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS " + SQLstring)
    except Error as e:
        print("Oh man, another error? Jeez, wtf are you even doing?\n" + e)

def fetchFromDB(conn, tableToFetch):
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + tableToFetch)
    
    fetchedData = []
    tempList = []
    fetchedData[0] = [tuple[0] for tuple in cur.description]
    rows = cur.fetchall()
       
    for tuple in rows:
        for item in tuple:
            tempList.append(item)
        fetchedData.append(tempList)
    return fetchedData

def clear():
    os.system('cls')

def generateEnemies():
    clear()
    print('Welcome to the enemy generator subroutine. It will help you to', 
           'generate a new group of enemies suitable for your party and', 
           'current area. Please provide some data first.\n')
    
    # Ask for user input to base the generation on
    print("Number of players: ",end="")
    numPlayers = input()
    print("Average player level: ",end="")
    playerLevel = input()
    print("Region to generate for: ",end="")
    targetRegion = input()
    
    # Process input
    
def checkSpells():
    clear()
    print('Welcome to the spell organizer subroutine. It will help you and',
          'your party to find suitable spells for their level, class and',
          'knowledge. Please provide some data to get started.\n')
    
    # Ask for user input to base the generation on
    print("Character class: ",end="")
    charClass = input()
    print("Character level: ",end="")
    charLevel = input()
    print("Magic level: ",end="")
    magicLevel = input()
    
    # Process input
    
def generateAdventure():
    clear()
    print('WARNING! THIS FEATURE IS HIGHLY EXPERIMENTAL!\n\n')
    print('Welcome to the super tight adventure generator (S.T.A.G.) which',
          'will help you to make a really nice adventure for your party.',
          'Damn straight, brosef, this will knock your socks off.')
    
    # Ask for user input to base the generation on
    print("Region [woods, desert, demon world, Africa, Soviet Russia]: ",end="")
    targetRegion = input()
    print("Number of players: ",end="")
    numPlayers = input()
    print("Average player level: ",end="")
    playerLevel = input()
    
    # Process input

#-----------------------------------------------------------------------------    
# Class definitions
#-----------------------------------------------------------------------------
class enemy:
    def __init__(self, name, type, alignment, armorClass, HP, speed, str, dex, con, wis, cha, senses, challenge, savingThrows=None, skills=None, vulnerabilites=None, damageResistance=None, damageImmunity=None, conditionImmunity=None, languages=None, traits=None, actions=None, legendaryActions=None):
        self.name = name
        self.type = type
        self.alignment = aligment
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
        self.vulnerabilites = vulnerabilities
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
