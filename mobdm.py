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
#For Reports
from xlwt import Workbook,Borders,XFStyle


#Global vars
Config = ConfigParser.ConfigParser()
#Format type for images
images = ['6h','12h','24h','48h']

#File with database info
databasefile = 'database.ini'
#databasefile = '/opt/mobmetrics/bin/database.ini'
database = {}

#Config paths
configpath = ""
#images_path = "/var/www/mobmetrics/images_plan/"
#rrddb_path = "/opt/mobmetrics/rrddb/"
images_path = "/home/manuel/www/mobmetrics/rrdimages/"
rrddb_path = "rrddb/"
reports_path = "reports/"


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

def getNewDatetime(strdate):
	outstrdate = datetime(int(strdate[0:4]),
	int(strdate[4:6]),
	int(strdate[6:8]),
	int(strdate[8:10]),0)
	return outstrdate

#Main
def main():
	
	#Global variables
	global database
	global images_path
	global rrddb_path
	global reports_path
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
	parser.add_argument("-uprrd", help="Insert bw up from 'iddevice,idplan,pathfile' to rrd DB",action="store_true")
	parser.add_argument("-I", help="Create images png",action="store_true")
	parser.add_argument("-cd", help="Get Configutarion of devices",action="store_true")
	parser.add_argument("-db", help="Get database information",action="store_true")
	parser.add_argument("-R", help="Create report for previous month",action="store_true")
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
							"DS:down:GAUGE:3600:%s:%s" % (str(0),maxdown),
							"RRA:AVERAGE:0.5:1:10000000")
				else:
					print "ERROR: DB %s exists" % namedb
					
				namedb = "%snet-%s-%s-%s-up.rrd" % (rrddb_path,result[0],result[1],result[2])
				if os.path.exists(namedb) == False:	
					print "Creating %s" % namedb
					maxup = str(int(result[2])*1024)
					ret = rrdtool.create(namedb,"--step","3600","--start",'%s' % start,
							"DS:up:GAUGE:3600:%s:%s" % (str(0),maxup),
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
		print getCurrentTime()

		#Get al plans
		query = "select id,bwdown,bwup from mob_plan order by id"
		results = selectValues(query)
		#datework - Current hour + 1 hour.
		datework = datetime.now() + timedelta(hours=1)
		#strdatework - String for sql-query
		strdatework = datework.strftime('%Y-%m-%d %H')
		
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
					#Get name of rrddb
					namedb="%snet-%s-%s-%s-down.rrd" %(rrddb_path,result[0],result[1],result[2])
					print "--->"
					for i in range(6,0,-1):
					#for i in range(0,6):
						#query_plan = "SELECT AVG(bw) from mob_bwdown where datereg < DATE_SUB('%s', INTERVAL %s HOUR) and datereg > DATE_SUB('%s', INTERVAL %s HOUR) and plan = %s and bw > 0" % (strdatework,str(i),strdatework,str(i+1),result[0])
						query_plan = "SELECT REPLACE(ROUND(AVG(bw),0),',','') from mob_bwdown where datereg < DATE_SUB('%s', INTERVAL %s HOUR) and datereg > DATE_SUB('%s', INTERVAL %s HOUR) and plan = %s and bw > 0" % (strdatework,str(i-1),strdatework,str(i),result[0])
						#query_plan = "SELECT DATE_SUB('%s', INTERVAL %s HOUR),DATE_SUB('%s', INTERVAL %s HOUR)" % (strdatework,str(i-1),strdatework,str(i))
						result_query = selectValues(query_plan)
						
						#datevalue - datetime for insert value on rrddb
						datevalue = datework - timedelta(hours=i)
						#strdate - String format of datevalue, this string has not min/sec values
						strdate = datevalue.strftime('%Y%m%d%H0000')
						
						#Check if rrddb exists
						if os.path.exists(namedb):
							daterrd = getNewDatetime(strdate).strftime('%s')
							bwvalue = str(result_query[0][0])
							store_value = '%s:%s' % (daterrd,bwvalue)
							if bwvalue != 'None':
								print "rrdtool.update('%s','%s')  (namedb,store_value));" % (namedb,store_value)
								try:
									ret = rrdtool.update('%s' % str(namedb),'%s' % store_value) 
								except:
									print "ERROR: Already exists data for this date(%s)" % daterrd 
									
	
	#Update rrd database for BW-up
	elif args.uprrd:
		print getCurrentTime()
		print datetime.now().strftime('%s')
		
		#Get al plans
		query = "select id,bwdown,bwup from mob_plan order by id"
		results = selectValues(query)
		
		#datework - Current hour + 1 hour.
		datework = datetime.now() + timedelta(hours=1)
		
		#strdatework - String for sql-query
		strdatework = datework.strftime('%Y-%m-%d %H')
		
		if results == False or len(results) == 0:
			print "not exists plans"
		else:
			for result in results:
					#Get name of rrddb
					namedb="%snet-%s-%s-%s-up.rrd" %(rrddb_path,result[0],result[1],result[2])
					print "--->"
					for i in range(6,0,-1):
						query_plan = "SELECT REPLACE(ROUND(AVG(bw),0),',','') from mob_bwup where datereg < DATE_SUB('%s', INTERVAL %s HOUR) and datereg > DATE_SUB('%s', INTERVAL %s HOUR) and plan = %s and bw > 0" % (strdatework,str(i-1),strdatework,str(i),result[0])
						result_query = selectValues(query_plan)
						
						#datevalue - datetime for insert value on rrddb
						datevalue = datework - timedelta(hours=i)
						
						#strdate - String format of datevalue, this string has not min/sec values
						strdate = datevalue.strftime('%Y%m%d%H0000')
						
						#Check if rrddb exists
						if os.path.exists(namedb):
							daterrd = getNewDatetime(strdate).strftime('%s')
							bwvalue = str(result_query[0][0])
							store_value = '%s:%s' % (daterrd,bwvalue)
							if bwvalue != 'None':
								print "rrdtool.update('%s','%s')  (namedb,store_value));" % (namedb,store_value)
								try:
									ret = rrdtool.update('%s' % str(namedb),'%s' % store_value) 
								except:
									print "ERROR: Already exists data for this date(%s)" % daterrd 
						
	
	#Create images for all plans
	elif args.I:
			print "create images for plans"
			#Get al plans
			query = "select id,bwdown,bwup from mob_plan order by id"
			results = selectValues(query)
			if results == False or len(results) == 0:
				print "not exists plans"
			else:
				#Check if directory exists
				#Check directory for rrddb
				if not os.path.exists(images_path):
					print "Creating directory for images"
					os.makedirs(images_path)
				
				for result in results:
					#Name of db
					namedbdown="%snet-%s-%s-%s-down.rrd" %(rrddb_path,result[0],result[1],result[2])
					namedbup="%snet-%s-%s-%s-up.rrd" %(rrddb_path,result[0],result[1],result[2])
					for image in images:
						nameimg = "%simg-%s-%s.png" % (images_path,result[0],image)
						print "Creating %s DOWN/UP" % nameimg
						ret = rrdtool.graph("%s" % nameimg,"--start","-%s" % image,"-w 680","-h 200","--vertical-label=kilobits",
						'--imgformat', 'PNG',
						"--title","PLAN %s - %s/%s (Pasadas %soras)" %(result[0],result[1],result[2],image),
						"DEF:d=%s:down:AVERAGE" % (namedbdown),
						"DEF:u=%s:up:AVERAGE" % (namedbup),
						"AREA:d#00FF00:Ancho de Banda Descarga\\r",
						"LINE:u#0000FF:Ancho de Banda Carga\\r",
						"CDEF:avdown=d,1024,/",
						"CDEF:avup=u,1024,/",
						"COMMENT:\\n",
						"GPRINT:avup:AVERAGE:Promedio Carga\: %4lf kilobits",
						"COMMENT:  ",
						"GPRINT:avdown:AVERAGE:Promedio Descarga\: %lf kilobits",
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
	
	#Create report for previous month
	elif args.R:
		#Get current date and Check if first of month
		datenow = datetime.now()
		datenow = datetime(2013,7,1)
		if not datenow.day == 1:
			sys.exit("!: It's not a day to do Reports :D")
		
		
		#Creating report
		namereport = (datenow + timedelta(hours=-24)).strftime("report_%Y_%m.xls")
		#strdatework - String for sql-query
		strdatework_end = (datenow + timedelta(hours=-24)).strftime('%Y-%m-%d')
		strdatework_beg = (datenow + timedelta(hours=-24)).strftime('%Y-%m-01')
			
		#Check directory for reports
		if not os.path.exists(reports_path):
			print "Creating directory for reports"
			os.makedirs(reports_path)
			
		#Check if report exists
		pathreport = "%s%s" %(reports_path,namereport)
		if os.path.exists(pathreport) == True:
			sys.exit("!: Report (%s) already exists" % (pathreport))
			
		#Creack book - xls 
		print "Creating ..."
		book = Workbook(encoding='utf-8')
		
		#Get Plans
		query = "select id,bwdown,bwup from mob_plan order by id"
		results = selectValues(query)
		if results == False or len(results) == 0:
			print "not exists plans"
		else:
			for result in results:
				newsheet = book.add_sheet('Plan%s' % (result[0]))
				newsheet.col(1).width = 5000
				newsheet.col(2).width = 5000
				row3 = newsheet.row(3)
				row3.write(1,'Ancho de Banda Nominal')
				row3.write(2,'%s/%s Kbps' % (result[1],result[2]))
				row4 = newsheet.row(4)
				row4.write(1,'Fecha de Generacion')
				row4.write(2,'%s' % (getCurrentTime()))
				#General Info
				newsheet.row(5).write(1,'Tecnologia')
				newsheet.row(6).write(1,'Ubicacion/localidad')
				newsheet.row(7).write(1,'Limite de descarga')
				
				#BW Average -DOWN
				query_avg = "select datereg,REPLACE(ROUND(AVG(bw),0),',','') from mob_bwdown where plan = %s and datereg BETWEEN '%s' and '%s' group by DAY(datereg) order by datereg" % (result[0],strdatework_beg,strdatework_end)
				results_avg = selectValues(query_avg)
				newsheet.row(9).write(1,'Fecha')
				newsheet.row(9).write(2,'Promedio AB - Descarga')
				rowcont = 10
				for avg in results_avg:
					newsheet.row(rowcont).write(1,avg[0])
					newsheet.row(rowcont).write(2,avg[1])
					rowcont+=1
				
				#BW Average -DOWN
				query_avg = "select datereg,REPLACE(ROUND(AVG(bw),0),',','') from mob_bwup where plan = %s and datereg BETWEEN '%s' and '%s' group by DAY(datereg) order by datereg" % (result[0],strdatework_beg,strdatework_end)
				results_avg = selectValues(query_avg)
				newsheet.row(9).write(4,'Fecha')
				newsheet.row(9).write(5,'Promedio AB - Descarga')
				rowcont = 10
				for avg in results_avg:
					newsheet.row(rowcont).write(4,avg[0])
					newsheet.row(rowcont).write(5,avg[1])
					rowcont+=1
					
					
		try:		
			book.save('%s' % (pathreport))
			print "Report success: %s" % pathreport
		except:
			print "Error saving report"
			
		
				
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
