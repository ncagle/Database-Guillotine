### Trash Heap from pull_local.py ###




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



#datasetList = arcpy.ListDatasets() #[arcpy.Describe(a).name for a in arcpy.ListDatasets()]
#write(datasetList)
#featureClasses = arcpy.ListFeatureClasses() #[arcpy.Describe(a).name for a in arcpy.ListFeatureClasses()]
#write(featureClasses)




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




################################################################
################################################################
# Sanitizing GDB name
# # T:\GEOINT\FEATURE DATA\Hexagon 250-251\SDE_Connections\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS
# tds_split = TDS.split("\\") # ['T:', 'GEOINT', 'FEATURE DATA', 'Hexagon 250-251', 'SDE_Connections', 'hexagon250_e04a_surge2.sde', 'hexagon250_e04a_surge2.sde.TDS']
# tds_split.pop() # hexagon250_e04a_surge2.sde.TDS
# gdb_file = tds_split.pop() # hexagon250_e04a_surge2.sde
# name_list = gdb_file.split(".") # ['hexagon250_e04a_surge2', 'sde']
# gdb_name_raw = name_list[0] # hexagon250_e04a_surge2
# gdb_name = gdb_name_raw + "_" + timestamp # hexagon250_e04a_surge2_2022Mar28_1608
# #gdb_ext = gdb_name + ".gdb" # hexagon250_e04a_surge2.gdb
# #out_path = "{0}\\{1}.gdb".format(out_folder, gdb_name) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2_2022Mar28_1608.gdb
# out_path = os.path.join(out_folder, gdb_name + ".gdb")
# #xml_out = "{0}\\{1}_schema.xml".format(out_folder, gdb_name) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2_schema.xml
# xml_out = os.path.join(out_folder, gdb_name + "_schema.xml")
# #out_tds = "{0}\\TDS".format(out_path) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2.gdb\TDS
# out_tds = os.path.join(out_path, "TDS")

# fc_split = fc.split(".")
# fc_strip = fc_split.pop() # AeronauticCrv
# input_fc = os.path.join(TDS, fc) # T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticCrv
# local_fc = os.path.join(out_tds, fc_strip) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2_timestamp.gdb\TDS\AeronauticCrv


# fc name hexagon250_e04a_surge2.sde.AeronauticPnt
# dsc.file
# fc path T:\GEOINT\FEATURE DATA\Hexagon 250-251\SDE_Connections\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticPnt
# dsc.catalogPath
# dataset path containing fc T:\GEOINT\FEATURE DATA\Hexagon 250-251\SDE_Connections\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS
# dsc.path


gdb_name_raw = re.findall(r"[\w']+", os.path.basename(os.path.split(TDS)[0]))[0]
gdb_name = gdb_name_raw + "_" + timestamp
xml_out = os.path.join(out_folder, gdb_name_raw + "_schema.xml")
out_path = os.path.join(out_folder, gdb_name + ".gdb")
# SDE
# TDS           = T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge.sde\hexagon250_e04a_surge2.sde.TDS
# path.split    = ('T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge.sde', 'hexagon250_e04a_surge2.sde.TDS')
# path.split[0] = T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge.sde
# path.basename = hexagon250_e04a_surge.sde
# re.findall    = ['hexagon250_e04a_surge', 'sde']
# re.findall[0] = hexagon250_e04a_surge
# gdb_name      = hexagon250_e04a_surge_2022Mar29_1923
# xml_out       = C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge_schema.xml
# out_path      = C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge_2022Mar29_1923.gdb
# Local
# TDS           = C:\Projects\njcagle\R&D\__Thunderdome\S1_C09C_20210427.gdb\TDS
# path.split    = ('C:\Projects\njcagle\R&D\__Thunderdome\S1_C09C_20210427.gdb', 'TDS')
# path.split[0] = C:\Projects\njcagle\R&D\__Thunderdome\S1_C09C_20210427.gdb
# path.basename = S1_C09C_20210427.gdb
# re.findall    = ['S1_C09C_20210427', 'gdb']
# re.findall[0] = S1_C09C_20210427
# gdb_name      = S1_C09C_20210427_2022Mar29_1925
# xml_out       = C:\Projects\njcagle\finishing\E04A\S1_C09C_20210427_schema.xml
# out_path      = C:\Projects\njcagle\finishing\E04A\S1_C09C_20210427_2022Mar29_1925.gdb

def get_local(out_path, dsc): # Gets the clean feature class name and its local path in the target GDB
	#local_fc_path, clean_fc_name = get_local(output_path, describe_obj)
	# dsc.file        = hexagon250_e04a_surge2.sde.AeronauticCrv
	# split(".")     = [hexagon250_e04a_surge2, sde, AeronauticCrv]
	# split(".")[-1] = AeronauticCrv
	fc_name = dsc.file.split(".")[-1] # AeronauticCrv
	local_fc = os.path.join(out_path, "TDS", fc_name) # C:\Projects\njcagle\finishing\E04A\hexagon250_e04a_surge2_2022Mar28_1608.gdb\TDS\AeronauticCrv
	return local_fc, fc_name

dsc = arcpy.Describe(fc)
fc_type = dsc.shapeType # Polygon, Polyline, Point, Multipoint, MultiPatch
input_fc = dsc.catalogPath # T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticCrv
local_fc, fc_name = get_local(out_path, dsc)
################################################################
################################################################




