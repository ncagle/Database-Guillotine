# -*- coding: utf-8 -*-
# ¸¸.·´¯`·.¸¸.·´¯`·.¸¸
# ║╚╔═╗╝║  │┌┘─└┐│  ▄█▀‾
# ======================== #
# Database Guillotine v1.8 #
# Nat Cagle 2022-09-27     #
# ======================== #
# Covered under GNU General Public License v3.0
# See full license at the end of the code

import arcpy as ap
from arcpy import AddMessage as write
from datetime import datetime as dt
import os
from collections import defaultdict
import sys
import time
import re
import uuid


#            _________________________________
#           | Copies a local or SDE TDS to a  |
#           | new database, extracts the data |
#           | based on a provided query, and  |
#           | splits features along the       |
#           | provided AOI boundary.          |
#      _    /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#   __(.)< ‾
#~~~\___)~~~



'''
╔═════════════════╗
║ Notes and To-Do ║
╚═════════════════╝

#### 4 hashtags in the code means things to be updated
## 2 hashtags in the code means recent changes/updates

#### Update Plans
  -


## Recent Changes
  - Added Tool Help section for each parameter.

2022-09-06
  - Fixed lingering og_oid field for split multipart feature classes
  - Fixed validation bug. If the custom SQL query option was checked, the default query parameter value deleted, and the custom SQL query option then unchecked, it would lock the tool until the option was rechecked and any value assigned to the parameter. It could then be deactivated again and the tool could continue without needed a valid query.
  - Sorted fc_list that is applied to parameter 10 "Field Name Reference"

2022-09-20
  - Added option to download all additional tables and files in the GDB in addition to the dataset. Used for final delivery copies.
  - Fixed task_summary bug with formatted spacing for query line.


'''



''''''''' Parameters '''''''''
## [0] If copying from SDE, make sure you are properly connected - Boolean - Default: False
## [1] TDS - Feature Dataset
TDS = ap.GetParameterAsText(1)
TDS_name = re.findall(r"[\w']+", os.path.basename(os.path.split(TDS)[0]))[0] # Detailed breakdown in pull_local.trash.py
## [2] Include additional files (TDS_CARTO, PD_Components, etc.) - Boolean
all_files = ap.GetParameter(2) # Default: False
## [3] Create new GDB and clone source schema - Boolean
create_GDB = ap.GetParameter(3) # Default: True
## [4] Name for split GDB - String
gdb_name = ap.GetParameterAsText(4) # Default: "Extracted_GDB_Name"
## [5] Destination folder for split GDB - Folder
out_folder = ap.GetParameterAsText(5) # Default: "C:\Users"
## [6] Dataload into existing data or empty GDB (Schemas must match) - Workspace
existing_GDB = ap.GetParameterAsText(6) # Default: "C:\Users"
## [7] Use Full Extent (No AOI) - Boolean
no_AOI = ap.GetParameter(7) # Default: False
## [8] AOI (Must be merged into a single feature) - Feature Class
AOI = ap.GetParameterAsText(8) # Default: "C:\Users\.."
## [9] Extract Scale: ZI026_CTUU >= - String
query_scale = "zi026_ctuu >= {0}".format(ap.GetParameterAsText(9)) # Scale value from list added to query - Default: "-999999"
## [10] Extract data using custom query - Boolean
manual = ap.GetParameter(10) # Default: False
## [11] Field Name Reference (The Query Builder needs a feature class to load field names) - Multivalue String - {Optional}
#field_ref = ap.GetParameter(11)
## [12] Custom Query (Query Builder --->) - String
# Obtained from Super Secret Parameter to get dynamic FC field names to display in the SQL Query Builder GUI
query_manual = ap.GetParameterAsText(12) # Default: "Ex: HGT >= 46  Applies to all feature classes"
## [13] Extract specific feature classes - Boolean
vogon = ap.GetParameter(13) # Default: False
## [14] Feature Class List - String
vogon_constructor_fleet = ap.GetParameter(14) # Said to hang in the air "the way that bricks don't" - Default: "¯\_(ツ)_/¯"
## [15] Super Secret Parameter: What is it for? Nobody knows... - Feature Class - Default: "(ㆆ_ㆆ)"
# It is the middle-man for after the user chooses the Field Name Reference feature class. This parameter is set to the TDS path + the FNR FC. query_manual is 'Obtained from' this parameter to fully utilize the SQL Query Builder.
# Get current time for gdb timestamp
#timestamp = dt.now().strftime("%Y%b%d_%H%M")
ap.env.workspace = TDS
ap.env.extent = TDS
ap.env.overwriteOutput = True



''''''''' General Functions '''''''''
def license_check():
	today = dt.today()
	license_term = dt.strptime('2023-10-21', '%Y-%m-%d')
	if today > license_term:
		return False
	else:
		return True

def write_info(name, var): # Write information for given variable
	#write_info('var_name', var)
	write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	write("Debug info for {0}:".format(name))
	write("   Variable Type: {0}".format(type(var)))
	if type(var) is str or type(var) is unicode:
		write("   Assigned Value: '{0}'".format(var))
	else:
		write("   Assigned Value: {0}".format(var))
	write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

def debug_view(**kwargs): # Input variable to view info in script output
	# Set x_debug = False outside of loop where x is defined
	# Set repeat = False to output for only the first loop or repeat = True to output for every loop
	# Example:
	#foo_debug = False
	#for fc in fc_list:
	#    foo = 'bar'
	#    debug_view(foo=foo,repeat=False)
	#
	#>>> ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#    Debug info for foo:
	#       Variable Type: <class 'str'>
	#       Assigned Value: 'bar'
	#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	arg_list = kwargs.keys() # Python 2: kwargs.keys()  # Python 3: list(kwargs.keys())
	arg_list.remove('repeat')
	while not globals()[arg_list[0] + "_debug"]:
		write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		write("Debug info for {0}:".format(arg_list[0]))
		write("   Variable Type: {0}".format(type(kwargs[arg_list[0]])))
		write("   Assigned Value: {0}".format(kwargs[arg_list[0]]))
		write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		if not kwargs['repeat']:
			globals()[arg_list[0] + "_debug"] = True
		else:
			return

def runtime(start, finish): # Time a process or code block
	# Add a start and finish variable markers surrounding the code to be timed
	#from datetime import datetime as dt
	#start/finish = dt.now()
	# Returns string of formatted elapsed time between start and finish markers
	time_delta = (finish - start).total_seconds()
	h = int(time_delta/(60*60))
	m = int((time_delta%(60*60))/60)
	s = time_delta%60.
	#time_elapsed = "{}:{:>02}:{:>05.4f}".format(h, m, s) # 00:00:00.0000
	if h == 1:
		hour_grammar = "hour"
	else:
		hour_grammar = "hours"
	if m == 1:
		minute_grammar = "minute"
	else:
		minute_grammar = "minutes"
	if h and m and s:
			time_elapsed = "{} {} {} {} and {} seconds".format(h, hour_grammar, m, minute_grammar, round(s))
	elif not h and m and s:
		time_elapsed = "{} {} and {:.1f} seconds".format(m, minute_grammar, s)
	elif not h and not m and s:
		time_elapsed = "{:.3f} seconds".format(s)
	else:
		time_elapsed = 0
	return time_elapsed

