# ============================= #
# SDE Summoner & AOI Guillotine #
# Nat Cagle 2022-02-21          #
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
#           | Default Values, Integrate and  |
#           | Repair for hydro, trans, and   |
#           | utilities, updates UFI values, |
#           | deletes identical features,    |
#           | calculates geometry metrics,   |
#           | repairs all NULL geometries,   |
#           | and explodes all multipart     |
#           | features.                      |
#      _    /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#   __(.)< ‾
#~~~\___)~~~



# with arcpy.da.SearchCursor(out_class, fieldnames) as scursor:
# 	with arcpy.da.InsertCursor(fc, fieldnames) as icursor:
# 		for row in scursor:
# 			icursor.insertRow(row)

####### SDE Summoner & AOI Guillotine #######
### To-Do List ###
# Split by scale with dropdown selection (default)
# optional custom query string
# option to merge all aoi polygons
# option for full extent of data (no aoi)
# dropdown multilist to specify feature classes to extract

# User parameters
TDS = arcpy.GetParameterAsText(1) # Path to SDE TDS after confirming you logged in
out_folder = arcpy.GetParameterAsText(2) # Path to folder where the local GDB will be created
AOI = arcpy.GetParameterAsText(3) # AOI used to split data
query_field = arcpy.GetParameterAsText(4) # Query used to specify data in cursors eventually turn into dropdown for scale options and add option for manual query input that overrides original scale query
query_value = arcpy.GetParameter(5)
vogon = arcpy.GetParameter(6)
arcpy.env.workspace = TDS
arcpy.env.overwriteOutput = True


# Get current time for gdb timestamp
datetime_now = dt.now() #tz=timezone('America/Chicago'))
timestamp = datetime_now.strftime("%Y%b%d_%H%M")
write("My timestamp: hexagon250_e04a_surge2_{0}.gdb\n".format(timestamp))

# Write information for given variable
def write_info(name,var): # write_info('var_name',var)
	write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	write("Debug info for {0}:".format(name))
	write("   Variable Type: {0}".format(type(var)))
	write("   Assigned Value: {0}".format(var))
	write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

def runtime(start,finish):
	# Add a start and finish variable markers surrounding the code to be timed
	#start/finish = dt.now().time()
	# Returns string of total seconds elapsed between start and finish markers
	date = dt.now().date()
	dt_finish = dt.combine(date, finish)
	dt_start = dt.combine(date, start)
	time_delta = dt_finish - dt_start
	time_elapsed = str(time_delta.total_seconds())
	return time_elapsed


# Sanitizing GDB name
# "T:\GEOINT\FEATURE DATA\Hexagon 250-251\SDE_Connections\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS"
tds_split = TDS.split("\\") # ['T:', 'GEOINT', 'FEATURE DATA', 'Hexagon 250-251', 'SDE_Connections', 'hexagon250_e04a_surge2.sde', 'hexagon250_e04a_surge2.sde.TDS']
tds_split.pop()
gdb_file = tds_split.pop() # hexagon250_e04a_surge2.sde
name_list = gdb_file.split(".") # ['hexagon250_e04a_surge2', 'sde']
gdb_name_raw = name_list[0] # hexagon250_e04a_surge2
gdb_name = gdb_name_raw + "_" + timestamp
#gdb_ext = gdb_name + ".gdb" # hexagon250_e04a_surge2.gdb
#out_path = "{0}\\{1}.gdb".format(out_folder, gdb_name) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2.gdb
out_path = os.path.join(out_folder, gdb_name + ".gdb")
#xml_out = "{0}\\{1}_schema.xml".format(out_folder, gdb_name) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2_schema.xml
#xml_out = os.path.join(out_folder, gdb_name + "_schema.xml")
xml_out = os.path.join(out_folder, gdb_name + "_schema.xml")
#out_tds = "{0}\\TDS".format(out_path) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2.gdb\TDS
out_tds = os.path.join(out_path, "TDS")
write("SDE-TDS input: {0}".format(TDS))
write("Local GDB path: {0}".format(out_path))
write("Schema XML output: {0}".format(xml_out))
write("out_tds path: {0}".format(out_tds))


# Remove Nones from a list
#cleaned_list = list(filter(None, filenames))


# checkbox: Use existing blank GDB or Create new GDB and schema
# input existing GDB Location
# input folder to make new GDB and schema
# check boxes for desired scales.
# input desired aoi. either one merged aoi or ask herbie if task/requirement field is standard and use that to make selection and create envelope
# Remind user to check their connection for the right location (jayhawk, kensington) and that the logged into the server
start_schema = dt.now().time()
write("\nExporting XML workspace")
arcpy.ExportXMLWorkspaceDocument_management(TDS, xml_out, "SCHEMA_ONLY", "BINARY", "METADATA")
write("Creating File GDB")
arcpy.CreateFileGDB_management(out_folder, gdb_name, "CURRENT")
write("Importing XML workspace")
arcpy.ImportXMLWorkspaceDocument_management(out_path, xml_out, "SCHEMA_ONLY")
write("Local blank GDB with schema successfully created")
finish_schema = dt.now().time()
schema_time = float(runtime(start_schema,finish_schema))
write("Created local GDB with schema in {0} seconds/{1} minutes".format(schema_time, (schema_time/60)))

# # make function and run for each checked input scale
# for fc in sde_featureclass_list:
# 	write(fc)
# 	local_fc = sanitized sde_fc # make sure everything is sorted and matched
# 			# Create search and insert cursor to insert new rows in fc from sde fc
# 			with arcpy.da.SearchCursor(sde_fc, fc_fields_all or use * , WHERE ctuu >= input_scale) as scursor:
# 				with arcpy.da.InsertCursor(local_fc, fc_fields_all or use * ) as icursor:
# 					for row in scursor:
# 						if row crosses boundary or is within input aoi
# 						icursor.insertRow(row)
#
#
# touches
# clip
# cut
# Boundary
# crosses
#
# search/insert row features that are within
# search/insert row features that touches AND are WITHIN
# search row features that crosses
# clip/cut them at AOI
# insert


