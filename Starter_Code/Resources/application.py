# Import the dependencies
from flask import Flask, jsonify
from sqlalchemy import create_engine, func, text, inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import pandas as pd
import datetime as dt
from datetime import datetime, timedelta

# Database Setup
engine = create_engine("sqlite:///" + "/Users/brysonwebb/Desktop/UTBootCamp/Homework/sqlalchemy-challenge/Starter_Code/Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
measurement =Base.classes.measurement
station =Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
measurement_session = session.query(measurement).all()
measurement_df = pd.DataFrame([vars(measurement) for measurement in measurement_session])
measurement_df_new = measurement_df.set_index("id")
print(measurement_df_new)
#################################################
# Flask Setup
#################################################
for column in measurement_df_new.columns:
    print(f"{column}: {measurement_df_new[column].dtype}")

# Your existing code for SQLAlchemy setup and data retrieval
# ...
most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
most_recent_date_str = most_recent_date[0]
if most_recent_date_str:
    twelve_months_ago = dt.datetime.strptime(most_recent_date_str, "%Y-%m-%d") - dt.timedelta(days=365)
    print(twelve_months_ago)
    # precipitation_data = session.query(measurement.date, measurement.prcp)\
    #     .filter(measurement.date >= twelve_months_ago)\
    #     .order_by(measurement.date).all()

# Create an instance of the Flask classy
app = Flask(__name__)

# Define the route for the homepage
@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precipitation_data = session.query(measurement.date, measurement.prcp)\
        .filter(measurement.date >= twelve_months_ago)\
        .order_by(measurement.date).all()
    precipitation_list = [{"date": date, "prcp": prcp} for date, prcp in precipitation_data]
    return jsonify(precipitation_list)
   
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(measurement.station).distinct().all()
    stations_list = [station[0] for station in stations]
    return jsonify({"stations": stations_list})

@app.route("/api/v1.0/tobs")
def tobs():
    twelve_months_ago = dt.datetime.strptime(most_recent_date_str, "%Y-%m-%d") - dt.timedelta(days=365)
    session = Session(engine)
    tobs_app = session.query(measurement.tobs)\
                        .filter(measurement.station == "USC00519281")\
                        .filter(measurement.date > twelve_months_ago)\
                        .group_by(measurement.tobs)\
                        .all()
                        
    date_app = session.query(measurement.date)\
                        .filter(measurement.station == "USC00519281")\
                        .filter(measurement.date > twelve_months_ago)\
                        .group_by(measurement.tobs)\
                        .all()
    tobs_list = [tob[0] for tob in tobs_app]
    date_list = [date[0] for date in date_app]
    tob_date_dict = {'tobs' : tobs_list,
                     'dates' : date_list}
    return jsonify("BELOW ARE THE TEMPATURES FOR THE LAST YEAR ON THE MOST ACTIVE STATION", [tob_date_dict])

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start = None, end = "2017-8-23"):
    session = Session(engine)
    print(" in stats")
    calculation = session.query(func.min(measurement.tobs),func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <=end).all()
    date_stats = {}
    date_stats["TMIN"]= calculation[0][0]
    date_stats["TAVG"]= round(calculation[0][1],2)
    date_stats["TMAX"]= calculation[0][2]
    return date_stats

if __name__ == "__main__":
    app.run(debug=True)

#################################################
# Flask Routes
#################################################