# with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor:
# 	if fc_type == 'Point':
# 		for srow in input_scursor:
# 			input_shp = srow[-1]
# 			if input_shp is None:
# 				write("{0} feature OID: {1} found with NULL geometry. Skipping transfer.".format(fc_strip, srow[-2]))
# 				continue
# 			elif input_shp.within(aoi_shp, "CLEMENTINI"):
# 				local_icursor.insertRow(srow)
# 				f_count += 1
# 				continue
# 		del local_icursor
# 		finish_cursor_search = dt.now()
# 		write("Time elapsed to search {0}: {1}".format(fc_strip, runtime(start_cursor_search,finish_cursor_search)))
# 		write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_strip))
# 		continue
# 	if fc_type == 'Polyline':
# 		for srow in input_scursor:
# 			input_shp = srow[-1]
# 			if input_shp is None:
# 				write("{0} feature OID: {1} found with NULL geometry. Skipping transfer.".format(fc_strip, srow[-2]))
# 				continue
# 			elif input_shp.crosses(aoi_shp):
# 				clip_shp = input_shp.clip(aoi_extent) # Current feature geometry object clipped by extent object of aoi geometry object
# 				srow = update_row_tuple(srow, -1, clip_shp)
# 				local_icursor.insertRow(srow)
# 				f_count += 1
# 				continue
# 			elif input_shp.within(aoi_shp, "CLEMENTINI"):
# 				local_icursor.insertRow(srow)
# 				f_count += 1
# 				continue
# 		del local_icursor
# 		finish_cursor_search = dt.now()
# 		write("Time elapsed to search {0}: {1}".format(fc_strip, runtime(start_cursor_search,finish_cursor_search)))
# 		write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_strip))
# 		continue
# 	if fc_type == 'Polygon':
# 		for srow in input_scursor:
# 			input_shp = srow[-1]
# 			if input_shp is None:
# 				write("{0} feature OID: {1} found with NULL geometry. Skipping transfer.".format(fc_strip, srow[-2]))
# 				continue
# 			if input_shp.crosses(aoi_line):
# 				clip_shp = input_shp.clip(aoi_extent) # Current feature geometry object clipped by extent object of aoi geometry object
# 				srow = update_row_tuple(srow, -1, clip_shp)
# 				local_icursor.insertRow(srow)
# 				f_count += 1
# 				continue
# 			in_shp_cent = srow[-1].trueCentroid
# 			if in_shp_cent.within(aoi_shp, "CLEMENTINI"):
# 				local_icursor.insertRow(srow)
# 				f_count += 1
# 				continue
# 		del local_icursor
# 		finish_cursor_search = dt.now()
# 		write("Time elapsed to search {0}: {1}".format(fc_strip, runtime(start_cursor_search,finish_cursor_search)))
# 		write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_strip))
# 		continue




################################################################
################################################################
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Debug info for field_list:
#    Variable Type: <type 'list'>
#    Assigned Value: [u'f_code', u'fcsubtype', u'aoo', u'apt', u'apt2', u'apt3', u'ara', u'asy', u'axs', u'caa', u'ffn', u'ffn2', u'ffn3', u'fpt', u'gug', u'haf', u'hgt', u'htp', u'iko', u'lmc', u'lzn', u'mag', u'mcc', u'mcc2', u'mcc3', u'na8', u'oth', u'pcf', u'pec', u'pym', u'ssr', u'ssr2', u'ssr3', u'tos', u'trs', u'trs2', u'trs3', u'ufi', u'vcm', u'vcm2', u'vcm3', u'voi', u'wid', u'zi004_rcg', u'zi005_fna', u'zi005_nfn', u'zi006_mem', u'zi019_asp', u'zi019_asp2', u'zi019_asp3', u'zi019_asu', u'zi019_asu2', u'zi019_asu3', u'zi019_asx', u'zi019_sfs', u'zi020_ge4', u'zi026_ctuc', u'zi026_ctul', u'zi026_ctuu', u'zva', u'zvh', u'aha', u'zi001_srt', u'zi001_sdv', u'zi001_sdp', u'zi001_sps', u'zi001_vsc', u'zi001_vsd', u'zi001_vsn', u'ccn', u'cdr', u'zsax_rs0', u'zsax_rx0', u'zsax_rx3', u'zsax_rx4', u'globalid', u'version', u'created_user', u'created_date', u'last_edited_user', u'last_edited_date', 'OID@', 'SHAPE@']
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Debug info for input_scursor srow:
#    Variable Type: <type 'tuple'>
#    Assigned Value: (u'GB030', 100441, -999999.0, -999999, -999999, -999999, 106.0, -999999, 2, -999999, -999999, -999999, -999999, -999999, -999999, 11, -999999.0, -999999, u'noInformation', -999999, 13.0, -999999.0, -999999, -999999, -999999, u'noInformation', u'noInformation', 2, -999999, -999999, -999999, -999999, -999999, -999999, -999999, -999999, -999999, u'8A58E940-7F1C-4FF9-A4F4-98AB0D635A80', -999999, -999999, -999999, u'noInformation', 8.0, 19, u'noInformation', u'noInformation', u'noInformation', -999999, -999999, -999999, 5, -999999, -999999, 1, 3, u'ge:GENC:3:1-2:RUS', 5, 1, 250000, -999999.0, -999999.0, -999999.0, 30, u'2019-10-29', u'DigitalGlobe', 1001, -999999, u'noInformation', u'noInformation', u'Copyright 2021 by the National Geospatial-Intelligence Agency, U.S. Government. No domestic copyright claimed under Title 17 U.S.C. All rights reserved.', u'noInformation', u'U', u'noInformation', u'noInformation', u'USA', u'{711B7810-9A08-4B69-914A-712D8920F98E}', u'Prj8', None, None, None, None, None, None, None, <PointGeometry object at 0x156f9ab0[0x156f9540]>)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
################################################################
################################################################