start_copy = dt.now().time()
fc_walk = arcpy.da.Walk(TDS, "FeatureClass")
for dirpath, dirnames, filenames in fc_walk:
	filenames.sort()
	filenames[:] = [x for x in filenames if 'MetadataSrf' not in x and 'ResourceSrf' not in x]
	if vogon:
		filenames[:] = [x for x in filenames if 'StructurePnt' not in x and 'StructureSrf' not in x]
	write("\ndirpath: {0}".format(dirpath))
	#write("\ndirnames: {0}".format(dirnames)) # No dirnames present
	write("\nfilenames: {0}".format(filenames))
	write("\nlength of filenames: {0}".format(len(filenames)))
	write("\nBegin fc loop:\n")
	for fc in filenames:
		total_feats = int(arcpy.GetCount_management(fc).getOutput(0))
		if total_feats == 0:
			continue
		#allow for any field query to be made
		#if query_field not in listfields(fc):
		#    continue
		#query_field = ".".join(fc, query_field)
		write_info('query_field', query_field)
		write_info('query_value', query_value)
		query = "{0} >= {1}".format(query_field, query_value)
		write_info('query', query)
		write("\nfc:")
		write(fc) # hexagon250_e04a_surge2.sde.AeronauticCrv
		fc_split = fc.split(".")
		fc_strip = fc_split.pop()
		write("fc_strip:")
		write(fc_strip) # AeronauticCrv
		sde_fc = os.path.join(TDS, fc)
		write("sde_fc:")
		write(sde_fc) # T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticCrv
		local_fc = os.path.join(out_tds, fc_strip)
		write("local_fc:")
		write(local_fc) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2_timestamp.gdb\TDS\AeronauticCrv
		if arcpy.Exists(local_fc):
			write("local {0} exists".format(fc_strip))

			#Collect all fields except the Geometry and OID fields
			dsc = arcpy.Describe(fc)
			fields = dsc.fields
			out_fields = [dsc.OIDFieldName, dsc.lengthFieldName, dsc.areaFieldName] # List of field names for OID, length, and area
			# Create list of field names that aren't Geometry or in out_fields
			field_list = [field.name for field in fields if field.type not in ['Geometry'] and field.name not in out_fields]
			# Make sure to clean the list for all possible geometry standards including ST_Geometry
			field_list[:] = [x for x in field_list if 'Shape' not in x and 'shape' not in x]
			field_list[:] = [x for x in field_list if 'area' not in x and 'length' not in x]
			field_list.append("SHAPE@") # add the full Geometry object
			write_info('field_list',field_list)

			# # Nested Search/Insert cursors for input/output feature classes to copy all rows with specified fields and geometry
			# with arcpy.da.SearchCursor(fc, field_list) as scursor:
			# 	with arcpy.da.InsertCursor(fc_out, field_list) as icursor:
			# 		for row in scursor:
			# 			icursor.insertRow(row)


			# Create Search and Insert Cursor
			f_count = 0
			local_icursor = arcpy.da.InsertCursor(local_fc, field_list)
			with arcpy.da.SearchCursor(AOI, ['SHAPE@']) as aoi_cur:
				aoi_next = aoi_cur.next()
				#write_info('aoi next record', aoi_next)
				aoi_shp = aoi_next[0]
				#write_info('aoi_shp', aoi_shp)
				start_fc_search = dt.now().time()
				#query = "'zi026_ctuu' >= 250000" #hexagon250_e04a_surge2.sde.AeronauticCrv.
				with arcpy.da.SearchCursor(sde_fc, field_list, query) as sde_scursor:
					for row in sde_scursor:
						#write_info('sde_scursor row', row)
						# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
						# Debug info for sde_scursor row:
						#    Variable Type: <type 'tuple'>
						#    Assigned Value: (u'GB030', 100441, -999999.0, -999999, -999999, -999999, 106.0, -999999, 2, -999999, -999999, -999999, -999999, -999999, -999999, 11, -999999.0, -999999, u'noInformation', -999999, 13.0, -999999.0, -999999, -999999, -999999, u'noInformation', u'noInformation', 2, -999999, -999999, -999999, -999999, -999999, -999999, -999999, -999999, -999999, u'8A58E940-7F1C-4FF9-A4F4-98AB0D635A80', -999999, -999999, -999999, u'noInformation', 8.0, 19, u'noInformation', u'noInformation', u'noInformation', -999999, -999999, -999999, 5, -999999, -999999, 1, 3, u'ge:GENC:3:1-2:RUS', 5, 1, 250000, -999999.0, -999999.0, -999999.0, 30, u'2019-10-29', u'DigitalGlobe', 1001, -999999, u'noInformation', u'noInformation', u'Copyright 2021 by the National Geospatial-Intelligence Agency, U.S. Government. No domestic copyright claimed under Title 17 U.S.C. All rights reserved.', u'noInformation', u'U', u'noInformation', u'noInformation', u'USA', u'{711B7810-9A08-4B69-914A-712D8920F98E}', u'Prj8', None, None, None, None, None, None, None, <PointGeometry object at 0x156f9ab0[0x156f9540]>)
						# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
						sde_shp = row[-1]
						if sde_shp is None:
							continue
						#write_info('sde_shp', sde_shp)
						#start_within = dt.now().time()
						if sde_shp.within(aoi_shp, "CLEMENTINI"):
							local_icursor.insertRow(row)
							f_count += 1
						#finish_within = dt.now().time()
						#write("Time elapsed for row within check: {0}".format(runtime(start_within,finish_within)))
						# if sde_shp.within(aoi_shp) or sde_shp.touches(aoi_shp):
						# 	local_icursor.insertRow(row)
						# if sde_shp.crosses(aoi_shp):
						# 	cut sde_shp at aoi_shp boundary
						# search/insert row features that are within
						# search/insert row features that touches AND are WITHIN
						# search row features that crosses
						# clip/cut them at AOI
						# insert
				finish_fc_search = dt.now().time()
				write("Time elapsed to search all of {0}: {1} seconds".format(fc_strip, runtime(start_fc_search,finish_fc_search)))
				write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_strip))


			# List all field names except the OID field and geometry fields
			# Replace 'Shape' with 'SHAPE@'

			# out_fields = [dsc.OIDFieldName, dsc.lengthFieldName, dsc.areaFieldName]
			# write("out_fields:")
			# write(out_fields)
			# field_list = [field.name for field in fields if field.name not in out_fields]
			# field_list[:] = [x for x in field_list if 'Shape' not in x and 'shape' not in x]
			# field_list[:] = [x for x in field_list if 'area' not in x and 'length' not in x]
			# field_list.append('SHAPE@')
			# write("Field list for {0}:".format(fc_strip))
			# write(field_list)




			# sde_scursor = arcpy.da.SearchCursor(sde_fc, field_list)
			# write("sde_scursor created")
			# local_scursor = arcpy.da.SearchCursor(local_fc, field_list)
			# write("local_scursor created")
			# local_icursor = arcpy.da.InsertCursor(local_fc, field_list)
			# write("local_icursor created")

			# Create a list of rows for target layer
			#local_rows = [row[0] for row in local_scursor]

			# # Iterate through rows of source and target cursor and insert rows into target from source if they don't exists in target featureclasses
			# rcount = 0
			# for row in sde_scursor:
			# 	rcount += 1
			# 	write("writing row {0}".format(rcount))
			# 	local_icursor.insertRow(row)
			# for row in sde_scursor:
			# 	if not row[0] in local_rows:
			# 		local_icursor.insertRow(row)
			# del sde_scursor, local_scursor, local_icursor
			del local_icursor
			write("cursors deleted\n")
			write("end of {0} loop\n".format(fc_strip))

