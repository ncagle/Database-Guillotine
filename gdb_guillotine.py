# ============================= #
# Database Guillotine - Scale and AOI #
# Nat Cagle 2022-02-25          #
# ============================= #
import arcpy
from arcpy import AddMessage as write
from datetime import datetime as dt
import os
from collections import defaultdict
import sys
import time


#            ________________________________
#           | Runs Populate FCode, Calculate |
#           | features.                      |
#      _    /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#   __(.)< ‾
#~~~\___)~~~



####### Database Guillotine - Scale and AOI #######

### Example of getting parameters in .pyt python toolbox as opposed to arcpy.GetParameterAsText(0) in python script tools
# def get_Parameter_Info(self):
#     # Define parameter definitions
#     param0 = arcpy._Parameter(
#         displayName="Input workspace",
#         name="workspace",
#         datatype="DEWorkspace",
#         parameterType="Required",
#         direction="Input")
#     param1 = arcpy._Parameter(
#         displayName="Input classified raster",
#         name="input_raster",
#         datatype="GPRasterLayer",
#         parameterType="Required",
#         direction="Input")
#     param2 = arcpy._Parameter(
#         displayName="Input features",
#         name="input_features",
#         datatype="GPFeatureLayer",
#         parameterType="Required",
#         direction="Input")
#
#
#     params = [param0, param1, param2]
#
#     return params
#
#
# toggled inputs are set to optional but throw error if not filled in
# if self.params[2].value == True:
#     self.params[3].enabled = 1
#     self.params[3].setIDMessage("ERROR", 735, self.params[3].displayName)
#     self.params[4].enabled = 0
#     self.params[4].clearMessage()
# else:
#     self.params[3].enabled = 0
#     self.params[3].clearMessage()
#     self.params[4].enabled = 1
#     self.params[4].setIDMessage("ERROR", 735, self.params[4].displayName)
#
#
# def _execute_(self, parameters, messages):
#     # The source code of the tool.
#     # Define some paths/variables
#     outWorkspace = parameters[0].valueAsText
#     arcpy.env.workspace = outWorkspace
#     output_location = parameters[0].valueAsText
#     input_raster = parameters[1].valueAsText
#     input_features = parameters[2].valueAsText

# User parameters
# Remind user to check their connection for the right location (jayhawk, kensington) and that they logged into the server
# Ask user if this is an SDE connection
# if so, enable parameter asking if they logged in and are in the right connection location
## [0] "Did you log into the SDE? - Boolean"
## [1] "TDS - Workspace"
TDS = arcpy.GetParameterAsText(1) # Path to TDS
## [2] "Create new GDB with schema from input - Boolean"
create_GDB = arcpy.GetParameter(2)
## [3] "Folder for local GDB - Folder"
out_folder = arcpy.GetParameterAsText(3) # Path to folder where the local GDB will be created
## [4] "Blank GDB with schema - Workspace"
existing_GDB = arcpy.GetParameterAsText(4)
# [5] "Use Full Extent (No AOI) - Boolean"
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
arcpy.env.workspace = TDS
arcpy.env.overwriteOutput = True
# Get current time for gdb timestamp
timestamp = dt.now().strftime("%Y%b%d_%H%M")



# Write information for given variable
def write_info(name,var): # write_info('var_name',var)
	write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	write("Debug info for {0}:".format(name))
	write("   Variable Type: {0}".format(type(var)))
	if type(var) is str:
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

def runtime(start,finish):
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

def update_row_tuple(urow, index, val):
	# For short tuples, slicing and concatenation is faster.
	# But performance of long tuples is more consistently efficient with list conversion.
	edit_row = list(urow)
	edit_row[index] = val
	return tuple(edit_row)

def get_count(fc_layer):
    results = int(arcpy.GetCount_management(fc_layer).getOutput(0))
    return results


