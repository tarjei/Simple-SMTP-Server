import asyncore
import smtpd
import os
import json
import pickle
import threading
import time
import copy
import email

#############################################################
#######################    Pickle    ########################
#############################################################

class PickleData:
	def __init__(self,fileName):
		self.fileName = fileName
		self.content = None

		if os.path.exists(self.fileName):
			readHandle = open(self.fileName,'r')
			try:
				self.content = pickle.load( readHandle )
			except:
				print "Empty or corrupt db"

			readHandle.close()

	def read(self):
		return self.content

	def save(self,c):
		self.content = c;
		writeHandle = open(self.fileName,'w+')
		pickle.dump(self.content, writeHandle)
		writeHandle.close()

#############################################################
######################## SMTP Server ########################
#############################################################

messageStore = PickleData('messageStore.txt')
messageQueue = []

class SMTPServer(smtpd.SMTPServer):
	def process_message(self,_peer,_from,_to,_data):
		messagePacket = {
			'from' : _from,
			'to' : _to,
			'data' : _data,
			'time' : time.time()
		}
		messageQueue.append(messagePacket)
		self.store_message(messagePacket)

		print "#####################################################"
		print 'Receiving from', _from
		print 'Sending to', _to
		print 'Peer', _peer
		print 'Data', _data

	def store_message(self,messagePacket):
		dump = messageStore.read()
		if dump is None:
			dump = {}
		if not dump.has_key( 'messages' ):
			dump['messages'] = []

		messagePacket['id'] = len(dump['messages']) + 1
		dump['messages'].append(messagePacket)
		messageStore.save(dump)

class SMTPServerThread(threading.Thread,object):
	def __init__(self, hostInfo):
		threading.Thread.__init__(self)
		self.hostInfo = hostInfo
		self.active = True
		self.server = None

	def run(self):
		while self.active:
			try:
				asyncore.loop()
			except Exception, e:
				print 'Asyncore Error'
			pass

		server.close()

	def close(self):
		asyncore.close_all()
		print 'Closing SMTP Server'
		self.active = False
		# self.server.close()
		
	#@staticmethod
	def setup(self):
		print 'Starting SMTP Server'
		self.start()
		self.server = SMTPServer(self.hostInfo, None)
		pass

#############################################################
########################    MAIN    #########################
#############################################################

runServer = True

server = SMTPServerThread(('127.0.0.1', 1130) )	#SMTP Server IP
try:
	if runServer:
		print 'Starting server'
		server.setup()

except Exception, e:
	print "Dead"
	#raise e
finally:
	server.close()
        print "Bye"
