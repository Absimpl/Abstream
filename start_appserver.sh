fuser -k 5000/tcp
fuser -k 8091/tcp
python stopshousekeep.py
ffserver -d -f ffserver_25feeds.conf &
python absimpl_abstream_housekeep.py & 
python absimpl_abstream.py 
python stopshousekeep.py
fuser -k 5000/tcp
fuser -k 8091/tcp


