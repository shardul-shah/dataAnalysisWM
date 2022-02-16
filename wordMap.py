import json
import os
from pathlib import Path

## TODOs:
# Remove punctuation
# Account for stop words
# Generate Word Map
# And more

def generatePathOfMessagesFolder(folderContainingMessages):
	currentWorkingDirectory = os.getcwd()
	dynamicPath = Path(currentWorkingDirectory)
	# print(currentWorkingDirectory)

	for objectName in os.listdir(currentWorkingDirectory):
		# print(objectName)
		if (objectName == folderContainingMessages):
			folderContainingMessagesPath = dynamicPath / objectName
			return folderContainingMessagesPath

def generateListOfJSONFiles(folderPath):
	# print(folderPath)
	messengerjSONFilesWithPath = []
	for fileOrFolder in os.listdir(folderPath):
		# print(fileOrFolder)
		fullPath = Path(folderPath) / fileOrFolder
		if os.path.isfile(fullPath):
			# print(fullPath)
			messengerjSONFilesWithPath.append(fullPath)
	return messengerjSONFilesWithPath

def parseJSONFiles(JSONFiles):
	counter = 0
	frequencyCounter = {}
	totalNumFiles = len(JSONFiles)
	# print(JSONFiles)
	for file in JSONFiles:
		counter+=1
		with open(file, 'r') as file:
			print("Parsing file " + str(counter) + " of " + str(totalNumFiles) + ".")
			data = json.load(file)
			# print(data)
			for messageInfo in data["messages"]:
				if "content" in messageInfo: 
					# for clarity, can directly loop through .split(" ") without assigning it to message (if needed for efficiency)
					message = messageInfo["content"].split(" ") 
					for word in message: 
						# print(word)
						sanitizedWords = removeUnicodeCharacters(word)

						for sanitizedWord in sanitizedWords:
							sanitizedWord = normalizeCase(sanitizedWord)
							if (sanitizedWord == ""):
								continue
							if sanitizedWord in frequencyCounter:
								frequencyCounter[sanitizedWord]+=1
							else:
								frequencyCounter[sanitizedWord] = 1

	# print(frequencyCounter)
	return frequencyCounter

def removeUnicodeCharacters(phrase):
	# generates list of sanitized words from a phrase

	nonUnicodeString = ''.join([i if ord(i) < 128 else ' ' for i in phrase]) 	# using list comprehension
	sanitizedString = ' '.join(nonUnicodeString.split())
	return sanitizedString.split() # return list of words instead of string

def normalizeCase(word):
	return word.lower()

def sortFrequencyCount(orderLowestToHighest, frequencyCountDict):
	return {k: v for k, v in sorted(frequencyCountDict.items(), key=lambda item: item[1], reverse=(orderLowestToHighest != True))}

def exportDataToFile(dataDict):
	with open('output.json', 'w') as outputFile:
		outputFile.write(json.dumps(dataDict))

def main():
	print("test")
	folderPath = generatePathOfMessagesFolder("JSONCollection")
	JSONFilePaths =  generateListOfJSONFiles(folderPath)
	# print(JSONFilePaths, len(JSONFilePaths))
	wordFrequencyCounter = parseJSONFiles(JSONFilePaths)
	sortedWordFrequencyCounter = sortFrequencyCount(wordFrequencyCounter, wordFrequencyCounter)
	exportDataToFile(sortedWordFrequencyCounter)
	# print(sortedWordFrequencyCounter)
	print("Output is ready!")

if __name__ == '__main__':
	main()