finish_copy = dt.now().time()
copy_time = float(runtime(start_copy, finish_copy))
write("Total time to copy features: {0} seconds/{1} minutes".format(copy_time, (copy_time/60)))


# with arcpy.da.SearchCursor(out_class, fieldnames) as scursor:
# 	with arcpy.da.InsertCursor(fc, fieldnames) as icursor:
# 		for row in scursor:
# 			icursor.insertRow(row)

# ### Technically works. Pulls everything slowly and doesn't make TDS
# fc_walk = arcpy.da.Walk(TDS)
# for dirpath, dirnames, filenames in fc_walk:
# 	filenames.sort()
# 	write("\ndirpath: {0}".format(dirpath))
# 	write("\nfilenames: {0}".format(filenames))
# 	write("\nlength of filenames: {0}".format(len(filenames)))
# 	for filename in filenames:
# 		#write("\nfc path: '{0}'".format(os.path.join(dirpath, filename)))
# 		fc_split = filename.split(".")
# 		fc_name = fc_split.pop()
# 		write("\nCopying {0} local...".format(fc_name))
# 		fc_inpath = os.path.join(dirpath, filename)
# 		fc_outpath = os.path.join(out_path, fc_name)
# 		arcpy.CopyFeatures_management(fc_inpath, fc_outpath)




# def data_report(tds):
#     elements = defaultdict(list)
#     write("elements blank: {0}".format(elements))
#     walk = arcpy.da.Walk(tds)
#     for dirpath, dirnames, filenames in walk:
# 		write("dirpath: {0}\ndirnames: {1}\nfilenames: {2}".format(dirpath, dirnames, filenames))
#         for dirname in dirnames:  # 'FeatureDataset'
#             write("dirpath+dirname: {0}".format(os.path.join(dirpath, dirname)))
#             desc = arcpy.Describe(os.path.join(dirpath, dirname))
#             write("desc['dataType']: {0}".format(desc.datasetType))
#             elements[desc['dataType']].append(desc)
#
#         for filename in filenames:
#             write("dirpath+filename: {0}".format(os.path.join(dirpath, dirname)))
#             desc = arcpy.Describe(os.path.join(dirpath, filename))
#             elements[desc['dataType']].append(desc)
#
#     report = []
#
#     for element_type, element_list in elements.items():
#         report.append(["{0}:".format(element_type)])
#         for element_description in element_list:
#             report.append(["\t\t{0}".format(element_description['catalogPath'])]) # Here I just output the path, but there's lots more info in the Describe object
#
#     return report
#
# report = data_report(TDS)
# write('\n'.join(report))
# print('\n'.join(report))




#datasetList = arcpy.ListDatasets() #[arcpy.Describe(a).name for a in arcpy.ListDatasets()]
#write(datasetList)
#featureClasses = arcpy.ListFeatureClasses() #[arcpy.Describe(a).name for a in arcpy.ListFeatureClasses()]
#write(featureClasses)



##### Trash Heap #####

