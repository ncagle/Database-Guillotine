# ======================================== #
# Database Guillotine - Scale and AOI v1.3 #
# Nat Cagle 2022-05-02                     #
# ======================================== #
import arcpy
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
  - Use validation logic from AO tool to add .gdb to the name that the user provides for the extracted copy
    if self.params[5].value is not None:
        if self.params[5].value.endswith(".gdb") == False and self.params[5].value != "":
            self.params[5].value = self.params[5].value + ".gdb"
  - option to use existing blank GDB
  - option to use full extent of data instead of AOI
  - option to use custom query to extract data
  - checkbox list to choose specific feature classes to extract or not

    if self.params[0].value == 'Energy Sector Model':
        if not self.params[6].value:
            self.params[6].setErrorMessage('Value is required')
        else:
            self.params[6].clearMessage()


    if self.params[1].hasBeenValidated == False:
	    if self.params[1].valueAsText is not None:
	        if arcpy.Exists(self.params[1].valueAsText):
	                arcpy.env.workspace = self.params[1].valueAsText
	                fc_list = arcpy.ListFeatureClasses()
	                self.params[15].filter.list = fc_list
	                self.params[15].value = fc_list
	        else:
	                arcpy.env.workspace = self.params[1].valueAsText
	                fc_list = arcpy.ListFeatureClasses()
	                self.params[15].filter.list = fc_list
	                self.params[15].value = fc_list

    if self.params[3].enabled == 1:
        if self.params[3].value == 'C:\Projects':
            self.params[3].setErrorMessage('Value is required')
    else:
        self.params[3].clearMessage()

    if self.params[4].enabled == 1:
        if self.params[4].value == 'C:\Projects':
            self.params[4].setErrorMessage('Value is required')
    else:
        self.params[4].clearMessage()

    if self.params[6].enabled == 1:
        if self.params[6].value == 'C:\Projects':
            self.params[6].setErrorMessage('Value is required')
    else:
        self.params[6].clearMessage()

    if self.params[9].enabled == 1:
        if self.params[9].value == "Ex: 'HGT' >= 46":
            self.params[9].setErrorMessage('Value is required')
    else:
        self.params[9].clearMessage()

## Recent Changes
  -

[u'AeronauticCrv', u'AeronauticPnt', u'AeronauticSrf', u'AgriculturePnt', u'AgricultureSrf', u'BoundaryPnt', u'CultureCrv', u'CulturePnt', u'CultureSrf', u'FacilityPnt', u'FacilitySrf', u'HydroAidNavigationPnt', u'HydroAidNavigationSrf', u'HydrographyCrv', u'HydrographyPnt', u'HydrographySrf', u'IndustryCrv', u'IndustryPnt', u'IndustrySrf', u'InformationCrv', u'InformationPnt', u'InformationSrf', u'MilitaryCrv', u'MilitaryPnt', u'MilitarySrf', u'PhysiographyCrv', u'PhysiographyPnt', u'PhysiographySrf', u'PortHarbourCrv', u'PortHarbourPnt', u'PortHarbourSrf', u'RecreationCrv', u'RecreationPnt', u'RecreationSrf', u'SettlementPnt', u'SettlementSrf', u'StoragePnt', u'StorageSrf', u'StructureCrv', u'StructurePnt', u'StructureSrf', u'TransportationGroundCrv', u'TransportationGroundPnt', u'TransportationGroundSrf', u'TransportationWaterCrv', u'TransportationWaterPnt', u'TransportationWaterSrf', u'UtilityInfrastructureCrv', u'UtilityInfrastructurePnt', u'UtilityInfrastructureSrf', u'VegetationCrv', u'VegetationPnt', u'VegetationSrf', u'MetadataSrf', u'ResourceSrf']

