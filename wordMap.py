import json
import os
from pathlib import Path
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import sys
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from PIL import Image
import numpy as np
import random


letterTypes = ["letters", "digits", "punctuation", "all"]

# structure (RGB color):
'''
	color: 
	{
		R: (min, max),
		G: (min, max),
		B: (min, max)
	}
'''
customColorPalettes = {	
	# a nice range of red/purple shades (RGB values)
	# 124, 82, 158
	# 140, 0, 255
	# 158, 82, 82
	# 255, 0, 0
	# results in:

	"red":
	{
		"R": (124, 255,),
		"G": (0, 82,),
		"B": (0, 255,),
	},

	"random":
	{
		"R": (0, 255,),
		"G": (0, 255,),
		"B": (0, 255,),
	}
}

currentPaletteName = ""

## TODOs:
# Remove punctuation
# Optimize removeUnicodeCharacters and keep punctuaction
# Add ability to add custom stopwords
# styling/customizing wordcloud/plot objects to perfect
# Improve removeUnneccessaryPunctuation()
# if sanitizedWord in stopwordsSet: - line 67 is really key. Include more stopwords from FB/Messenger keywords themselves (there's quite a few)
# and change syntax so it's like "if SanitizedWord not in stopwordsset, do..."
# look up algorithm to clean up pnuctuation from words and keep words
# Specialized stopwords: only remove FB stopwords when the words are actually in the same sentence/together there are trigger words.
# e.g. sentences "... missed your call", "you missed a call from ...", "... sent an attachment", "... set the emoji to", "... called you"
# "you called ...", etc.
# use # refer to specialized to do above comment
# regex to clean up words or better ways to do it?
# maybe add called back in from list of stopwordds (remove from list)
# turn into class, so state var can be retained (above color variables especially would be helpful)
# possibly change font

def generatePathOfFolderOrFile(folderOrFile):
	currentWorkingDirectory = os.getcwd()
	dynamicPath = Path(currentWorkingDirectory)
	# print(currentWorkingDirectory, dynamicPath)

	for objectName in os.listdir(currentWorkingDirectory):
		# debug files not found errors here:
		# print(objectName, folderOrFile)
		if (objectName == folderOrFile):
			targetPath = dynamicPath / objectName
			print("Relevant file found: " + str(targetPath))
			return targetPath

	# no such folder or file found	
	print(folderOrFile + " was not found in " + currentWorkingDirectory + ", please try again.")
	sys.exit()


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

def parseJSONFiles(JSONFiles, stopwordsSet):
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
							sanitizedWord = cleanWord(sanitizedWord)
							
							# skip stop words from frequency counter formation (naive approach right now; not looking at neighboring words)
							if sanitizedWord in stopwordsSet:
								# refer to specialized to do above - TODO, to be implemented
								# use this to see which Messenger specific words are to be removed and which are not
								# if (sanitizedWord == "emoji" or sanitizedWord == "missed"):
								if (sanitizedWord == "called" or sanitizedWord == "effects" or sanitizedWord == "video"):
									# print(sanitizedWord, message)
									pass
								continue

							# skip empty words, if any	
							if (sanitizedWord == "" or sanitizedWord == " "):
								continue

							if sanitizedWord in frequencyCounter:
								frequencyCounter[sanitizedWord]+=1
							else:
								frequencyCounter[sanitizedWord] = 1

	# print(frequencyCounter)
	return frequencyCounter

def removeUnicodeCharacters(phrase):
	# generates list of sanitized words from a phrase
	# this algorithm is not perfect yet

	nonUnicodeString = ''.join([i if ord(i) < 128 else ' ' for i in phrase])
	# using list comprehension
	# print(1, nonUnicodeString) 	
	sanitizedString = ' '.join(nonUnicodeString.split())
	# print(2, sanitizedString)
	# print(3, sanitizedString.split())
	return sanitizedString.split() # return list of words instead of string

def cleanWord(word):
	word = normalizeCase(word)
	return removeUnneccessaryPunctuation(word)

def normalizeCase(word):
	return word.lower()

def getCharactersOfType(charType):
	# type = letters, digits, or punctuation, all
	if charType not in letterTypes:
		raise ValueError("Wrong type specified for getCharactersOfType. Only the following are acceptable:\n", letterTypes)

	elif charType == "all":
		return string.ascii_letters + string.digits + string.punctuation

	return getattr(string, charType)