# ### Original Copying ArcSDE geodatabase to file geodatabase script V1 ###
# import arcpy, os, shutil, time
# import logging as log
# from datetime import datetime
#
# def formatTime(x):
#     minutes, seconds_rem = divmod(x, 60)
#     if minutes >= 60:
#         hours, minutes_rem = divmod(minutes, 60)
#         return "%02d:%02d:%02d" % (hours, minutes_rem, seconds_rem)
#     else:
#         minutes, seconds_rem = divmod(x, 60)
#         return "00:%02d:%02d" % (minutes, seconds_rem)
#
# def getDatabaseItemCount(workspace):
#     arcpy.env.workspace = workspace
#     feature_classes = []
#     for dirpath, dirnames, filenames in arcpy.da.Walk(workspace,datatype="Any",type="Any"):
#         for filename in filenames:
#             feature_classes.append(os.path.join(dirpath, filename))
#     return feature_classes, len(feature_classes)
#
# def replicateDatabase(dbConnection, out_path):
#     startTime = time.time()
#
#     featSDE,cntSDE = getDatabaseItemCount(dbConnection)
#     featGDB,cntGDB = getDatabaseItemCount(out_path)
#
#     now = datetime.now()
#     logName = now.strftime("SDE_REPLICATE_SCRIPT_%Y-%m-%d_%H-%M-%S.log")
#     log.basicConfig(datefmt='%m/%d/%Y %I:%M:%S %p', format='%(asctime)s %(message)s',\
#     filename=logName,level=log.INFO)
#
#     print "Old Target Geodatabase: %s -- Feature Count: %s" %(out_path, cntGDB)
#     log.info("Old Target Geodatabase: %s -- Feature Count: %s" %(out_path, cntGDB))
#     print "Geodatabase being copied: %s -- Feature Count: %s" %(dbConnection, cntSDE)
#     log.info("Geodatabase being copied: %s -- Feature Count: %s" %(dbConnection, cntSDE))
#
#     arcpy.env.workspace = dbConnection
#
#     #deletes old out_path
#     try:
#         shutil.rmtree(out_path)
#         print "Deleted Old %s" %(os.path.split(out_path)[-1])
#         log.info("Deleted Old %s" %(os.path.split(out_path)[-1]))
#     except Exception as e:
#         print e
#         log.info(e)
#
#     #creates a new out_path
#     GDB_Path, GDB_Name = os.path.split(out_path)
#     print "Now Creating New %s" %(GDB_Name)
#     log.info("Now Creating New %s" %(GDB_Name))
#     arcpy.CreateFileGDB_management(GDB_Path, GDB_Name)
#
#     datasetList = [arcpy.Describe(a).name for a in arcpy.ListDatasets()]
#     featureClasses = [arcpy.Describe(a).name for a in arcpy.ListFeatureClasses()]
#     tables = [arcpy.Describe(a).name for a in arcpy.ListTables()]
#
#     #Compiles a list of the previous three lists to iterate over
#     allDbData = datasetList + featureClasses + tables
#
#     for sourcePath in allDbData:
#         targetName = sourcePath.split('.')[-1]
#         targetPath = os.path.join(out_path, targetName)
#         if arcpy.Exists(targetPath)==False:
#             try:
#                 print "Atempting to Copy %s to %s" %(targetName, targetPath)
#                 log.info("Atempting to Copy %s to %s" %(targetName, targetPath))
#                 arcpy.Copy_management(sourcePath, targetPath)
#                 print "Finished copying %s to %s" %(targetName, targetPath)
#                 log.info("Finished copying %s to %s" %(targetName, targetPath))
#             except Exception as e:
#                 print "Unable to copy %s to %s" %(targetName, targetPath)
#                 print e
#                 log.info("Unable to copy %s to %s" %(targetName, targetPath))
#                 log.info(e)
#         else:
#             print "%s already exists....skipping....." %(targetName)
#             log.info("%s already exists....skipping....." %(targetName))
#     featGDB,cntGDB = getDatabaseItemCount(out_path)
#     print "Completed replication of %s -- Feature Count: %s" %(dbConnection, cntGDB)
#     log.info("Completed replication of %s -- Feature Count: %s" %(dbConnection, cntGDB))
#     totalTime = (time.time() - startTime)
#     totalTime = formatTime(totalTime)
#     log.info("Script Run Time: %s" %(totalTime))
#
# if __name__== "__main__":
#     databaseConnection = r"YOUR_SDE_CONNECTION"
#     out_path = "DESTINATION_PATH\\SDE_Replicated.gdb"
#     replicateDatabase(databaseConnection, out_path)
#
#
#
#
#
#
# ### Original Copying ArcSDE geodatabase to file geodatabase script V2 ###
# import time, os, datetime, sys, logging, logging.handlers, shutil
# import arcpy
#
# ########################## user defined functions ##############################
#
# def getDatabaseItemCount(workspace):
#     log = logging.getLogger("script_log")
#     """returns the item count in provided database"""
#     arcpy.env.workspace = workspace
#     feature_classes = []
#     log.info("Compiling a list of items in {0} and getting count.".format(workspace))
#     for dirpath, dirnames, filenames in arcpy.da.Walk(workspace,datatype="Any",type="Any"):
#         for filename in filenames:
#             feature_classes.append(os.path.join(dirpath, filename))
#     log.info("There are a total of {0} items in the database".format(len(feature_classes)))
#     return feature_classes, len(feature_classes)
#
# def replicateDatabase(dbConnection, out_path):
#     log = logging.getLogger("script_log")
#     startTime = time.time()
#
#     if arcpy.Exists(dbConnection):
#         featSDE,cntSDE = getDatabaseItemCount(dbConnection)
#         log.info("Geodatabase being copied: %s -- Feature Count: %s" %(dbConnection, cntSDE))
#         if arcpy.Exists(out_path):
#             featGDB,cntGDB = getDatabaseItemCount(out_path)
#             log.info("Old Target Geodatabase: %s -- Feature Count: %s" %(out_path, cntGDB))
#             try:
#                 shutil.rmtree(out_path)
#                 log.info("Deleted Old %s" %(os.path.split(out_path)[-1]))
#             except Exception as e:
#                 log.info(e)
#
#         GDB_Path, GDB_Name = os.path.split(out_path)
#         log.info("Now Creating New %s" %(GDB_Name))
#         arcpy.CreateFileGDB_management(GDB_Path, GDB_Name)
#
#         arcpy.env.workspace = dbConnection
#
#         try:
#             datasetList = [arcpy.Describe(a).name for a in arcpy.ListDatasets()]
#         except Exception, e:
#             datasetList = []
#             log.info(e)
#         try:
#             featureClasses = [arcpy.Describe(a).name for a in arcpy.ListFeatureClasses()]
#         except Exception, e:
#             featureClasses = []
#             log.info(e)
#         try:
#             tables = [arcpy.Describe(a).name for a in arcpy.ListTables()]
#         except Exception, e:
#             tables = []
#             log.info(e)
#
#         #Compiles a list of the previous three lists to iterate over
#         allDbData = datasetList + featureClasses + tables
#
#         for sourcePath in allDbData:
#             targetName = sourcePath.split('.')[-1]
#             targetPath = os.path.join(out_path, targetName)
#             if not arcpy.Exists(targetPath):
#                 try:
#                     log.info("Atempting to Copy %s to %s" %(targetName, targetPath))
#                     arcpy.Copy_management(sourcePath, targetPath)
#                     log.info("Finished copying %s to %s" %(targetName, targetPath))
#                 except Exception as e:
#                     log.info("Unable to copy %s to %s" %(targetName, targetPath))
#                     log.info(e)
#             else:
#                 log.info("%s already exists....skipping....." %(targetName))
#
#         featGDB,cntGDB = getDatabaseItemCount(out_path)
#         log.info("Completed replication of %s -- Feature Count: %s" %(dbConnection, cntGDB))
#
#     else:
#         log.info("{0} does not exist or is not supported! \
#         Please check the database path and try again.".format(dbConnection))
#
# #####################################################################################
#
# def formatTime(x):
#     minutes, seconds_rem = divmod(x, 60)
#     if minutes >= 60:
#         hours, minutes_rem = divmod(minutes, 60)
#         return "%02d:%02d:%02d" % (hours, minutes_rem, seconds_rem)
#     else:
#         minutes, seconds_rem = divmod(x, 60)
#         return "00:%02d:%02d" % (minutes, seconds_rem)
#
# if __name__ == "__main__":
#     startTime = time.time()
#     now = datetime.datetime.now()
#
#     ############################### user variables #################################
#     '''change these variables to the location of the database being copied, the target
#     database location and where you want the log to be stored'''
#
#     logPath = ""
#     databaseConnection = "path_to_sde_or_gdb_database"
#     out_path = "apth_to_replicated_gdb\\Replicated.gdb"
#
#     ############################### logging items ###################################
#     # Make a global logging object.
#     logName = os.path.join(logPath,(now.strftime("%Y-%m-%d_%H-%M.log")))
#
#     log = logging.getLogger("script_log")
#     log.setLevel(logging.INFO)
#
#     h1 = logging.FileHandler(logName)
#     h2 = logging.StreamHandler()
#
#     f = logging.Formatter("[%(levelname)s] [%(asctime)s] [%(lineno)d] - %(message)s",'%m/%d/%Y %I:%M:%S %p')
#
#     h1.setFormatter(f)
#     h2.setFormatter(f)
#
#     h1.setLevel(logging.INFO)
#     h2.setLevel(logging.INFO)
#
#     log.addHandler(h1)
#     log.addHandler(h2)
#
#     log.info('Script: {0}'.format(os.path.basename(sys.argv[0])))
#
#     try:
#         ########################## function calls ######################################
#
#         replicateDatabase(databaseConnection, out_path)
#
#         ################################################################################
#     except Exception, e:
#         log.exception(e)
#
#     totalTime = formatTime((time.time() - startTime))
#     log.info('--------------------------------------------------')
#     log.info("Script Completed After: {0}".format(totalTime))
#     log.info('--------------------------------------------------')
#
#
#
#
#
#
#
# ### My failed modifications ###
# import time
# import os
# import datetime
# import sys
# #import logging, logging.handlers,
# import shutil
# import arcpy
#
# ########################## user defined functions ##############################
#
# def getDatabaseItemCount(workspace):
#     #log = logging.getLogger("script_log")
#     """returns the item count in provided database"""
#     arcpy.env.workspace = workspace
#     feature_classes = []
#     arcpy.AddMessage("Compiling a list of items in {0} and getting count.".format(workspace))
#     for dirpath, dirnames, filenames in arcpy.da.Walk(workspace,datatype="Any",type="Any"):
#         for filename in filenames:
#             feature_classes.append(os.path.join(dirpath, filename))
#     arcpy.AddMessage("There are a total of {0} items in the database".format(len(feature_classes)))
#     return feature_classes, len(feature_classes)
#
# def replicateDatabase(dbConnection, out_path):
#     #log = logging.getLogger("script_log")
#     startTime = time.time()
#
#     if arcpy.Exists(dbConnection):
#         featSDE,cntSDE = getDatabaseItemCount(dbConnection)
#         arcpy.AddMessage("Geodatabase being copied: %s -- Feature Count: %s" %(dbConnection, cntSDE))
#         if arcpy.Exists(out_path):
#             featGDB,cntGDB = getDatabaseItemCount(out_path)
#             arcpy.AddMessage("Old Target Geodatabase: %s -- Feature Count: %s" %(out_path, cntGDB))
#             try:
#                 shutil.rmtree(out_path)
#                 arcpy.AddMessage("Deleted Old %s" %(os.path.split(out_path)[-1]))
#             except Exception as e:
#                 arcpy.AddMessage(e)
#
#         GDB_Path, GDB_Name = os.path.split(out_path)
#         arcpy.AddMessage("Now Creating New %s" %(GDB_Name))
#         arcpy.CreateFileGDB_management(GDB_Path, GDB_Name)
#
#         arcpy.env.workspace = dbConnection
#
#         try:
#             datasetList = [arcpy.Describe(a).name for a in arcpy.ListDatasets()]
#         except Exception, e:
#             datasetList = []
#             arcpy.AddMessage(e)
#         try:
#             featureClasses = [arcpy.Describe(a).name for a in arcpy.ListFeatureClasses()]
#         except Exception, e:
#             featureClasses = []
#             arcpy.AddMessage(e)
#         try:
#             tables = [arcpy.Describe(a).name for a in arcpy.ListTables()]
#         except Exception, e:
#             tables = []
#             arcpy.AddMessage(e)
#
#         #Compiles a list of the previous three lists to iterate over
#         allDbData = datasetList + featureClasses + tables
#
#         for sourcePath in allDbData:
#             targetName = sourcePath.split('.')[-1]
#             targetPath = os.path.join(out_path, targetName)
#             if not arcpy.Exists(targetPath):
#                 try:
#                     arcpy.AddMessage("Atempting to Copy %s to %s" %(targetName, targetPath))
#                     arcpy.Copy_management(sourcePath, targetPath)
#                     arcpy.AddMessage("Finished copying %s to %s" %(targetName, targetPath))
#                 except Exception as e:
#                     arcpy.AddMessage("Unable to copy %s to %s" %(targetName, targetPath))
#                     arcpy.AddMessage(e)
#             else:
#                 arcpy.AddMessage("%s already exists....skipping....." %(targetName))
#
#         featGDB,cntGDB = getDatabaseItemCount(out_path)
#         arcpy.AddMessage("Completed replication of %s -- Feature Count: %s" %(dbConnection, cntGDB))
#
#     else:
#         arcpy.AddMessage("{0} does not exist or is not supported! \
#         Please check the database path and try again.".format(dbConnection))
#
# #####################################################################################
#
# def formatTime(x):
#     minutes, seconds_rem = divmod(x, 60)
#     if minutes >= 60:
#         hours, minutes_rem = divmod(minutes, 60)
#         return "%02d:%02d:%02d" % (hours, minutes_rem, seconds_rem)
#     else:
#         minutes, seconds_rem = divmod(x, 60)
#         return "00:%02d:%02d" % (minutes, seconds_rem)
#
# #if __name__ == "__main__":
# startTime = time.time()
# now = datetime.datetime.now()
#
# ############################### user variables #################################
# '''change these variables to the location of the database being copied, the target
# database location and where you want the log to be stored'''
#
# databaseConnection = arcpy.GetParameter(0)
# out_path = arcpy.GetParameterAsText(1)
# #logPath = arcpy.GetParameterAsText(2)
#
# # ############################### logging items ###################################
# # # Make a global logging object.
# # logName = os.path.join(logPath,(now.strftime("%Y-%m-%d_%H-%M.log")))
# #
# # log = logging.getLogger("script_log")
# # log.setLevel(logging.INFO)
# #
# # h1 = logging.FileHandler(logName)
# # h2 = logging.StreamHandler()
# #
# # f = logging.Formatter("[%(levelname)s] [%(asctime)s] [%(lineno)d] - %(message)s",'%m/%d/%Y %I:%M:%S %p')
# #
# # h1.setFormatter(f)
# # h2.setFormatter(f)
# #
# # h1.setLevel(logging.INFO)
# # h2.setLevel(logging.INFO)
# #
# # log.addHandler(h1)
# # log.addHandler(h2)
# #
# # log.info('Script: {0}'.format(os.path.basename(sys.argv[0])))
#
# try:
#     ########################## function calls ######################################
#
#     replicateDatabase(databaseConnection, out_path)
#
#     ################################################################################
# except Exception, e:
#     arcpy.AddMessage(exception(e))
#
# totalTime = formatTime((time.time() - startTime))
# arcpy.AddMessage(totalTime)
# # log.info('--------------------------------------------------')
# # log.info("Script Completed After: {0}".format(totalTime))
# # log.info('--------------------------------------------------')