[u'AeronauticCrv', u'AeronauticPnt', u'AeronauticSrf', u'AgriculturePnt', u'AgricultureSrf', u'BoundaryPnt', u'CultureCrv', u'CulturePnt', u'CultureSrf', u'FacilityPnt', u'FacilitySrf', u'HydroAidNavigationPnt', u'HydroAidNavigationSrf', u'HydrographyCrv', u'HydrographyPnt', u'HydrographySrf', u'IndustryCrv', u'IndustryPnt', u'IndustrySrf', u'InformationCrv', u'InformationPnt', u'InformationSrf', u'MilitaryCrv', u'MilitaryPnt', u'MilitarySrf', u'PhysiographyCrv', u'PhysiographyPnt', u'PhysiographySrf', u'PortHarbourCrv', u'PortHarbourPnt', u'PortHarbourSrf', u'RecreationCrv', u'RecreationPnt', u'RecreationSrf', u'SettlementPnt', u'SettlementSrf', u'StoragePnt', u'StorageSrf', u'StructureCrv', u'StructurePnt', u'StructureSrf', u'TransportationGroundCrv', u'TransportationGroundPnt', u'TransportationGroundSrf', u'TransportationWaterCrv', u'TransportationWaterPnt', u'TransportationWaterSrf', u'UtilityInfrastructureCrv', u'UtilityInfrastructurePnt', u'UtilityInfrastructureSrf', u'VegetationCrv', u'VegetationPnt', u'VegetationSrf', u'MetadataSrf', u'ResourceSrf']

