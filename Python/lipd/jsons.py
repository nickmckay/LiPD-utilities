from .misc import rm_empty_fields, get_appended_name
from .loggers import create_logger
from .regexes import re_ensemble_collapse

import json
import demjson
from collections import OrderedDict
import os
import re

logger_jsons = create_logger("jsons")


# IMPORT

def read_jsonld():
	"""
	Find jsonld file in the cwd (or within a 2 levels below cwd), and load it in.
	:return dict: Jsonld data
	"""
	_d = {}

	try:
		# Find a jsonld file in cwd. If none, fallback for a json file. If neither found, return empty.
		_filename = [file for file in os.listdir() if file.endswith(".jsonld")][0]
		if not _filename:
			_filename = [file for file in os.listdir() if file.endswith(".json")][0]

		if _filename:
			try:
				# Load and decode
				_d = demjson.decode_file(_filename, decode_float=float)
				logger_jsons.info("Read JSONLD successful: {}".format(_filename))
			except FileNotFoundError as fnf:
				print("Error: metadata file not found: {}".format(_filename))
				logger_jsons.error("read_jsonld: FileNotFound: {}, {}".format(_filename, fnf))
			except Exception:
				try:
					_d = demjson.decode_file(_filename, decode_float=float, encoding="latin-1")
					logger_jsons.info("Read JSONLD successful: {}".format(_filename))
				except Exception as e:
					print("Error: unable to read metadata file: {}".format(e))
					logger_jsons.error("read_jsonld: Exception: {}, {}".format(_filename, e))
		else:
			print("Error: metadata file (.jsonld) not found in LiPD archive")
	except Exception as e:
		print("Error: Unable to find jsonld file in LiPD archive. This may be a corrupt file.")
		logger_jsons.error("Error: Unable to find jsonld file in LiPD archive. This may be a corrupt file.")
	logger_jsons.info("exit read_json_from_file")
	return _d


def read_json_from_file(filename):
	"""
	Import the JSON data from target file.
	:param str filename: Target File
	:return dict: JSON data
	"""
	logger_jsons.info("enter read_json_from_file")
	d = OrderedDict()
	try:
		# Load and decode
		d = demjson.decode_file(filename, decode_float=float)
		logger_jsons.info("successful read from json file")
	except FileNotFoundError:
		# Didn't find a jsonld file. Maybe it's a json file instead?
		try:
			d = demjson.decode_file(os.path.splitext(filename)[0] + '.json', decode_float=float)
		except FileNotFoundError as e:
			# No json or jsonld file. Exit
			print("Error: jsonld file not found: {}".format(filename))
			logger_jsons.debug("read_json_from_file: FileNotFound: {}, {}".format(filename, e))
		except Exception:
			print("Error: unable to read jsonld file")

	if d:
		d = rm_empty_fields(d)
	logger_jsons.info("exit read_json_from_file")
	return d


def idx_num_to_name(L):
	"""
	Switch from index-by-number to index-by-name.

	:param dict L: Metadata
	:return dict L: Metadata
	"""
	logger_jsons.info("enter idx_num_to_name")

	try:
		if "paleoData" in L:
			L["paleoData"] = _import_data(L["paleoData"], "paleo")
		if "chronData" in L:
			L["chronData"] = _import_data(L["chronData"], "chron")
	except Exception as e:
		logger_jsons.error("idx_num_to_name: {}".format(e))
		print("Error: idx_name_to_num: {}".format(e))

	logger_jsons.info("exit idx_num_to_name")
	return L