# Sanitizing GDB name
# "T:\GEOINT\FEATURE DATA\Hexagon 250-251\SDE_Connections\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS"
tds_split = TDS.split("\\") # ['T:', 'GEOINT', 'FEATURE DATA', 'Hexagon 250-251', 'SDE_Connections', 'hexagon250_e04a_surge2.sde', 'hexagon250_e04a_surge2.sde.TDS']
tds_split.pop() # hexagon250_e04a_surge2.sde.TDS
gdb_file = tds_split.pop() # hexagon250_e04a_surge2.sde
name_list = gdb_file.split(".") # ['hexagon250_e04a_surge2', 'sde']
gdb_name_raw = name_list[0] # hexagon250_e04a_surge2
gdb_name = gdb_name_raw + "_" + timestamp # hexagon250_e04a_surge2_2022Mar28_1608
#gdb_ext = gdb_name + ".gdb" # hexagon250_e04a_surge2.gdb
#out_path = "{0}\\{1}.gdb".format(out_folder, gdb_name) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2.gdb
out_path = os.path.join(out_folder, gdb_name + ".gdb")
#xml_out = "{0}\\{1}_schema.xml".format(out_folder, gdb_name) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2_schema.xml
xml_out = os.path.join(out_folder, gdb_name + "_schema.xml")
#out_tds = "{0}\\TDS".format(out_path) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2.gdb\TDS
out_tds = os.path.join(out_path, "TDS")
write("\nTDS input: {0}".format(TDS))
write("\nSplit GDB output path: {0}\n".format(out_path))


start_schema = dt.now()
write("Exporting XML workspace")
arcpy.ExportXMLWorkspaceDocument_management(TDS, xml_out, "SCHEMA_ONLY", "BINARY", "METADATA")
write("Creating File GDB")
arcpy.CreateFileGDB_management(out_folder, gdb_name, "CURRENT")
write("Importing XML workspace")
arcpy.ImportXMLWorkspaceDocument_management(out_path, xml_out, "SCHEMA_ONLY")
write("Local blank GDB with schema successfully created")
os.remove(xml_out)
finish_schema = dt.now()
write("Time to create local GDB with schema: {0}".format(runtime(start_schema,finish_schema)))


