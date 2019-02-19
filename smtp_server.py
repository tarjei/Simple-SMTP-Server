import asyncore
import smtpd
import os
import json
import pickle
import threading
import bottle
import time
import copy
import email
import datetime
import smtplib
import re
import traceback

from bottle import Bottle, route, run as bottlerun, static_file, install


from string import Template

def render(name, values):

	fh = open("static/%s" % (name), 'r')
	content = fh.read()
	fh.close()

	return Template(content).substitute(values)

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


from settings import smtp_host, smtp_port, user, passwd, regexpMatches

def sendSmtpMessage(message, from_addr, to_addr):
	# open authenticated SMTP connection and send message with
	# specified envelope from and to addresses
	smtp = smtplib.SMTP(smtp_host, smtp_port)
	smtp.starttls()
	smtp.login(user, passwd)
	smtp.sendmail(from_addr, to_addr, message.as_string())
	smtp.quit()

class SMTPServer(smtpd.SMTPServer):
	def process_message(self,_peer,_from,_to,_data):
		try:
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


			# create a Message instance from the email data
			message = email.message_from_string(_data)
			#message = _data

			print repr(_to)

			for toAddress,regexp in regexpMatches.iteritems():
				for to in _to:
					if regexp.match(to):
						# replace headers (could do other processing here)
						message.replace_header("To", toAddress)
						sendSmtpMessage(message, _from, toAddress)

		except Exception as e:
			print e.message
			traceback.print_exc()
			return

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
############################ APP ############################
#############################################################

app = Bottle()
initialMessageCount = 0

@app.route('/static/<path>')
def serveStaticContent(path):
	# return "Foo %s" % path
	return static_file( path, root="static" )

@app.route('/api/has_new')
def hasNew():
	if len(messageQueue) > 0:
		return 'true'
	return 'false'

@app.route('/api/read/<id>')
def readMsg(id=-1):
	content = messageStore.read()
	messages = []

	try:
		id = int(id)
		messages = content['messages']
		msg = filter( lambda m: m['id'] == id, messages ).pop()

		if not msg.has_key('read') or msg['read'] != True:
			msg['read'] = True
			messageStore.save(content)
			messageQueue = []
			# return json.dumps(content, indent=4)

		return json.dumps(msg, indent=4)
	except:
		return json.dumps(False)


@app.route('/page-<pageNum>')
@app.route('/')
def home(pageNum=1):
	content = messageStore.read()
	messages = []

	if content is None:
		messages = []
	elif content.has_key('messages'):
		messages = content['messages']

	host = "%s:%s" % server.hostInfo
	messages = copy.deepcopy(content['messages'])
	messages.sort( lambda A, B: [-1,1][ A['time'] < B['time'] ] )

	initialMessageCount = len(messages)
	for each in messages:
		emsg = email.message_from_string(each['data'])
		title = ''
		if emsg['subject'] is not None:
			title += emsg['subject']
		else:
			title += emsg.get_payload()

		each['title'] = title[:40]
		# print each['title']




	template ="""
	<div class="msgRow $readClass" msgId='$id'>
			<div class='fromField'>$from</div>
			<div class='toField'>$to</div>
			<div class='msgField'>$title</div>
			<div class='timeField'>$date</div>
		</div>
	"""

	if len(messages):

		rep = []

		for message in messages:

			if hasattr( message,'read') and message.read:
				message['readClass'] = 'msgRead'
			else:
				message['readClass'] = ''

			message['date']= datetime.datetime.fromtimestamp(message['time']).isoformat()

			rep.append((Template(template).substitute(message)))

		messagesHtml = "\n".join(rep)

	else:
		messagesHtml = """<div class="msgRow msgRead txtCenter">
			No messages
		</div>"""


	return render("home.template.html",{ 'messagesHtml':messagesHtml, 'page':pageNum, 'host':host })

#############################################################
########################    MAIN    #########################
#############################################################

runServer = True

server = SMTPServerThread(('127.0.0.1', 1130) )	#SMTP Server IP
try:
	if runServer:
		print 'Starting server'
		server.setup()

	print 'Starting bottle'
	bottle.debug(True)
	bottle.run(app, host='localhost', port=8080, reloader=(not runServer))
except Exception, e:
	print "Dead"
	#raise e
finally:
	server.close()
	print "Bye"
