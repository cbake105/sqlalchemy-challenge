# Import the dependencies

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
import datetime as dt

#################################################
# Database Setup
#################################################


# create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Homepage

@app.route("/")
def home():
    return (f"<h1> <b> Welcome to the Hawaiian Climate Page <b/></h1>"
        f"<br/>"
        f"<ol>"
        f"<strong><h2> Available Pages : </h2></strong><br/>"
        f"<li><h3> Precipitation - /api/v1.0/precipiation </h3><br/>"
        f"<li><h3> List of Stations - /api/v1.0/stations </h3><br/>"
        f"<li><h3> Most Active Stations - /api/v1.0/tobs </h3><br/>"
        f"<li><h3> Temp Details: Start dates - /api/v1.0/temp/<start></h3><br/>"
        f"<li><h3> Temp Details: Start and End dates - /api/v1.0/temp/<start>/<end> </h3><br/>"
        f"<ol>"
        )
        
# Precipitation Analysis: Rates 8/23/16 to 8/23/2017

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    scores = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    session.close()

    last_year_date_prcp_list = []
    for date, prcp in scores:
        last_year_prcp_dict = {}
        last_year_prcp_dict["date"] = date
        last_year_prcp_dict["prcp"] = prcp
        last_year_date_prcp_list.append(last_year_prcp_dict)
    return jsonify(last_year_date_prcp_list)
    
# List station names

@app.route("/api/v1.0/stations")
def stations():
        session = Session(engine)
        scores = session.query(Station.station)
        session.close()
        
        # Convert to list
        all_station_names = list(np.ravel(scores))
        return jsonify (all_station_names)
        
# Most active stastoins

@app.route("/api/v1.0/tobs")
def active_stations():
    session = Sessoin(engine)
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    scores = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= last_year).all()
    session.close()
    scores = list(np.ravel(scores))
    return jsonify (scores)
    
# Return JSON min, max and avg for specific start /start-end range

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def start_end(start=None, end=None):

    # Select statement
    min_max_avg = [func.min(Measurement.tobs),
                   func.max(Measurement.tobs),
                   func.avg(Measurement.tobs)]
                   
    if not end:
    
        start = dt.datetime.strptime(start, "%m%d%Y")
        
        # Compute min, max, avg of start date
        scores = session.query(*min_max_avg).filter(Measurement.date >= start).all()
        session.close()
        
        # Convet to list
        temp = list(np.ravel(scores))
        return jsonify (temp)
        
    
    # Compute min, max, avg of start and end date
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    scores = session.query(*min_max_avg).filter(Measurement.date >= start).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    session.close()
    temps = list(np.ravel(scores))
    return jsonify(temps=temps)
    
# Running the app
if __name__ == "__main__":
    app.run(debug=True)
