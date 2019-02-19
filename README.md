## Simple SMTP Sink and forwarding Server

An simple python based SMTP server, with a simple web interface for viewing all the messages that hit this server. It basically acts as a sink for all emails and so message are neither validated, proxied nor delivered to any recepient.

Useful for testing out smtp/emails of your project.

This is a fork of kalyan02/Simple-SMTP-Server with the following changes:

-   You can setup regexp based forwarding rules - very usefull for testing.
-   No external dependencies
-   A settings file

## Web Interface

![Screenshot](https://raw.github.com/kalyan02/Simple-SMTP-Server/master/screenshot.png)

## Instructions

### Usage

Run

```
$ python smtp_server.py
```

open web interface at

```
http://localhost:8080/
```

### Config

1. Default web url : http://localhost:8080/
2. Default SMTP host: http://localhost:1130/
3. Edit `server = SMTPServerThread(('127.0.0.1', 1130) )` to your desired SMTP ip & port.
4. Edit `bottle.run(app, host='localhost', port=8080, reloader=(not runServer))` to your desired web ip & port

5. Copy settings.py.example to settings.py and edit it for forwarding.

### Pre-requisits

-   python >= 2.5

Comes packaged with bottle.py

### Note

All data is stored in pickled format and is loaded into memory. You may want to delete the data file from time to time.

### Todo:

-   Allow deletion of messages
-   Render HTML email content
