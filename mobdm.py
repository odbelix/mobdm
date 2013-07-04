#!/usr/bin/env python
########################################################################
#
# Author:: Manuel Moscoso <mmoscoso@mobiquos.cl>
#
# Copyright 2013, Mobiquos LTDA
########################################################################
import sys
import argparse
import os
import rrdtool
import os.path
import ConfigParser
import MySQLdb
import time
import datetime
from datetime import datetime
from datetime import timedelta


#Global vars
Config = ConfigParser.ConfigParser()
#Format type for images
images = ['-6h','-12h','-24h','-48h']

#File with database info
databasefile = 'database.ini'
#databasefile = '/opt/mobmetrics/bin/database.ini'
database = {}

#Config paths
configpath = ""
#images_path = "/var/www/mobmetrics/images_plan/"
#rrddb_path = "/opt/mobmetrics/rrddb/"
images_path = ""
rrddb_path = "rrddb/"


#Check if file exists
def checkFile(filename):
	if os.path.exists(filename) == False :
		print "File not exists"
		return False
	else:
		if os.path.isdir(filename) == True:
			print "Is a directory"
			return False
		else:
			return True
			
			
#Get database information from file
def getDataBaseInfo():
	global databasefile
	data = ConfigParser.ConfigParser()
	if os.path.exists(databasefile) == False:
		print "ERROR: %s not exists" % databasefile
		return False
	else:
		data.read(databasefile)
		#Put values to array
		database.update({'host':data.get('database','host')})
		database.update({'name':data.get('database','name')})
		database.update({'user':data.get('database','user')})
		database.update({'password':data.get('database','password')})
		database.update({'prefix':data.get('database','prefix')})
		return True


# Insert values of "arr" in "table"
def insertValues(table,iddevice,idplan,arr):
	if len(arr) >= 9:
		#timestamp -> string
		date = arr[0]
		if len(arr) == 9:
			query = "INSERT INTO %s(device,plan,datereg,ipsrc,portsrc,ipdst,portdst,idconn,ival,transfer,bw,jitter,lostdatagrams,totaldatagrams,percentlost,outdatagrams) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(table,iddevice,idplan,date,arr[1],arr[2],arr[3],arr[4],arr[5],arr[6],arr[7],arr[8],'0','0','0','0','0')
		else:	
			query = "INSERT INTO %s(device,plan,datereg,ipsrc,portsrc,ipdst,portdst,idconn,ival,transfer,bw,jitter,lostdatagrams,totaldatagrams,percentlost,outdatagrams) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(table,iddevice,idplan,date,arr[1],arr[2],arr[3],arr[4],arr[5],arr[6],arr[7],arr[8],arr[9],arr[10],arr[11],arr[12],arr[13])
	else:
		sys.exit('Not enough arguments')
		
	getDataBaseInfo()
	db = MySQLdb.connect(database['host'],database['user'],database['password'],database['name'])
	cursor = db.cursor()
	try:
		cursor.execute(query)
		db.commit()
		return True
	except MySQLdb.Error, e:
		db.rollback()
		print "An error has been passed. %s" %e
		return False


#Execute query
def selectValues(query):
	getDataBaseInfo()
	db = MySQLdb.connect(database['host'],database['user'],database['password'],database['name'])
	cursor = db.cursor()
	try:
		cursor.execute(query)
		results = cursor.fetchall()
		return results
	except MySQLdb.Error, e:
		print "An error has been passed. %s" %e
		return False

#Get current time to incorporate in Images
def getCurrentTimeForImage():
	current = datetime.now()
	scurrent = current.strftime("%d/%m/%y %H-%M")
	return scurrent

#Get current time
def getCurrentTime():
	current = datetime.now()
	scurrent = current.strftime("%d/%m/%y %H-%M")+"\t:"
	return scurrent