def removeUnneccessaryPunctuation(word):
	# custom and perhaps naive approach to remove punctuation (temporary):
		# remove all punctuation at the last character, to avoid the "?", ".", "'.", etc. at the end of words
		# keep manually typed emojis (e.g. :), :(, ^_^, <3, etc. by keeping track of 1st letter of word's type)
		# keep end brackets, don't remove them
	# need to improve algorithm!

	# if 1st character of word is a punctuation (most common example: manually typed emoji)
	if word[0] in getCharactersOfType(letterTypes[-2]):
		return word

	# if enclosing bracket
	if word[-1] in (']', '}', ')'):
		return word

	# if punctuation at the end of a word
	if not word[-1].isalpha():
		# print(word, word[:-1])
		return word[:-1]
	
	return word

def setCurrentPalette(paletteName):
	global currentPaletteName
	currentPaletteName = paletteName

def sortFrequencyCount(orderLowestToHighest, frequencyCountDict):
	return {k: v for k, v in sorted(frequencyCountDict.items(), 
	key=lambda item: item[1], reverse=(orderLowestToHighest != True))}

def exportDataToFile(dataDict, outputFileName):
	with open(outputFileName, 'w') as outputFile:
		outputFile.write(json.dumps(dataDict))

	print("\nFind your full, processed word frequency usage in the JSON file " + outputFileName + ".")