def _import_data(sections, crumbs):
	"""
	Import the section metadata and change it to index-by-name.

	:param list sections: Metadata
	:param str pc: paleo or chron
	:return dict _sections: Metadata
	"""
	logger_jsons.info("enter import_data: {}".format(crumbs))
	_sections = OrderedDict()
	try:
		for _idx, section in enumerate(sections):
			_tmp = OrderedDict()

			# Process the paleo measurement table
			if "measurementTable" in section:
				_tmp["measurementTable"] = _idx_table_by_name(section["measurementTable"], "{}{}{}".format(crumbs, _idx, "measurement"))

			# Process the paleo model
			if "model" in section:
				_tmp["model"] = _import_model(section["model"], "{}{}{}".format(crumbs, _idx, "model"))

			# Get the table name from the first measurement table, and use that as the index name for this table
			_table_name = "{}{}".format(crumbs, _idx)

			# If we only have generic table names, and one exists already, don't overwrite. Create dynamic name
			if _table_name in _sections:
				_table_name = "{}_{}".format(_table_name, _idx)

			# Put the final product into the output dictionary. Indexed by name
			_sections[_table_name] = _tmp

	except Exception as e:
		logger_jsons.error("import_data: Exception: {}".format(e))
		print("Error: import_data: {}".format(e))

	logger_jsons.info("exit import_data: {}".format(crumbs))
	return _sections


def _import_model(models, crumbs):
	"""
	Change the nested items of the paleoModel data. Overwrite the data in-place.

	:param list models: Metadata
	:param str crumbs: Crumbs
	:return dict _models: Metadata
	"""
	logger_jsons.info("enter import_model".format(crumbs))
	_models = OrderedDict()
	try:
		for _idx, model in enumerate(models):
			# Keep the original dictionary, but replace the three main entries below

			# Do a direct replacement of chronModelTable columns. No table name, no table work needed.
			if "summaryTable" in model:
				model["summaryTable"] = _idx_table_by_name(model["summaryTable"], "{}{}{}".format(crumbs, _idx, "summary"))
			# Do a direct replacement of ensembleTable columns. No table name, no table work needed.
			if "ensembleTable" in model:
				model["ensembleTable"] = _idx_table_by_name(model["ensembleTable"], "{}{}{}".format(crumbs, _idx, "ensemble"))
			if "distributionTable" in model:
				model["distributionTable"] = _idx_table_by_name(model["distributionTable"], "{}{}{}".format(crumbs, _idx, "distribution"))

			_table_name = "{}{}".format(crumbs, _idx)
			_models[_table_name] = model
	except Exception as e:
		logger_jsons.error("import_model: {}".format(e))
		print("Error: import_model: {}".format(e))
	logger_jsons.info("exit import_model: {}".format(crumbs))
	return _models


def _idx_table_by_name(tables, crumbs):
	"""
	Import summary, ensemble, or distribution data.

	:param list tables: Metadata
	:return dict _tables: Metadata
	"""
	_tables = OrderedDict()
	try:
		for _idx, _table in enumerate(tables):
			# Use "name" as tableName
			_name = "{}{}".format(crumbs, _idx)
			# Call idx_table_by_name
			_tmp = _idx_col_by_name(_table)
			if _name in _tables:
				_name = "{}_{}".format(_name, _idx)
			_tmp["tableName"] = _name
			_tables[_name] = _tmp
	except Exception as e:
		logger_jsons.error("idx_table_by_name: {}".format(e))
		print("Error: idx_table_by_name: {}".format(e))

	return _tables


def _idx_col_by_name(table):
	"""
	Iter over columns list. Turn indexed-by-num list into an indexed-by-name dict. Keys are the variable names.

	:param dict table: Metadata
	:return dict _table: Metadata
	"""
	_columns = OrderedDict()
	_prev_num = 0

	# Iter for each column in the list
	try:
		for _column in table["columns"]:
			try:
				_name = _column["variableName"]
				# Ensemble table, expand columns
				if isinstance(_column["number"], list):
					_column["isEnsemble"] = True
					_column["ensembleName"] = _name
					for num in _column["number"]:
						_copy_col = dict(_column)
						_copy_col["number"] = num
						_name = "{}-{}-ens".format(_column["variableName"], num)
						_copy_col["variableName"] = _name
						_prev_num = num
						_columns[_name] = _copy_col
				else:
					if _name in _columns:
						_name = get_appended_name(_name, _columns)
					_prev_num = _column["number"]
					_columns[_name] = _column
			except Exception as e:
				print("Error: idx_col_by_name: inner: {}".format(e))
				logger_jsons.info("idx_col_by_name: inner: {}".format(e))

		table["columns"] = _columns
	except Exception as e:
		print("Error: idx_col_by_name: {}".format(e))
		logger_jsons.error("idx_col_by_name: {}".format(e))

	return table