#Main
def main():
	
	#Global variables
	global database
	global images_path
	global images
	global datetime
	
	# Create Argument Parser
	parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description="Mobmeters - Options",
	epilog=".....................\n.....................")
	
	
	#Set arguments
	parser.add_argument("-l", help="List of devices and plans",action="store_true")
	parser.add_argument("-c", help="Create rrdtools dbs",action="store_true")
	parser.add_argument("-down", help="Insert bw down from 'iddevice,idplan,pathfile' args")
	parser.add_argument("-up", help="Insert bw up from 'iddevice,idplan,pathfile' args")
	parser.add_argument("-downrrd", help="Insert bw down from 'iddevice,idplan,pathfile' to rrd DB",action="store_true")
	parser.add_argument("-uprrd", help="Insert bw up from 'iddevice,idplan,pathfile' to rrd DB")
	parser.add_argument("-I", help="Create images png",action="store_true")
	parser.add_argument("-i", help="Create images for one device")
	parser.add_argument("-cd", help="Get Configutarion of devices",action="store_true")
	parser.add_argument("-db", help="Get database information",action="store_true")
	parser.add_argument("-query", help="Execute query")
	
	
	#Parse argv to args 
	args = parser.parse_args()


	#Workflow for arguments selection
	#
	#List of devices
	if args.l:
		
			query = "select id,name,ipaddress,mac from mob_device order by id"
			results = selectValues(query)
			print "Devices:"
			print "id\tname\tip-address\tmac"
			for result in results:
				print "%s\t%s\t%s\t%s\t" % (result[0],result[1],result[2],result[3])
				
			print "\t\t--------------------\n"
			query = "select id,bwdown,bwup from mob_plan order by id"
			results = selectValues(query)
			print "Plans:"
			print "id\tbwdown\tvwup"
			for result in results:
				print "%s\t%s\t%s\t" % (result[0],result[1],result[2])
			print "\t\t--------------------\n"
	
	#Create rrd Databases
	elif args.c:
		query = "select id,bwdown,bwup from mob_plan order by id"
		results = selectValues(query)
		
		#Date to start DB
		datestart = datetime(2013,1,1,0,0)
		start = datestart.strftime('%s')
		dateend = datetime(2013,6,17,0,0)
		print datestart.strftime('%s')
		print dateend.strftime('%s')
		
		if results == False or len(results) == 0:
			print "not exists plans"
		else:
			#Check directory for rrddb
			if not os.path.exists(rrddb_path):
				print "Creating directory for rrddb"
				os.makedirs(rrddb_path)	
				
			#Creating rrddb		
			for result in results:
				namedb="%snet-%s-%s-%s-down.rrd" %(rrddb_path,result[0],result[1],result[2])
				if os.path.exists(namedb) == False:
					print "Creating %s" % namedb
					maxdown = str(int(result[1])*1024)
					ret = rrdtool.create(namedb,"--step","3600","--start",'%s' % start,
							"DS:down:GAUGE:360:%s:%s" % (str(0),maxdown),
							"RRA:AVERAGE:0.5:1:10000000")
				else:
					print "ERROR: DB %s exists" % namedb
					
				namedb = "%snet-%s-%s-%s-up.rrd" % (rrddb_path,result[0],result[1],result[2])
				if os.path.exists(namedb) == False:	
					print "Creating %s" % namedb
					maxup = str(int(result[2])*1024)
					ret = rrdtool.create(namedb,"--step","3600","--start",'%s' % start,
							"DS:up:GAUGE:360:%s:%s" % (str(0),maxup),
							"RRA:AVERAGE:0.5:1:10000000")
				else:
					print "ERROR: DB %s exists" % namedb
					
					
	#Insert bandwidth down values in database
	elif args.down:
			print "insert down"
			table = "mob_bwdown"
			
			#args.down = iddevice,idplan,localization of file
			arguments = args.down.split(",")
			iddevice = arguments[0]
			idplan = arguments[1]
			locfile = arguments[2]
			
			if checkFile(locfile) == False:
				sys.exit('Error in file')
			else:
				print "insert from file in %s" % table
				FILEIN = open(locfile,"r+")
				lines = FILEIN.readlines()
				for line in lines:
					arr = line.split(",")
					insertValues(table,iddevice,idplan,arr)
					
					
	#Insert bandwidth down values in database
	elif args.up:
			print "insert up"
			table = "mob_bwup"
			
			# args.up = = iddevice,idplan,localization of file
			arguments = args.up.split(",")
			iddevice = arguments[0]
			idplan = arguments[1]
			locfile = arguments[2]
			
			if checkFile(locfile) == False:
				sys.exit('Error in file')
			else:
				print "insert from file in %s" % table
				FILEIN = open(locfile,"r+")
				lines = FILEIN.readlines()
				for line in lines:
					arr = line.split(",")
					insertValues(table,iddevice,idplan,arr)				
	
	#Update rrd database for BW-down
	elif args.downrrd:
		#Get al plans
		query = "select id,bwdown,bwup from mob_plan order by id"
		results = selectValues(query)
		datework = datetime.now() + timedelta(hours=1)
		
		#dnow = datenow.strftime('%Y-%m-%d% H')
		#print datenow
		#print datework
		#print datenow.strftime('%s')
		#Format YYYYmmddHmmss
		#print datenow.strftime('%Y%m%d%H0000')
		
		if results == False or len(results) == 0:
			print "not exists plans"
		else:
			for result in results:
					namedb="%snet-%s-%s-%s-down.rrd" %(rrddb_path,result[0],result[1],result[2])
					#query_plan = "select AVG(bw) from mob_bwdown where bw > 0 and plan = %s" % (result[0])
					for i in range(0,6):
						query_plan = "SELECT DATE_SUB('%s', INTERVAL %s HOUR),DATE_SUB('%s', INTERVAL %s HOUR)" % (datework.strftime('%Y-%m-%d %H'),str(i),datework.strftime('%Y-%m-%d %H'),str(i+1))
						result_query = selectValues(query_plan)
						if os.path.exists(namedb):
							print query_plan
							print result_query[0][0]," ",result_query[0][1]
		
		
		
	#Update rrd database for BW-up
	elif args.uprrd:
		print "update rrd up"
		print "update rrd down"
		table = "mob_bwup"
		arguments = args.uprrd.split(",")
		iddevice = arguments[0]
		idplan = arguments[1]
		locfile = arguments[2]
		if checkFile(locfile) == False:
			sys.exit('Error in file')
		else:
			FILEIN = open(locfile,"r+")
			lines = FILEIN.readlines()
			for line in lines:
				arr = line.split(",")
				date = datetime.strptime(arr[0], "%Y%m%d%H%M%S")
				query = "select datereg,device,plan,bw from %s where datereg = '%s'" % (table,date)
				result = selectValues(query)
				if len(result) == 1:
					#Result OK for update
					data = result[0]
					ret = rrdtool.update('%snet-%s-%s-up.rrd' %(rrddb_path,data[1],data[2]),data[0].strftime('%s')+':' + str(data[3]));
	
	
	#Create images for all devices 
	elif args.I:
			print "create images for devices"
			query = "select device,plan from mob_device_plan order by device asc"
			results = selectValues(query)
			if results == False or len(results) == 0:
				print "not exists relationship between device(id=%s) and plans" % (args.i)
			else:
				#Creating images
				for result in results:
					for image in images:						
						ret = rrdtool.graph("%snet-%s-%s-down%s.png"%(images_path,result[0],result[1],image),"--start","%s" % image,"-w 680","-h 200","--vertical-label=kilobits",
						"--title","TITULO",
						"DEF:d=net-%s-%s-down.rrd:down:AVERAGE" % (result[0],result[1]),
						"AREA:d#00FF00:Ancho de Banda Descarga\\r",
						"CDEF:avdown=d,1024,/",
						"COMMENT:\\n",
						"GPRINT:avdown:AVERAGE:Promedio Descarga\: %lf kilobits",
						"COMMENT:\\n",
						"COMMENT:Grafico creado %s" %(getCurrentTimeForImage()))
						ret = rrdtool.graph("%snet-%s-%s-up%s.png"%(images_path,result[0],result[1],image),"--start","%s" % image,"-w 680","-h 200","--vertical-label=kilobits",
						"--title","TITULO",
						"DEF:d=net-%s-%s-up.rrd:up:AVERAGE" % (result[0],result[1]),
						"AREA:d#0332fc:Ancho de Banda Carga\\r",
						"CDEF:avup=d,1024,/",
						"COMMENT:\\n",
						"GPRINT:avup:AVERAGE:Promedio Carga\: %lf kilobits",
						"COMMENT:\\n",
						"COMMENT:Grafico creado %s" %(getCurrentTimeForImage()))			
	
	#Create images for one devices		
	elif args.i:
			print "create images for one device %s" % args.i
			query = "select device,plan from mob_device_plan where device = %s order by plan asc" % args.i
			results = selectValues(query)
			if results == False or len(results) == 0:
				print "not exists relationship between device(id=%s) and plans" % (args.i)
			else:
				#Creating images
				for result in results:
					for image in images:						
						ret = rrdtool.graph("%snet-%s-%s-down%s.png"%(images_path,result[0],result[1],image),"--start","%s" % image,"-w 680","-h 200","--vertical-label=kilobits",
						"--title","TITULO",
						"DEF:d=net-%s-%s-down.rrd:down:AVERAGE" % (result[0],result[1]),
						"AREA:d#00FF00:Ancho de Banda Descarga\\r",
						"CDEF:avdown=d,1024,/",
						"COMMENT:\\n",
						"GPRINT:avdown:AVERAGE:Promedio Descarga\: %lf kilobits",
						"COMMENT:\\n",
						"COMMENT:Grafico creado %s" %(getCurrentTimeForImage()))
						ret = rrdtool.graph("%snet-%s-%s-up%s.png"%(images_path,result[0],result[1],image),"--start","%s" % image,"-w 680","-h 200","--vertical-label=kilobits",
						"--title","TITULO",
						"DEF:d=net-%s-%s-up.rrd:up:AVERAGE" % (result[0],result[1]),
						"AREA:d#0332fc:Ancho de Banda Carga\\r",
						"CDEF:avup=d,1024,/",
						"COMMENT:\\n",
						"GPRINT:avup:AVERAGE:Promedio Carga\: %lf kilobits",
						"COMMENT:\\n",
						"COMMENT:Grafico creado %s" %(getCurrentTimeForImage()))

	#Get configuration information for "RUNMETER"
	elif args.cd:
			query = "select dev.id,dev.ipaddress,pla.id,pla.bwdown,pla.bwup from mob_device dev,mob_plan pla,mob_device_plan dp where dp.device = dev.id "
			query += " and dp.plan = pla.id order by dev.id"
			results = selectValues(query)
			#print "iddevice,ip,idplan,bwdown,bwup"
			for result in results:
				print "%s,%s,%s,%s,%s" % (result[0],result[1],result[2],result[3],result[4])
	
	
	#Get configuration information for "RUNMETER"
	elif args.db:
		if(getDataBaseInfo()):
			print "Database information\n"
			for k in database.keys():
				print "%s => %s\n" % (k,database[k])
				
			results = selectValues("show tables;")
			for result in results:
				print "Table :%s" % result[0]
				datas = selectValues("desc %s" % result[0])
				for data in datas:
					print data
				print
				
	#Execute a particular QUERY
	elif args.query:
			results = selectValues(args.query)
			if results == False:
				print "Error in query"
			else:
				for result in results:
					print result
				
	else:
		#No set any argument
		parser.print_help()
	
#end main	
	
#Main
if  __name__ =='__main__':main()
