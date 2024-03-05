import datetime
import os
import psycopg2
import requests
import pytest
from .main import App
app = App()

DATABASE_URL = os.getenv('DATABASE_URL', 'Database URL not found')
temperatureLogTestTable = "temperaturelogtest"
hvacActionLogTestTable = "hvacactionlogtest"

@pytest.fixture(autouse=True)
def clear_test_table():
    sql1 = f"""DELETE FROM {temperatureLogTestTable}"""
    sql2 = f"DELETE FROM {hvacActionLogTestTable}"
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(sql1)
                cur.execute(sql2)
                conn.commit()
    except (requests.exceptions.RequestException, psycopg2.DatabaseError) as e:
        print(e)
        pass
    yield

def test_save_temperature_to_database():
    app.save_temperature_to_database(datetime.datetime.now(), 44, temperatureLogTestTable)
    rows = get_rows_from_table(temperatureLogTestTable)
    assert len(rows) > 0

def test_save_temperature_to_database_null_timestamp():
    app.save_temperature_to_database(None, 44, temperatureLogTestTable)
    rows = get_rows_from_table(temperatureLogTestTable)
    assert len(rows) == 0
    
def test_save_event_to_database_null_temperature():
    app.save_temperature_to_database(datetime.datetime.now(), None, temperatureLogTestTable)
    rows = get_rows_from_table(temperatureLogTestTable)
    assert len(rows) == 0
    
def test_save_hvac_action_to_database():
    app.save_hvac_action_to_database(datetime.datetime.now(), "TurnOnHeater", 10, 22, hvacActionLogTestTable)
    rows = get_rows_from_table(hvacActionLogTestTable)
    assert len(rows) == 1
    
def test_save_hvac_action_to_database_null_temperature():
    app.save_hvac_action_to_database(datetime.datetime.now(), "TurnOnHeater", None, 22, hvacActionLogTestTable)
    rows = get_rows_from_table(hvacActionLogTestTable)
    assert len(rows) == 0

def test_save_hvac_action_to_database_null_targetTemperature():
    app.save_hvac_action_to_database(datetime.datetime.now(), "TurnOnHeater", 10, None, hvacActionLogTestTable)
    rows = get_rows_from_table(hvacActionLogTestTable)
    assert len(rows) == 0

def test_save_hvac_action_to_database_null_action():
    app.save_hvac_action_to_database(datetime.datetime.now(), None, 10, 22, hvacActionLogTestTable)
    rows = get_rows_from_table(hvacActionLogTestTable)
    assert len(rows) == 0

def get_rows_from_table(testTable):
    sql = f"""SELECT * FROM {testTable}"""
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()
    except (requests.exceptions.RequestException, psycopg2.DatabaseError) as e:
            print(e)
            pass