'''



''''''''' Parameters '''''''''
# Remind user to check their connection for the right location (jayhawk, kensington) and that they logged into the server
# Ask user if this is an SDE connection
# if so, enable parameter asking if they logged in and are in the right connection location
## [0] "If copying from SDE, did you log in? - Boolean"
## [1] "TDS - Workspace"
TDS = arcpy.GetParameterAsText(1) # Path to TDS
## [2] "Create new GDB with schema from input - Boolean"
create_GDB = arcpy.GetParameter(2)
## [3] "Location and Filename of output GDB (Ex: C:\Projects\Client\TPC\Custom_Name_TPC_250k.gdb) - Folder"
out_folder = arcpy.GetParameterAsText(3) # Path to folder where the local GDB will be created
## [4] "Blank GDB with schema - Workspace"
existing_GDB = arcpy.GetParameterAsText(4)
## [5] "Use Full Extent (No AOI) - Boolean"
no_AOI = arcpy.GetParameter(5)
## [6] "AOI (Merged into single feature) - Feature Class"
AOI = arcpy.GetParameterAsText(6) # AOI used to split data
## [7] "Extract Scale: ZI026_CTUU >= - String"
query_scale = arcpy.GetParameter(7) # Scale value from list for query
## [8] "Extract data using custom query - Boolean"
manual = arcpy.GetParameter(8)
## [9] "Custom Query (Ex: 'HGT' >= 46) - String"
query_manual = arcpy.GetParameterAsText(9) # Custom query input
## [10] "Extract Specific Feature Classes - String"
specific = arcpy.GetParameter(10)
## [11] "Extract Specific Feature Classes - String"
fc_list_param = arcpy.GetParameter(11)
# Get current time for gdb timestamp
timestamp = dt.now().strftime("%Y%b%d_%H%M")
arcpy.env.workspace = TDS
arcpy.env.overwriteOutput = True




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

def runtime(start,finish): # Time a process or code block
	# Add a start and finish variable markers surrounding the code to be timed
	#from datetime import datetime as dt
	#start/finish = dt.now()
	# Returns string of formatted elapsed time between start and finish markers
	time_delta = (finish - start).total_seconds()
	h = int(time_delta/(60*60))
	m = int((time_delta%(60*60))/60)
	s = time_delta%60.
	time_elapsed = "{}:{:>02}:{:>05.4f}".format(h, m, s) # 00:00:00.0000
	return time_elapsed

def get_count(fc_layer): # Returns feature count
	results = int(arcpy.GetCount_management(fc_layer).getOutput(0))
	return results


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
	arcpy.ExportXMLWorkspaceDocument_management(TDS, xml_out, "SCHEMA_ONLY", "BINARY", "METADATA")
	write("Creating File GDB")
	arcpy.CreateFileGDB_management(out_folder, gdb_name, "CURRENT")
	write("Importing XML workspace")
	arcpy.ImportXMLWorkspaceDocument_management(out_path, xml_out, "SCHEMA_ONLY")
	write("Local blank GDB with schema successfully created")
	arcpy.env.workspace = out_tds
	featureclass = arcpy.ListFeatureClasses()
	featureclass.sort()
	for fc in featureclass:
		desc = arcpy.Describe(fc)
		if desc.editorTrackingEnabled:
			try:
				arcpy.DisableEditorTracking_management(fc)
				#write("{0} - Disabled".format(fc))
			except:
				write("Error disabling editor tracking for {0}. Please check the data manually and try again.".format(fc))
				pass
	write("Editor Tracking has been disabled on local copy.")
	os.remove(xml_out)
	arcpy.RefreshCatalog(out_folder)
	finish_schema = dt.now()
	write("Time to create local GDB with schema: {0}".format(runtime(start_schema,finish_schema)))

def fractinull(shp):#, fc_name, oid): # Checks for NULL geometry
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
	#oid = row[-2]
	fc_type = shp.type
	if fc_type != 'polyline':
		shp = shp.trueCentroid # Gets the centroid of the current feature
	if shp.within(aoi, "CLEMENTINI"): # Geometry method checks if the feature geometry is within the AOI polygon
		inner_peace = True
		#write_info("irow in within_insert normal", row)
		if og_oid_row:
			row = add_row_tuple(row, -3, None)
			#write_info("irow with NULL og_oid", row)
			icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB
		else:
			icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB
	return inner_peace


''''''''' Main '''''''''
# Get name of input database for either SDE or file GDB to construct output variables
gdb_name_raw = re.findall(r"[\w']+", os.path.basename(os.path.split(TDS)[0]))[0] # Detailed breakdown in pull_local.trash.py
gdb_name = gdb_name_raw + "_" + timestamp
xml_out = os.path.join(out_folder, gdb_name_raw + "_schema.xml")
#if create_GDB True
out_path = os.path.join(out_folder, gdb_name + ".gdb")
#else out_path = existing_GDB
out_tds = os.path.join(out_path, "TDS")
write("\nTDS input: {0}".format(TDS))
write("\nSplit GDB output path: {0}\n".format(out_path))

#### add user input for gdb name
make_gdb_schema(TDS, xml_out, out_folder, gdb_name, out_path, out_tds)
arcpy.env.workspace = TDS


fc_walk = arcpy.da.Walk(TDS, "FeatureClass")
for dirpath, dirnames, filenames in fc_walk: # No dirnames present. Use Walk to navigate inconsistent SDEs. Also works on local.
	filenames.sort()
	#def vogon_constructor_fleet(): # Said to hang in the air "the way that bricks don't"
	#if vogon: ## [12] "Exclude Specific Feature Classes - Boolean"
	#	filenames[:] = [x for x in filenames if 'StructurePnt' not in x and 'StructureSrf' not in x]
	in_class = os.path.join(out_tds, "multi")
	out_class = os.path.join(out_tds, "single")
	split_dict = {}

	write("FCs loaded from input GDB: {0}\n".format(len(filenames)))
	for fc in filenames:
		total_feats = get_count(fc)
		if total_feats == 0:
			write("{0} is empty".format(fc))
			continue

		dsc = arcpy.Describe(fc)
		fc_type = dsc.shapeType # Polygon, Polyline, Point, Multipoint, MultiPatch
		input_fc = dsc.catalogPath # T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticCrv
		oid_field = dsc.OIDFieldName # Get the OID field name.
		local_fc, fc_name = get_local(out_path, dsc)
		field_list = make_field_list(dsc)
		og_oid = 'og_oid'
		f_count = 0
		criss = False
		start_cursor_search = dt.now()

		#allow for any field query to be made
		#if query_manual not in listfields(fc):
		#    continue
		query = """{0} >= {1}""".format(arcpy.AddFieldDelimiters(fc, 'zi026_ctuu'), query_scale)
		#write_info('query', query)

		### re-add if arcpy.exists    if doesn't exist throw warning to user that the output gdb provided doesn't match the schema of the data being copied. progress will continue with feature classes that match the schema. output which feature classes don't match at end of run.

		# Create Search and Insert Cursor
		write("Checking {0} features".format(fc_name))
		#local_icursor = arcpy.da.InsertCursor(local_fc, field_list)
		with arcpy.da.SearchCursor(AOI, ['SHAPE@']) as aoi_cur:
			aoi_next = aoi_cur.next()
			aoi_shp = aoi_next[0]
			if aoi_shp is None: # Must check for NULL geometry before using any geometry methods
				write("NULL geometry found in input AOI. Please check the AOI polygon and try again.")
				sys.exit(0) # If the AOI polygon has NULL geometry, exit the tool. The AOI needs to be checked by the user
			if 'MetadataSrf' in fc or 'ResourceSrf' in fc: # Check for these first since they are a special case
				query = '' # Metadata and Resource surfaces have different fields. Copy them regardless of query. Can be excluded in Advanced Options.
				write("Found {0}. Ignoring ctuu query and copying all within provided AOI.".format(fc))
				with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields
					with arcpy.da.InsertCursor(local_fc, field_list) as local_icursor:
						for irow in input_scursor: # Loop thru each Metadata or Resource surface in the input feature class
							input_shp = irow[-1] # Geometry object of current feature
							#input_oid = irow[-2] # OID object of current row
							if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
								continue
							# Metadata and Resource specific method
							#in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current feature
							if within_insert(aoi_shp, local_icursor, irow, False): # If feature's centroid is within the AOI, insert it into the new GDB
								f_count +=1
								continue
				split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats) # Close insert cursor, output runtime, output total features copied, and continue to next feature class
			else: # Proceed assuming normal TDS feature classes
				with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields and user defined query
					if fc_type == 'Point': # Points are either within or without the AOI
						#with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields and user defined query
						with arcpy.da.InsertCursor(local_fc, field_list) as local_icursor:
							for irow in input_scursor: # Loop thru each point in the input feature class
								input_shp = irow[-1] # Geometry object of current point
								#input_oid = irow[-2] # OID object of current row
								if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
									continue
								# Point specific method
								#in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current point
								if within_insert(aoi_shp, local_icursor, irow, False): # If point is within the AOI, insert it into the new GDB
									f_count +=1
									continue
					if fc_type == 'Polyline': # Lines can cross the AOI boundary or be fully within
						#arcpy.AddField_management(input_fc, og_oid, "double")
						#with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields and user defined query
						arcpy.AddField_management(local_fc, og_oid, "double")
						field_list.insert(-2, og_oid)
						#og_oid_row = True
						#aoi_line = aoi_shp.boundary() # Line geometry object of the AOI boundary
						#write_info("field_list updated", field_list)
						with arcpy.da.InsertCursor(local_fc, field_list) as local_icursor:
							for irow in input_scursor: # Loop thru each point in the input feature class
								input_shp = irow[-1] # Geometry object of current line
								input_oid = irow[-2] # OID object of current row
								if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
									continue
								# Line specific method
								if crosses_insert(aoi_shp, local_icursor, irow): # Check if line crosses AOI before within then clip, insert, and continue
									#sys.exit(0)
									#oid_list.append(input_oid)
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
						#arcpy.AddField_management(input_fc, og_oid, "double")
						#with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields and user defined query
						arcpy.AddField_management(local_fc, og_oid, "double")
						field_list.insert(-2, og_oid)
						#og_oid_row = True
						aoi_line = aoi_shp.boundary() # Line geometry object of the AOI boundary
						#temp_fields = [field.name for field in arcpy.ListFields(local_fc)]
						#write_info("list fields after adding 'og_oid'", temp_fields)
						#write_info("field_list updated", field_list)
						with arcpy.da.InsertCursor(local_fc, field_list) as local_icursor:
							for irow in input_scursor: # Loop thru each point in the input feature class
								input_shp = irow[-1] # Geometry object of current polygon
								input_oid = irow[-2] # OID object of current row
								if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
									continue
								# Polygon specific method
								#in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current polygon
								if crosses_insert(aoi_shp, local_icursor, irow): # Check if polygon crosses AOI before within then clip, insert, and continue
									#sys.exit(0)
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
		# Clean up, runtime, and feature count outputs
		finish_cursor_search = dt.now() # Stop runtime clock
		write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_name))
		write("Time elapsed to search {0}: {1}".format(fc_name, runtime(start_cursor_search, finish_cursor_search)))

		# Explode multipart features that crossed the boundary
		if criss:
			write("\nSplit features at AOI boundary. Exploding the resultant geometries...")
			oid_query = """{0} IS NOT NULL""".format(arcpy.AddFieldDelimiters(local_fc, og_oid))
			# Create a new feature class to put the multipart features in to decrease processing time. fields based on original fc template
			arcpy.CreateFeatureclass_management(out_tds, "multi", fc_type, local_fc, "", "", out_tds)
			# Add multipart features to new feature class based on OID
			incount = 0
			with arcpy.da.SearchCursor(local_fc, field_list, oid_query) as scursor: # Search current fc using for only OIDs that are in the multipart oid_list.
				with arcpy.da.InsertCursor(in_class, field_list) as icursor: # Insert cursor for the newly created feature class with the same fields as scursor
					for srow in scursor:
						incount +=1
						icursor.insertRow(srow) # Insert that feature row into the temp feature class, in_class "multi"
			write("Added {0} features to in_class, running multipart to singlepart".format(incount))
			arcpy.MultipartToSinglepart_management(in_class, out_class) # New feature class output of just the converted single parts
			with arcpy.da.UpdateCursor(local_fc, og_oid, oid_query) as ucursor: # Deletes features in fc that have OIDs flagged as multiparts from the oid_list
				for urow in ucursor:
					write("Deleting feature OID {0} in local_fc".format(urow[0]))
					ucursor.deleteRow()
			with arcpy.da.UpdateCursor(out_class, 'ufi') as ucursor: # Populate the ufi for the newly created singlepart features
				for urow in ucursor:
					urow[0] = str(uuid.uuid4())
					ucursor.updateRow(urow)
			# out_class is one field shorter than the local_fc and they need to match to insert the row
			field_list.remove('globalid') # local_fc has a 'globalid' field that out_class does not. out_class also has an 'ORIG_FID' field that isn't in local_fc, but we only need to remove 'globalid' since it doesn't exist in out_class. The lengths should match and be able to insert
			with arcpy.da.SearchCursor(out_class, field_list) as scursor: # Insert new rows in fc from MultipartToSinglepart output out_class
				with arcpy.da.InsertCursor(local_fc, field_list) as icursor:
					for srow in scursor:
						write("Inserting feature OID {0} from out_class to local_fc after explode.".format(srow[-3]))
						icursor.insertRow(srow)
			try:
				write("Deleting og_oid field from local_fc\nDeleting in_class and out_class from current loop")
				arcpy.DeleteField_management(local_fc, og_oid)
				#arcpy.DeleteField_management(input_fc, og_oid)
				arcpy.Delete_management(in_class)
				arcpy.Delete_management(out_class)
			except:
				write("No in_class or out_class created. Or processing layers have already been cleaned up. Continuing...")
				pass
			write("Finished exploding split features in {0}".format(fc_name))
	arcpy.RefreshCatalog(out_folder)
	write("\n\nHere is a list of source database feature OIDs that crossed the AOI boundary and were split in the output.")
	write("Use this with Select by Attribute if you wish to confirm that features were split properly.\n")
	split_list = split_dict.keys()
	split_list.sort()
	for fc in split_list:
		write("{0}:\n{1}\n".format(fc, split_dict[fc]))
	write("\n")