def writeresults(tool_name): # If tool fails, get messages and output error report before endind process
	ap.AddError("\n\n***Failed to run {0}.***\n".format(tool_name))
	trace_back = ''
	tb_info = ''
	python_errors = ''
	arcpy_errors = ''
	warnings = ''
	try:
		trace_back = sys.exc_info()[2] # Get the traceback object
		tb_info = traceback.format_tb(trace_back)[0] # Format the traceback information
		python_errors = "Traceback Info:\n{0}\nError Info:\n{1}\n".format(tb_info, sys.exc_info()[1]) # Concatenate error information together
		arcpy_errors = "ArcPy Error Output:\n{0}".format(ap.GetMessages(0))
		warnings = ap.GetMessages(1)
	except:
		pass

	if len(warnings) > 0:
		ap.AddError("Tool Warnings:")
		ap.AddError("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		ap.AddError(warnings)
		ap.AddError("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
	ap.AddError("Error Report:")
	ap.AddError("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	ap.AddError(python_errors)
	ap.AddError(arcpy_errors)
	ap.AddError("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
	ap.AddError('                       ______\n                    .-"      "-.\n                   /            \\\n       _          |              |          _\n      ( \\         |,  .-.  .-.  ,|         / )\n       > "=._     | )(__/  \\__)( |     _.=" <\n      (_/"=._"=._ |/     /\\     \\| _.="_.="\\_)\n             "=._ (_     ^^     _)"_.="\n                 "=\\__|IIIIII|__/="\n                _.="| \\IIIIII/ |"=._\n      _     _.="_.="\\          /"=._"=._     _\n     ( \\_.="_.="     `--------`     "=._"=._/ )\n      > _.="                            "=._ <\n     (_/                                    \\_)\n')
	ap.AddError("Please double check the data and tool options before rerunning the tool.\nIt is possible one of the feature classes is too big or something else has gone wrong.".format(tool_name))
	ap.AddError("Exiting tool.\n")
	sys.exit(0)
	#print(u'                 uuuuuuu\n             uu$$$$$$$$$$$uu\n          uu$$$$$$$$$$$$$$$$$uu\n         u$$$$$$$$$$$$$$$$$$$$$u\n        u$$$$$$$$$$$$$$$$$$$$$$$u\n       u$$$$$$$$$$$$$$$$$$$$$$$$$u\n       u$$$$$$$$$$$$$$$$$$$$$$$$$u\n       u$$$$$$"   "$$$"   "$$$$$$u\n       "$$$$"      u$u       $$$$"\n        $$$u       u$u       u$$$\n        $$$u      u$$$u      u$$$\n         "$$$$uu$$$   $$$uu$$$$"\n          "$$$$$$$"   "$$$$$$$"\n            u$$$$$$$u$$$$$$$u\n             u$"|¨|¨|¨|¨|"$u\n  uuu        $$u|¯|¯|¯|¯|u$$       uuu\n u$$$$        $$$$$u$u$u$$$       u$$$$\n  $$$$$uu      "$$$$$$$$$"     uu$$$$$$\nu$$$$$$$$$$$uu    """""    uuuu$$$$$$$$$$\n$$$$"""$$$$$$$$$$uuu   uu$$$$$$$$$"""$$$"\n """      ""$$$$$$$$$$$uu ""$"""\n           uuuu ""$$$$$$$$$$uuu\n  u$$$uuu$$$$$$$$$uu ""$$$$$$$$$$$uuu$$$\n  $$$$$$$$$$""""           ""$$$$$$$$$$$"\n   "$$$$$"                      ""$$$$""\n     $$$"                         $$$$"')

def get_count(fc_layer): # Returns feature count
	results = int(ap.GetCount_management(fc_layer).getOutput(0))
	return results

def format_spacing(var, filled): # format line with the right amount of spacing for task_summary variables
	exs = ''
	spacing = 48 - filled - len(var)
	if spacing > 0:
		for i in range(spacing):
			exs += ' '
	return exs

def task_summary():#TDS_name, gdb_name, existing_name, query_manual, query_scale): # Tool title, input, output, and list of user selected task options
	# ¯ MACRON
	# · MIDDLE DOT
	# ¸ CEDILLA
	# ´ ACUTE ACCENT
	write(u"\n({2}`{0}.{3}{3}.{0}{1}{2}`{0}.{3}{3}.{0}{1}{2}`{0}.{3}{3}.{0}{1}{2}`{0}.{3}{3}.{0}{1}{2}`{0}.{3}{3}.{0}{1}{2})".format(u'\N{MIDDLE DOT}', u'\N{ACUTE ACCENT}', u'\N{MACRON}', u'\N{CEDILLA}'))
	write(" )                                            ( ")
	write("(           ~ Database  Guillotine ~           )")
	if not license_check():
		write(" )                                            ( ")
		ap.AddError("(    The license for this tool has expired.    )")
		write(" )                                   _        ( ")
		write("(                                 __(.)<       )")
		write(u"(_.{0}{1}{2}`{0}.{3}{3}.{0}{1}{2}`{0}.{3}{3}.{0}{1}{2}`{0}.{3}{3}.{0}{1}{2}`\\___){0}{1}{2}`{0}.{3}_)\n".format(u'\N{MIDDLE DOT}', u'\N{ACUTE ACCENT}', u'\N{MACRON}', u'\N{CEDILLA}'))
		sys.exit(0)
	if all_files:
		write(" )           Copying additional files         ( ")
		write("(       (TDS_CARTO, PD_Components, etc.)       )")
	write(" )   Source: {0}{1}( ".format(TDS_name, format_spacing(TDS_name, 15)))
	if create_GDB:
		write("(    Output: {0}{1} )".format(gdb_name, format_spacing(gdb_name, 15)))
		write(" )   - Create new GDB based on source schema  ( ")
	else:
		existing_name = re.findall(r"[\w']+", os.path.split(existing_GDB)[-1])[0] # Detailed breakdown in pull_local.trash.py # Modified for GDB path not TDS path
		write("(    Output: {0}{1} )".format(existing_name, format_spacing(existing_name, 15)))
		write(" )   - Extract data to existing blank GDB     ( ")
	if no_AOI:
		write("(    - Search full extent of the data          )")
	else:
		write("(    - Cut features at AOI boundary            )")
	if manual:
		write(" )   - Query: {0}{1}( ".format(query_manual, format_spacing(query_manual, 16)))
	else:
		write(" )   - Query: {0}{1}( ".format(query_scale, format_spacing(query_scale, 16)))
	if vogon:
		write("(    - Only read specified feature classes     )")
	else:
		write("(    - Read all source feature classes         )")
	write(" )                                   _        ( ")
	write("(                                 __(.)<       )")
	write(u"(_.{0}{1}{2}`{0}.{3}{3}.{0}{1}{2}`{0}.{3}{3}.{0}{1}{2}`{0}.{3}{3}.{0}{1}{2}`\\___){0}{1}{2}`{0}.{3}_)\n".format(u'\N{MIDDLE DOT}', u'\N{ACUTE ACCENT}', u'\N{MACRON}', u'\N{CEDILLA}'))
	'''
					"(¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯)"48
					" )                                            ( "
					"(           ~ Database  Guillotine ~           )"
					" )   Source: {0}{1}                           ( ".format(TDS_name, format_spacing(TDS_name, 15))
	if create_GDB:	"(    Output: {0}{1}                            )".format(gdb_name, format_spacing(gdb_name, 15))
					" )   - Create new GDB based on source schema  ( "
	else:			"(    Output: {0}{1}                            )".format(existing_name, format_spacing(existing_name, 15))
					" )   - Extract data to existing blank GDB     ( "
	if no_AOI:		"(    - Search full extent of the data          )"
	else:			"(    - Cut features at AOI boundary            )"
	if manual:		" )   - Query: {0}{1}                          ( ".format(query_manual, format_spacing(query_manual, 16))
	else:			" )   - Query: ZI026_CTUU >= {0}{1}            ( ".format(query_scale, format_spacing(query_scale, 30))
	if vogon:		"(    - Only read specified feature classes     )"
	else:			"(    - Read all source feature classes         )"
					" )                                   _        ( "
					"(                                 __(.)<       )"
					"(_.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`\___)·´¯`·.¸_)"
	'''
	'''
	   ¸·¸
	 ¸´   `¸
	 │  │  |
	  \  \·´
	 ·´\  \
	 │  │  |
	 '¸   ¸'
	   `.´
	'''


''''''''' Task Functions '''''''''
def add_row_tuple(add_row, index, val): # Adds new index in row tuple with specified value
	# Reminder: The length of the row tuple has to match the target cursor to be applied
	#for add_row in cursor:
	##add_row = add_row_tuple(add_row, index, value)
	##icursor.insertRow(add_row)
	add_row = list(add_row)
	place = int((abs(index)-1) * (index/abs(index)))
	add_row.insert(place, val)
	return tuple(add_row)

def update_row_tuple(edit_row, index, val): # Update a specific row field inside a cursor tuple
	# Usually used for updating geometry before copying the row
	# For short tuples, slicing and concatenation is faster
	# But performance of long tuples is more consistently efficient with list conversion
	#for edit_row in cursor:
	##edit_row = update_row_tuple(edit_row, index, value)
	##icursor.insertRow(edit_row)
	edit_row = list(edit_row)
	edit_row[index] = val
	return tuple(edit_row)

def remove_row_tuple(rem_row, index): # Remove specified index from row tuple
	# Reminder: The length of the row tuple has to match the target cursor to be applied
	#for rem_row in cursor:
	##rem_row = remove_row_tuple(rem_row, index, value)
	##icursor.insertRow(rem_row)
	rem_row = list(rem_row)
	rem_row.pop(index)
	return tuple(rem_row)

def make_field_list(dsc): # Construct a list of proper feature class fields
	# Sanitizes Geometry fields to work on File Geodatabases or SDE Connections
	#field_list = make_field_list(describe_obj)
	fields = dsc.fields # List of all fc fields
	out_fields = [dsc.OIDFieldName, dsc.lengthFieldName, dsc.areaFieldName, 'shape', 'area', 'length', 'global'] # List Geometry and OID fields to be removed
	# Construct sanitized list of field names
	field_list = [field.name for field in fields if field.type not in ['Geometry'] and not any(substring in field.name.lower() for substring in out_fields if substring)]
	# Add ufi field to index[-3], OID@ token to index[-2], and Shape@ geometry token to index[-1]
	field_list.append('OID@')
	field_list.append('SHAPE@')
	return field_list

def get_local(out_path, dsc): # Gets the clean feature class name and its local path in the target GDB
	#local_fc_path, clean_fc_name = get_local(output_path, describe_obj)
	# dsc.file        = hexagon250_e04a_surge2.sde.AeronauticCrv
	# split(".")     = [hexagon250_e04a_surge2, sde, AeronauticCrv]
	# split(".")[-1] = AeronauticCrv
	fc_name = dsc.file.split(".")[-1] # AeronauticCrv
	local_fc = os.path.join(out_path, "TDS", fc_name) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2_2022Mar28_1608.gdb\TDS\AeronauticCrv
	return local_fc, fc_name

def make_gdb_schema(TDS, xml_out, out_folder, gdb_name, out_path, out_tds): # Creates a new file GDB with an empty schema identical to the source
	# Works to replicate schema from SDE
	# TDS - Path to source TDS with schema to replicate       # "T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge.sde\hexagon250_e04a_surge2.sde.TDS"
	# xml_out - Output path for schema xml file               # "C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge_schema.xml"
	# out_folder - Folder path where new GDB will be created  # "C:\Projects\njcagle\finishing\E04A"
	# gdb_name - Name of GDB to be created                    # "hexagon250_e04a_surge_2022Mar29_1923"
	# out_path - Path of newly created GDB                    # "C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge_2022Mar29_1923.gdb"
	start_schema = dt.now()
	write("Exporting XML workspace")
	ap.ExportXMLWorkspaceDocument_management(TDS, xml_out, "SCHEMA_ONLY", "BINARY", "METADATA")
	write("Creating File GDB")
	ap.CreateFileGDB_management(out_folder, gdb_name, "CURRENT")
	write("Importing XML workspace")
	ap.ImportXMLWorkspaceDocument_management(out_path, xml_out, "SCHEMA_ONLY")
	write("Local blank GDB with schema successfully created")
	ap.env.workspace = out_tds
	featureclass = ap.ListFeatureClasses()
	featureclass.sort()
	for fc in featureclass:
		if ap.Describe(fc).editorTrackingEnabled:
			try:
				ap.DisableEditorTracking_management(fc)
			except:
				write("Error disabling editor tracking for {0}. Please check the data manually and try again.".format(fc))
				pass
	write("Editor Tracking has been disabled on local copy")
	os.remove(xml_out)
	ap.RefreshCatalog(out_folder)
	finish_schema = dt.now()
	write("Time to create local GDB with schema: {0}".format(runtime(start_schema,finish_schema)))

def fractinull(shp): # Checks for NULL geometry
	# If geometry is NULL, output the feature class and OID and continue to next feature
	#fractinull(geometry_obj, fc_name, oid)
	oh_dear_god = False
	if shp is None:
		oh_dear_god = True
		#write("{0} feature OID: {1} found with NULL geometry. Skipping transfer.".format(fc_name, oid))
	return oh_dear_god

def crosses_insert(aoi, icursor, row): # Inserts feature if the geometry crosses the AOI boundary after clipping it to be within
	# Crosses() geometry method can only compare line-line or polygon-line, NOT polygon-polygon
	# So to check if a polygon crosses another polygon, one of them must be a polyline object made with the boundary() geometry method
	#crosses_insert(input_geom_obj, aoi_geom_obj, extent_geom_obj, insert_cursor, insert_row)
	criss = False
	shp = row[-1]
	boundary = aoi.boundary() # Line geometry object of the AOI boundary
	if shp.type == 'polyline':
		dim = 2
	elif shp.type == 'polygon':
		dim = 4
	if shp.crosses(boundary): # Geometry method checks if the feature geometry crosses the AOI polygon boundary
		criss = True
		oid = row[-2]
		row = add_row_tuple(row, -3, oid)
		clip_shp = shp.intersect(aoi, dim) # Feature geometry is clipped the intersection overlap of the AOI polygon and the feature
		row = update_row_tuple(row, -1, clip_shp) # Updates the SHAPE@ token with the newly clipped geometry object
		icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB after geometry clip and replace
	return criss

def within_insert(aoi, icursor, row, og_oid_row): # Inserts feature if the geometry is within the AOI
	#within_insert(input_geom_obj, aoi_geom_obj, insert_cursor, insert_row)
	inner_peace = False
	shp = row[-1]
	fc_type = shp.type
	if fc_type != 'polyline':
		shp = shp.trueCentroid # Gets the centroid of the current feature
	if shp.within(aoi, "CLEMENTINI"): # Geometry method checks if the feature geometry is within the AOI polygon
		inner_peace = True
		if og_oid_row:
			row = add_row_tuple(row, -3, None)
			icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB
		else:
			icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB
	return inner_peace


''''''''' Guillotine Function '''''''''
def pull_all_files():
	source_path = os.path.dirname(TDS)
	tup = next(ap.da.Walk(source_path, topdown=True, followlinks=True, datatype='Any', type='All'))
	gdb_file_list = tup[1] + tup[2]
	if 'TDS' in gdb_file_list: gdb_file_list.remove('TDS')
	write("Copying additional files:")

	for misc in gdb_file_list:
		write("Copying {0} to target GDB".format(misc))
		if not ap.Exists(os.path.join(out_path, misc)):
			ap.Copy_management(os.path.join(source_path, misc), os.path.join(out_path, misc))

def guillotine(fc_list, out_path):
	if manual: # Allow for any field query to be made
		# Obtained from Super Secret Parameter to get dynamic FC field names for SQL Query Builder option
		query = query_manual
		query_validation = query.split(' ')
		if len(query_validation) <= 1: # Not strictly necessary. Should have been confirmed in tool dialogue validation, but leaving it in as safety
			ap.AddError("\n**********\n\"{0}\" is not a valid query.\nPlease check for field delimiters such as quotes and ensure that unique values are separated by spaces.\n**********\n".format(query))
			sys.exit(0)
	else:
		query = query_scale # Scale value from list added to query

	out_tds = os.path.join(out_path, "TDS")
	split_dict = {}
	schema_mismatch = []
	for fc in fc_list:
		write("")
		total_feats = get_count(fc)
		if not total_feats:
			write("{0} is empty\n".format(fc))
			continue

		dsc = ap.Describe(fc)
		fc_type = dsc.shapeType # Polygon, Polyline, Point, Multipoint, MultiPatch
		input_fc = dsc.catalogPath # T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticCrv
		oid_field = dsc.OIDFieldName # Get the OID field name.
		local_fc, fc_name = get_local(out_path, dsc)
		field_list = make_field_list(dsc)
		og_oid = 'og_oid'
		f_count = 0
		criss = False
		start_cursor_search = dt.now()

		# If the user is using an existing GDB and schema, check that each feature class is present in the target before continuing
		# Output a warning if a feature class in the source does not exist in the target and continue to the next feature class without extracting data
		# Saves schema mismatched feature classes and outputs a list at the end of the tool
		if not create_GDB:
			fc_path = os.path.join(out_tds, fc)
			if not ap.Exists(fc_path):
				write("*** The provided output GDB and schema does not match the schema of the source data for the {0} feature class! ***\n*** Progress will continue for feature classes that match the schema. A list of schema mismatched feature classes that were not copied will be provided after the tool has completed. ***".format(fc))
				schema_mismatch.append(fc)
				continue

		# Create Search and Insert Cursor
		write("Checking {0} features".format(fc_name))
		with ap.da.SearchCursor(AOI, ['SHAPE@']) as aoi_cur:
			aoi_next = aoi_cur.next()
			aoi_shp = aoi_next[0]
			if aoi_shp is None: # Must check for NULL geometry before using any geometry methods
				write("NULL geometry found in input AOI. Please check the AOI polygon and try again.")
				sys.exit(0) # If the AOI polygon has NULL geometry, exit the tool. The AOI needs to be checked by the user

			if 'MetadataSrf' in fc or 'ResourceSrf' in fc: # Check for these first since they are a special case
				if manual:
					continue
				try:
					mr_query = '' # Metadata and Resource surfaces have different fields. Copy them regardless of query. Can be excluded in Advanced Options.
					write("Found {0}. Ignoring queries and copying all within provided AOI.".format(fc))
					with ap.da.SearchCursor(input_fc, field_list, mr_query) as input_scursor: # Search the input feature class with the specified fields
						with ap.da.InsertCursor(local_fc, field_list) as local_icursor:
							for irow in input_scursor: # Loop thru each Metadata or Resource surface in the input feature class
								input_shp = irow[-1] # Geometry object of current feature
								if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
									continue
								# Metadata and Resource specific method
								if within_insert(aoi_shp, local_icursor, irow, False): # If feature's centroid is within the AOI, insert it into the new GDB
									f_count +=1
									continue
				except ap.ExecuteError:
					writeresults("Guillotine on MetadataSrf/ResourceSrf")
			else: # Proceed assuming normal TDS feature classes
				try:
					with ap.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields and user defined query
						try:
							if fc_type == 'Point': # Points are either within or without the AOI
								with ap.da.InsertCursor(local_fc, field_list) as local_icursor:
									for irow in input_scursor: # Loop thru each point in the input feature class
										input_shp = irow[-1] # Geometry object of current point
										if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
											continue
										# Point specific method
										if within_insert(aoi_shp, local_icursor, irow, False): # If point is within the AOI, insert it into the new GDB
											f_count +=1
											continue

							if fc_type == 'Polyline': # Lines can cross the AOI boundary or be fully within
								ap.AddField_management(local_fc, og_oid, "long")
								field_list.insert(-2, og_oid)
								with ap.da.InsertCursor(local_fc, field_list) as local_icursor:
									for irow in input_scursor: # Loop thru each point in the input feature class
										input_shp = irow[-1] # Geometry object of current line
										input_oid = irow[-2] # OID object of current row
										if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
											continue
										# Line specific method
										if crosses_insert(aoi_shp, local_icursor, irow): # Check if line crosses AOI before within then clip, insert, and continue
											if criss is False: # If the crossing feature is the first in the fc
												split_dict[fc_name] = [input_oid] # Create a dictionary key of the feature class with the source oid in a list
												criss = True # Mark the current fc as having at least one crossing feature and the fc_name dictionary key has been made
											elif criss is True: # If a crossing feature has already been found and the initial fc_name dictionary key is set up
												split_dict[fc_name].append(input_oid) # Append the source oid to the list of the current fc
											f_count +=1
											continue
										if within_insert(aoi_shp, local_icursor, irow, True): # If line doesn't cross AOI and is within(Clementini) then insert and continue
											f_count +=1
											continue

							if fc_type == 'Polygon': # Polygons can cross the AOI boundary or be fully within
								ap.AddField_management(local_fc, og_oid, "long")
								field_list.insert(-2, og_oid)
								aoi_line = aoi_shp.boundary() # Line geometry object of the AOI boundary
								with ap.da.InsertCursor(local_fc, field_list) as local_icursor:
									for irow in input_scursor: # Loop thru each point in the input feature class
										input_shp = irow[-1] # Geometry object of current polygon
										input_oid = irow[-2] # OID object of current row
										if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
											continue
										# Polygon specific method
										if crosses_insert(aoi_shp, local_icursor, irow): # Check if polygon crosses AOI before within then clip, insert, and continue
											if criss is False: # If the crossing feature is the first in the fc
												split_dict[fc_name] = [input_oid] # Create a dictionary key of the feature class with the source oid in a list
												criss = True # Mark the current fc as having at least one crossing feature and the fc_name dictionary key has been made
											elif criss is True: # If a crossing feature has already been found and the initial fc_name dictionary key is set up
												split_dict[fc_name].append(input_oid) # Append the source oid to the list of the current fc
											f_count +=1
											continue
										if within_insert(aoi_shp, local_icursor, irow, True): # If polygon doesn't cross AOI and its centroid is within(Clementini) then insert and continue
											f_count +=1
											continue

						except ap.ExecuteError:
							writeresults("Guillotine on extracting {0}".format(fc))
				except:
					if manual:
						write("{0} does not contain field specified in custom query. Continuing to next.\n".format(fc))
						continue
					else:
						writeresults("Guillotine starting search of {0}.".format(fc))

		# Clean up, runtime, and feature count outputs
		write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_name))
		if not criss:
			try:
				write("Deleting og_oid field from local_fc")
				ap.DeleteField_management(local_fc, og_oid)
			except:
				pass

		# Explode multipart features that crossed the boundary
		if criss:
			write("Split features at AOI boundary. Exploding the resultant geometries...")
			in_class = os.path.join(out_tds, "multi")
			out_class = os.path.join(out_tds, "single")
			oid_query = """{0} IS NOT NULL""".format(ap.AddFieldDelimiters(local_fc, og_oid))
			# Create a new feature class to put the multipart features in to decrease processing time. fields based on original fc template
			ap.CreateFeatureclass_management(out_tds, "multi", fc_type, local_fc, "", "", out_tds)

			# Add multipart features to new feature class based on OID
			incount = 0
			with ap.da.SearchCursor(local_fc, field_list, oid_query) as scursor: # Search current fc using for only OIDs that are in the multipart oid_list.
				with ap.da.InsertCursor(in_class, field_list) as icursor: # Insert cursor for the newly created feature class with the same fields as scursor
					for srow in scursor:
						incount +=1
						icursor.insertRow(srow) # Insert that feature row into the temp feature class, in_class "multi"

			write("Added {0} features to in_class, multipart rupture in progress.".format(incount))
			ap.MultipartToSinglepart_management(in_class, out_class) # New feature class output of just the converted single parts
			with ap.da.UpdateCursor(local_fc, og_oid, oid_query) as ucursor: # Deletes features in fc that have OIDs flagged as multiparts from the oid_list
				for urow in ucursor:
					write("Deleting feature OID {0} in local_fc".format(urow[0]))
					ucursor.deleteRow()
			with ap.da.UpdateCursor(out_class, 'ufi') as ucursor: # Populate the ufi for the newly created singlepart features
				for urow in ucursor:
					urow[0] = str(uuid.uuid4())
					ucursor.updateRow(urow)

			# out_class is one field shorter than the local_fc and they need to match to insert the row
			field_list = [field for field in field_list if 'globalid' not in field.lower()]
			with ap.da.SearchCursor(out_class, field_list) as scursor: # Insert new rows in fc from MultipartToSinglepart output out_class
				with ap.da.InsertCursor(local_fc, field_list) as icursor:
					for srow in scursor:
						write("Inserting feature OID {0} from out_class to local_fc after explode.".format(srow[-3]))
						icursor.insertRow(srow)

			try:
				write("Deleting in_class and out_class from current loop.")
				ap.Delete_management(in_class)
				ap.Delete_management(out_class)
			except:
				write("No in_class or out_class created. Or processing layers have already been cleaned up. Continuing...")
				pass
			try:
				write("Deleting og_oid field from local_fc")
				ap.DeleteField_management(local_fc, og_oid)
			except:
				pass

			write("Finished exploding split features in {0}".format(fc_name))

		finish_cursor_search = dt.now() # Stop runtime clock
		write("Time elapsed to search {0}: {1}\n".format(fc_name, runtime(start_cursor_search, finish_cursor_search)))

	if split_dict:
		write("\n\nHere is a list of source database feature OIDs that crossed the AOI boundary and were split in the output.")
		write("Use this with Select by Attribute if you wish to confirm that features were split properly.\n")
		split_list = split_dict.keys()
		split_list.sort()
		for fc in split_list:
			write("{0}:\n{1}\n".format(fc, split_dict[fc]))
		write("\n")

	if schema_mismatch:
		write("*** The blank GDB and schema provided did not match the source data for all feature classes. ***\n*** The following mismatched feature classes were not copied. ***\n")
		write(schema_mismatch)
		write("\n")


''''''''' Main '''''''''
task_summary()

# Get name of input database for either SDE or file GDB to construct output variables
if create_GDB:
	existing_name = existing_GDB #
	xml_out = os.path.join(out_folder, gdb_name + "_schema.xml")
	out_path = os.path.join(out_folder, gdb_name + ".gdb")
	out_tds = os.path.join(out_path, "TDS")
	make_gdb_schema(TDS, xml_out, out_folder, gdb_name, out_path, out_tds)
	ap.env.workspace = TDS
else:
	existing_name = re.findall(r"[\w']+", os.path.split(existing_GDB)[-1])[0] # Detailed breakdown in pull_local.trash.py # Modified for GDB path not TDS path
	out_path = existing_GDB
	out_tds = os.path.join(out_path, "TDS")

if all_files: pull_all_files()

if no_AOI:
	ap.env.extent = TDS
	AOI = "in_memory\\the_grid" # A digital frontier.
	ap.CopyFeatures_management(ap.env.extent.polygon, AOI)

if not vogon:
	fc_walk = ap.da.Walk(TDS, "FeatureClass")
	for dirpath, dirnames, filenames in fc_walk: # No dirnames present. Use Walk to navigate inconsistent SDEs. Also works on local.
		filenames.sort()
		write("FCs loaded from input GDB: {0}\n".format(len(filenames)))
		guillotine(filenames, out_path)
else:
	vogon_constructor_fleet.sort()
	write("\nExtracting user specified feature classes:")
	for fc in vogon_constructor_fleet: write(fc)
	write("FCs loaded from input GDB: {0}\n".format(len(vogon_constructor_fleet)))
	guillotine(vogon_constructor_fleet, out_path)


ap.RefreshCatalog(out_folder)
ap.RefreshCatalog(out_tds)
task_summary()
ap.AddWarning("\nSplit GDB output location: {0}\n".format(out_path))





'''
 !_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!
                ╔═════════════════════════════════╗
                ║ GNU General Public License v3.0 ║
                ╚═════════════════════════════════╝
 !_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!_!‾!


                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.

                       TERMS AND CONDITIONS

  0. Definitions.

  "This License" refers to version 3 of the GNU General Public License.

  "Copyright" also means copyright-like laws that apply to other kinds of
works, such as semiconductor masks.

  "The Program" refers to any copyrightable work licensed under this
License.  Each licensee is addressed as "you".  "Licensees" and
"recipients" may be individuals or organizations.

  To "modify" a work means to copy from or adapt all or part of the work
in a fashion requiring copyright permission, other than the making of an
exact copy.  The resulting work is called a "modified version" of the
earlier work or a work "based on" the earlier work.

  A "covered work" means either the unmodified Program or a work based
on the Program.

  To "propagate" a work means to do anything with it that, without
permission, would make you directly or secondarily liable for
infringement under applicable copyright law, except executing it on a
computer or modifying a private copy.  Propagation includes copying,
distribution (with or without modification), making available to the
public, and in some countries other activities as well.

  To "convey" a work means any kind of propagation that enables other
parties to make or receive copies.  Mere interaction with a user through
a computer network, with no transfer of a copy, is not conveying.

  An interactive user interface displays "Appropriate Legal Notices"
to the extent that it includes a convenient and prominently visible
feature that (1) displays an appropriate copyright notice, and (2)
tells the user that there is no warranty for the work (except to the
extent that warranties are provided), that licensees may convey the
work under this License, and how to view a copy of this License.  If
the interface presents a list of user commands or options, such as a
menu, a prominent item in the list meets this criterion.

  1. Source Code.

  The "source code" for a work means the preferred form of the work
for making modifications to it.  "Object code" means any non-source
form of a work.

  A "Standard Interface" means an interface that either is an official
standard defined by a recognized standards body, or, in the case of
interfaces specified for a particular programming language, one that
is widely used among developers working in that language.

  The "System Libraries" of an executable work include anything, other
than the work as a whole, that (a) is included in the normal form of
packaging a Major Component, but which is not part of that Major
Component, and (b) serves only to enable use of the work with that
Major Component, or to implement a Standard Interface for which an
implementation is available to the public in source code form.  A
"Major Component", in this context, means a major essential component
(kernel, window system, and so on) of the specific operating system
(if any) on which the executable work runs, or a compiler used to
produce the work, or an object code interpreter used to run it.

  The "Corresponding Source" for a work in object code form means all
the source code needed to generate, install, and (for an executable
work) run the object code and to modify the work, including scripts to
control those activities.  However, it does not include the work's
System Libraries, or general-purpose tools or generally available free
programs which are used unmodified in performing those activities but
which are not part of the work.  For example, Corresponding Source
includes interface definition files associated with source files for
the work, and the source code for shared libraries and dynamically
linked subprograms that the work is specifically designed to require,
such as by intimate data communication or control flow between those
subprograms and other parts of the work.

  The Corresponding Source need not include anything that users
can regenerate automatically from other parts of the Corresponding
Source.

  The Corresponding Source for a work in source code form is that
same work.

  2. Basic Permissions.

  All rights granted under this License are granted for the term of
copyright on the Program, and are irrevocable provided the stated
conditions are met.  This License explicitly affirms your unlimited
permission to run the unmodified Program.  The output from running a
covered work is covered by this License only if the output, given its
content, constitutes a covered work.  This License acknowledges your
rights of fair use or other equivalent, as provided by copyright law.

  You may make, run and propagate covered works that you do not
convey, without conditions so long as your license otherwise remains
in force.  You may convey covered works to others for the sole purpose
of having them make modifications exclusively for you, or provide you
with facilities for running those works, provided that you comply with
the terms of this License in conveying all material for which you do
not control copyright.  Those thus making or running the covered works
for you must do so exclusively on your behalf, under your direction
and control, on terms that prohibit them from making any copies of
your copyrighted material outside their relationship with you.

  Conveying under any other circumstances is permitted solely under
the conditions stated below.  Sublicensing is not allowed; section 10
makes it unnecessary.

  3. Protecting Users' Legal Rights From Anti-Circumvention Law.

  No covered work shall be deemed part of an effective technological
measure under any applicable law fulfilling obligations under article
11 of the WIPO copyright treaty adopted on 20 December 1996, or
similar laws prohibiting or restricting circumvention of such
measures.

  When you convey a covered work, you waive any legal power to forbid
circumvention of technological measures to the extent such circumvention
is effected by exercising rights under this License with respect to
the covered work, and you disclaim any intention to limit operation or
modification of the work as a means of enforcing, against the work's
users, your or third parties' legal rights to forbid circumvention of
technological measures.

  4. Conveying Verbatim Copies.

  You may convey verbatim copies of the Program's source code as you
receive it, in any medium, provided that you conspicuously and
appropriately publish on each copy an appropriate copyright notice;
keep intact all notices stating that this License and any
non-permissive terms added in accord with section 7 apply to the code;
keep intact all notices of the absence of any warranty; and give all
recipients a copy of this License along with the Program.

  You may charge any price or no price for each copy that you convey,
and you may offer support or warranty protection for a fee.

  5. Conveying Modified Source Versions.

  You may convey a work based on the Program, or the modifications to
produce it from the Program, in the form of source code under the
terms of section 4, provided that you also meet all of these conditions:

    a) The work must carry prominent notices stating that you modified
    it, and giving a relevant date.

    b) The work must carry prominent notices stating that it is
    released under this License and any conditions added under section
    7.  This requirement modifies the requirement in section 4 to
    "keep intact all notices".

    c) You must license the entire work, as a whole, under this
    License to anyone who comes into possession of a copy.  This
    License will therefore apply, along with any applicable section 7
    additional terms, to the whole of the work, and all its parts,
    regardless of how they are packaged.  This License gives no
    permission to license the work in any other way, but it does not
    invalidate such permission if you have separately received it.

    d) If the work has interactive user interfaces, each must display
    Appropriate Legal Notices; however, if the Program has interactive
    interfaces that do not display Appropriate Legal Notices, your
    work need not make them do so.

  A compilation of a covered work with other separate and independent
works, which are not by their nature extensions of the covered work,
and which are not combined with it such as to form a larger program,
in or on a volume of a storage or distribution medium, is called an
"aggregate" if the compilation and its resulting copyright are not
used to limit the access or legal rights of the compilation's users
beyond what the individual works permit.  Inclusion of a covered work
in an aggregate does not cause this License to apply to the other
parts of the aggregate.

  6. Conveying Non-Source Forms.

  You may convey a covered work in object code form under the terms
of sections 4 and 5, provided that you also convey the
machine-readable Corresponding Source under the terms of this License,
in one of these ways:

    a) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by the
    Corresponding Source fixed on a durable physical medium
    customarily used for software interchange.

    b) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by a
    written offer, valid for at least three years and valid for as
    long as you offer spare parts or customer support for that product
    model, to give anyone who possesses the object code either (1) a
    copy of the Corresponding Source for all the software in the
    product that is covered by this License, on a durable physical
    medium customarily used for software interchange, for a price no
    more than your reasonable cost of physically performing this
    conveying of source, or (2) access to copy the
    Corresponding Source from a network server at no charge.

    c) Convey individual copies of the object code with a copy of the
    written offer to provide the Corresponding Source.  This
    alternative is allowed only occasionally and noncommercially, and
    only if you received the object code with such an offer, in accord
    with subsection 6b.

    d) Convey the object code by offering access from a designated
    place (gratis or for a charge), and offer equivalent access to the
    Corresponding Source in the same way through the same place at no
    further charge.  You need not require recipients to copy the
    Corresponding Source along with the object code.  If the place to
    copy the object code is a network server, the Corresponding Source
    may be on a different server (operated by you or a third party)
    that supports equivalent copying facilities, provided you maintain
    clear directions next to the object code saying where to find the
    Corresponding Source.  Regardless of what server hosts the
    Corresponding Source, you remain obligated to ensure that it is
    available for as long as needed to satisfy these requirements.

    e) Convey the object code using peer-to-peer transmission, provided
    you inform other peers where the object code and Corresponding
    Source of the work are being offered to the general public at no
    charge under subsection 6d.

  A separable portion of the object code, whose source code is excluded
from the Corresponding Source as a System Library, need not be
included in conveying the object code work.

  A "User Product" is either (1) a "consumer product", which means any
tangible personal property which is normally used for personal, family,
or household purposes, or (2) anything designed or sold for incorporation
into a dwelling.  In determining whether a product is a consumer product,
doubtful cases shall be resolved in favor of coverage.  For a particular
product received by a particular user, "normally used" refers to a
typical or common use of that class of product, regardless of the status
of the particular user or of the way in which the particular user
actually uses, or expects or is expected to use, the product.  A product
is a consumer product regardless of whether the product has substantial
commercial, industrial or non-consumer uses, unless such uses represent
the only significant mode of use of the product.

  "Installation Information" for a User Product means any methods,
procedures, authorization keys, or other information required to install
and execute modified versions of a covered work in that User Product from
a modified version of its Corresponding Source.  The information must
suffice to ensure that the continued functioning of the modified object
code is in no case prevented or interfered with solely because
modification has been made.

  If you convey an object code work under this section in, or with, or
specifically for use in, a User Product, and the conveying occurs as
part of a transaction in which the right of possession and use of the
User Product is transferred to the recipient in perpetuity or for a
fixed term (regardless of how the transaction is characterized), the
Corresponding Source conveyed under this section must be accompanied
by the Installation Information.  But this requirement does not apply
if neither you nor any third party retains the ability to install
modified object code on the User Product (for example, the work has
been installed in ROM).

  The requirement to provide Installation Information does not include a
requirement to continue to provide support service, warranty, or updates
for a work that has been modified or installed by the recipient, or for
the User Product in which it has been modified or installed.  Access to a
network may be denied when the modification itself materially and
adversely affects the operation of the network or violates the rules and
protocols for communication across the network.

  Corresponding Source conveyed, and Installation Information provided,
in accord with this section must be in a format that is publicly
documented (and with an implementation available to the public in
source code form), and must require no special password or key for
unpacking, reading or copying.

  7. Additional Terms.

  "Additional permissions" are terms that supplement the terms of this
License by making exceptions from one or more of its conditions.
Additional permissions that are applicable to the entire Program shall
be treated as though they were included in this License, to the extent
that they are valid under applicable law.  If additional permissions
apply only to part of the Program, that part may be used separately
under those permissions, but the entire Program remains governed by
this License without regard to the additional permissions.

  When you convey a copy of a covered work, you may at your option
remove any additional permissions from that copy, or from any part of
it.  (Additional permissions may be written to require their own
removal in certain cases when you modify the work.)  You may place
additional permissions on material, added by you to a covered work,
for which you have or can give appropriate copyright permission.

  Notwithstanding any other provision of this License, for material you
add to a covered work, you may (if authorized by the copyright holders of
that material) supplement the terms of this License with terms:

    a) Disclaiming warranty or limiting liability differently from the
    terms of sections 15 and 16 of this License; or

    b) Requiring preservation of specified reasonable legal notices or
    author attributions in that material or in the Appropriate Legal
    Notices displayed by works containing it; or

    c) Prohibiting misrepresentation of the origin of that material, or
    requiring that modified versions of such material be marked in
    reasonable ways as different from the original version; or

    d) Limiting the use for publicity purposes of names of licensors or
    authors of the material; or

    e) Declining to grant rights under trademark law for use of some
    trade names, trademarks, or service marks; or

    f) Requiring indemnification of licensors and authors of that
    material by anyone who conveys the material (or modified versions of
    it) with contractual assumptions of liability to the recipient, for
    any liability that these contractual assumptions directly impose on
    those licensors and authors.

  All other non-permissive additional terms are considered "further
restrictions" within the meaning of section 10.  If the Program as you
received it, or any part of it, contains a notice stating that it is
governed by this License along with a term that is a further
restriction, you may remove that term.  If a license document contains
a further restriction but permits relicensing or conveying under this
License, you may add to a covered work material governed by the terms
of that license document, provided that the further restriction does
not survive such relicensing or conveying.

  If you add terms to a covered work in accord with this section, you
must place, in the relevant source files, a statement of the
additional terms that apply to those files, or a notice indicating
where to find the applicable terms.

  Additional terms, permissive or non-permissive, may be stated in the
form of a separately written license, or stated as exceptions;
the above requirements apply either way.

  8. Termination.

  You may not propagate or modify a covered work except as expressly
provided under this License.  Any attempt otherwise to propagate or
modify it is void, and will automatically terminate your rights under
this License (including any patent licenses granted under the third
paragraph of section 11).

  However, if you cease all violation of this License, then your
license from a particular copyright holder is reinstated (a)
provisionally, unless and until the copyright holder explicitly and
finally terminates your license, and (b) permanently, if the copyright
holder fails to notify you of the violation by some reasonable means
prior to 60 days after the cessation.

  Moreover, your license from a particular copyright holder is
reinstated permanently if the copyright holder notifies you of the
violation by some reasonable means, this is the first time you have
received notice of violation of this License (for any work) from that
copyright holder, and you cure the violation prior to 30 days after
your receipt of the notice.

  Termination of your rights under this section does not terminate the
licenses of parties who have received copies or rights from you under
this License.  If your rights have been terminated and not permanently
reinstated, you do not qualify to receive new licenses for the same
material under section 10.

  9. Acceptance Not Required for Having Copies.

  You are not required to accept this License in order to receive or
run a copy of the Program.  Ancillary propagation of a covered work
occurring solely as a consequence of using peer-to-peer transmission
to receive a copy likewise does not require acceptance.  However,
nothing other than this License grants you permission to propagate or
modify any covered work.  These actions infringe copyright if you do
not accept this License.  Therefore, by modifying or propagating a
covered work, you indicate your acceptance of this License to do so.

  10. Automatic Licensing of Downstream Recipients.

  Each time you convey a covered work, the recipient automatically
receives a license from the original licensors, to run, modify and
propagate that work, subject to this License.  You are not responsible
for enforcing compliance by third parties with this License.

  An "entity transaction" is a transaction transferring control of an
organization, or substantially all assets of one, or subdividing an
organization, or merging organizations.  If propagation of a covered
work results from an entity transaction, each party to that
transaction who receives a copy of the work also receives whatever
licenses to the work the party's predecessor in interest had or could
give under the previous paragraph, plus a right to possession of the
Corresponding Source of the work from the predecessor in interest, if
the predecessor has it or can get it with reasonable efforts.

  You may not impose any further restrictions on the exercise of the
rights granted or affirmed under this License.  For example, you may
not impose a license fee, royalty, or other charge for exercise of
rights granted under this License, and you may not initiate litigation
(including a cross-claim or counterclaim in a lawsuit) alleging that
any patent claim is infringed by making, using, selling, offering for
sale, or importing the Program or any portion of it.

  11. Patents.

  A "contributor" is a copyright holder who authorizes use under this
License of the Program or a work on which the Program is based.  The
work thus licensed is called the contributor's "contributor version".

  A contributor's "essential patent claims" are all patent claims
owned or controlled by the contributor, whether already acquired or
hereafter acquired, that would be infringed by some manner, permitted
by this License, of making, using, or selling its contributor version,
but do not include claims that would be infringed only as a
consequence of further modification of the contributor version.  For
purposes of this definition, "control" includes the right to grant
patent sublicenses in a manner consistent with the requirements of
this License.

  Each contributor grants you a non-exclusive, worldwide, royalty-free
patent license under the contributor's essential patent claims, to
make, use, sell, offer for sale, import and otherwise run, modify and
propagate the contents of its contributor version.

  In the following three paragraphs, a "patent license" is any express
agreement or commitment, however denominated, not to enforce a patent
(such as an express permission to practice a patent or covenant not to
sue for patent infringement).  To "grant" such a patent license to a
party means to make such an agreement or commitment not to enforce a
patent against the party.

  If you convey a covered work, knowingly relying on a patent license,
and the Corresponding Source of the work is not available for anyone
to copy, free of charge and under the terms of this License, through a
publicly available network server or other readily accessible means,
then you must either (1) cause the Corresponding Source to be so
available, or (2) arrange to deprive yourself of the benefit of the
patent license for this particular work, or (3) arrange, in a manner
consistent with the requirements of this License, to extend the patent
license to downstream recipients.  "Knowingly relying" means you have
actual knowledge that, but for the patent license, your conveying the
covered work in a country, or your recipient's use of the covered work
in a country, would infringe one or more identifiable patents in that
country that you have reason to believe are valid.

  If, pursuant to or in connection with a single transaction or
arrangement, you convey, or propagate by procuring conveyance of, a
covered work, and grant a patent license to some of the parties
receiving the covered work authorizing them to use, propagate, modify
or convey a specific copy of the covered work, then the patent license
you grant is automatically extended to all recipients of the covered
work and works based on it.

  A patent license is "discriminatory" if it does not include within
the scope of its coverage, prohibits the exercise of, or is
conditioned on the non-exercise of one or more of the rights that are
specifically granted under this License.  You may not convey a covered
work if you are a party to an arrangement with a third party that is
in the business of distributing software, under which you make payment
to the third party based on the extent of your activity of conveying
the work, and under which the third party grants, to any of the
parties who would receive the covered work from you, a discriminatory
patent license (a) in connection with copies of the covered work
conveyed by you (or copies made from those copies), or (b) primarily
for and in connection with specific products or compilations that
contain the covered work, unless you entered into that arrangement,
or that patent license was granted, prior to 28 March 2007.

  Nothing in this License shall be construed as excluding or limiting
any implied license or other defenses to infringement that may
otherwise be available to you under applicable patent law.

  12. No Surrender of Others' Freedom.

  If conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot convey a
covered work so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you may
not convey it at all.  For example, if you agree to terms that obligate you
to collect a royalty for further conveying from those to whom you convey
the Program, the only way you could satisfy both those terms and this
License would be to refrain entirely from conveying the Program.

  13. Use with the GNU Affero General Public License.

  Notwithstanding any other provision of this License, you have
permission to link or combine any covered work with a work licensed
under version 3 of the GNU Affero General Public License into a single
combined work, and to convey the resulting work.  The terms of this
License will continue to apply to the part which is the covered work,
but the special requirements of the GNU Affero General Public License,
section 13, concerning interaction through a network will apply to the
combination as such.

  14. Revised Versions of this License.

  The Free Software Foundation may publish revised and/or new versions of
the GNU General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

  Each version is given a distinguishing version number.  If the
Program specifies that a certain numbered version of the GNU General
Public License "or any later version" applies to it, you have the
option of following the terms and conditions either of that numbered
version or of any later version published by the Free Software
Foundation.  If the Program does not specify a version number of the
GNU General Public License, you may choose any version ever published
by the Free Software Foundation.

  If the Program specifies that a proxy can decide which future
versions of the GNU General Public License can be used, that proxy's
public statement of acceptance of a version permanently authorizes you
to choose that version for the Program.

  Later license versions may give you additional or different
permissions.  However, no additional obligations are imposed on any
author or copyright holder as a result of your choosing to follow a
later version.

  15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  16. Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES.

  17. Interpretation of Sections 15 and 16.

  If the disclaimer of warranty and limitation of liability provided
above cannot be given local legal effect according to their terms,
reviewing courts shall apply local law that most closely approximates
an absolute waiver of all civil liability in connection with the
Program, unless a warranty or assumption of liability accompanies a
copy of the Program in return for a fee.

                     END OF TERMS AND CONDITIONS

            How to Apply These Terms to Your New Programs

  If you develop a new program, and you want it to be of the greatest
possible use to the public, the best way to achieve this is to make it
free software which everyone can redistribute and change under these terms.

  To do so, attach the following notices to the program.  It is safest
to attach them to the start of each source file to most effectively
state the exclusion of warranty; and each file should have at least
the "copyright" line and a pointer to where the full notice is found.

    <one line to give the program's name and a brief idea of what it does.>
    Copyright (C) <year>  <name of author>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

Also add information on how to contact you by electronic and paper mail.

  If the program does terminal interaction, make it output a short
notice like this when it starts in an interactive mode:

    <program>  Copyright (C) <year>  <name of author>
    This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details.

The hypothetical commands `show w' and `show c' should show the appropriate
parts of the General Public License.  Of course, your program's commands
might be different; for a GUI interface, you would use an "about box".

  You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU GPL, see
<https://www.gnu.org/licenses/>.

  The GNU General Public License does not permit incorporating your program
into proprietary programs.  If your program is a subroutine library, you
may consider it more useful to permit linking proprietary applications with
the library.  If this is what you want to do, use the GNU Lesser General
Public License instead of this License.  But first, please read
<https://www.gnu.org/licenses/why-not-lgpl.html>.
'''