################################################################
################################################################
def fractinull(shp, fc_name, oid):
	# If geometry is NULL, output the feature class and OID and continue to next feature
	if shp is None:
		write("{0} feature OID: {1} found with NULL geometry. Skipping transfer.".format(fc_name, oid))
		continue

def within_insert(shp, aoi, icursor, row):
	global f_count
	if shp.within(aoi, "CLEMENTINI"):
		icursor.insertRow(row)
		f_count += 1
		continue

def crosses_insert(shp, aoi, extent, icursor, row):
	global f_count
	if shp.crosses(aoi):
		clip_shp = shp.clip(extent) # Current feature geometry object clipped by extent object of aoi geometry object
		row = update_row_tuple(row, -1, clip_shp)
		icursor.insertRow(row)
		f_count += 1
		continue

def split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats):
	del local_icursor
	finish_cursor_search = dt.now()
	write("Time elapsed to search {0}: {1}".format(fc_name, runtime(start_cursor_search,finish_cursor_search)))
	write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_name))
	continue


# def pbnj_bananasplit(AOI, fc, input_fc, field_list, query, input_shp, fc_name, input_oid, in_shp_cent, aoi_shp, local_icursor, fc_type, aoi_extent, aoi_line):

with arcpy.da.SearchCursor(AOI, ['SHAPE@']) as aoi_cur:
	#aoi_next = aoi_cur.next()
	#aoi_shp = aoi_next[0]
	aoi_shp = aoi_cur.next()[0] # Go to next(first and should be only) AOI polygon row record and return its geometry object
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
				fractinull(input_shp, fc_name, input_oid) # Must check for NULL geometry before using any geometry methods
				# Metadata and Resource specific method
				in_shp_cent = irow[-1].trueCentroid # Gets the centroid of the current feature
				within_insert(in_shp_cent, aoi_shp, local_icursor, irow) # If feature's centroid is within the AOI, insert it into the new GDB
		split_ends() # Close insert cursor, output runtime, output total features copied, and continue to next feature class
	else: # Proceed assuming normal TDS feature classes
		with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields and user defined query
			if fc_type == 'Point': # Points are either within or without the AOI
				for irow in input_scursor: # Loop thru each point in the input feature class
					input_shp = irow[-1] # Geometry object of current point
					input_oid = irow[-2] # OID object of current row
					fractinull(input_shp, fc_name, input_oid) # Must check for NULL geometry before using any geometry methods
					# Point specific method
					in_shp_cent = irow[-1].trueCentroid # Gets the centroid of the current point
					within_insert(in_shp_cent, aoi_shp, local_icursor, irow) # If point is within the AOI, insert it into the new GDB
			if fc_type == 'Polyline': # Lines can cross the AOI boundary or be fully within
				aoi_extent = aoi_shp.extent # AOI extent object is used to clip line geometries
				for irow in input_scursor: # Loop thru each point in the input feature class
					input_shp = irow[-1] # Geometry object of current line
					input_oid = irow[-2] # OID object of current row
					fractinull(input_shp, fc_name, input_oid) # Must check for NULL geometry before using any geometry methods
					# Line specific method
					crosses_insert(input_shp, aoi_shp, aoi_extent, local_icursor, irow) # Check if line crosses AOI before within then clip, insert, and continue
					within_insert(input_shp, aoi_shp, local_icursor, irow) # If line doesn't cross AOI and is within(Clementini) then insert and continue
			if fc_type == 'Polygon': # Polygons can cross the AOI boundary or be fully within
				aoi_extent = aoi_shp.extent # AOI extent object is used to clip polygon geometries
				aoi_line = aoi_shp.boundary() # Crosses() geometry method can only compare line-line or polygon-line, NOT polygon-polygon cz of course polygons never cross...
				for irow in input_scursor: # Loop thru each point in the input feature class
					input_shp = irow[-1] # Geometry object of current polygon
					input_oid = irow[-2] # OID object of current row
					fractinull(input_shp, fc_name, input_oid) # Must check for NULL geometry before using any geometry methods
					# Polygon specific method
					in_shp_cent = irow[-1].trueCentroid # Gets the centroid of the current polygon
					crosses_insert(input_shp, aoi_line, aoi_extent, local_icursor, irow) # Check if polygon crosses AOI before within then clip, insert, and continue
					within_insert(in_shp_cent, aoi_shp, local_icursor, irow) # If polygon doesn't cross AOI and its centroid is within(Clementini) then insert and continue
		split_ends() # Close insert cursor, output runtime, output total features copied, and continue to next feature class
################################################################
################################################################




# def make_gdb_schema(TDS, xml_out, out_folder, gdb_name, out_path):
# 	start_schema = dt.now()
# 	write("Exporting XML workspace")
# 	arcpy.ExportXMLWorkspaceDocument_management(TDS, xml_out, "SCHEMA_ONLY", "BINARY", "METADATA")
# 	write("Creating File GDB")
# 	arcpy.CreateFileGDB_management(out_folder, gdb_name, "CURRENT")
# 	write("Importing XML workspace")
# 	arcpy.ImportXMLWorkspaceDocument_management(out_path, xml_out, "SCHEMA_ONLY")
# 	write("Local blank GDB with schema successfully created")
# 	os.remove(xml_out)
# 	finish_schema = dt.now()
# 	write("Time to create local GDB with schema: {0}".format(runtime(start_schema,finish_schema)))




