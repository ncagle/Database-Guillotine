# =================================== #
# Database Guillotine - Scale and AOI #
# Nat Cagle 2022-03-31                #
# =================================== #
import arcpy
from arcpy import AddMessage as write
from datetime import datetime as dt
import os
from collections import defaultdict
import sys
import time
import re


#            _________________________________
#           | Copies a local or SDE TDS to a  |
#           | new database, extracts the data |
#           | based on a provided scale, and  |
#           | splits features along the       |
#           | provided AOI boundary.          |
#      _    /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#   __(.)< ‾
#~~~\___)~~~



''''''''' Parameters '''''''''
## [0] "Did you log into the SDE? - Boolean"
## [1] "TDS - Workspace"
TDS = arcpy.GetParameterAsText(1) # Path to TDS
## [2] "Create new GDB with schema from input - Boolean"
create_GDB = arcpy.GetParameter(2)
## [3] "Folder for local GDB - Folder"
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
## [10] "Extract Specific Feature Classes - Boolean"
extract = arcpy.GetParameter(10)
## [11] "Extract: - Feature Class"
extract_fc = arcpy.GetParameterAsText(11)
## [12] "Exclude Specific Feature Classes - Boolean"
vogon = arcpy.GetParameter(12)
## [13] "Exclude: - Feature Class"
vogon_fc = arcpy.GetParameterAsText(13)
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
def update_row_tuple(irow, index, val): # Update a specific row field inside an insert cursor
	# Usually used for updating geometry before copying the row
	# For short tuples, slicing and concatenation is faster
	# But performance of long tuples is more consistently efficient with list conversion
	#geometry_obj = SHAPE@.method()
	#irow = update_row_tuple(irow, -1, geometry_obj)
	#icursor.insertRow(irow)
	edit_row = list(irow)
	edit_row[index] = val
	return tuple(edit_row)

def make_field_list(dsc): # Construct a list of proper feature class fields
	# Sanitizes Geometry fields to work on File Geodatabases or SDE Connections
	#field_list = make_field_list(describe_obj)
	fields = dsc.fields # List of all fc fields
	out_fields = [dsc.OIDFieldName, dsc.lengthFieldName, dsc.areaFieldName] # List Geometry and OID fields to be removed
	# Construct sanitized list of field names
	field_list = [field.name for field in fields if field.type not in ['Geometry'] and field.name not in out_fields]
	# Further cleaning to account for other possible geometry standards including ST_Geometry
	field_list[:] = [x for x in field_list if 'Shape' not in x and 'shape' not in x and 'Area' not in x and 'area' not in x and 'Length' not in x and 'length' not in x]
	# Add OID@ token to index[-2] and Shape@ geometry token to index[-1]
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

def make_gdb_schema(TDS, xml_out, out_folder, gdb_name, out_path): # Creates a new file GDB with an empty schema identical to the source
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
	out_tds = os.path.join(out_path, "TDS")
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

def fractinull(shp, fc_name, oid): # Checks for NULL geometry
	# If geometry is NULL, output the feature class and OID and continue to next feature
	#fractinull(geometry_obj, fc_name, oid)
	oh_dear_god = False
	if shp is None:
		oh_dear_god = True
		write("{0} feature OID: {1} found with NULL geometry. Skipping transfer.".format(fc_name, oid))
	return oh_dear_god

def crosses_insert(shp, aoi, boundary, dimension, icursor, row): # Inserts feature if the geometry crosses the AOI boundary after clipping it to be within
	# Crosses() geometry method can only compare line-line or polygon-line, NOT polygon-polygon
	# So to check if a polygon crosses another polygon, one of them must be a polyline object made with the boundary() geometry method
	#crosses_insert(input_geom_obj, aoi_geom_obj, extent_geom_obj, insert_cursor, insert_row)
	criss = False
	if shp.crosses(boundary): # Geometry method checks if the feature geometry crosses the AOI polygon boundary
		criss = True
		clip_shp = shp.intersect(aoi, dimension) # Feature geometry is clipped the intersection overlap of the AOI polygon and the feature
		row = update_row_tuple(row, -1, clip_shp) # Updates the SHAPE@ token with the newly clipped geometry object
		icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB after geometry clip and replace
	return criss

def within_insert(shp, aoi, icursor, row): # Inserts feature if the geometry is within the AOI
	#within_insert(input_geom_obj, aoi_geom_obj, insert_cursor, insert_row)
	inner_peace = False
	if shp.within(aoi, "CLEMENTINI"): # Geometry method checks if the feature geometry is within the AOI polygon
		inner_peace = True
		icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB
	return inner_peace

def split_ends(icursor, fc_name, start_runtime, f_count, total): # Clean up, runtime, and feature count outputs
	#split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats)
	del icursor # Close the insert cursor for the current feature class
	finish_cursor_search = dt.now() # Stop runtime clock
	write("Time elapsed to search {0}: {1}".format(fc_name, runtime(start_runtime, finish_cursor_search)))
	write("Copied {0} of {1} {2} features local".format(f_count, total, fc_name))


