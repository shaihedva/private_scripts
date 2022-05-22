#!/usr/bin/python2.7
# find Nationality by  player name
from email.parser import Parser
import requests 
import json
import argparse

from yaml import parse 

parser = argparse.ArgumentParser(description='find the player')
parser.add_argument('strPlayer', metavar='strPlayer' , type=str , help='enter your player first name: ')
args = parser.parse_args()
strPlayer = args.strPlayer


#strPlayer = "Ari"
#strPlayer = input ("enter player first name: ")

url = 'https://www.thesportsdb.com/api/v1/json/2/searchplayers.php?p=' + strPlayer
r= requests.get(url)
data=json.loads(r.text)

print (data['player'][0]['strNationality'])


