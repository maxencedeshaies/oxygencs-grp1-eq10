import datetime
import os
import psycopg2
import requests
import pytest
from .main import App
app = App()

DATABASE_URL = os.getenv('DATABASE_URL', 'Database URL not found')
testtable = "temperaturelogtest"

@pytest.fixture(autouse=True)
def clear_test_table():
    sql = f"""DELETE FROM {testtable}"""
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()
    except (requests.exceptions.RequestException, psycopg2.DatabaseError) as e:
        print(e)
        pass
    yield

def test_save_temperature_to_database():
    app.save_temperature_to_database(datetime.datetime.now(), 44, DATABASE_URL, testtable)
    rows = get_rows()
    assert len(rows) > 0

def test_save_temperature_to_database_null_timestamp():
    app.save_temperature_to_database(None, 44, DATABASE_URL, testtable)
    rows = get_rows()
    assert len(rows) == 0
    
def test_save_event_to_database_null_temperature():
    app.save_temperature_to_database(datetime.datetime.now(), None, DATABASE_URL, testtable)
    rows = get_rows()
    assert len(rows) == 0

def get_rows():
    sql = f"""SELECT * FROM {testtable}"""
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()
    except (requests.exceptions.RequestException, psycopg2.DatabaseError) as e:
            print(e)
            pass