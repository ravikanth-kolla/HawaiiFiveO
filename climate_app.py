import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.stations
Measurement = Base.classes.measurements

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)





#################################################
# Flask Routes
#################################################

##Root page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt and /api/v1.0/&ltstart&gt/&ltend&gt"
    )

###Precipitation data
@app.route("/api/v1.0/precipitation")
def precipitations():
    """Return the tobs data as json"""

    record = session.query(Station.station).filter(Station.name.like('%HONOLULU%')).first()
    (honolulu_station,) = record

    ##choose a 15 day vacation trip
    vac_start_date = '2015-09-01' # start date for Sep 1st 2015
    vac_end_date = '2015-09-16'
    data_start_date = dt.date(2015,9,1) - dt.timedelta(days=365)

    tobs_records = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.station == honolulu_station).\
    filter(Measurement.date >= str(data_start_date)).\
    filter(Measurement.date <= vac_start_date).all()
    
    tobs_data = []
    for record in tobs_records:
        tobs_data.append({record.date:record.prcp})

    return jsonify(tobs_data)

##Station Data
@app.route("/api/v1.0/stations")
def station_list():
    """Return the station list data as json"""
    
    station_records = session.query(Station).all()
    station_list = []
    for record in station_records:
            station_list.append({record.station:record.name})
    return jsonify(station_list)

##Temperature data
@app.route("/api/v1.0/tobs")
def tobs_data():
    """Return the tobs data as json"""

    record = session.query(Station.station).filter(Station.name.like('%HONOLULU%')).first()
    (honolulu_station,) = record

    ##choose a 15 day vacation trip
    vac_start_date = '2015-09-01' # start date for Sep 1st 2015
    vac_end_date = '2015-09-16'
    data_start_date = dt.date(2015,9,1) - dt.timedelta(days=365)

    tobs_records = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.station == honolulu_station).\
    filter(Measurement.date >= str(data_start_date)).\
    filter(Measurement.date <= vac_start_date).all()
    
    tobs_data = []
    for record in tobs_records:
        tobs_data.append({record.date:record.tobs})

    return jsonify(tobs_data)

##Temperature statistics with start date
@app.route("/api/v1.0/<start>")
def temp_date_from_date(start):
    try:
        start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    except:
        return (f"Not a valid date format")
    record = session.query(Station.station).filter(Station.name.like('%HONOLULU%')).first()
    (honolulu_station,) = record
    (oldest_start_date,) = session.query(func.min(Measurement.date)).\
    filter(Measurement.station == honolulu_station).first()

    if(start < oldest_start_date):
        return(f"Start date is earlier than oldest start date")
    tmin = session.query(func.min(Measurement.tobs)).\
    filter(Measurement.station == honolulu_station).\
    filter(Measurement.date >= start).all()[0][0]

    tmax = session.query(func.max(Measurement.tobs)).\
    filter(Measurement.station == honolulu_station).\
    filter(Measurement.date >= start).all()[0][0]

    tavg = round(session.query(func.avg(Measurement.tobs)).\
    filter(Measurement.station == honolulu_station).\
    filter(Measurement.date >= start).all()[0][0],2)

    return (jsonify({"TMIN":tmin,"TMAX":tmax,"TAVG":tavg}))

##Temperature statistics with start and end date
@app.route("/api/v1.0/<start>/<end>")
def temp_date_from_date_to_date(start,end):
    try:
        start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    except:
        return (f"Not a valid start date format")

    try:
        end_date = dt.datetime.strptime(end,"%Y-%m-%d")
    except:
        return (f"Not a valid end date format")

    try:
        start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    except:
        return (f"Not a valid date format")
    record = session.query(Station.station).filter(Station.name.like('%HONOLULU%')).first()
    (honolulu_station,) = record

    (oldest_start_date,) = session.query(func.min(Measurement.date)).\
    filter(Measurement.station == honolulu_station).first()

    (max_end_date,) = session.query(func.max(Measurement.date)).\
    filter(Measurement.station == honolulu_station).first()

    if(start < oldest_start_date):
        return(f"Start date is earlier than oldest start date")

    if(end > max_end_date):
        return(f"End date is after than latest end date")

    tmin = session.query(func.min(Measurement.tobs)).\
    filter(Measurement.station == honolulu_station).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()[0][0]

    tmax = session.query(func.max(Measurement.tobs)).\
    filter(Measurement.station == honolulu_station).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()[0][0]

    tavg = round(session.query(func.avg(Measurement.tobs)).\
    filter(Measurement.station == honolulu_station).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()[0][0],2)

    return (jsonify({"TMIN":tmin,"TMAX":tmax,"TAVG":tavg}))

if __name__ == "__main__":
    app.run(debug=True)