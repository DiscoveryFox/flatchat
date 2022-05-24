import json
import sqlite3
import secrets
import time


class Database:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def get_password(self, id: int):
        self.cursor.execute("SELECT password FROM users WHERE id = ?", (id,))
        password = self.cursor.fetchone()[0]
        print(password)
        return password

    def add_user(self, username, email, password):
        # get highest id from the Database
        self.cursor.execute("SELECT MAX(id) FROM users")
        self.connection.commit()
        id = self.cursor.fetchone()[0]
        if id is None:
            id = 1
        else:
            id += 1
        self.cursor.execute("INSERT INTO users ( username, userid, email, password) VALUES (?, "
                            "?, ?, "
                            "?)", (username, f'{username}#{id}', email, password))
        self.connection.commit()

    def generate_api_key(self, id):
        # generate api token
        api_key = secrets.token_urlsafe(64)
        # get linux timestamp
        timestamp = int(time.time())
        # store token and time in a list to serialize it to json to store it in the Database
        api_list = [timestamp, api_key]
        # add the serialized list to the Database
        self.cursor.execute("UPDATE users SET api_key = ? WHERE id = ?", (json.dumps(api_list), id))
        self.connection.commit()
        return api_key

    def get_api_key(self, id):
        self.cursor.execute("SELECT api_key FROM users WHERE id = ?", (id,))
        api_key = self.cursor.fetchone()[0][1]
        return api_key

    def check_api_key(self, id):
        self.cursor.execute("SELECT api_key FROM users WHERE id = ?", (id,))
        timestamp, api_key = self.cursor.fetchone()[0]

        if int(time.time()) - timestamp > 172800:
            # clear api_key if it is older than 2 days
            self.cursor.execute("UPDATE users SET api_key = ? WHERE id = ?", (None, id))

    def get_all_users(self):
        self.cursor.execute("SELECT * FROM users")
        data = self.cursor.fetchall()
        newdata = list()
        for entry in data:
            entry = list(entry)
            entry[5] = json.loads(entry[5])
            newdata.append(entry)
        return newdata

    def close(self):
        self.connection.close()