# def within_check(shp, aoi):
# 	inner_peace = False
# 	if shp.within(aoi, "CLEMENTINI"):
# 		inner_peace = True
# 	return inner_peace
#
# def within_insert(shp, aoi, icursor, row): # Inserts feature if the geometry is within the AOI
# 	#within_insert(input_geom_obj, aoi_geom_obj, insert_cursor, insert_row)
# 	if shp.within(aoi, "CLEMENTINI"): # Geometry method checks if the feature geometry is within the AOI polygon
# 		icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB
#
# if within_check(input_shp, aoi_shp): # If line doesn't cross AOI and is within(Clementini) then insert and continue
# 	local_icursor.insertRow(irow)
# 	f_count +=1




################################################################
################################################################
def make_multi_list(multi_cross, fc, input_oid):
	global fc_multi
	if not multi_cross: # And if that multipart feature is the first in the fc
		fc_multi[fc] = [input_oid] # Create a dictionary key of the feature class with a value of the first mutlipart oid in a list
		multi_cross = True # Mark the current fc as having multipart features and that the initial feature dictionary has been created
	elif multi_cross: # If a multipart feature has already been found and the initial dictionary key is set up
		fc_multi[fc].append(input_oid)
	return multi_cross


dsc = arcpy.Describe(fc)
fc_type = dsc.shapeType # Polygon, Polyline, Point, Multipoint, MultiPatch
input_fc = dsc.catalogPath # T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticCrv
local_fc, fc_name = get_local(out_path, dsc)
query = """{0} >= {1}""".format(arcpy.AddFieldDelimiters(fc, 'zi026_ctuu'), query_scale)
field_list = make_field_list(dsc)


try:
	arcpy.Delete_management(os.path.join(out_tds, in_class))
	arcpy.Delete_management(os.path.join(out_tds, out_class))
	#arcpy.Delete_management("curr_fc")
except:
	write("No in_class or out_class created. Or processing layers have already been cleaned up. Continuing...")
	pass


# Explode multiparts created by clipping features that cross the AOI boundary
# fc_multi = {
#     'Aero'      : [1,2,3],
#     'Agro'      : [5,8,3],
#     'Trans'     : [2,9,8],
#     'Hydro'     : [4,5,2],
#     'Utilities' : [7,3,5]
# }
fc_multi = {} # Create empty dictionary to house lists of mulitpart features and their feature classes
fc_multi_list = fc_multi.keys() # Iterable list of feature classes that have multipart features
write_info("fc_multi.keys()", fc_multi_list)
in_class = "multi"
out_class = "single"
oid_field = dsc.OIDFieldName # Get the OID field name.

# SHAPE@ = row[-1]
# OID@   = row[-2]

# Modified Hypernova Burst base
	# for fc in fc_multi.keys(): # Iterable list of feature classes that have multipart features
	# 	oid_list = str(tuple(fc_multi[fc]))
	# 	query = """{0} in {1}""".format(arcpy.AddFieldDelimiters(fc, oid_field), oid_list) # Formats the query from the above variables as: OBJECTID in (1, 2, 3)
	#
	# 	# Create a new feature class to put the multipart features in to decrease processing time. fields based on original fc template
	# 	arcpy.CreateFeatureclass_management(out_tds, in_class, fc_type, local_fc, "", "", out_tds)
	#
	# 	# Add multipart features to new feature class based on OID
	# 	with arcpy.da.SearchCursor(local_fc, field_list, query) as scursor: # Search current fc using for only OIDs that are in the multipart oid_list.
	# 		with arcpy.da.InsertCursor(in_class, field_list) as icursor: # Insert cursor for the newly created feature class with the same fields as scursor
	# 			for row in scursor:
	# 				icursor.insertRow(row) # Insert that feature row into the temp feature class, in_class "multi"
	#
	# 	arcpy.MultipartToSinglepart_management(in_class, out_class) # New feature class output of just the converted single parts
	#
	# 	with arcpy.da.UpdateCursor(out_class, 'ufi') as ucursor: # Populate the ufi for the newly created singlepart features
	# 		for row in ucursor:
	# 			row[0] = str(uuid.uuid4())
	# 			ucursor.updateRow(row)
	#
	# 	with arcpy.da.UpdateCursor(local_fc, oid_field, query) as ucursor: # Deletes features in fc that have OIDs flagged as multiparts from the oid_list
	# 		for row in ucursor:
	# 			ucursor.deleteRow()
	#
	# 	with arcpy.da.SearchCursor(out_class, field_list) as scursor: # Insert new rows in fc from MultipartToSinglepart output out_class
	# 		with arcpy.da.InsertCursor(local_fc, field_list) as icursor:
	# 			for row in scursor:
	# 				icursor.insertRow(row)
	#
	# 	try:
	# 		arcpy.Delete_management(os.path.join(out_tds, in_class))
	# 		arcpy.Delete_management(os.path.join(out_tds, out_class))
	# 		#arcpy.Delete_management("curr_fc")
	# 	except:
	# 		write("No in_class or out_class created. Or processing layers have already been cleaned up. Continuing...")
	# 		pass
################################################################
################################################################




