import sqlite3
import ipaddress
from flask import Flask, request

TABLE_CREATE_STRING = ("CREATE TABLE IF NOT EXISTS address"
                       "(id integer PRIMARY KEY,"
                       " address text NOT NULL,"
                       " status text NOT NULL);")

INSERT_STRING = ("INSERT INTO address (address, status) VALUES(?, ?)")

UPDATE_STRING = "UPDATE address SET status = ? WHERE address = ?"

CHECK_ADDRESS = "SELECT * FROM address WHERE address = ?"

database = sqlite3.connect("file::memory:?cache=shared")

app = Flask("ipaddr")


class DatabaseCursor:
    def __enter__(self):
        self.localconn = sqlite3.connect("file::memory:?cache=shared")
        return self.localconn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.localconn.commit()


def init_response():
    response = {}
    response['status'] = "Failure"
    return response


def address_available(address):
    with DatabaseCursor() as cursor:
        values = (address,)
        cursor.execute(CHECK_ADDRESS, values)
        return False if cursor.fetchone() is None else True


def update_address(address, option):
    with DatabaseCursor() as cursor:
        try:
            values = (option, address)
            cursor.execute(UPDATE_STRING, values)
            return True
        except sqlite3.Error as error:
            print("Error: " + str(error) )
            return False


@app.route('/create', methods=["POST"])
def add_address():
    response = init_response()
    response["status"] = "failure"
    address_block = request.args.get("address-block")
    localconn = sqlite3.connect("file::memory:?cache=shared")
    if address_block is not None:
        with DatabaseCursor() as cursor:
            try:
                network = ipaddress.ip_network(address_block)
                for ipa in network:
                    values = (str(ipa), 'available')
                    cursor.execute(INSERT_STRING, values)
                localconn.commit()
                response["status"] = "Success"
            except ValueError as error:
                response["message"] = str(error)
                print("Error")
    return response

@app.route('/acquire', methods=["POST"])
def acquire_address():
    response = init_response()
    address = request.args.get("address")
    if address_available(address):
        if update_address(address, 'acquired'):
            response["status"] = "Success"
            response["message"] = "Address " + address + " acquired"
        else:
            response["message"] = "Internal error occurred"
    else:
        response["message"] = "Address not available"
    return response


@app.route('/release', methods=["POST"])
def release_address():
    response = init_response()
    address = request.args.get("address")
    if address_available(address):
        if address_available(address):
            if update_address(address, 'available'):
                response["status"] = "Success"
                response["message"] = "Address " + address + " released"
            else:
                response["message"] = "Internal error occurred"
        else:
            response["message"] = "Address not available"
    return response


@app.route('/list', methods=["GET"])
def get_address():
    response = init_response()
    with DatabaseCursor() as cursor:
        cursor.execute("SELECT * FROM address;")
        address_list = []
        for result in cursor:
            item = {}
            item["address"] = result[1]
            item["status"] = result[2]
            address_list.append(item)
    response["status"] = "success"
    response["data"] = address_list
    return response


def init_db():
    cursor = database.cursor()
    cursor.execute(TABLE_CREATE_STRING)
    cursor.close()


def run_app():
    app.run()

if __name__ == "__main__":
    init_db()
    run_app()
    database.close()