def generateWordClouds(wordFrequencies, imageMask, generateCustomWordCloud = False, customPreferences = None, imageOutputFormat=".png"):
	# TODO: based on a few types specified (arguments), generate different types of word clouds
	# TODO: consider adding max_words arugments? Not sure if it's needed.

	if generateCustomWordCloud != False:
		if (customPreferences is None):
			print("Specify custom preferences if you want to generate a custom word cloud.")
		else:
			# implement here
			pass

	# some examples of the different kind of varieties of word clouds possible below
	# shows the number of possibilities and creativity possible

	else:
		print("Setting up word cloud structures.")
		wordCloudBases = []

		# version 1: maskless, min font size = 12, bg color = yellow, black font colours
		# max_words = 50000 (as many as will fit in the wordmap - comprehensive)
		wordCloudBases.append(
		WordCloud(
			width = 2000, 
			height = 2000, 
			max_words = 50000,
			background_color = "yellow", 
			color_func=lambda *args, **kwargs: (0,0,0),
			min_font_size = 12)
		)

		# version 2: maskless, min font size = 12, bg color = yellow, blue font colours
		# max_words = 50000 (as many as will fit in the wordmap - comprehensive)
		wordCloudBases.append(
		WordCloud(
			width = 2000, 
			height = 2000, 
			max_words = 50000,
			background_color = "yellow", 
			color_func=lambda *args, **kwargs: (0, 0, 255),
			min_font_size = 12)
		)

		# version 3: maskless, min font size = 10, bg color = light purple
		# font colours = black
		wordCloudBases.append(
		WordCloud(
			width = 2000, 
			height = 2000, 
			background_color = (173, 105, 209), 
			color_func=lambda *args, **kwargs: (0, 0, 0),
			min_font_size = 10)
		)

		# version 4: maskless, min font size = 10, bg color = yellow, word colour = black
		wordCloudBases.append(
		WordCloud(
			width = 2000,
			height = 2000,
			background_color = "yellow",
			color_func=lambda *args, **kwargs: (0, 0, 0),
			min_font_size = 10)
		)

		# version 5: heart mask, word colour = random red/purple/pink shades, min font size = 10,
		# max_words = 50000
		wordCloudBases.append(
		WordCloud(
			width = 2000, 
			height = 2000,
			background_color ='black',
			min_font_size = 10, 
			# contour_width = 0.5,
			mask=imageMask, 
			max_words = 50000,
			color_func=makeColorPalette("red"))
		)

		# version 6: heart mask, background color = white, word colour = only black, min font size = 10
		wordCloudBases.append(
		WordCloud(
			width = 2000,
			height = 2000,
			background_color = "white",
			min_font_size = 10, 
			color_func=lambda *args, **kwargs: (0,0,0))
		)

		# version 7: maskless, word color = viridis base colour theme,
		# background_color = white, default min and max font sizes, 
		# height and width = 2000
		wordCloudBases.append(
		WordCloud(
			width = 2000, 
			height = 2000, 
			background_color = "white")
		)

		# # version 7: maskless, word color = virdis, background_color = black, default min and max font sizes, 
		# # height and width = 2000
		# wordCloudBases.append(
		# WordCloud(
		# 	width = 2000, 
		# 	height = 2000, 
		# 	background_color = "black")
		# )

		# version 8: maskless, word color = virdis, background_color = black, min font size = 10
		# height and width = 2000
		wordCloudBases.append(
		WordCloud(
			width = 2000,
			height = 2000,
			background_color = "black",
			min_font_size = 10)
		)

		# version 9: maskless, min font size = 10, bg color = yellow, word colour = red
		wordCloudBases.append(
		WordCloud(
			width = 2000,
			height = 2000,
			background_color = "yellow",
			min_font_size = 10, 
			color_func=lambda *args, **kwargs: (255,0,0))
		)

		# version 10: heart mask, word colour = just red, min font size = 10,
		# max_words = 50000
		wordCloudBases.append(
		WordCloud(
			width = 2000, 
			height = 2000,
			background_color ='black',
			min_font_size = 10, 
			mask=imageMask, 
			max_words = 50000,
			color_func=lambda *args, **kwargs: (255,0,0))
		)

		# version 11: heart mask, word colour = just black, min font size = 10, background_color = light purple
		# max_words = 50000
		wordCloudBases.append(
		WordCloud(
			width = 2000, 
			height = 2000,
			background_color = (173, 105, 209),
			min_font_size = 10, 
			mask=imageMask, 
			max_words = 50000,
			color_func=lambda *args, **kwargs: (0,0,0))
		)


		# version 12: heart mask, background color = black, word colour = only white, min font size = 10
		wordCloudBases.append(
		WordCloud(
			width = 2000,
			height = 2000,
			background_color = "black",
			min_font_size = 10, 
			color_func=lambda *args, **kwargs: (255,255,255))
		)

		# TODO: allow multiple use of makeColourPalette() with different palletes 
		# It is currently storing the last used colour in the pallete because of the nature of 
		# global functions. Must spend more time into it.

		# UNCOMMENT below to create fully random coloured images (temp.)

		# version 13: heart mask, background color = black, word colour = totally random, min font size = 10
		# wordCloudBases.append(
		# WordCloud(
		# 	width = 2000,
		# 	height = 2000,
		# 	background_color = "black",
		# 	min_font_size = 10, 
		# 	color_func=makeColorPalette("random"))
		# )

		# # TODO: allow multiple use of makeColourPalette() with different palletes 
		# # It is currently storing the last used colour in the pallete because of the nature of 
		# # global functions. Must spend more time into it.

		# # version 14: heart mask, word colour = totally random, min font size = 10,
		# # max_words = 50000
		# wordCloudBases.append(
		# WordCloud(
		# 	width = 2000, 
		# 	height = 2000,
		# 	background_color ='black',
		# 	min_font_size = 10, 
		# 	mask=imageMask, 
		# 	max_words = 50000,
		# 	color_func=makeColorPalette("random"))
		# )

		#TODO
		# version 15: change font...

	counter = 1
	numWordClouds = len(wordCloudBases)
	for wordCloudBases in wordCloudBases:
		print("Generating word cloud " + str(counter) + " of " + str(numWordClouds) + ".")
		wordCloud = wordCloudBases.fit_words(wordFrequencies)
		plotWordCloud(wordCloud, "wordCloudV" + str(counter) + imageOutputFormat)
		counter+=1

def makeColorPalette(paletteName):
	if paletteName not in customColorPalettes:
		print("This palette is not currently available. Going with base colour pattern (virdis colour palette).")
		return None

	setCurrentPalette(paletteName)
	# print("line 407", paletteName) # debugging
	# print("line 408", currentPaletteName) # debugging
	return wordCloudColorFunc

def wordCloudColorFunc(*args, **kwargs):
	# print(args, kwargs)
	if args[0].lower() == "love" or args[0] == "<3":
		return (255, 0, 0) # red

	else:
		# print(currentPaletteName)
		return generateRandColorFromPalette()

