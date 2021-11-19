# -*- coding: utf-8 -*-

"""A utility for performing Classification of Text into IMIST-AMBO categories
   
Provides a class 'ClassifyText' that is responsible for classifying the text,
obtained from Voice-to-text conversion of audio recodings (uploaded by users)
The sentences from the text are classified into IMIST-AMBO categories, on the
basis of the Imist_ambo_template, which is a database collection. This
collection stores keyword-category pairs. If a word in a sentence, matches 
with a keyword in Imist_ambo_template, then that sentence will belong to 
the corresponding category of the keyword-category pair. 

To fetch the words from sentences, Natural Language Processing (NLP) is done
for cleaning and filtering.

It saves and updates the categorizedText in db and is also responsible in 
retrieving the categorizedText from db
"""

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer
from string import punctuation
from nltk.stem import WordNetLemmatizer
import re

from P5VoiceToText import db
from P5VoiceToText.models import Imist_ambo_template, Voice_files
from P5VoiceToText.models import Voice_text_conversion, Text_categorization

__author__ = "Shefali Anand"
__copyright__ = "Copyright 2020, P5VoiceToText"
__credits__ = ["Shefali Anand", "Surya Cherukuri"]
__version__ = "1.0"
__maintainer__ = ["Shefali Anand"]
__email__ = "sanand22@asu.edu"
__status__ = "Production"

ps = PorterStemmer() 
wordnet_lemmatizer = WordNetLemmatizer()


