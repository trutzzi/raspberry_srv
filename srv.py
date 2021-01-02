from gpiozero import CPUTemperature
from flask import Flask
from flask_cors import CORS, cross_origin
from datetime import datetime
import json
import psutil
import sqlite3
def get_DLNA():
    # Set file URL, name and path to files from dlna config

    # Connect to db file
    conn = sqlite3.connect('/var/cache/minidlna/files.db')
    c = conn.cursor()

    # Movies
    movies =  c.execute('SELECT * FROM DETAILS WHERE PATH LIKE "/exhdd/dlna/video/%" AND DURATION NOT NULL')
    moviesCount = 0
    for row in movies:
        moviesCount = moviesCount + 1

    # Photos
    photosCount = 0
    photos =  c.execute('SELECT * FROM DETAILS WHERE PATH LIKE "/exhdd/dlna/photos/%"')
    for row in photos:
        photosCount = photosCount + 1

    # Audio
    audioCount = 0
    audio =  c.execute('SELECT * FROM DETAILS WHERE PATH LIKE "/exhdd/dlna/audio/%"')
    for row in photos:
        audioCount = audioCount + 1
    
    return '{"movies":"%s", "photos":"%s", "audio":"%s"}'%(moviesCount,photosCount,audioCount)

app = Flask(__name__)

# Enable CORS
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# NAS PATH
nurl = '/exhdd'
hdd = psutil.disk_usage(nurl)
def get_space():
    total =  hdd.total / (2**30)
    used =  hdd.used / (2**30)
    free = hdd.free / (2**30)
    return '{"total":"%s", "used":"%s", "free":"%s"}'%(total,used,free)

def get_time():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

def get_srv():
    cpu = psutil.cpu_percent()
    temp = CPUTemperature().temperature
    memory = psutil.virtual_memory()
    # Divide from Bytes -> KB -> MB
    available_ram = round(memory.available/1024.0/1024.0,1)
    total_ram = round(memory.total/1024.0/1024.0,1)
    return '{"temp":"%s","cpu":"%s","ram": {"available":"%s","total":"%s"}}'%(temp,cpu,available_ram,total_ram)

# ROUTER
@app.route('/')
@cross_origin()
def result():
    return '{"srv":%s,"time_server":"%s","nas":%s, "dlna":%s}'%(get_srv(), get_time(),get_space(),get_DLNA())

if __name__ == '__main__':
    app.run(host='192.168.1.200', port=8080)