def generateRandColorFromPalette():
	# TODO: make this dynamic so it is not hardcoded

	# print("line 423", currentPaletteName) # debugging

	R = random.randint(customColorPalettes[currentPaletteName]["R"][0], customColorPalettes[currentPaletteName]["R"][1])
	G = random.randint(customColorPalettes[currentPaletteName]["G"][0], customColorPalettes[currentPaletteName]["G"][1])
	B = random.randint(customColorPalettes[currentPaletteName]["B"][0], customColorPalettes[currentPaletteName]["B"][1])
	# print(R, G, B)
	return (R, G, B)

def plotWordCloud(wordCloud, fileName):
	# plot the WordCloud image					
	plt.figure(figsize = (25, 25), facecolor = None)
	plt.imshow(wordCloud) #, interpolation="bilinear")
	plt.axis("off")
	plt.tight_layout(pad = 0)
	plt.savefig(fileName)


def addCustomStopwords(stopwordsList):
	# add custom stopwords here
	# includes Messenger words which count as words but are not actually words used in the conversation by people
	# will shift Messenge words to "specialized stopwords" to do above with a different array
	# TODO separate commonly used stopwords from messenger stopwords and combine the 2 lists for self-documenting code
	customStopWords = ["the", "to", "but", "am", "is", "or", "a", "with", "sent", "an", "a", "attachment", "your", "reacted", "message", 
	"call", "emoji", "you", "from", "called", "okay", "chat", "ok", "set", "voice", "photo", "video", "sticker", "GIF", "Tenor", "sound",
	"theme"]

	# extra custom stopwords
	# customStopWords.append("") 
	# customStopWords.append("") 

	# other words to consider: "video", "effects", "missed"
	# print(stopwordsList)
	stopwordsList+=customStopWords
	# print("\n",stopwordsList)
	return set(stopwordsList)

def initStopwords():
	# default stopwords list
	stopwordsList = stopwords.words('english')
	custStopwords = addCustomStopwords(stopwordsList)
	return custStopwords

def getImageArray(imagePath):
	# Is Image Found?: 
	# print(Image.open(imagePath))

	return np.array(Image.open(imagePath))

def generateStatistics(sortedWordFrequencyCounter):

	top3MostUsedWords = {key: sortedWordFrequencyCounter[key] for key in list(sortedWordFrequencyCounter)[:3]}
	return {
	"numUniqueWords": len(sortedWordFrequencyCounter),
	"top3MostUsedWords": top3MostUsedWords
	}

def formatTopMostUsedWords(topXMostUsedWords):
	output = ""
	for word in topXMostUsedWords:
		output+=f"{word} used {topXMostUsedWords[word]} times.\n"

	return output

def main():
	stopwordsSet = initStopwords()

	# validate stopwords
	# print(stopwordsSet)

	print("\n")
	folderPath = generatePathOfFolderOrFile("JSONCollection")
	imagePath = generatePathOfFolderOrFile("heartMask.png")
	imageArr = getImageArray(imagePath)
	# print(list(list(imageArr)))

	print("\nGenerating list of files to process for word cloud generation.")
	JSONFilePaths =  generateListOfJSONFiles(folderPath)
	# print(JSONFilePaths, len(JSONFilePaths))

	print("Starting natural language processing.\n")
	wordFrequencyCounter = parseJSONFiles(JSONFilePaths, stopwordsSet)

	# TODO: evaluate - is sorting a dictionary even worth it? Maybe not? More efficient ways?
	sortedWordFrequencyCounter = sortFrequencyCount(wordFrequencyCounter, wordFrequencyCounter)

	exportDataToFile(sortedWordFrequencyCounter, "output.json")

	conversationStats = generateStatistics(sortedWordFrequencyCounter)
	print("The number of unique words you have used in this conversation are:", conversationStats["numUniqueWords"])
	print("The top 3 most used words in this conversation are:\n" + formatTopMostUsedWords(conversationStats["top3MostUsedWords"]))

	generateWordClouds(sortedWordFrequencyCounter, imageArr)
	print("\nTa-da! The wordclouds are ready. Look in the directory for \"wordCloudsV#.png\" files.")

if __name__ == '__main__':
	main()