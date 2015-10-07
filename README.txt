ABSTREAM is a live streaming (Broadcasting) application where any event can be broadcasted Live from your Desktop and can be watched in a Browser.We are currently working on Mobile version of the same.

PRE REQUISITES

ffmpeg  install link   https://www.ffmpeg.org/
python 2.7+ with additional modules like kivy, pyinstaller,tkinter,pymongo etc.  install link  https://www.python.org
To install kivy visit kivy.org
use pip install pymongo tkinter pyinstaller to install python modules
mongodb install link  https://www.mongodb.org/downloads
Any other os, python modules if needed.

INSTALLATION AND EXECUTION.

Main server program is absimpl_abstream.py(web and app server)
Additional directories static, templates contains html, javascript files  for web application

feedcreation.txt is to create mongodb records(livestream users).You can extend as you wish. Keep in sync with ffserver config file.

start_appserver is automated shell script to start main app server, ffserver

absimpl_abstream_housekeep.py is housekeeping scheduler for mongodb records(similar to garbage collection)

ffserver_25feeds.conf is configured to accept 25 feeds. You can extend as you wish. Keep in sync with feedcreation.txt.

kivytest_version2_10_ubuntu is standalone python application for ubuntu desktop which is created by pyinstaller. To execute run runstream.sh.

kivytest_version2_12_windows is standalone python application for windows desktop which is created by pyinstaller. To execute run runstream.bat.

You need to substitute your host IP at 'your host' text and  your port at 'your port' text in all the files

You can run web application at your host:your port address.This web application is to view all current events which needs user login.

Live streaming should be started from desktop application(kivytest_version2_10_ubuntu.py, kivytest_version2_12_windows.py) which also needs user login.

Currently it works well with Chrome web browser. We are improving to make it work on other browsers as well.

PLease feel free to enrich,enhance and let us know your feedback.

