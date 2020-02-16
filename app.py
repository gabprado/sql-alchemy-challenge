from flask import Flask, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import json
import datetime


app = Flask(__name__)
engine = create_engine("sqlite:///Data/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


@app.route("/")
def home():
    return (
        f"<h1>Welcome!</h1><br/>"
        f"<h3>Available Routes:</h3><br/>"
        f"<a href = ../api/v1.0/precipitation>Precipitation Observations</a> <br/>"
        f"<a href = ../api/v1.0/stations>Sation List</a> <br/>"
        f"<a href = ../api/v1.0/tobs>Temprature Observations</a><br/>"
        f"<a href = ../api/v1.0/2016-08-26>Temprature Observartion Summary Starting 2016-08-26</a><br/>"
        f"<a href = ../api/v1.0/2015-08-26/2016-08-26>Temprature Observartion Summary From 2015-08-26 To 2016-08-26</a><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    max_date = session.query(func.max(Measurement.date)).scalar()
    rain = (
        session.query(
            func.strftime("%m-%Y", Measurement.date).label("obs_date"),
            func.sum(Measurement.prcp),
        )
        .group_by("obs_date")
        .order_by(Measurement.date)
        .filter(
            Measurement.date
            >= func.strftime("%Y-%m-%d", max_date, "start of month", "-11 months")
        )
        .all()
    )
    precip_dict = dict(rain)
    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
def stations():
    stations = (
        session.query(
            Measurement.station,
            Station.name,
            func.count(Measurement.date).label("Observations"),
        )
        .join(Station, Station.station == Measurement.station)
        .group_by(Measurement.station, Station.name)
        .order_by(desc("Observations"))
        .all()
    )
    stations_dict = [
        {
            "station_id": station[0],
            "station_name": station[1],
            "observation_count": station[2],
        }
        for station in stations
    ]

    return jsonify(stations_dict)


@app.route("/api/v1.0/tobs")
def tobs():
    max_date = session.query(func.max(Measurement.date)).scalar()
    temp_obs = (
        session.query(
            Measurement.date, Measurement.station, Station.name, Measurement.tobs
        )
        .join(Station, Station.station == Measurement.station)
        .filter(Measurement.date > func.strftime("%Y-%m-%d", max_date, "-1 years"))
        .all()
    )
    tobs_dict = [
        {
            "observation_date": temp_ob[0],
            "station_id": temp_ob[1],
            "station_name": temp_ob[2],
            "temp_observation": temp_ob[3],
        }
        for temp_ob in temp_obs
    ]
    return jsonify(tobs_dict)


@app.route("/api/v1.0/<start_date>")
def temp_start(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    temp_smry = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start_date)
        .all()
    )
    temp_smry_dict = [
        {
            "min_temprature": obs[0],
            "average_temprature": obs[1],
            "max_temprature": obs[2],
        }
        for obs in temp_smry
    ]
    return jsonify(temp_smry_dict)


@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_range(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    temp_smry = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start_date)
        .filter(Measurement.date <= end_date)
        .all()
    )
    temp_smry_dict = [
        {
            "min_temprature": obs[0],
            "average_temprature": obs[1],
            "max_temprature": obs[2],
        }
        for obs in temp_smry
    ]
    return jsonify(temp_smry_dict)


if __name__ == "__main__":
    app.run(debug=True)