# PREP FOR EXPORT


def get_csv_from_json(d):
	"""
	Get CSV values when mixed into json data. Pull out the CSV data and put it into a dictionary.
	:param dict d: JSON with CSV values
	:return dict: CSV values. (i.e. { CSVFilename1: { Column1: [Values], Column2: [Values] }, CSVFilename2: ... }
	"""
	logger_jsons.info("enter get_csv_from_json")
	csv_data = OrderedDict()

	if "paleoData" in d:
		csv_data = _get_csv_from_section(d, "paleoData", csv_data)

	if "chronData" in d:
		csv_data = _get_csv_from_section(d, "chronData", csv_data)

	logger_jsons.info("exit get_csv_from_json")
	return csv_data


def _get_csv_from_section(d, pc, csv_data):
	"""
	Get csv from paleo and chron sections
	:param dict d: Metadata
	:param str pc: Paleo or chron
	:return dict: running csv data
	"""
	logger_jsons.info("enter get_csv_from_section: {}".format(pc))

	for table, table_content in d[pc].items():
		# Create entry for this table/CSV file (i.e. Asia-1.measTable.PaleoData.csv)
		# Note: Each table has a respective CSV file.
		csv_data[table_content['filename']] = OrderedDict()
		for column, column_content in table_content['columns'].items():
			# Set the "values" into csv dictionary in order of column "number"
			csv_data[table_content['filename']][column_content['number']] = column_content['values']

	logger_jsons.info("exit get_csv_from_section: {}".format(pc))
	return csv_data


def remove_csv_from_json(d):
	"""
	Remove all CSV data 'values' entries from paleoData table in the JSON structure.
	:param dict d: JSON data - old structure
	:return dict: Metadata dictionary without CSV values
	"""
	logger_jsons.info("enter remove_csv_from_json")

	# Check both sections
	if "paleoData" in d:
		d = _remove_csv_from_section(d, "paleoData")

	if "chronData" in d:
		d = _remove_csv_from_section(d, "chronData")

	logger_jsons.info("exit remove_csv_from_json")
	return d


def _remove_csv_from_section(d, pc):
	"""
	Remove CSV from metadata in this section
	:param dict d: Metadata
	:param str pc: Paleo or chron
	:return dict: Modified metadata
	"""
	logger_jsons.info("enter remove_csv_from_json: {}".format(pc))

	for table, table_content in d[pc].items():
		for column, column_content in table_content['columns'].items():
			try:
				# try to delete the values key entry
				del column_content['values']
			except KeyError as e:
				# if the key doesn't exist, keep going
				logger_jsons.debug("remove_csv_from_json: KeyError: {}, {}".format(pc, e))

	logger_jsons.info("exit remove_csv_from_json: {}".format(pc))
	return d


# EXPORT


def write_json_to_file(json_data, filename="metadata"):
	"""
	Write all JSON in python dictionary to a new json file.
	:param dict json_data: JSON data
	:param str filename: Target filename (defaults to 'metadata.jsonld')
	:return None:
	"""
	logger_jsons.info("enter write_json_to_file")
	json_data = rm_empty_fields(json_data)
	# Use demjson to maintain unicode characters in output
	json_bin = demjson.encode(json_data, encoding='utf-8', compactly=False)
	# Write json to file
	try:
		open("{}.jsonld".format(filename), "wb").write(json_bin)
		logger_jsons.info("wrote data to json file")
	except FileNotFoundError as e:
		print("Error: Writing json to file: {}".format(filename))
		logger_jsons.debug("write_json_to_file: FileNotFound: {}, {}".format(filename, e))
	logger_jsons.info("exit write_json_to_file")
	return