# Original Hypernova Burst
	# arcpy.AddField_management(fc, og_oid, "double")
	# with arcpy.da.UpdateCursor(fc, [oid_field, og_oid]) as ucursor:
	# 	for row in ucursor:
	# 		if row[0] in oid_list:
	# 			row[1] = row[0]
	# 			ucursor.updateRow(row)
	#
	# fieldnames = fc_fields[fcr]
	# fieldnames.insert(0, og_oid)
	# fieldnames.insert(0, oid_field)
	# oid_list_str = str(fc_multi[fc])
	# oid_list_str = oid_list_str[1:-1]
	# query = "{0} in ({1})".format(oid_field, oid_list_str)
	#
	# arcpy.CreateFeatureclass_management(arcpy.env.workspace, in_class, fc_type, fc, "", "", arcpy.env.workspace)
	#
	# with arcpy.da.SearchCursor(fc, fieldnames, query) as scursor:
	# 	with arcpy.da.InsertCursor(in_class, fieldnames) as icursor:
	# 		for row in scursor:
	# 			icursor.insertRow(row)
	#
	# arcpy.MultipartToSinglepart_management(in_class, out_class)
	#
	# with arcpy.da.UpdateCursor(fc, oid_field) as ucursor:
	# 	for row in ucursor:
	# 		if row[0] in oid_list:
	# 			ucursor.deleteRow()
	#
	# with arcpy.da.SearchCursor(out_class, fieldnames) as scursor:
	# 	with arcpy.da.InsertCursor(fc, fieldnames) as icursor:
	# 		for row in scursor:
	# 			icursor.insertRow(row)
	#
	# query2 = "{0} IS NOT NULL".format(og_oid)
	#
	# with arcpy.da.UpdateCursor(fc, 'ufi', query2) as ucursor:
	# 	for row in ucursor:
	# 		row[0] = str(uuid.uuid4())
	# 		ucursor.updateRow(row)
	# arcpy.DeleteField_management(fc, og_oid)




# fc_walk = arcpy.da.Walk(TDS, "FeatureClass")
# for dirpath, dirnames, filenames in fc_walk: # No dirnames present. Use Walk to navigate inconsistent SDEs. Also works on local.
# 	filenames.sort()
# 	#def vogon_constructor_fleet(): # Said to hang in the air "the way that bricks don't"
# 	#if vogon: ## [12] "Exclude Specific Feature Classes - Boolean"
# 	#	filenames[:] = [x for x in filenames if 'StructurePnt' not in x and 'StructureSrf' not in x]
#
# 	write("\nFCs loaded from input GDB: {0}".format(len(filenames)))
# 	for fc in filenames:
# 		total_feats = get_count(fc)
# 		if total_feats == 0:
# 			write("{0} is empty".format(fc))
# 			continue
#
# 		dsc = arcpy.Describe(fc)
# 		fc_type = dsc.shapeType # Polygon, Polyline, Point, Multipoint, MultiPatch
# 		input_fc = dsc.catalogPath # T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticCrv
# 		#oid_field = dsc.OIDFieldName # Get the OID field name.
# 		local_fc, fc_name = get_local(out_path, dsc)
# 		field_list = make_field_list(dsc)
#
# 		#allow for any field query to be made
# 		#if query_manual not in listfields(fc):
# 		#    continue
# 		query = """{0} >= {1}""".format(arcpy.AddFieldDelimiters(fc, 'zi026_ctuu'), query_scale)
# 		#write_info('query', query)
#
#
# 		### re-add if arcpy.exists    if doesn't exist throw warning to user that the output gdb provided doesn't match the schema of the data being copied. progress will continue with feature classes that match the schema. output which feature classes don't match at end of run.
#
# 		# Create Search and Insert Cursor
# 		write("Checking {0} features".format(fc_name))
# 		start_cursor_search = dt.now()
# 		f_count = 0
# 		local_icursor = arcpy.da.InsertCursor(local_fc, field_list)
# 		with arcpy.da.SearchCursor(AOI, ['SHAPE@']) as aoi_cur:
# 			aoi_next = aoi_cur.next()
# 			aoi_shp = aoi_next[0]
# 			if aoi_shp is None: # Must check for NULL geometry before using any geometry methods
# 				write("NULL geometry found in input AOI. Please check the AOI polygon and try again.")
# 				sys.exit(0) # If the AOI polygon has NULL geometry, exit the tool. The AOI needs to be checked by the user
# 			if 'MetadataSrf' in fc or 'ResourceSrf' in fc: # Check for these first since they are a special case
# 				query = '' # Metadata and Resource surfaces have different fields. Copy them regardless of query. Can be excluded in Advanced Options.
# 				write("Found {0}. Ignoring ctuu query and copying all within provided AOI.".format(fc))
# 				with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields
# 					for irow in input_scursor: # Loop thru each Metadata or Resource surface in the input feature class
# 						input_shp = irow[-1] # Geometry object of current feature
# 						input_oid = irow[-2] # OID object of current row
# 						if fractinull(input_shp, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
# 							continue
# 						# Metadata and Resource specific method
# 						in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current feature
# 						if within_insert(in_shp_cent, aoi_shp, local_icursor, irow): # If feature's centroid is within the AOI, insert it into the new GDB
# 							f_count +=1
# 							continue
# 				split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats) # Close insert cursor, output runtime, output total features copied, and continue to next feature class
# 			else: # Proceed assuming normal TDS feature classes
# 				with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields and user defined query
# 					if fc_type == 'Point': # Points are either within or without the AOI
# 						for irow in input_scursor: # Loop thru each point in the input feature class
# 							input_shp = irow[-1] # Geometry object of current point
# 							input_oid = irow[-2] # OID object of current row
# 							if fractinull(input_shp, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
# 								continue
# 							# Point specific method
# 							in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current point
# 							if within_insert(in_shp_cent, aoi_shp, local_icursor, irow): # If point is within the AOI, insert it into the new GDB
# 								f_count +=1
# 								continue
# 					if fc_type == 'Polyline': # Lines can cross the AOI boundary or be fully within
# 						#aoi_extent = aoi_shp.extent # AOI extent object is used to clip line geometries
# 						aoi_line = aoi_shp.boundary() # Line geometry object of the AOI boundary
# 						for irow in input_scursor: # Loop thru each point in the input feature class
# 							input_shp = irow[-1] # Geometry object of current line
# 							input_oid = irow[-2] # OID object of current row
# 							if fractinull(input_shp, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
# 								continue
# 							# Line specific method
# 							if crosses_insert(input_shp, aoi_shp, aoi_line, 2, local_icursor, irow): # Check if line crosses AOI before within then clip, insert, and continue
# 								f_count +=1
# 								continue
# 							if within_insert(input_shp, aoi_shp, local_icursor, irow): # If line doesn't cross AOI and is within(Clementini) then insert and continue
# 								f_count +=1
# 								continue
# 					if fc_type == 'Polygon': # Polygons can cross the AOI boundary or be fully within
# 						#aoi_extent = aoi_shp.extent # AOI extent object is used to clip polygon geometries
# 						aoi_line = aoi_shp.boundary() # Line geometry object of the AOI boundary
# 						for irow in input_scursor: # Loop thru each point in the input feature class
# 							input_shp = irow[-1] # Geometry object of current polygon
# 							input_oid = irow[-2] # OID object of current row
# 							if fractinull(input_shp, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
# 								continue
# 							# Polygon specific method
# 							in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current polygon
# 							if crosses_insert(input_shp, aoi_shp, aoi_line, 4, local_icursor, irow): # Check if polygon crosses AOI before within then clip, insert, and continue
# 								f_count +=1
# 								continue
# 							if within_insert(in_shp_cent, aoi_shp, local_icursor, irow): # If polygon doesn't cross AOI and its centroid is within(Clementini) then insert and continue
# 								f_count +=1
# 								continue
# 				split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats) # Close insert cursor, output runtime, output total features copied, and continue to next feature class