# Being frustrated at the unnecessarily long processing times of the Merge and/or Append tools for large datasets, I wrote some simple Python code (using the data access module in v10.1) to emulate the same functionality. Took my 2 hour Merge processing time to 11 minutes  I hope someone else can benefit from this code. Right now it is designed to just run on polygon FCs with the same schema, although it could be enhanced to do field mapping as well (not on my time though). It relies on a simple search and insert cursor using the arcpy.da module. BTW, ESRI surely gets some huge props from me for the new cursor model...
#
# Code:
# import arcpy
# fcList = [a list of FCs that you want to merge together]
# outputFC = r"C:\temp\test.gdb\merge"
# for fc in fcList:
#     if fcList.index(fc) == 0:
#         arcpy.CopyFeatures_management(fc, outputFC)
#         insertRows = arcpy.da.InsertCursor(outputFC, ["SHAPE@","*"])
#     else:
#         searchRows = arcpy.da.SearchCursor(fc, ["SHAPE@","*"])
#         for searchRow in searchRows:
#             insertRows.insertRow(searchRow)
#         del searchRow, searchRows
#     print "Appended " + str(fc) + "..."
# del insertRows
#
#
#
#
#
# #####
#
#
#
# '''-------------------------------------------------------------------------------------------
# Tool Name: Polygon Bisector in percent parts Source Name: polygonbisector.py and splitPolygonsWithLines Version: ArcGIS 10.0 Author: ESRI, Inc. Required Arguments: Input Features (Feature Layer) Output Feature Class (Feature Class) Optional Arguments: Axis (X|Y) Group Field(s) (Field) Acceptable Error Percent (Double) Description: Computes a line that bisects, or divides in Commulative Percent value, a polygon area along a line of constant latitude or longitude. each successive input polygon's area will be on either side of the bisecting line. https://www.arcgis.com/home/item.html?id=9aadb577ccb74f0e88b13a0e3643ca4d Credits (Attribution) Esri, Inc. dflater@esri.com http://www.arcgis.com/home/item.html?id=cd6b2d45df654245b7806a896670a431 Split Polygons using Line features Shapefile by daltongis Credits (Attribution) GIS.StackExchange.com updated by : Sham Davande, GIS Analyst - sham.davande@gmail.com
# -------------------------------------------------------------------------------------------'''
# # Import system modules
# import arcpy
# from arcpy import env
# import os
# import sys
# import math
# import time
# arcpy.env.overwriteOutput = True
# # Change input polygon feature class name and path here
# split_poly = "D:\\temp\\polygon2.shp"
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # Split percent Commulative Percent value for python code
# # 3.7 3.7 # 25.5 29.2 # 20.8 50.0 # 10.5 60.5 # 31.5 92.0 # 8.0
# # its cumulative percent values to split polygon with N number percent parts list = ["3.7","29.2","50.0","60.5","92.0"]
# # Set local variables
# out_folder_path = "C:\\"
# out_name = "temp71"
# # Set workspace
# env.workspace = "C:\\temp71"
# # Execute CreateFolder
# arcpy.CreateFolder_management(out_folder_path, out_name)
# # Set local variables
# out_folder = "C:\\temp71"
# out_name = "NewGdb.gdb"
# out_name2 = "C:\\temp71\\NewGdb.gdb"
# geometry_type = "POLYLINE"
# template = ""
# has_m = "DISABLED"
# has_z = "DISABLED"
# # Execute CreateFileGDB
# arcpy.CreateFileGDB_management(out_folder, out_name)
# percent_lines = "C:\\temp71\\NewGdb.gdb\\line1"
# line2 = "C:\\temp71\\NewGdb.gdb\\line2"
# line3 = "C:\\temp71\\NewGdb.gdb\\line3"
# allLines = "C:\\temp71\\NewGdb.gdb\\all_lines"
# outFeatureClass1 = "polygon"
# outFeatureClass2 = "C:\\temp71\\NewGdb.gdb\\polygon"
# expression = ""
# #############################################
# # No hard coded input files path mentioned in the code below here after # and don't want interfere somebodies C:\Temp folder, so C:\temp71 folder automatically created by code below.
# #############################################
# file_prj1 = os.path.splitext(split_poly)[0]
# file_prj2 = str(file_prj1 + ".prj")
# out_coordinate_system = str(file_prj2)
# # Execute CreateFeatureclass
# arcpy.CreateFeatureclass_management(out_name2,"all_lines", "POLYLINE", "", "DISABLED", "DISABLED", out_coordinate_system)
# # Execute FeatureClassToFeatureClass
# arcpy.FeatureClassToFeatureClass_conversion(split_poly, out_name2, outFeatureClass1, expression)
# for i in list:
# if i > 0:
# percent_area = float(i)
# ith_part = 100/percent_area
# print "Generating a polyline to split a polygon into two horizontal parts of", percent_area, "% and",100-percent_area, "% areas" print ith_part, "ith part of polygon"
# schemaType = "NO_TEST"
# fieldMappings = ""
# subtype = ""
# # Main function, all functions run in GravityModel
# def PolygonBisector(in_features, out_fc, axis="x", groupfields=[], error=0.001):
# # Error if sufficient license is not available
# if arcpy.ProductInfo().lower() not in ['arcinfo']:
# arcpy.AddError("An ArcInfo/Advanced license is required.")
# sys.exit()
# # Set geoprocessing environments
# arcpy.env.overwriteOutput = True
# arcpy.env.qualifiedFieldNames = False
# shapefield = arcpy.Describe(in_features).shapeFieldName
# rounder = GetRounder(in_features)
# # If group fields are specified, dissolve by them
# if groupfields:
# in_features = arcpy.management.Dissolve(in_features, "in_memory/grouped", groupfields)
# else: groupfields = [arcpy.Describe(in_features).OIDFieldName]
# fields = [shapefield] + groupfields
# # Create output feature class and set up cursor
# icur = irow = scur = None
# arcpy.management.CreateFeatureclass(os.path.dirname(out_fc), os.path.basename(out_fc), "POLYLINE", "", "", "", arcpy.Describe(in_features).spatialReference)
# arcpy.management.AddField(out_fc, "Group_", "TEXT", "", "", "", "Group: {0}".format(", ".join(groupfields)))
# icur = arcpy.InsertCursor(out_fc)
# scur = arcpy.SearchCursor(in_features, "", "", ";".join(fields))
# count = int(arcpy.management.GetCount(in_features).getOutput(0))
# arcpy.SetProgressor("step", "Processing polygons...", 0, count, 1)
# bigi = 1
# # Begin processing try: for row in scur: minx = miny = float("inf") maxx = maxy = float("-inf") totalarea = 0 feat = row.getValue(shapefield) totalarea = row.getValue(shapefield).area group = [] for field in groupfields: group.append(str(row.getValue(field))) partnum = 0 # Get the min and max X and Y for part in feat: for point in feat.getPart(partnum): if point: minx = point.X if point.X < minx else minx miny = point.Y if point.Y < miny else miny maxx = point.X if point.X > maxx else maxx maxy = point.Y if point.Y > maxy else maxy partnum += 1 # Process the polygon # Some variables conditionmet = False difference = 0 lastdifference = float("inf") differences = {} itys = {} i = 1 strike = 0 # The starting bisector (half the distance from min to max) if axis == "x": ity = (miny + maxy)/2.0 else: ity = (minx + maxx)/2.0 while not conditionmet: # Construct a line through the middle if axis == "x": line = MakeBisector(minx, maxx, ity, in_features, axis) else: line = MakeBisector(miny, maxy, ity, in_features, axis) # The FeatureToPolygon function does not except a geometry object, so make a temporary feature class templine = arcpy.management.CopyFeatures(line, "in_memory/templine") temppoly = arcpy.management.CopyFeatures(feat, "in_memory/temppoly") # Intersect then Feature To Polygon bisected = arcpy.management.FeatureToPolygon([temppoly, templine], "in_memory/bisected") clip = arcpy.analysis.Clip(bisected, in_features, "in_memory/clip") # Group bisected polygons according to above or below the bisector arcpy.management.AddField(clip, "FLAG", "SHORT") ucur = arcpy.UpdateCursor(clip, "", "") flag = 0 try: for urow in ucur: ufeat = urow.getValue(arcpy.Describe(clip).shapeFieldName) partnum = 0 for upart in ufeat: for upoint in ufeat.getPart(partnum): if upoint: if axis == "x": if round(upoint.Y, rounder) > round(ity, rounder): flag = 1 break elif round(upoint.Y, rounder) < round(ity, rounder): flag = -1 break else: if round(upoint.X, rounder) > round(ity, rounder): flag = 1 break elif round(upoint.X, rounder) < round(ity, rounder): flag = -1 break partnum += 1 urow.setValue("FLAG", flag) ucur.updateRow(urow) except: raise finally: if ucur: del ucur # Check if the areas are halved dissolve = arcpy.management.Dissolve(clip, "in_memory/dissolve", "FLAG") scur2 = arcpy.SearchCursor(dissolve) try: for row2 in scur2: firstarea = row2.getValue(arcpy.Describe(dissolve).shapeFieldName).area firstflag = row2.getValue("FLAG") break except: raise finally: if scur2: del scur2 difference = abs(firstarea - (totalarea/ith_part)) differences[i] = difference itys[i] = ity print round(100*(difference/(totalarea/ith_part)),5) #arcpy.AddWarning(round(100*(difference/(totalarea/ith_part)),5)) # Stop if tolerance is achieved if (difference/(totalarea/ith_part))*100 <= error: conditionmet = True break # Moving the line in the wrong direction? due to coordinate system origins or over-compensation if difference > lastdifference: firstflag = firstflag*-1.0 # If we're not improving if abs(difference) > min(differences.values()): strike+=1 # Or if the same values keep appearing if differences.values().count(difference) > 3 or strike >=3: arcpy.AddWarning("Tolerance could not be achieved. Output will be the closest possible.") # Reconstruct the best line if axis == "x": line = MakeBisector(minx, maxx, itys[min(differences,key = lambda a: differences.get(a))], in_features, axis) else: line = MakeBisector(miny, maxy, itys[min(differences,key = lambda a: differences.get(a))], in_features, axis) break # Otherwise move the bisector so that the areas will be more evenly split else: if firstflag == 1: if axis == "x": ity = ((ity-miny)/((totalarea/ith_part)/firstarea)) + miny else: ity = ((ity-minx)/((totalarea/ith_part)/firstarea)) + minx elif firstflag == -1: if axis == "x": ity = ((ity-miny)*math.sqrt((totalarea/ith_part)/firstarea)) + miny else: ity = ((ity-minx)*math.sqrt((totalarea/ith_part)/firstarea)) + minx lastdifference = difference i +=1 irow = icur.newRow() irow.setValue(arcpy.Describe(out_fc).shapeFieldName, line) irow.setValue("Group_", ", ".join(group)) icur.insertRow(irow) arcpy.SetProgressorPosition() arcpy.AddMessage("{0}/{1}".format(bigi, count)) bigi +=1 except: if arcpy.Exists(out_fc): arcpy.management.Delete(out_fc) raise finally: if scur: del scur if icur: del icur if irow: del irow for data in ["in_memory/grouped", temppoly, templine, clip, bisected, dissolve]: if data: try: arcpy.management.Delete(data) except: "" def MakeBisector(min,max,constant, templatefc, axis): if axis == "x": array = arcpy.Array() array.add(arcpy.Point(min, constant)) array.add(arcpy.Point(max, constant)) else: array = arcpy.Array() array.add(arcpy.Point(constant, min)) array.add(arcpy.Point(constant, max)) line = arcpy.Polyline(array, arcpy.Describe(templatefc).spatialReference) return line def GetRounder(in_features): try: unit = arcpy.Describe(in_features).spatialReference.linearUnitName.lower() except: unit = "dd" if unit.find("foot") > -1: rounder = 1 elif unit.find("kilo") > -1: rounder = 3 elif unit.find("meter") > -1: rounder = 1 elif unit.find("mile") > -1: rounder = 3 elif unit.find("dd") > -1: rounder = 5 else: rounder = 3 return rounder # Run the script if __name__ == '__main__': # Get Parameters in_features = str(outFeatureClass2) out_fc = percent_lines axis = arcpy.GetParameterAsText(2).lower() or "x" groupfields = arcpy.GetParameterAsText(3).split(";") if arcpy.GetParameterAsText(3) else [] error = float(arcpy.GetParameter(4)) if arcpy.GetParameter(4) else 0.001 out_data = line2 # Run the main script PolygonBisector(in_features, out_fc, axis, groupfields, error) arcpy.Copy_management(out_fc, out_data) # Use Append tool to move features into single dataset arcpy.Append_management(out_data, allLines, schemaType, fieldMappings, subtype) print "again generating a polyline to split same polygon" print "" else: print "Error" print "finished" print "" print "Splitting polygon using multiple lines generated for a percent area values provided by you..." def splitPolygonsWithLines(Poly, Lines, LinesQuery="", outPoly=""): inputPoly=Poly inputLines=Lines query=LinesQuery inputPolyName=os.path.basename(inputPoly) inputLinesName=os.path.basename(inputLines) parDir=os.path.abspath(inputPoly+"\..") if outPoly=="": outputPolyName=os.path.splitext(inputPolyName)[0]+u"_Split"+os.path.splitext(inputPolyName)[1] outputPoly=os.path.join(parDir,outputPolyName) else: outputPolyName=os.path.basename(outPoly) outputPoly=outPoly sr=arcpy.Describe(inputPoly).spatialReference fieldNameIgnore=["SHAPE_Area", "SHAPE_Length"] fieldTypeIgnore=["OID", "Geometry"] ############################################################################################################################# arcpy.CreateFeatureclass_management (parDir, outputPolyName, "POLYGON", "", "", "", sr) arcpy.AddField_management(outputPoly, "OLD_OID", "LONG") for field in arcpy.ListFields(inputPoly): if (field.type not in fieldTypeIgnore and field.name not in fieldNameIgnore): arcpy.AddField_management (outputPoly, field.name, field.type) arcpy.MakeFeatureLayer_management(inputLines,inputLinesName+"Layer",query) arcpy.MakeFeatureLayer_management(inputPoly,inputPolyName+"Layer") arcpy.SelectLayerByLocation_management(inputPolyName+"Layer","INTERSECT",inputLinesName+"Layer","","NEW_SELECTION") arcpy.SelectLayerByAttribute_management(inputPolyName+"Layer", "SWITCH_SELECTION") fieldmappings = arcpy.FieldMappings() for field in arcpy.ListFields(inputPoly): if (field.type not in fieldTypeIgnore and field.name not in fieldNameIgnore): fm=arcpy.FieldMap() fm.addInputField(outputPoly, field.name) fm.addInputField(inputPolyName+"Layer", field.name) fm_name = fm.outputField fm_name.name = field.name fm.outputField = fm_name fieldmappings.addFieldMap (fm) fm=arcpy.FieldMap() fm.addInputField(outputPoly, "OLD_OID") fm.addInputField(inputPolyName+"Layer", "OBJECTID") fm_name = fm.outputField fm_name.name = "OLD_OID" fm.outputField = fm_name fieldmappings.addFieldMap (fm) arcpy.Append_management(inputPolyName+"Layer", outputPoly, "NO_TEST", fieldmappings) polySelect=arcpy.SelectLayerByLocation_management(inputPolyName+"Layer","INTERSECT",inputLinesName+"Layer","","NEW_SELECTION") lineSelect=arcpy.SelectLayerByLocation_management(inputLinesName+"Layer","INTERSECT",inputPolyName+"Layer","","NEW_SELECTION") ############################################################################################################################# fields=[f.name for f in arcpy.ListFields(inputPoly) if (f.type not in fieldTypeIgnore and f.name not in fieldNameIgnore)] fields.append("SHAPE@") totalFeatures=int(arcpy.GetCount_management(polySelect).getOutput(0)) count=0 timePrev=time.time() with arcpy.da.SearchCursor(polySelect,["OID@"]+fields) as curInput: for rowInput in curInput: linesTemp=arcpy.SelectLayerByLocation_management(lineSelect,"INTERSECT",rowInput[-1],"","NEW_SELECTION") geometry=arcpy.CopyFeatures_management(linesTemp,arcpy.Geometry()) geometry.append(rowInput[-1].boundary()) arcpy.FeatureToPolygon_management (geometry, "in_memory\polygons_init") arcpy.Clip_analysis ("in_memory\polygons_init", rowInput[-1], "in_memory\polygons_clip") with arcpy.da.SearchCursor("in_memory\polygons_clip","SHAPE@") as curPoly: newGeom=[] for rowP in curPoly: if not rowP[0].disjoint(rowInput[-1]): newGeom.append(rowP[0]) arcpy.Delete_management("in_memory") with arcpy.da.InsertCursor(outputPoly, ["OLD_OID"]+fields) as insCur: for geom in newGeom: insertFeature=[r for r in rowInput[:-1]] insertFeature.append(geom) insCur.insertRow(insertFeature) count+=1 if int(time.time()-timePrev)%5==0 and int(time.time()-timePrev)>0: timePrev=time.time() arcpy.AddMessage("\r{0}% done, {1} features processed".format(int(count*100/totalFeatures),int(count))) def main(): arcpy.env.overwriteOutput = True arcpy.env.XYTolerance = "0.1 Meters" inputPoly = arcpy.GetParameterAsText(0) # required inputLines = arcpy.GetParameterAsText(1) # required linesQuery = arcpy.GetParameterAsText(2) # optional outPoly = arcpy.GetParameterAsText(3) # optional if inputPoly=="": inputPoly=outFeatureClass2 if arcpy.Exists(inputPoly): arcpy.AddMessage("Input polygons: "+inputPoly) else: arcpy.AddError("Input polygons layer %s is invalid" % (inputPoly)) if inputLines=="": inputLines=allLines if arcpy.Exists(inputLines): arcpy.AddMessage("Input lines: "+inputPoly) else: arcpy.AddError("Input lines layer %s is invalid" % (inputLines)) if linesQuery=="": arcpy.AddMessage("Performing without query") if outPoly == "": arcpy.AddMessage("Output will be created at the same location as input polygons layer is.") splitPolygonsWithLines(inputPoly, inputLines, linesQuery, outPoly) if __name__ == "__main__": main() print "" print "Done"