class ClassifyText:

	"""
	This is a class for classifying sentences into IMIST-AMBO categories.

	Attributes
	----------
	voice_file : Voice_files
		DB collection object
	text : str
		will store text(called convertedText) from voice-to-text conversion 
		of the voice file
	sentences : list of str
		will store list of cleaned and filtered words 
	category_keyword : dictionary
		dictionary with key as category and value as a list of sentences
	"""

	def __init__(self):
		self.voice_file = None
		self.text = ""
		self.sentences = []
		self.category_keyword = { "identification" : [],
								  "mechanism" : [],
								  "injury": [],
								  "signs": [],
								  "treatment": [],
								  "allergy": [],
								  "medication": [],
								  "background": [],
								  "other": [] }


	def if_voice_file_exists(self, filename):
		"""The function to check if the given voice file exists in DB

		Parameters
		----------
		filename : str
			name of the voice file

		Returns
		-------
		bool 
			returns true if the file exists, otherwise false
		"""
		self.voice_file = Voice_files.objects.filter(filename=filename)
		return len(self.voice_file) > 0


	def if_converted_text_exists(self, filename):
		"""The function to check if the text(called convertedText) from 
		voice-to-text conversion of the voice file, exists in 
		Voice_text_conversion db collection.

		Parameters
		-----------
		filename : str 
			name of the voice file

		Returns
		-------
		bool 
			returns true if the text exists, otherwise false
		"""
		self.voice_file = Voice_files.objects.filter(filename=filename)[0]
		voice_text_conversion = Voice_text_conversion.objects\
								.filter(voiceFile=self.voice_file)
		if len(voice_text_conversion)>0:
			self.text = voice_text_conversion[0].converted_text
		return len(voice_text_conversion) > 0


	def if_categorized_text_exists(self, filename):
		"""The function to check if the text(called categorizedText) from 
		categorization of convertedText of the voice file, exists in 
		Text_categorization db collection.

		Parameters
		----------
		filename : str
			name of the voice file

		Returns
		-------
		bool 
			returns true if the text exists, otherwise false
		"""
		self.voice_file = Voice_files.objects.filter(filename=filename)[0]
		text_categorization = Text_categorization.objects\
											.filter(voiceFile=self.voice_file)
		return len(text_categorization) > 0 


	def split_into_sentences(self):
		"""Splits the convertedText into separate sentences

		It splits the convertedText into sentences by "." (period). However, 
		the text might also include decimals and abbreviations which includes 
		"." (periods). Hence, the text is split into sentences, taking decimals
		and abbreviations into consideration.

		Returns
		-------
		list of string
			returns a list of all sentences belonging to convertedText
		"""
		text = self.text

		#Split not by decimals e.g 3.14
		digits = "([0-9])"
		text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2", text)
		
		#Split not by abbreviations
		alphabets= "([A-Za-z])"
		#e.g: G.C.S.
		text = re.sub(" " + alphabets + "[.]" + alphabets + "[.]" + alphabets \
	 		+ "[.] "," \\1<abbr>\\2<abbr>\\3<abbr> ",text)
	  	#e.g: G.C.S
		text = re.sub(" " + alphabets + "[.]" + alphabets + "[.]" + alphabets \
	 		+ " "," \\1<abbr>\\2<abbr>\\3<abbr> ",text)
	  	#e.g: G. C. S
		text = re.sub(" " + alphabets + "[.] " + alphabets + "[.] " + alphabets \
	 		+ " " ," \\1<abbr>\\2<abbr>\\3<abbr> ",text)
	  	#e.g: G. C. S.
		text = re.sub(" " + alphabets + "[.] " + alphabets + "[.] " + alphabets \
	 		+ "[.] "," \\1<abbr>\\2<abbr>\\3<abbr> ",text)
	  	#e.g: G C S
		text = re.sub(" " + alphabets + " " + alphabets + " " + alphabets \
	 		+ " "," \\1<abbr>\\2<abbr>\\3<abbr> ",text)
	    #e.g: R.R.
		text = re.sub(" "+alphabets + "[.]" + alphabets + "[.] ",\
			" \\1<abbr>\\2<abbr> ",text)
	  	#e.g: R.R
		text = re.sub(" "+alphabets + "[.]" + alphabets + " ",\
			" \\1<abbr>\\2<abbr> ",text)
	  	#e.g: R. R
		text = re.sub(" " +alphabets + "[.] " + alphabets +" " ,\
			" \\1<abbr>\\2<abbr> ",text)
	  	#e.g: R. R.
		text = re.sub(" " + alphabets + "[.] " + alphabets + "[.] ",\
			" \\1<abbr>\\2<abbr> ",text)
	  	#e.g: R R
		text = re.sub(" " + alphabets + " " + alphabets + " " ,\
			"  \\1<abbr>\\2<abbr> ",text)

		if "”" in text: text = text.replace(".”","”.")
		if "\"" in text: text = text.replace(".\"","\".")
		if "!" in text: text = text.replace("!\"","\"!")
		text = text.replace(".",".<stop>")
		text = text.replace("!","!<stop>")
		text = text.replace("<prd>",".")
		text = text.replace("<abbr>",".")
		sentences = text.split("<stop>")
		sentences = sentences[:-1]
		sentences = [s.strip() for s in sentences]
		return sentences


	def remove_stopwords(self, sentence):
		"""The function to filter the sentence by removing stopwords 
		(e.g. punctuations, articles)

		Parameters
		----------
		sentence : str
			a sentence from which stopwords are to be removed

		Returns
		-------
		list of string: 
			filtered sentence of the given sentence

		"""
		sentence = sentence.lower()
		stop_words = set(stopwords.words('english') + list(punctuation)) 		
		word_tokens = word_tokenize(sentence) 
		filtered_sentence = [w for w in word_tokens if not w in stop_words] 
		filtered_sentence = [] 
		for w in word_tokens: 
			if w not in stop_words: 
				filtered_sentence.append(w) 

		return filtered_sentence 


	def stemming_and_lemmatization_text(self, words):
		"""The function to get root of words using Stemming and Lemmatization
		It avoids abbreviations.

		Parameters
		----------
		words : list of str 
			list of words to be stemmed and lemmatized

		Returns
		-------
		list of str
			list of root of the given words.
		"""
		alphabets= "([A-Za-z])"
		abbr_3letter = alphabets+"[.]"+alphabets+"[.]"+alphabets
		abbr_2letter = alphabets+"[.]"+alphabets
		res_words = []
		for word in words:
			if re.search(abbr_3letter, word):
				word = re.sub(abbr_3letter, "\\1\\2\\3", word)
			elif re.search(abbr_2letter, word):
				word = re.sub(abbr_2letter, "\\1\\2", word)
			else:
				word = wordnet_lemmatizer.lemmatize(ps.stem(word))
			res_words.append(word)
		return res_words
		

	def clean_text(self, sentence):
		"""The function to clean and filter a sentence.

		Parameters
		----------
		sentence : str 
			a sentence to be cleaned and filtered.

		Returns
		-------
		list of string
			cleaned and filtered list of words of the given sentence 
		"""
		words = self.remove_stopwords(sentence)
		words = self.stemming_and_lemmatization_text(words)
		return words


	def classify_text_into_categories(self, sentence, words):
		"""The function to classify the given sentence into imist-ambo 
		categories, by checking if any word of the sentence matches with any 
		keyword of the keyword-category pairs of imist_ambo_template db 
		collection. 

		If a sentence has multiple words that gets matched to the keywords, 
		then the same sentence will be classified into the corresponding 
		categories of the keyword-category pairs of imist_ambo_template db 
		collection. Hence, one sentence can be classified into more than one 
		IMIST-AMBO categories. 

		Parameters
		----------
		sentence : str 
			sentence to be classified into IMIST-AMBO
		words : list of str 
			words of the sentence, to be matched with keywords of 
			imist_ambo_template.

		Returns
		-------
		category_keyword 
			updated class variable, a dictionary which adds the 
			given sentence as value to the corresponding key (category)

		"""
		is_category_assigned = False
		
		# Every word of the sentence is matched. There are cases when there are
		# keywords with two words (bigram) or three words (trigram). Hence 
		# unigram, bigrams and trigrams are matched. 
		for i in range(0, len(words)):
			#unigrams
			imist_ambos = Imist_ambo_template.objects.filter(keyword=words[i])
			if len(imist_ambos) and (sentence not in \
					self.category_keyword[imist_ambos[0].category]):
				self.category_keyword[imist_ambos[0].category].append(sentence)
				is_category_assigned = True

			#bigrams
			if i<(len(words)-1):
				search_keyword = words[i]+" "+words[i+1]
				imist_ambos = Imist_ambo_template.objects\
						.filter(keyword=search_keyword)
				if len(imist_ambos) and (sentence not in \
						self.category_keyword[imist_ambos[0].category]):
					self.category_keyword[imist_ambos[0].category]\
						.append(sentence)
					is_category_assigned = True

			#trigrams		
			if i<(len(words)-2):
				search_keyword = words[i]+" "+words[i+1]+" "+words[i+2]
				imist_ambos = Imist_ambo_template.objects\
				.filter(keyword=search_keyword)				
				if len(imist_ambos) and (sentence not in \
						self.category_keyword[imist_ambos[0].category]):
					self.category_keyword[imist_ambos[0].category]\
						.append(sentence)
					is_category_assigned = True

		# If a sentence has no word that could be matched to any keyword, it 
		# will be classified into 'Other' category.
		if is_category_assigned==False and len(words)>2:
			self.category_keyword['other'].append(sentence)



	def clean_and_classify(self):
		"""This function will first call split_into_sentences() to split the 
		convertedTet into sentences, then clean_text() function to filter the 
		sentences of convertedText and then call classify_text_into_categories()
		function to classify the sentences of convertedText into IMIST-AMBO 
		categories.

		Parameters
		----------

		Returns
		-------
		category_keyword 
			updated class variable, a dictionary which adds the 
			given sentence as value to the corresponding key (category)

		"""
		self.sentences = self.split_into_sentences()

		for sentence in self.sentences:
			words = self.clean_text(sentence)
			self.classify_text_into_categories(sentence, words)
		return self.category_keyword


	def save_categorizedText_in_db(self):
		"""The function to save dictionary category_keyword as categorizedText 
		into Text_categorization db collection for the current voice_file.

		Parameters
		----------

		Returns
		-------
		
		"""
		text_categorization = Text_categorization(voiceFile=self.voice_file)
		text_categorization.identification = \
			self.category_keyword['identification']
		text_categorization.mechanism = self.category_keyword['mechanism']
		text_categorization.injury = self.category_keyword['injury']
		text_categorization.signs = self.category_keyword['signs']
		text_categorization.treatment = self.category_keyword['treatment']
		text_categorization.allergy = self.category_keyword['allergy']
		text_categorization.medication = self.category_keyword['medication']
		text_categorization.background = self.category_keyword['background']
		text_categorization.other = self.category_keyword['other']
		text_categorization.save()


	def update_categorizedText_in_db(self):
		"""The function to update Text_categorization db collection with the 
		updated value of category_keyword dictionary for the current voice file.

		Parameters
		----------

		Returns
		-------

		"""
		text_categorization = \
			Text_categorization.objects.filter(voiceFile=self.voice_file)[0]
		text_categorization.identification = \
			self.category_keyword['identification']
		text_categorization.mechanism = self.category_keyword['mechanism']
		text_categorization.injury = self.category_keyword['injury']
		text_categorization.signs = self.category_keyword['signs']
		text_categorization.treatment = self.category_keyword['treatment']
		text_categorization.allergy = self.category_keyword['allergy']
		text_categorization.medication = self.category_keyword['medication']
		text_categorization.background = self.category_keyword['background']
		text_categorization.other = self.category_keyword['other']
		text_categorization.save()


	def get_categorizedText_from_db(self, filename):
		"""The function to retrieve categorizedText of the given voice_file 
		from Text_categorization db collection.

		Parameters
		----------
		filename : str
			name of the voice file

		Returns
		-------
		category_keyword 
			updated class variable, a dictionary which adds the 
			given sentence as value to the corresponding key (category)

		"""

		self.voice_file = Voice_files.objects.filter(filename=filename)[0]
		text_categorization = \
			Text_categorization.objects.filter(voiceFile=self.voice_file)[0]
		self.category_keyword['identification'] = \
			text_categorization.identification
		self.category_keyword['mechanism'] = text_categorization.mechanism
		self.category_keyword['injury'] = text_categorization.injury
		self.category_keyword['signs'] = text_categorization.signs
		self.category_keyword['treatment'] = text_categorization.treatment
		self.category_keyword['allergy'] = text_categorization.allergy
		self.category_keyword['medication'] = text_categorization.medication
		self.category_keyword['background'] = text_categorization.background
		self.category_keyword['other'] = text_categorization.other
		return self.category_keyword


	def update_categorized_text_forall_records(self):
		"""This function will be called whenever Imist_ambo_template DB 
		collection is updated by inserting or deleting or updating any 
		keyword-category pair.

		The categorizedText for all the voice_files needs to be updated to 
		employ the changes made in Imist_ambo_template

		This function will iterate over all the documents of 
		Text_categorization db collection and update them according to the 
		changed Imist_ambo_template db collection. 

		Parameters
		----------

		Returns
		-------

		"""
		categorized_texts = Text_categorization.objects
		for categorized_text in categorized_texts:
			self.voice_file = None
			self.text = ""
			self.sentences = []
			self.category_keyword = { "identification" : [],
								  "mechanism" : [],
								  "injury": [],
								  "signs": [],
								  "treatment": [],
								  "allergy": [],
								  "medication": [],
								  "background": [],
								  "other": [] }
			self.voice_file = categorized_text.voiceFile
			self.category_keyword
			self.text = Voice_text_conversion.objects\
				.filter(voiceFile=self.voice_file)[0].converted_text
			self.clean_and_classify()
			self.update_categorizedText_in_db()