def idx_name_to_num(L):
	"""
	Switch from index-by-name to index-by-number.
	:param dict L: Metadata
	:return dict: Modified metadata
	"""
	logger_jsons.info("enter idx_name_to_num")

	# Process the paleoData section
	if "paleoData" in L:
		L["paleoData"] = _export_section(L["paleoData"], "paleo")

	# Process the chronData section
	if "chronData" in L:
		L["chronData"] = _export_section(L["chronData"], "chron")

	logger_jsons.info("exit idx_name_to_num")
	return L


def _export_section(sections, pc):
	"""
	Switch chron data to index-by-number
	:param dict sections: Metadata
	:return list _sections: Metadata
	"""
	logger_jsons.info("enter export_data: {}".format(pc))
	_sections = []

	for name, section in sections.items():

		# Process chron models
		if "model" in section:
			section["model"] = _export_model(section["model"])

		# Process the chron measurement table
		if "measurementTable" in section:
			section["measurementTable"] = _idx_table_by_num(section["measurementTable"])

		# Add only the table to the output list
		_sections.append(section)

	logger_jsons.info("exit export_data: {}".format(pc))
	return _sections


def _export_model(models):
	"""
	Switch model tables to index-by-number

	:param dict models: Metadata
	:return dict _models: Metadata
	"""
	logger_jsons.info("enter export_model")
	_models = []
	try:
		for name, model in models.items():

			if "summaryTable" in model:
				model["summaryTable"] = _idx_table_by_num(model["summaryTable"])

			# Process ensemble table (special two columns)
			if "ensembleTable" in model:
				model["ensembleTable"] = _idx_table_by_num(model["ensembleTable"])

			if "distributionTable" in model:
				model["distributionTable"] = _idx_table_by_num(model["distributionTable"])

			_models.append(model)

	except Exception as e:
		logger_jsons.error("export_model: {}".format(e))
		print("Error: export_model: {}".format(e))
	logger_jsons.info("exit export_model")
	return _models


def _idx_table_by_num(tables):
	"""
	Switch tables to index-by-number

	:param dict tables: Metadata
	:return list _tables: Metadata
	"""
	logger_jsons.info("enter idx_table_by_num")
	_tables = []
	for name, table in tables.items():
		try:
			# Get the modified table data
			tmp = _idx_col_by_num(table)
			# Append it to the growing calibrated age list of tables
			_tables.append(tmp)
		except Exception as e:
			logger_jsons.error("idx_table_by_num: {}".format(e))
	logger_jsons.info("exit idx_table_by_num")
	return _tables


def _idx_col_by_num(table):
	"""
	Index columns by number instead of by name. Use "number" key in column to maintain order

	:param dict table: Metadata
	:return list _table: Metadata
	"""
	_columns = []
	_ens_parse = False
	_ens_tmp = {}
	try:
		# Loop and start placing data in the output list based on its "number" entry
		for _name, _dat in table["columns"].items():
			try:
				found = False
				if "ensembleName" in _dat and "isEnsemble" in _dat:
					m = re.match(re_ensemble_collapse, _name)
					for i in _columns:
						if "ensembleName" in i:
							if i["ensembleName"] == m.group(1):
								found = True
								i["number"].append(_dat["number"])
					if not found:
						found = False
						_num = _dat["number"]
						_dat["number"] = [_num]
						_columns.append(_dat)

				else:
					_columns.append(_dat)
			except KeyError as ke:
				print("Error: idx_col_by_num: {}".format(ke))
				logger_jsons.error("idx_col_by_num: KeyError: missing number key: {}, {}".format(_name, ke))
			except Exception as e:
				print("Error: idx_col_by_num: {}".format(e))
				logger_jsons.error("idx_col_by_num: Exception: {}".format(e))

		for i in _columns:
			if "ensembleName" in i and "isEnsemble" in i:
				del i["ensembleName"]
				del i["isEnsemble"]
		table["columns"] = _columns
	except Exception as e:
		logger_jsons.error("idx_col_by_num: {}".format(e))
		print("Error: idx_col_by_num: {}".format(e))

	return table


