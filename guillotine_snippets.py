# -*- coding: utf-8 -*-
#¸¸.·´¯`·.¸¸.·´¯`·.¸¸
# ║╚╔═╗╝║  │┌┘─└┐│  ▄█▀‾
# ======================== #
# Database Guillotine v1.7 #
# Nat Cagle 2022-08-04     #
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



''''''''' Parameters '''''''''
## [1] TDS - Feature Dataset
TDS = ap.GetParameterAsText(1)
TDS_name = re.findall(r"[\w']+", os.path.basename(os.path.split(TDS)[0]))[0] # Detailed breakdown in pull_local.trash.py

## [5] Dataload into existing data or empty GDB (Schemas must match) - Workspace GDB
existing_GDB = ap.GetParameterAsText(5) # Default: "C:\Users"

## [7] AOI (Must be merged into a single feature) - Feature Class
AOI = ap.GetParameterAsText(7) # Default: "C:\Users\.."

ap.env.workspace = TDS
ap.env.extent = TDS
ap.env.overwriteOutput = True



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

def fractinull(shp): # Checks for NULL geometry
	#fractinull(geometry_object)
	oh_dear_god = False
	if shp is None:
		oh_dear_god = True
	return oh_dear_god

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
def guillotine(fc_list, out_path):
	query = "zi026_ctuu >= {0}".format(ap.GetParameterAsText(8)) # Scale value from list added to query - Default: "-999999"

	out_tds = os.path.join(out_path, "TDS")
	schema_mismatch = []
	for fc in fc_list:
		total_feats = get_count(fc)
		if not total_feats:
			write("{0} is empty\n".format(fc))
			continue

		dsc = ap.Describe(fc)
		fc_type = dsc.shapeType # Polygon, Polyline, Point, Multipoint, MultiPatch
		input_fc = dsc.catalogPath # T:\GEOINT\FEATURE DATA\hexagon250_e04a_surge2.sde\hexagon250_e04a_surge2.sde.TDS\hexagon250_e04a_surge2.sde.AeronauticCrv
		local_fc, fc_name = get_local(out_path, dsc)
		field_list = make_field_list(dsc)
		og_oid = 'og_oid'
		f_count = 0
		start_cursor_search = dt.now()

		# Check that each feature class is present in the target before continuing
		# Output a warning if a feature class in the source does not exist in the target and continue to the next feature class without extracting data
		# Saves schema mismatched feature classes and outputs a list at the end of the tool
		if not ap.Exists(os.path.join(out_tds, fc)):
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
										if within_insert(aoi_shp, local_icursor, irow, True): # If polygon doesn't cross AOI and its centroid is within(Clementini) then insert and continue
											f_count +=1
											continue
						except ap.ExecuteError:
							writeresults("Guillotine on extracting {0}".format(fc))
				except:
					writeresults("Guillotine starting search of {0}.".format(fc))

		# Clean up, runtime, and feature count outputs
		write("Copied {0} of {1} {2} features local".format(f_count, total_feats, fc_name))
		ap.DeleteField_management(local_fc, og_oid)
		write("Time elapsed to search {0}: {1}\n".format(fc_name, runtime(start_cursor_search, dt.now())))

	if schema_mismatch:
		write("*** The blank GDB and schema provided did not match the source data for all feature classes. ***\n*** The following mismatched feature classes were not copied. ***\n")
		write(schema_mismatch)
		write("\n")



''''''''' Main '''''''''
guillotine(filenames, existing_GDB)
