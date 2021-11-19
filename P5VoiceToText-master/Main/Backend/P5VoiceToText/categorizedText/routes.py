# -*- coding: utf-8 -*-

"""This file contains all the APIs for categorizedText and imistambo_glossary

For every voice file, voice-to-text conversion takes place which gives us 
convertedText. The sentences of every convertedText, needs to be classified 
into imist-ambo categories. The classification results are called 
categorizedTexts. This file provides POST, PUT and GET request APIs for 
categorizedTexts.

The classification into IMIST-AMBO categories depends on IMIST-AMBO Glossary
which is saved into the database as Imist_ambo_template. This Glossary contains
keyword-category pairs. If a word in a sentence, matches with a keyword in 
Imist_ambo_template, then that sentence will belong to the corresponding 
category of the keyword-category pair. This file provides, POST and GET request
APIs for IMIST-AMBO Glossary.
"""

from flask import request, flash, jsonify, Blueprint

from P5VoiceToText.config import Config
from P5VoiceToText.categorizedText.utils_classifytext import ClassifyText
from P5VoiceToText.categorizedText.utils_imistambo import ImistAmbo


__author__ = "Shefali Anand"
__copyright__ = "Copyright 2020, P5VoiceToText"
__credits__ = ["Shefali Anand", "Surya Cherukuri"]
__version__ = "1.0"
__maintainer__ = ["Shefali Anand"]
__email__ = "sanand22@asu.edu"
__status__ = "Production"


categorizedText = Blueprint('categorizedText', __name__)


@categorizedText.route('/api/categorizedText/<filename>', methods = ['POST'])
def textCategorization(filename):
	"""This is a POST API request for categorizedText. It takes the filename
	of the voice file, performs categorization and save the categorizedText 
	result for that voice file in the Text_categorization db collection.

	Parameters
	----------
	filename : str
		name of the voice file for which categorization needs to be done

	Returns
	-------
	JSON object 
		Error Message or reults of convertedText
	"""
	try:
		classifyText = ClassifyText()
		if not classifyText.if_voice_file_exists(filename):
			message = {
				"message": "File not found in our records"
			}
			return jsonify(message), 404
		if not classifyText.if_converted_text_exists(filename):
			message = {
				"message": "Converted Text not found in our records"
			}
			return jsonify(message), 404

		if classifyText.if_categorized_text_exists(filename):
			print("Categorized Text already exists")
			text = classifyText.get_categorizedText_from_db(filename)
			return jsonify(text), 200

		text = classifyText.clean_and_classify()
		classifyText.save_categorizedText_in_db()
		return jsonify(text), 201
	except:
		message = {
			"message": "Internal Server Error, something went wrong"
		}
		return jsonify(message), 500



@categorizedText.route('/api/categorizedText/<filename>', methods = ['GET'])
def get_categorizedText(filename):
	"""This is a GET API request for categorizedText. It takes the filename
	of the voice file, and retrieves the categorizedText result for that 
	voice file in the Text_categorization db collection.

	Parameters
	----------
	filename : str
		name of the voice file for which categorizedText results have to be 
		obtained

	Returns
	-------
	JSON object 
		Error Message or reults of convertedText
	"""
	try:
		classifyText = ClassifyText()
		if not classifyText.if_voice_file_exists(filename):
			message = {
				"message": "File not found in our records"
			}
			return jsonify(message), 404
		if not classifyText.if_categorized_text_exists(filename):
			message = {
				"message": "Categorized Text not found in our records"
			}
			return jsonify(message), 404
		text = classifyText.get_categorizedText_from_db(filename)
		return jsonify(text), 200
	except:
		message = {
			"message": "Internal Server Error, something went wrong"
		}
		return jsonify(message), 500