################################################################
################################################################
## UFI replace attempt
# def crosses_insert(shp, aoi, dimension, icursor, row): # Inserts feature if the geometry crosses the AOI boundary after clipping it to be within
# 	clip_shp = shp.intersect(aoi, dimension) # Feature geometry is clipped the intersection overlap of the AOI polygon and the feature
# 	row = update_row_tuple(row, -1, clip_shp) # Updates the SHAPE@ token with the newly clipped geometry object
# 	icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB after geometry clip and replace

# def crosses_insert(shp, aoi, boundary, dimension, icursor, row): # Inserts feature if the geometry crosses the AOI boundary after clipping it to be within
# 	# Crosses() geometry method can only compare line-line or polygon-line, NOT polygon-polygon
# 	# So to check if a polygon crosses another polygon, one of them must be a polyline object made with the boundary() geometry method
# 	#crosses_insert(input_geom_obj, aoi_geom_obj, extent_geom_obj, insert_cursor, insert_row)
# 	criss = False
# 	if shp.crosses(boundary): # Geometry method checks if the feature geometry crosses the AOI polygon boundary
# 		criss = True
# 		clip_shp = shp.intersect(aoi, dimension) # Feature geometry is clipped the intersection overlap of the AOI polygon and the feature
# 		row = update_row_tuple(row, -1, clip_shp) # Updates the SHAPE@ token with the newly clipped geometry object
# 		icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB after geometry clip and replace
# 	return criss