start_copy = dt.now()
fc_walk = arcpy.da.Walk(TDS, "FeatureClass")
for dirpath, dirnames, filenames in fc_walk: # No dirnames present
	filenames.sort()
	if vogon:
		filenames[:] = [x for x in filenames if 'StructurePnt' not in x and 'StructureSrf' not in x]
	write("\nFCs loaded from input GDB: {0}".format(len(filenames)))
	for fc in filenames: # hexagon250_e04a_surge2.sde.AeronauticCrv
		if get_count(fc) == 0:
			write("{0} is empty".format(fc))
			continue
		#allow for any field query to be made
		#if query_manual not in listfields(fc):
		#    continue
		query = """{0} >= {1}""".format(arcpy.AddFieldDelimiters(fc, 'zi026_ctuu'), query_scale)
		#write_info('query', query)
		fc_split = fc.split(".")
		fc_strip = fc_split.pop() # AeronauticCrv
		input_fc = os.path.join(TDS, fc) # T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticCrv
		local_fc = os.path.join(out_tds, fc_strip) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2_timestamp.gdb\TDS\AeronauticCrv
		if arcpy.Exists(local_fc):
			write("Checking {0} features".format(fc_strip))
			# Collect all fields except the Geometry and OID fields
			dsc = arcpy.Describe(fc)
			fc_type = dsc.shapeType # Polygon, Polyline, Point, Multipoint, MultiPatch
			fields = dsc.fields
			out_fields = [dsc.OIDFieldName, dsc.lengthFieldName, dsc.areaFieldName] # List of field names for OID, length, and area
			# Create list of field names that aren't Geometry or in out_fields
			field_list = [field.name for field in fields if field.type not in ['Geometry'] and field.name not in out_fields]
			# Make sure to clean the list for all possible geometry standards including ST_Geometry
			field_list[:] = [x for x in field_list if 'Shape' not in x and 'shape' not in x]
			field_list[:] = [x for x in field_list if 'area' not in x and 'length' not in x]
			field_list.append('OID@')
			field_list.append('SHAPE@') # add the full Geometry object
			write_info('field_list',field_list)

			# Create Search and Insert Cursor
			start_cursor_search = dt.now()
			f_count = 0
			local_icursor = arcpy.da.InsertCursor(local_fc, field_list)
			with arcpy.da.SearchCursor(AOI, ['SHAPE@']) as aoi_cur:
				aoi_next = aoi_cur.next()
				aoi_shp = aoi_next[0]
				aoi_extent = aoi_shp.extent
				aoi_line = aoi_shp.boundary()
				if 'MetadataSrf' in fc or 'ResourceSrf' in fc:
					write("Found {0}. Ignoring ctuu query and copying all within provided AOI.".format(fc))
					with arcpy.da.SearchCursor(input_fc, field_list) as input_scursor:
						for srow in input_scursor:
							input_shp = srow[-1]
							if input_shp is None:
								continue
							in_shp_cent = srow[-1].trueCentroid
							if in_shp_cent.within(aoi_shp, "CLEMENTINI"):
								local_icursor.insertRow(srow)
								f_count += 1
								continue
					del local_icursor
					finish_cursor_search = dt.now()
					write("Time elapsed to search {0}: {1}".format(fc_strip, runtime(start_cursor_search,finish_cursor_search)))
					write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_strip))
					continue
				with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor:
					if fc_type == 'Point':
						#write("{0} is a {1} shapeType".format(fc_strip, fc_type))
						for srow in input_scursor:
							input_shp = srow[-1]
							if input_shp is None:
								write("{0} feature OID: {1} found with NULL geometry. Skipping transfer.".format(fc_strip, srow[-2]))
								continue
							elif input_shp.within(aoi_shp, "CLEMENTINI"):
								local_icursor.insertRow(srow)
								f_count += 1
								continue
						del local_icursor
						finish_cursor_search = dt.now()
						write("Time elapsed to search {0}: {1}".format(fc_strip, runtime(start_cursor_search,finish_cursor_search)))
						write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_strip))
						continue
					if fc_type == 'Polyline':
						#write("{0} is a {1} shapeType".format(fc_strip, fc_type))
						for srow in input_scursor:
							input_shp = srow[-1]
							if input_shp is None:
								write("{0} feature OID: {1} found with NULL geometry. Skipping transfer.".format(fc_strip, srow[-2]))
								continue
							elif input_shp.crosses(aoi_shp):
								clip_shp = input_shp.clip(aoi_extent) # Current feature geometry object clipped by extent object of aoi geometry object
								srow = update_row_tuple(srow, -1, clip_shp)
								local_icursor.insertRow(srow)
								f_count += 1
								continue
							elif input_shp.within(aoi_shp, "CLEMENTINI"):
								local_icursor.insertRow(srow)
								f_count += 1
								continue
						del local_icursor
						finish_cursor_search = dt.now()
						write("Time elapsed to search {0}: {1}".format(fc_strip, runtime(start_cursor_search,finish_cursor_search)))
						write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_strip))
						continue
					if fc_type == 'Polygon':
						#write("{0} is a {1} shapeType".format(fc_strip, fc_type))
						for srow in input_scursor:
							input_shp = srow[-1]
							if input_shp is None:
								write("{0} feature OID: {1} found with NULL geometry. Skipping transfer.".format(fc_strip, srow[-2]))
								continue
							if input_shp.crosses(aoi_line):
								clip_shp = input_shp.clip(aoi_extent) # Current feature geometry object clipped by extent object of aoi geometry object
								srow = update_row_tuple(srow, -1, clip_shp)
								local_icursor.insertRow(srow)
								f_count += 1
								continue
							in_shp_cent = srow[-1].trueCentroid
							if in_shp_cent.within(aoi_shp, "CLEMENTINI"):
								local_icursor.insertRow(srow)
								f_count += 1
								continue
						del local_icursor
						finish_cursor_search = dt.now()
						write("Time elapsed to search {0}: {1}".format(fc_strip, runtime(start_cursor_search,finish_cursor_search)))
						write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_strip))
						continue
						# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
						# Debug info for input_scursor srow:
						#    Variable Type: <type 'tuple'>
						#    Assigned Value: (u'GB030', 100441, -999999.0, -999999, -999999, -999999, 106.0, -999999, 2, -999999, -999999, -999999, -999999, -999999, -999999, 11, -999999.0, -999999, u'noInformation', -999999, 13.0, -999999.0, -999999, -999999, -999999, u'noInformation', u'noInformation', 2, -999999, -999999, -999999, -999999, -999999, -999999, -999999, -999999, -999999, u'8A58E940-7F1C-4FF9-A4F4-98AB0D635A80', -999999, -999999, -999999, u'noInformation', 8.0, 19, u'noInformation', u'noInformation', u'noInformation', -999999, -999999, -999999, 5, -999999, -999999, 1, 3, u'ge:GENC:3:1-2:RUS', 5, 1, 250000, -999999.0, -999999.0, -999999.0, 30, u'2019-10-29', u'DigitalGlobe', 1001, -999999, u'noInformation', u'noInformation', u'Copyright 2021 by the National Geospatial-Intelligence Agency, U.S. Government. No domestic copyright claimed under Title 17 U.S.C. All rights reserved.', u'noInformation', u'U', u'noInformation', u'noInformation', u'USA', u'{711B7810-9A08-4B69-914A-712D8920F98E}', u'Prj8', None, None, None, None, None, None, None, <PointGeometry object at 0x156f9ab0[0x156f9540]>)
						# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

finish_copy = dt.now()
write("\nTotal time to copy features: {0}\n".format(runtime(start_copy, finish_copy))