@categorizedText.route('/api/categorizedText/<filename>', methods = ['PUT'])
def update_categorizedText(filename):
	"""This is a PUT API request for categorizedText. It takes the filename
	of the voice file, and updates the categorizedText result for that 
	voice file in the Text_categorization db collection. The categorizedText is
	updated when the convertedText is edited by the user.

	Parameters
	----------
	filename : str
		name of the voice file for which categorizedText results have to be 
		updated

	Returns
	-------
	JSON object 
		Error Message or reults of convertedText
	"""
	try:
		classifyText = ClassifyText()
		if not classifyText.if_voice_file_exists(filename):
			message = {
				"message": "File not found in our records"
			}
			return jsonify(message), 404
		if not classifyText.if_converted_text_exists(filename):
			message = {
					"message": "Converted Text not found in our records"
				}
			return jsonify(message), 404
		if not classifyText.if_categorized_text_exists(filename):
			message = {
				"message": "Categorized Text not found in our records"
				}
			return jsonify(message), 404

		text = classifyText.clean_and_classify()
		classifyText.update_categorizedText_in_db()
		return jsonify(text), 200
	except:
		message = {
			"message": "Internal Server Error, something went wrong"
		}
		return jsonify(message), 500



@categorizedText.route('/api/imistambo_glossary_inbulk', methods = ['POST'])
def add_imistambo_glossary_inbulk():
	"""This is a POST API request for imistambo_glossary. It inserts all the 
	initial keyword-category pairs in the imist_ambo_template db collection.

	Parameters
	----------

	Returns
	-------
	JSON object 
		Error Message or Success Message
	"""
	try:
		imistAmbo = ImistAmbo()
		imistAmbo.insert_into_imist_ambo_inbulk()
		message = {
			"message": "Successfully added"
		}
		return jsonify(message), 201
	except:
		message = {
			"message": "Internal Server Error, something went wrong"
		}
		return jsonify(message), 500


@categorizedText.route('/api/imistambo_glossary', methods = ['POST'])
def add_imistambo_glossary():
	"""This is a POST API request for imistambo_glossary. It inserts a new 
	keyword-category pair or update the older pair in the Imist_ambo_template
	db collection.

	Parameters
	----------

	Returns
	-------
	JSON object 
		Error Message or Success Message
	"""
	try:
		keyword = request.json['keyword']
		category = request.json['category']
		imistAmbo = ImistAmbo()
		result = imistAmbo.insert_into_imist_ambo(keyword, category)
		if result == 2:
			message = {
				"message": "Keyword-Category Pair already exists"
			}
			return jsonify(message), 200
		else:
			message = {
				"message": "Keyword-Category Pair added and all the CategorizedTexts are updated"
			}
			return jsonify(message), 201
	except:
		message = {
			"message": "Internal Server Error, something went wrong"
		}
		return jsonify(message), 500



@categorizedText.route('/api/imistambo_glossary', methods = ['GET'])
def getall_imistambo_glossary():
	"""This is a GET API request for imistambo_glossary to get all the 
	keyword-category pairs of the Imist_ambo_template db collection.

	Parameters
	----------

	Returns
	-------
	JSON object 
		Error Message or List of keyword-category pairs of IMISTAMBO glossary
	"""
	try:
		imistAmbo = ImistAmbo()
		keyword_category_list = imistAmbo.getall_imist_ambo()
		return jsonify(keyword_category_list), 200
	except:
		message = {
			"message": "Internal Server Error, something went wrong"
		}
		return jsonify(message), 500



@categorizedText.route('/api/imistambo_glossary/<searchword>', \
methods = ['GET'])
def get_imistambo_glossary(searchword):
	"""This is a GET API request for imistambo_glossary to get a list of the 
	keyword-category pairs, filtered by keyword or category, of the 
	Imist_ambo_template db collection.

	Parameters
	----------
	searchword : str
		use this to get filtered list of keyword-category pairs of IMISTAMBO
		glossary.

	Returns
	-------
	JSON object 
		Error Message or List of keyword-category pairs of IMISTAMBO glossary
	"""
	try:
		imistAmbo = ImistAmbo()
		keyword_category_list = imistAmbo.get_imist_ambo(searchword)
		return jsonify(keyword_category_list), 200
	except:
		message = {
			"message": "Internal Server Error, something went wrong"
		}
		return jsonify(message), 500