# fc_walk = arcpy.da.Walk(TDS, "FeatureClass")
# for dirpath, dirnames, filenames in fc_walk:
# 	filenames.sort()
#
# 	####
# 	in_class = os.path.join(out_tds, "multi")
# 	out_class = os.path.join(out_tds, "single")
# 	####
#
# 	write("\nFCs loaded from input GDB: {0}".format(len(filenames)))
# 	for fc in filenames:
# 		total_feats = get_count(fc)
# 		if total_feats == 0:
# 			write("{0} is empty".format(fc))
# 			continue
#
# 		dsc = arcpy.Describe(fc)
# 		fc_type = dsc.shapeType
# 		input_fc = dsc.catalogPath
# 		####
# #		oid_field = dsc.OIDFieldName # Get the OID field name
# 		ufi_list = []
# 		####
# 		local_fc, fc_name = get_local(out_path, dsc)
#
#
# 		query = """{0} >= {1}""".format(arcpy.AddFieldDelimiters(fc, 'zi026_ctuu'), query_scale)
#
# 		write("Checking {0} features".format(fc_name))
# 		field_list = make_field_list(dsc)
#
# 		# Create Search and Insert Cursor
# 		start_cursor_search = dt.now()
# 		f_count = 0
# 		local_icursor = arcpy.da.InsertCursor(local_fc, field_list)
# 		with arcpy.da.SearchCursor(AOI, ['SHAPE@']) as aoi_cur:
# 			aoi_next = aoi_cur.next()
# 			aoi_shp = aoi_next[0]
# 			if aoi_shp is None:
# 				write("NULL geometry found in input AOI. Please check the AOI polygon and try again.")
# 				sys.exit(0)
# 			if 'MetadataSrf' in fc or 'ResourceSrf' in fc:
# 				query = ''
# 				write("Found {0}. Ignoring ctuu query and copying all within provided AOI.".format(fc))
# 				with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor:
# 					for irow in input_scursor:
# 						input_shp = irow[-1]
# 						input_oid = irow[-2]
# 						if fractinull(input_shp, fc_name, input_oid):
# 							continue
# 						in_shp_cent = input_shp.trueCentroid
# 						if within_insert(in_shp_cent, aoi_shp, local_icursor, irow):
# 							f_count +=1
# 							continue
# 				split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats)
# 			else:
# 				with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor:
# 					if fc_type == 'Point':
# 						for irow in input_scursor:
# 							input_shp = irow[-1]
# 							input_oid = irow[-2]
# 							if fractinull(input_shp, fc_name, input_oid):
# 								continue
# 							in_shp_cent = input_shp.trueCentroid
# 							if within_insert(in_shp_cent, aoi_shp, local_icursor, irow):
# 								f_count +=1
# 								continue
# 					if fc_type == 'Polyline':
# 						aoi_line = aoi_shp.boundary()
# 						for irow in input_scursor:
# 							input_shp = irow[-1]
# 							input_oid = irow[-2]
# 							#input_ufi = irow[-3]
# 							if fractinull(input_shp, fc_name, input_oid):
# 								continue
# 							if input_shp.crosses(aoi_line):
# 								new_ufi = str(uuid.uuid4())
# 								write_info("old irow ufi", irow)
# 								irow = update_row_tuple(irow, -3, new_ufi)
# 								write_info("new irow ufi", irow)
# 								ufi_list.append(new_ufi)
# 								crosses_insert(input_shp, aoi_shp, 2, local_icursor, irow)
# 								f_count +=1
# 								continue
# 							# if crosses_insert(input_shp, aoi_shp, aoi_line, 2, local_icursor, irow):
# 							# 	f_count +=1
# 							# 	continue
# 							if within_insert(input_shp, aoi_shp, local_icursor, irow):
# 								f_count +=1
# 								continue
# 					if fc_type == 'Polygon':
# 						aoi_line = aoi_shp.boundary()
# 						for irow in input_scursor:
# 							input_shp = irow[-1]
# 							input_oid = irow[-2]
# 							#input_ufi = irow[-3]
# 							if fractinull(input_shp, fc_name, input_oid):
# 								continue
# 							in_shp_cent = input_shp.trueCentroid
# 							if input_shp.crosses(aoi_line):
# 								new_ufi = str(uuid.uuid4())
# 								write_info("old irow ufi", irow)
# 								irow = update_row_tuple(irow, -3, new_ufi)
# 								write_info("new irow ufi", irow)
# 								ufi_list.append(new_ufi)
# 								crosses_insert(input_shp, aoi_shp, 4, local_icursor, irow)
# 								f_count +=1
# 								continue
# 							# if crosses_insert(input_shp, aoi_shp, aoi_line, 4, local_icursor, irow):
# 							# 	oid_list.append(input_oid)
# 							# 	f_count +=1
# 							# 	continue
# 							if within_insert(in_shp_cent, aoi_shp, local_icursor, irow):
# 								f_count +=1
# 								continue
# 				split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats)
#
# 		# Explode multipart features that crossed the boundary
# #		og_oid = "oidid"
# 		ufi_query = str(tuple(ufi_list))
# 		ex_query = """{0} in {1}""".format(arcpy.AddFieldDelimiters(fc, 'ufi'), ufi_query) # Formats the query from the above variables as: OBJECTID in (1, 2, 3)
#
# #		arcpy.AddField_management(fc, og_oid, "double")
# #		with arcpy.da.UpdateCursor(fc, [oid_field, og_oid]) as ucursor:
# #			for row in ucursor:
# #				if row[0] in oid_list:
# #					row[1] = row[0]
# #					ucursor.updateRow(row)
#
# 		# Create a new feature class to put the multipart features in to decrease processing time. fields based on original fc template
# 		arcpy.CreateFeatureclass_management(out_tds, "multi", fc_type, local_fc, "", "", out_tds)
#
# 		# Add multipart features to new feature class based on OID
# 		with arcpy.da.SearchCursor(local_fc, field_list, ex_query) as scursor: # Search current fc using for only OIDs that are in the multipart ufi_list.
# 			with arcpy.da.InsertCursor(in_class, field_list) as icursor: # Insert cursor for the newly created feature class with the same fields as scursor
# 				for srow in scursor:
# 					icursor.insertRow(srow) # Insert that feature row into the temp feature class, in_class "multi"
#
# 		arcpy.MultipartToSinglepart_management(in_class, out_class) # New feature class output of just the converted single parts
#
# 		with arcpy.da.UpdateCursor(local_fc, 'ufi', ex_query) as ucursor: # Deletes features in fc that have OIDs flagged as multiparts from the oid_list
# 			for urow in ucursor:
# 				ucursor.deleteRow()
#
# 		with arcpy.da.UpdateCursor(out_class, 'ufi') as ucursor: # Populate the ufi for the newly created singlepart features
# 			for urow in ucursor:
# 				urow[0] = str(uuid.uuid4())
# 				ucursor.updateRow(urow)
#
# 		with arcpy.da.SearchCursor(out_class, field_list) as scursor: # Insert new rows in fc from MultipartToSinglepart output out_class
# 			with arcpy.da.InsertCursor(local_fc, field_list) as icursor:
# 				for srow in scursor:
# 					icursor.insertRow(srow)
# 		try:
# 			arcpy.Delete_management(in_class)
# 			arcpy.Delete_management(out_class)
# 		except:
# 			write("No in_class or out_class created. Or processing layers have already been cleaned up. Continuing...")
# 			pass
################################################################
################################################################





################################################################
################################################################
## Refactor of functions to minimize parameters and use row record to construct the needed geometry vars inside the Functions
def fractinull(shp):#, fc_name, oid): # Checks for NULL geometry
	# If geometry is NULL, output the feature class and OID and continue to next feature
	#fractinull(geometry_obj, fc_name, oid)
	oh_dear_god = False
	if shp is None:
		oh_dear_god = True
		#write("{0} feature OID: {1} found with NULL geometry. Skipping transfer.".format(fc_name, oid))
	return oh_dear_god

