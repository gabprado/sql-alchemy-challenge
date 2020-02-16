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
        f"Welcome!<br/>"
        f"Available Routes:<br/>"
        f"<a href = ../api/v1.0/precipitation>Precipitation</a> <br/>"
        f"<a href = ../api/v1.0/stations>Station</a> <br/>"
        f"<a href = ../api/v1.0/tobs>Temprature Observations</a> <br/>"
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
            "station_name": temp_ob[1],
            "temp_observation": temp_ob[2],
        }
        for temp_ob in temp_obs
    ]
    return jsonify(tobs_dict)


if __name__ == "__main__":
    app.run(debug=True)
