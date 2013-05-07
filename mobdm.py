#!/usr/bin/env python
import sys
import argparse
import os
import rrdtool
import os.path
import ConfigParser
import MySQLdb
import time
import datetime
import matplotlib.pyplot as plt
from matplotlib.pyplot import legend
from datetime import datetime

#Global vars
log_f = open('logs','a')
Config = ConfigParser.ConfigParser()
images = ['-1h','-3h','-1d','-1w']
databasefile = 'database.ini'
database = {}
configpath = ""


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

def getDataBaseInfo():
	global databasefile
	data = ConfigParser.ConfigParser()
	if os.path.exists(databasefile) == False:
		print "ERROR: %s not exists" % databasefile
		return False
	else:
		data.read(databasefile)
		database.update({'host':data.get('database','host')})
		database.update({'name':data.get('database','name')})
		database.update({'user':data.get('database','user')})
		database.update({'password':data.get('database','password')})
		database.update({'prefix':data.get('database','prefix')})
		return True

def insertValues(table,iddevice,idplan,arr):
	if len(arr) == 14:
		#timestamp -> string
		date = arr[0]
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

def getDevicesFromConfigFile():
	global Config
	if os.path.exists('config.ini') == False:
			print "ERROR: config.ini not exists"
			return False
	else:
		Config.read('config.ini')
		sections = Config.sections()
	
	return sections

def getCurrentTimeForImage():
	current = datetime.now()
	scurrent = current.strftime("%d/%m/%y %H-%M")
	return scurrent

def getCurrentTime():
	current = datetime.now()
	scurrent = current.strftime("%d/%m/%y %H-%M")+"\t:"
	return scurrent

def getListDevices():
	global Config
	devices = getDevicesFromConfigFile()
	for device in devices:
		print device.rstrip('\n')
#end getListDevices

def main():
	
	global database
	# Create Argument Parser
	parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description="Mobmeters - Options",
	epilog=".....................\n.....................")
	
	
	#Set arguments
	parser.add_argument("-l", help="List of devices and plans",action="store_true")
	parser.add_argument("-down", help="Insert bw down from 'iddevice,idplan,pathfile' args")
	parser.add_argument("-up", help="Insert bw up from 'iddevice,idplan,pathfile' args")
	parser.add_argument("-I", help="Create images png",action="store_true")
	parser.add_argument("-i", help="Create images for one device")
	parser.add_argument("-cd", help="Get Configutarion of devices",action="store_true")
	parser.add_argument("-db", help="Get database information",action="store_true")
	parser.add_argument("-query", help="Execute query")
	
	#Parse argv to args 
	args = parser.parse_args()

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
			
	elif args.down:
			print "insert down"
			table = "mob_bwdown"
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

	elif args.up:
			print "insert up"
			table = "mob_bwup"
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
				
	elif args.I:
			print "Create images"
	elif args.i:
			print "create images for one device"
			query = "select datereg,bw from mob_bwdown where device=1 and plan=2 order by datereg"
			results = selectValues(query)
			dates = []
			values = []
			i = 1
			for element in results:
					#dates.append(element[0])
					dates.append(i)
					i+=1
					if element[1] == '':
						values.append(0)
					else:
						values.append(int(element[1]))
					
			print dates
			print values
			
			#p1, = plt.plot([1,2,3,4], [800,900,950,1020], '-bo')
			p1, = plt.plot([1,2,3,4],values[5:9], '-bo')
			#p2, = plt.plot([1,2,3,4], [512,457,500,375], '-go')


			plt.title('Ancho de Banda')
			#text,fontsize,color
			plt.ylabel('Kbps',fontsize=12,color='black')
			plt.xlabel('Mediciones')
			plt.grid(True)
			legend([p1], ["Descarga"],loc=4)

			#xmin,xmax,ymix,ymax
			plt.axis([0, 10, min(values),max(values)])
			#save in image
			plt.savefig('example-pyplot-3.png')
						
			
	elif args.cd:
			query = "select dev.id,dev.ipaddress,pla.id,pla.bwdown,pla.bwup from mob_device dev,mob_plan pla,mob_device_plan dp where dp.device = dev.id "
			query += " and dp.plan = pla.id order by dev.id"
			results = selectValues(query)
			print "iddevice,ip,idplan,bwdown,bwup"
			for result in results:
				print "%s,%s,%s,%s,%s" % (result[0],result[1],result[2],result[3],result[4])
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
	
	log_f.close()
#end main	
	
#Main
if  __name__ =='__main__':main()
