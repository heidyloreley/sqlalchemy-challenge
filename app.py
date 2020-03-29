# Depndencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################


engine = create_engine("sqlite:///Resources\hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")  
def home():
    return (
        f"Welcome to the Climate Information App of Hawaii!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

  # 1. Precipitation route
@app.route("/api/v1.0/precipitation") 
def precipitation():
    # Create session & perform query to get the precipitation values
    session = Session(engine)
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    lastdateD = dt.datetime.strptime(lastdate,'%Y-%m-%d')
    last12monthsS = lastdateD - dt.timedelta(days=366)
    prcpL12Months = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= last12monthsS).all()
    session.close()

    #* Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    prcpData = []
    for date, prcp in prcpL12Months:
        prcpDict = {}
        prcpDict["date"] = date
        prcpDict["prcp"] = prcp
        prcpData.append(prcpDict)

    #* Return the JSON representation of your dictionary.
    return jsonify(PrecipDict)

  # 2. Stations route
@app.route("/api/v1.0/stations") 
def stations():
    # Create session & perform query to get the list of stations
    session = Session(engine)
    stations = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(stations))
    return jsonify(stations)

  # 3. Temperature route
@app.route("/api/v1.0/tobs") 
def temp_obs():
    # Create session & perform query to get the dates and temperature observations of the most active station for the last year of data.
    session = Session(engine)
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    lastdateD = dt.datetime.strptime(lastdate,'%Y-%m-%d')
    last12monthsS = lastdateD - dt.timedelta(days=366)
    MostActiveStationT = session.query(Measurement.station).group_by(Measurement.station).order_by(Measurement.tobs.desc()).first()
    TempLast12Months = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= last12monthsS).filter(Measurement.station == MostActiveStationT[0]).all()
    session.close()

    #* Return a JSON list of temperature observations (TOBS) for the previous year.
    tobsList = []
    for date, tobs in TempLast12Months:
        tobsList.append(tobs)        
    return jsonify(stations)

  # 4. Dates Start route
@app.route("/api/v1.0/<start>") 
def start(start_date):
    # Create session & perform query to calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    start_date = input("Which date do you want to start? (use this format yyyy-mm-dd)")
    start_date = dt.datetime.strptime(start_date,'%Y-%m-%d')

    TempStDate = session.query(func.avg(Measurement.tobs),func.min(Measurement.tobs),func.min(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close()

    #* Return TMIN, TAVG, and TMAX.
    avgTemp=TempStDate[0][0]
    minTemp=TempStDate[0][1]
    maxTemp=TempStDate[0][2]
    return (
    f'The average temperature after your start date is: {avgTemp} ',
    f'The minimum temperature after your start date is:{minTemp} ',
    f'The maximium temperature after your start date is:{maxTemp}')

  # 5. Dates Start-End route
@app.route("/api/v1.0/<start>/<end>") 
def start_end(start_date):
    # Create session & perform query to calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    start_date = input("Which date do you want to start? (use this format yyyy-mm-dd)")
    start_date = dt.datetime.strptime(start_date,'%Y-%m-%d')
    end_date = input("Which date do you want to end? (use this format yyyy-mm-dd)")
    end_date = dt.datetime.strptime(end_date,'%Y-%m-%d')

    BetwTempDate = session.query(func.avg(Measurement.tobs),func.min(Measurement.tobs),func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
    return jsonify(BetwTempDate)


if __name__ == "__main__":  # to keep running the application
    app.run(debug=True)