def within_insert(aoi, icursor, row): # Inserts feature if the geometry is within the AOI
	#within_insert(input_geom_obj, aoi_geom_obj, insert_cursor, insert_row)
	inner_peace = False
	shp = row[-1]
	if shp.type != 'polyline':
		shp = shp.trueCentroid # Gets the centroid of the current feature
	if shp.within(aoi, "CLEMENTINI"): # Geometry method checks if the feature geometry is within the AOI polygon
		inner_peace = True
		if row[-3] == 'ogoid':
			oid = None
			row = update_row_tuple(row, -3, oid)
		icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB
	return inner_peace

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
		clip_shp = shp.intersect(aoi, dim) # Feature geometry is clipped the intersection overlap of the AOI polygon and the feature
		write_info("irow before", row)
		row = update_row_tuple(row, -1, clip_shp) # Updates the SHAPE@ token with the newly clipped geometry object
		row = update_row_tuple(row, -3, oid)
		write_info("irow after", row)
		icursor.insertRow(row) # Insert the feature into the corresponding feature class in the target GDB after geometry clip and replace
	return criss

def split_ends(fc_name, start_runtime, f_count, total): # Clean up, runtime, and feature count outputs
	#split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats)
	#del icursor # Close the insert cursor for the current feature class
	finish_cursor_search = dt.now() # Stop runtime clock
	write("Time elapsed to search {0}: {1}".format(fc_name, runtime(start_runtime, finish_cursor_search)))
	write("Copied {0} of {1} {2} features local".format(f_count, total, fc_name))


fc_walk = arcpy.da.Walk(TDS, "FeatureClass")
for dirpath, dirnames, filenames in fc_walk: # No dirnames present. Use Walk to navigate inconsistent SDEs. Also works on local.
	filenames.sort()
	#def vogon_constructor_fleet(): # Said to hang in the air "the way that bricks don't"
	#if vogon: ## [12] "Exclude Specific Feature Classes - Boolean"
	#	filenames[:] = [x for x in filenames if 'StructurePnt' not in x and 'StructureSrf' not in x]

	write("\nFCs loaded from input GDB: {0}".format(len(filenames)))
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
		og_oid = "oidid"
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
							if within_insert(aoi_shp, local_icursor, irow): # If feature's centroid is within the AOI, insert it into the new GDB
								f_count +=1
								continue
				split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats) # Close insert cursor, output runtime, output total features copied, and continue to next feature class
			else: # Proceed assuming normal TDS feature classes
				with arcpy.da.SearchCursor(input_fc, field_list, query) as input_scursor: # Search the input feature class with the specified fields and user defined query
					if fc_type == 'Point': # Points are either within or without the AOI
						with arcpy.da.InsertCursor(local_fc, field_list) as local_icursor:
							for irow in input_scursor: # Loop thru each point in the input feature class
								input_shp = irow[-1] # Geometry object of current point
								#input_oid = irow[-2] # OID object of current row
								if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
									continue
								# Point specific method
								#in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current point
								if within_insert(aoi_shp, local_icursor, irow): # If point is within the AOI, insert it into the new GDB
									f_count +=1
									continue
					if fc_type == 'Polyline': # Lines can cross the AOI boundary or be fully within
						#aoi_line = aoi_shp.boundary() # Line geometry object of the AOI boundary
						arcpy.AddField_management(local_fc, og_oid, "double")
						field_list.insert(-2, og_oid)
						write_info("field_list updated", field_list)
						with arcpy.da.InsertCursor(local_fc, field_list) as local_icursor:
							for irow in input_scursor: # Loop thru each point in the input feature class
								input_shp = irow[-1] # Geometry object of current line
								#input_oid = irow[-2] # OID object of current row
								if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
									continue
								# Line specific method
								if crosses_insert(aoi_shp, local_icursor, irow): # Check if line crosses AOI before within then clip, insert, and continue
									sys.exit(0)
									#oid_list.append(input_oid)
									criss = True
									f_count +=1
									continue
								if within_insert(aoi_shp, local_icursor, irow): # If line doesn't cross AOI and is within(Clementini) then insert and continue
									f_count +=1
									continue
					if fc_type == 'Polygon': # Polygons can cross the AOI boundary or be fully within
						aoi_line = aoi_shp.boundary() # Line geometry object of the AOI boundary
						arcpy.AddField_management(local_fc, og_oid, "double")
						write_info("list fields after adding 'ogoid'", arcpy.ListFields(local_fc))
						field_list.insert(-2, og_oid)
						write_info("field_list updated", field_list)
						with arcpy.da.InsertCursor(local_fc, field_list) as local_icursor:
							for irow in input_scursor: # Loop thru each point in the input feature class
								input_shp = irow[-1] # Geometry object of current polygon
								#input_oid = irow[-2] # OID object of current row
								if fractinull(input_shp):#, fc_name, input_oid): # Must check for NULL geometry before using any geometry methods
									continue
								# Polygon specific method
								#in_shp_cent = input_shp.trueCentroid # Gets the centroid of the current polygon
								if crosses_insert(aoi_shp, local_icursor, irow): # Check if polygon crosses AOI before within then clip, insert, and continue
									sys.exit(0)
									criss = True
									f_count +=1
									continue
								if within_insert(aoi_shp, local_icursor, irow): # If polygon doesn't cross AOI and its centroid is within(Clementini) then insert and continue
									f_count +=1
									continue
				split_ends(local_icursor, fc_name, start_cursor_search, f_count, total_feats) # Close insert cursor, output runtime, output total features copied, and continue to next feature class
################################################################
################################################################