''''''''' Main '''''''''
# Get name of input database for either SDE or file GDB to construct output variables
gdb_name_raw = re.findall(r"[\w']+", os.path.basename(os.path.split(TDS)[0]))[0] # Detailed breakdown in pull_local.trash.py
gdb_name = gdb_name_raw + "_" + timestamp
xml_out = os.path.join(out_folder, gdb_name_raw + "_schema.xml")
out_path = os.path.join(out_folder, gdb_name + ".gdb")
write("\nTDS input: {0}".format(TDS))
write("\nSplit GDB output path: {0}\n".format(out_path))


make_gdb_schema(TDS, xml_out, out_folder, gdb_name, out_path)
arcpy.env.workspace = TDS


#start_copy = dt.now()
fc_walk = arcpy.da.Walk(TDS, "FeatureClass")
for dirpath, dirnames, filenames in fc_walk: # No dirnames present. Use Walk to navigate inconsistent SDEs. Also works on local.
	filenames.sort()
	write("\nFCs loaded from input GDB: {0}".format(len(filenames)))
	for fc in filenames:
		total_feats = get_count(fc)
		if total_feats == 0:
			write("{0} is empty".format(fc))
			continue

		dsc = arcpy.Describe(fc)
		fc_type = dsc.shapeType # Polygon, Polyline, Point, Multipoint, MultiPatch
		input_fc = dsc.catalogPath # T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticCrv
		local_fc, fc_name = get_local(out_path, dsc)
		query = """{0} >= {1}""".format(arcpy.AddFieldDelimiters(fc, 'zi026_ctuu'), query_scale)
		field_list = make_field_list(dsc)

		# Create Search and Insert Cursor
		write("Checking {0} features".format(fc_name))
		start_cursor_search = dt.now()
		f_count = 0
		local_icursor = arcpy.da.InsertCursor(local_fc, field_list)
		# AOI, fc, input_fc, field_list, query, input_shp, fc_name, input_oid, in_shp_cent, aoi_shp, local_icursor, fc_type, aoi_extent, aoi_line
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
					for irow in input_scursor: # Loop thru each Metadata or Resource surface in the input feature class
						input_shp = irow[-1] # Geometry object of current feature
						input_oid = irow[-2] # OID object of current row
						if fractinull(input_shp, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
							continue
						# Metadata and Resource specific method
						in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current feature
						if within_insert(in_shp_cent, aoi_shp, local_icursor, irow): # If feature's centroid is within the AOI, insert it into the new GDB
							f_count +=1
							continue
				split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats) # Close insert cursor, output runtime, output total features copied, and continue to next feature class
			else: # Proceed assuming normal TDS feature classes
				with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields and user defined query
					if fc_type == 'Point': # Points are either within or without the AOI
						for irow in input_scursor: # Loop thru each point in the input feature class
							input_shp = irow[-1] # Geometry object of current point
							input_oid = irow[-2] # OID object of current row
							if fractinull(input_shp, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
								continue
							# Point specific method
							in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current point
							if within_insert(in_shp_cent, aoi_shp, local_icursor, irow): # If point is within the AOI, insert it into the new GDB
								f_count +=1
								continue
					if fc_type == 'Polyline': # Lines can cross the AOI boundary or be fully within
						#aoi_extent = aoi_shp.extent # AOI extent object is used to clip line geometries
						aoi_line = aoi_shp.boundary() # Line geometry object of the AOI boundary
						for irow in input_scursor: # Loop thru each point in the input feature class
							input_shp = irow[-1] # Geometry object of current line
							input_oid = irow[-2] # OID object of current row
							if fractinull(input_shp, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
								continue
							# Line specific method
							if crosses_insert(input_shp, aoi_shp, aoi_line, 2, local_icursor, irow): # Check if line crosses AOI before within then clip, insert, and continue
								f_count +=1
								continue
							if within_insert(input_shp, aoi_shp, local_icursor, irow): # If line doesn't cross AOI and is within(Clementini) then insert and continue
								f_count +=1
								continue
					if fc_type == 'Polygon': # Polygons can cross the AOI boundary or be fully within
						#aoi_extent = aoi_shp.extent # AOI extent object is used to clip polygon geometries
						aoi_line = aoi_shp.boundary() # Line geometry object of the AOI boundary
						for irow in input_scursor: # Loop thru each point in the input feature class
							input_shp = irow[-1] # Geometry object of current polygon
							input_oid = irow[-2] # OID object of current row
							if fractinull(input_shp, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
								continue
							# Polygon specific method
							in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current polygon
							if crosses_insert(input_shp, aoi_shp, aoi_line, 4, local_icursor, irow): # Check if polygon crosses AOI before within then clip, insert, and continue
								f_count +=1
								continue
							if within_insert(in_shp_cent, aoi_shp, local_icursor, irow): # If polygon doesn't cross AOI and its centroid is within(Clementini) then insert and continue
								f_count +=1
								continue
				split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats) # Close insert cursor, output runtime, output total features copied, and continue to next feature class

write("\n*** Please run the Hypernova Burst Multipart tool in the Finishing Tool Suite after splitting. ***\n")
