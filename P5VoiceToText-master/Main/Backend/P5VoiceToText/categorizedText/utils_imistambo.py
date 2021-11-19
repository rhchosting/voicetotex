# -*- coding: utf-8 -*-

"""A utility for inserting, updating and retrieving IMIST-AMBO keyword-category
   
Provides a class 'ImistAmbo' that helps in handling inserting, updating and 
retrieving keyword-category pais requests into the Imist_AMBO_template db.

Also, when a keyword-pair is added it is responsible for updating all the 
existing categorizedText.
"""

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer
from string import punctuation
from nltk.stem import WordNetLemmatizer
import re

from P5VoiceToText import db
from P5VoiceToText.models import Imist_ambo_template
from P5VoiceToText.categorizedText.utils_classifytext import ClassifyText

__author__ = "Shefali Anand"
__copyright__ = "Copyright 2020, P5VoiceToText"
__credits__ = ["Shefali Anand"]
__version__ = "1.0"
__maintainer__ = ["Shefali Anand"]
__email__ = "sanand22@asu.edu"
__status__ = "Production"

ps = PorterStemmer() 
wordnet_lemmatizer = WordNetLemmatizer()

class ImistAmbo:

	"""
	This is a class for helping in performing DB operations for 
	Imist_ambo_template db collection

	Attributes
	----------
	classifyText : ClassifyText
		object for ClassifyText class. It is used when a new keyword-category 
		pair is added and this object's functions needs to be called to update 
		all the categorizedText.
	"""

	def __init__(self):
		self.classifyText = ClassifyText()

	def insert_into_imist_ambo_inbulk(self):
		"""The function to add all the initial keyword-category pairs in the 
		Imist_ambo_template db collection. These keyword-category pairs are 
		collected from the Requirement Documents shared by the sponsor.

		The categories are fixed: IMIST-AMBO.
		I - Identification
		M - Mechanism
		I - Injury
		S - Signs
		T - Treatment
		O - Other
		However, as discussed with Sponsor, we have only considered IMIST and O
		as the categories.
		For each category, there are and will be various keywords. Using NLP, 
		we have stored the keywords as the root of word, by performing stemming
		and lemmatization.

		These keyword-category pairs provides a meta-data for categorization. 
		A sentence containing a word that matches with the keyword of one of 
		the keyword-category pairs, will be classified into the corresponding
		category.

		Parameters
		----------

		Returns
		-------

		"""
		map_keyword_category = [
			{"keyword": "age",
			 "category": "identification"},
			{"keyword": "year old",
			 "category": "identification"},
			{"keyword": "month old",
			 "category": "identification"},
			{"keyword": "male",
			 "category": "identification"},
			{"keyword": "femal",
			 "category": "identification"},
			{"keyword": "mca",
			 "category": "mechanism"},
			{"keyword": "rollov",
			 "category": "mechanism"},
			{"keyword": "eject",
			 "category": "mechanism"},
			{"keyword": "death other occupant",
			 "category": "mechanism"},
			{"keyword": "pedestrian",
			 "category": "mechanism"},
			{"keyword": "motorcyclist",
			 "category": "mechanism"},
			{"keyword": "cyclist",
			 "category": "mechanism"},
			 {"keyword": "motorcycl",
			 "category": "mechanism"},
			{"keyword": "cycl",
			 "category": "mechanism"},
			{"keyword": "fall",
			 "category": "mechanism"},
			{"keyword": "fell",
			 "category": "mechanism"},
			{"keyword": "burn",
			 "category": "mechanism"},
			{"keyword": "hit",
			 "category": "mechanism"},
			{"keyword": "explos",
			 "category": "mechanism"},
			{"keyword": "trap",
			 "category": "mechanism"},
			{"keyword": "time entrap",
			 "category": "mechanism"},
			{"keyword": "mba",
			 "category": "mechanism"},
			{"keyword": "extric",
			 "category": "mechanism"},
			{"keyword": "fatal",
			 "category": "mechanism"},
			{"keyword": "accid",
			 "category": "mechanism"},
			{"keyword": "penetr",
			 "category": "injury"},
			{"keyword": "blunt",
			 "category": "trauma"},
			{"keyword": "head",
			 "category": "injury"},
			{"keyword": "neck",
			 "category": "injury"},
			{"keyword": "chest",
			 "category": "injury"},
			{"keyword": "abdomen",
			 "category": "injury"},
			{"keyword": "abdomin",
			 "category": "injury"},
			{"keyword": "forehead",
			 "category": "injury"},
			{"keyword": "pelvi",
			 "category": "injury"},
			{"keyword": "axilla",
			 "category": "injury"},
			{"keyword": "groin",
			 "category": "injury"},
			{"keyword": "limb",
			 "category": "injury"},
			{"keyword": "amput",
			 "category": "injury"},
			{"keyword": "crush",
			 "category": "injury"},
			{"keyword": "spinal",
			 "category": "injury"},
			{"keyword": "tension pneumothorax",
			 "category": "injury"},
			{"keyword": "rigid abdomen",
			 "category": "injury"},
			{"keyword": "fractur",
			 "category": "injury"},
			{"keyword": "facial burn",
			 "category": "injury"},
			{"keyword": "disloc",
			 "category": "injury"},
			{"keyword": "eviscer",
			 "category": "injury"},
			{"keyword": "blast",
			 "category": "injury"},
			{"keyword": "pain",
			 "category": "injury"},
			{"keyword": "trauma",
			 "category": "injury"},    
			{"keyword": "pr",
			 "category": "signs"},
			{"keyword": "bp",
			 "category": "signs"},
			{"keyword": "gcs",
			 "category": "signs"},
			{"keyword": "evm",
			 "category": "signs"},
			{"keyword": "pupil size",
			 "category": "signs"},
			{"keyword": "reactiv",
			 "category": "signs"},
			{"keyword": "rr",
			 "category": "signs"},
			{"keyword": "t degree",
			 "category": "signs"},
			{"keyword": "spo",
			 "category": "signs"},
			{"keyword": "sob",
			 "category": "signs"},
			{"keyword": "sbp",
			 "category": "signs"},
			{"keyword": "cervic collar",
			 "category": "treatment"},
			{"keyword": "op airway",
			 "category": "treatment"},
			{"keyword": "np airway",
			 "category": "treatment"},
			{"keyword": "lma",
			 "category": "treatment"},
			{"keyword": "ett",
			 "category": "treatment"},
			{"keyword": "rsi",
			 "category": "treatment"},
			{"keyword": "ventil",
			 "category": "treatment"},
			{"keyword": "chest decompress",
			 "category": "treatment"},
			{"keyword": "iv access",
			 "category": "treatment"},
			{"keyword": "iv hartmann",
			 "category": "treatment"},
			{"keyword": "methoxyfluran",
			 "category": "treatment"},
			{"keyword": "maxolon",
			 "category": "treatment"},
			{"keyword": "morphin",
			 "category": "treatment"},
			{"keyword": "midazolam",
			 "category": "treatment"},
			{"keyword": "fentanyl",
			 "category": "treatment"},
			{"keyword": "suxamethonium",
			 "category": "treatment"},
			{"keyword": "pancuronium",
			 "category": "treatment"},
			{"keyword": "adrenalin",
			 "category": "treatment"},
			{"keyword": "intub",
			 "category": "treatment"},
			{"keyword": "haemost dressing",
			 "category": "treatment"},
			{"keyword": "toumiquet",
			 "category": "treatment"},
			{"keyword": "blood transfus",
			 "category": "treatment"},
			{"keyword": "neuromuscular block",
			 "category": "treatment"},
			{"keyword": "allergi",
			 "category": "other"},
			{"keyword": "mass casualti",
			 "category": "other"},
			{"keyword": "inter hospit transfer",
			 "category": "other"},
			{"keyword": "pregnanc",
			 "category": "other"},
			{"keyword": "pregnant",
			 "category": "other"},
			{"keyword": "co-morbid",
			 "category": "other"},
			{"keyword": "anticoagul therapi",
			 "category": "other"}
			]
		arr = [Imist_ambo_template(**data) for data in map_keyword_category]
		Imist_ambo_template.objects.insert(arr, load_bulk=True)


	def insert_into_imist_ambo(self, keyword, category):
		"""The function to insert one pair of keyword-category in 
		Imist_ambo_template DB Collection.

		Parameters
		----------
		keyword : str
			a word which will be stemmed and lemmatized to store its root word
			but if it's an acronym or abbreviation then it won't be stemmed or
			lemmatized
		category : str
			any of the IMIST or O category

		Returns
		-------
		int
		status telling if the keyword-category pair is stored

		"""	

		# if the keyword is not an abbreviation, we need to get its stemmed and
		# lemmatized root word. 
		alphabets= "([A-Za-z])"
		abbr_3letter = alphabets+"[.]"+alphabets+"[.]"+alphabets+"[.]"
		abbr_2letter = alphabets+"[.]"+alphabets+"[.]"

		keyword_arr = keyword.split(" ")
		keyword = ""
		for key in keyword_arr:
			if re.search(abbr_3letter, key):
				keyword += re.sub(abbr_3letter, "\\1\\2\\3", key) + " "
			elif re.search(abbr_2letter, key):
				keyword += re.sub(abbr_2letter, "\\1\\2", key) + " "
			else:	
				keyword += wordnet_lemmatizer.lemmatize(ps.stem(key)) + " "
		keyword = keyword.strip()

		# If keyword exits in DB
		# 	corresponding category is same as that given by user then exit.
		#	corresponding category not same then update the category in DB.
		# If it doesn't exist
		# 	new keyword-category pair is inserted in DB.
		imist_ambos = Imist_ambo_template.objects.filter(keyword=keyword)
		if len(imist_ambos)>0:
			imist_ambo = imist_ambos[0]
			if imist_ambo.category==category:
				return 2
			else:
				imist_ambo.category = category
				imist_ambo.save()
		else:
			imist_ambo = \
				Imist_ambo_template(keyword=keyword, category=category).save()

		# When the keyword-category pair is updated or new one is inserted, 
		# all the categorizedTexts in DB needs to be updated to reflect the 
		# change in IMIST-AMBO Glossary.
		self.classifyText.update_categorized_text_forall_records()
		return 1


	def getall_imist_ambo(self):
		"""The function to retrieve all the keyword-category pairs stored in 
		Imist_ambo_template db collection

		Parameters
		----------

		Returns
		-------
		list of Imist_ambo_template objects

		"""
		keyword_category_list = Imist_ambo_template.objects
		return keyword_category_list


	def get_imist_ambo(self, searchword):
		"""The function to retrieve all the keyword-category pairs stored in 
		Imist_ambo_template db collection, filtered by category or keyword

		Parameters
		----------

		Returns
		-------
		list of Imist_ambo_template objects

		"""
		keyword_category_list = \
			Imist_ambo_template.objects.filter(category=searchword)
		if len(keyword_category_list)>0:
			return keyword_category_list
		
		searchword = wordnet_lemmatizer.lemmatize(ps.stem(searchword))
		keyword_category_list = \
			Imist_ambo_template.objects.filter(keyword=searchword)
		if len(keyword_category_list)>0:
			return keyword_category_list
		return []