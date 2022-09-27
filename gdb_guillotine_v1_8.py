# -*- coding: utf-8 -*-
#¸¸.·´¯`·.¸¸.·´¯`·.¸¸
# ║╚╔═╗╝║  │┌┘─└┐│  ▄█▀‾
# ======================== #
# Database Guillotine v1.8 #
# Nat Cagle 2022-09-27     #
# ======================== #
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
  - Add note to user that this only works on databases using the CTUU format. Does not work on CACI GDBs in the Scale format
    if self.params[5].value is not None:
        if self.params[5].value.endswith(".gdb") == False and self.params[5].value != "":
            self.params[5].value = self.params[5].value + ".gdb"
  - option to use custom query to extract data
  - checkbox list to choose specific feature classes to extract or not
  - checkbox for 50k LOC Features


####
Fixed validation bug. If the custom SQL query option was checked, the default query parameter value deleted, and the custom SQL query option then unchecked, it would lock the tool until the option was rechecked and any value assigned to the parameter. It could then be deactivated again and the tool could continue without needed a valid query.

add option for final delivery that pulls everything in the GDB like tables and extra datasets
####


## Recent Changes
  - option to use existing blank GDB
  - input name of GDB output
  - new param for folder location
  - option to use full extent of data instead of AOI
  - re-add if ap.exists    if doesn't exist throw warning to user that the output gdb provided doesn't match the schema of the data being copied. progress will continue with feature classes that match the schema. output which feature classes don't match at end of run.
  - Added Tool Help section for each parameter.

2022-09-06
  - Fixed lingering og_oid field for split multipart featureclasses
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

task_summary()

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
