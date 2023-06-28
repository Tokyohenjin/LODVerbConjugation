```Python
#Definitions and import
import requests
#import re

api_url = "https://lod.lu/api/"
lang = "en" #Change to desired language
fileName = 'sample_input.txt'
langLib = {'de':"Deutsch",'en':"English",'fr':"Français",'pt':"Português"}
pronounLib = {'p1':'ech','p2':'du','p3':'hien/si/hatt/et','p4':'mir','p5':'dir/Dir','p6':'si'} #List to convert entries to personal pronouns

#Function to manage prefixes for reflexive verbs. Creates a two-entry library of prefix and search word
def prefix_handler(word):
    if word[:5] == 'sech ':
        return({'prefix': word[:4],'searchWord': word[5:]})
    else:
        return({'prefix': '','searchWord': word})

#Function to re-join prefixes for searching
def prefix_join(prefix,word):
    myString = ''
    if prefix == '':
        return(word)
    elif prefix != "d'":
        return(prefix+' '+word)
    else:
        return(prefix+word)

#Function to pull multiple meanings (up to 3 entries, but can be changed)
def get_trans(item):
    myList = []
    for i in item:
        if i['type'] == 'translation':
            myList.append(i['content'])
        elif i['type'] == 'semanticClarifier':
            myList[-1] += ' ('+i['content']+')'
    myString = ''
    for item in myList[:3]:
        myString += item + ', '
    return(myString.rstrip(', '))

##VERBS

#Function to pull conjugation table out of entry
def get_conjugation(table):
    conjugationDict = {}
    conjugationDict['infinitive'] = table['infinitive']
    conjugationDict['indicativePresent'] = table['indicative']['present']
    try: #Not every very has an imperitive
        conjugationDict['imperitive'] = table['imperative']['present']
    except:
        conjugationDict['imperitive'] = {}
    return(conjugationDict)

#Function provide passé composé form of verb and handle transitive/intransitive forms
def verb_handler(entry,verb,conjugation):
    myDict = {}
    myDict['entry'] = prefix_join(entry['prefix'],entry['word'])
    myDict['partOfSpeech'] = 'VRB'
    auxiliaryVerb = verb['auxiliaryVerb']
    pastParticiple = verb['pastParticiple'][0]
    if entry['prefix'] == 'sech': #Reflexive verb!
        for x in verb['grammaticalUnits']:
            if x['grammaticalInformation'][0] == 'reflexiv': #Reflexive verb!
                myDict['Translation'] = get_trans(x['meanings'][0]['targetLanguages'][lang]['parts'])
    else: #Transitive verb!
        myDict['Translation'] = get_trans(verb['grammaticalUnits'][0]['meanings'][0]['targetLanguages'][lang]['parts'])
    if pastParticiple[:1] in ['u','n','i','t','e','d','z','o','a','h']: #N-Reegel
        myDict['pastParticiple'] = auxiliaryVerb+' '+pastParticiple
    else:
        myDict['pastParticiple'] = auxiliaryVerb.rstrip('n')+' '+pastParticiple
    myDict['Translation'] = get_trans(verb['grammaticalUnits'][0]['meanings'][0]['targetLanguages'][lang]['parts'])
    myDict['Conjugation'] = get_conjugation(conjugation)
    return(myDict)

# Import file as list
with open(fileName,'r') as f:
    lines = f.readlines()
    
lines = list(set(lines)) #Removing duplicates

# Pull LOD IDs for each entry in file. Outputs nested list with each entry showing word and LOD ID.
# For items not found, put them into an error list for later checking
# Strip newlines from all entries
idList = []
errorList = []

for i in lines:
    myWord = prefix_handler(i.strip())
    response = requests.get(api_url+lang+'/advanced-search?query='+myWord['searchWord']+'&full_text_search=false&case_sensitive=true&include_alternative_forms=false&include_examples=false&include_synonyms=false&parts_of_speech%5B%5D=VRB&items_per_page=10&page=1') #Advanced search, limit to verbs
    myResponse = response.json()
    try:
        if len(myResponse['results']) > 1: #More than one entry
            tempList = []
            def keySort(entry): #Simple sorting function
                return(entry[1]) #Sort by first letter
            for item in myResponse['results']:
                tempList.append([myWord,item['id']])
            tempList.sort(key=keySort)
            idList.append(tempList[0]) #Limit to first result
        else:
            idList.append([myWord,myResponse['results'][0]['id']])
    except:
        errorList.append(i.strip())

# Create another nested list to hold entry, LOD ID, and LOD entry data
newList = []
for item in idList:
    tempList = []
    tempList = item.copy() #Copy over to leave the original alone
    response = requests.get(api_url+lang+'/entry/'+item[1])
    myResponse = response.json()
    tempList[0]['word'] = myResponse['entry']['lemma'] #Adds word entry to ensure searched word is not conjugation or declination of original
    tempList.append(myResponse['entry']['microStructures'][0]) #Third item in list is part of the API response with translations
    tempList.append(myResponse['entry']['tables']['verbConjugation']) #Fourth item in list is part of API response with verb conjugations
    newList.append(tempList) #Now append everything to the new list

#Next step is to parse through the LOD entry data and pull relevant information for output

#Parse through the nested list created above and output to new list which will be used for output.
#Output is a list of dictionary entries. Content of the dictionary depends on the part of speech.
#Any items that cannot be parsed go to another list for error checking. This is usually because of blank definitions.
finalList = []
checkingList = []
parseErrorList = []
for item in newList:
    try:
        if item[0]['searchWord'] != item[0]['word']: #Small list of words to manually check
            checkingList.append(item)
        elif item[2]['partOfSpeech'] == 'VRB':
            try:
                finalList.append(verb_handler(item[0],item[2],item[3]))
            except:
                parseErrorList.append([item[0],item[2]])
    except:
        parseErrorList.append([item[0],item[2]])

newIdList = []
newerList = []

for item in parseErrorList:
    print('Current values: ',item, '\n')
    myInput = input('Please provide the requested ID: ')
    newIdList.append([item[0],myInput])
    parseErrorList.remove(item)

for item in newIdList:
    tempList = []
    tempList = item.copy() #Copy over to leave the original alone
    response = requests.get(api_url+lang+'/entry/'+item[1])
    myResponse = response.json()
    tempList[0]['word'] = myResponse['entry']['lemma'] #Adds word entry to ensure searched word is not conjugation or declination of original
    tempList.append(myResponse['entry']['microStructures'][0]) #Third item in list is part of the API response with translations
    tempList.append(myResponse['entry']['tables']['verbConjugation']) #Fourth item in list is part of API response with verb conjugations
    newerList.append(tempList) #Now append everything to the newer list

for item in newerList:
    try:
        if item[0]['searchWord'] != item[0]['word']: #Small list of words to manually check
            checkingList.append(item)
        elif item[2]['partOfSpeech'] == 'VRB':
            try:
                finalList.append(verb_handler(item[0],item[2],item[3]))
            except:
                parseErrorList.append([item[0],item[2]])
    except:
        parseErrorList.append([item[0],item[2]])
```
