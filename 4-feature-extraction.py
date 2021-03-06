from colors import bcolors
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import unicode as unicode
import json
import os
import csv
import datetime
import re

companies = [
	"maybank",
	"axiata",
	"cimb",
	"petronas",
	"sime darby"
]

directories = [
	"data/labelled/positive",
	"data/labelled/negative",
	"data/labelled/neutral"
]

def format_date_to_historical(date_value):
	dt = datetime.datetime.strptime(date_value, '%d/%m/%Y')
	return datetime.date.strftime(dt, "%Y-%m-%d")

def remove_stopword(text):
	ps = PorterStemmer()
	stop_words = set(stopwords.words('english'))
	words = word_tokenize(text)

	new_text = ''
	for word in words:
		if not word in stop_words:
			new_text = new_text + word + " "

	return new_text

def word_stemming(text):
	ps = PorterStemmer()
	words = word_tokenize(text)

	new_text = ''
	for word in words:
		new_text = new_text + ps.stem(word) + " "

	return new_text

def remove_unicode(text):
	for symbol in unicode.get_unicode_list():
		text = re.sub(symbol, '', text).replace('\\', '')

	return text

def remove_punctuation(text):
	punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
	no_punct = ""
	for char in text:
		if char not in punctuations:
			no_punct = no_punct + char
	return no_punct

def print_summary():
	print('')
	print(bcolors.BOLD + '------- SUMMARY -------')
	for company in companies:
		print(bcolors.OKGREEN + company.upper() + bcolors.ENDC)
		filename = company.replace(" ", "-") + "-data.json"
		for directory in directories:
			with open(directory + '/' + filename) as json_file:
				data = json.load(json_file)
				data_type = directory.replace('data/labelled/', '').upper()
				print(data_type + ' : ' + str(len(data)))

		print('')
	print(bcolors.BOLD + '-----------------------' + bcolors.ENDC)

for company in companies:
	filename = company.replace(" ", "-") + "-data.json"
	historical_filename = company.replace(" ", "-") + "-historical-prices.csv"
	with open('data/cleaned/' + filename) as json_file:
		data = json.load(json_file)

		# create directory
		for directory in directories:
			if not os.path.exists(directory):
				print(directory)
				os.makedirs(directory)

		# create file
		positive_data_file = open("data/labelled/positive/" + filename, "w", encoding="utf-8")
		negative_data_file = open("data/labelled/negative/" + filename, "w", encoding="utf-8")
		neutral_data_file = open("data/labelled/neutral/" + filename, "w", encoding="utf-8")

		# create neutral, positive, negative dict
		positive_dict = {}
		negative_dict = {}
		neutral_dict = {}
		positive_index = 0
		negative_index = 0
		neutral_index = 0

		# loop for key and value for json file
		for key_json, value_json in data.items():
			print(company.upper() + " : " + format_date_to_historical(value_json['date_posted']) + ' - ' + value_json['title'])
			
			# open historical
			# 0 - Date, 1 - Open, 2 - High, 3 - Low, 4- Close, 5- Adj Close, 6 - Volume, 7 - y
			historical_file = open('historical-prices/calculated/' + historical_filename)
			historical_data_list = csv.reader(historical_file, delimiter=',')

			for historical_data in historical_data_list:
				if (format_date_to_historical(value_json['date_posted']) == historical_data[0]):
					y = float(historical_data[7])
					value_json['title'] = value_json['title'].lower()
					value_json['article'] = value_json['article'].lower()

					value_json['title'] = remove_unicode(value_json['title'])
					value_json['article'] = remove_unicode(value_json['article'])
					value_json['title'] = word_stemming(value_json['title'])
					value_json['article'] = word_stemming(value_json['article'])
					value_json['title'] = remove_stopword(value_json['title'])
					value_json['article'] = remove_stopword(value_json['article'])
					value_json['title'] = remove_punctuation(value_json['title'])
					value_json['article'] = remove_punctuation(value_json['article'])

					if (y == float(0)):
						status = bcolors.OKBLUE + 'NEUTRAL' + bcolors.ENDC
						neutral_dict[neutral_index] = value_json
						neutral_index += 1
					elif (y > float(0)):
						status = bcolors.OKGREEN + 'POSITIVE' + bcolors.ENDC
						positive_dict[positive_index] = value_json
						positive_index += 1
					else:
						status = bcolors.WARNING + 'NEGATIVE' + bcolors.ENDC
						negative_dict[negative_index] = value_json
						negative_index += 1
					break
				else:
					status = bcolors.FAIL + 'NOT FOUND' + bcolors.ENDC

			historical_file.close()
			print(status)

		# write to positive file
		data_to_write = json.dumps(positive_dict)
		positive_data_file.write(data_to_write)
		positive_data_file.close()

		# write to negative file
		data_to_write = json.dumps(negative_dict)
		negative_data_file.write(data_to_write)
		negative_data_file.close()

		# write to neutral file
		data_to_write = json.dumps(neutral_dict)
		neutral_data_file.write(data_to_write)
		neutral_data_file.close()

print_summary()