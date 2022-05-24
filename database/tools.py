import json
import sqlite3
import secrets
import time
from secrets import compare_digest


class Database:
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def get_password(self, id: int):
        self.cursor.execute("SELECT password FROM users WHERE id = ?", (id,))
        password = self.cursor.fetchone()[0]
        print(password)
        return password

    def add_user(self, username: str, email: str, password):
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

    def generate_api_key(self, id: int):
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

    def get_api_key(self, id: int):
        self.cursor.execute("SELECT api_key FROM users WHERE id = ?", (id,))
        api_key = self.cursor.fetchone()[0][1]
        return api_key

    def check_api_key(self, id: int):
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

    def get_contacts(self, id: int):
        self.cursor.execute("SELECT contacts FROM users WHERE id = ?", (id,))
        contacts = self.cursor.fetchone()[0]
        if contacts is None:
            return []
        else:
            return json.loads(contacts)

    def add_contact(self, id: int, contact_id: int):
        self.cursor.execute("SELECT contacts FROM users WHERE id = ?", (id,))
        contacts = self.cursor.fetchone()[0]
        if contacts is None:
            contacts = []
        else:
            contacts = json.loads(contacts)
        contacts.append(contact_id)
        contacts = list(set(contacts))
        self.cursor.execute("UPDATE users SET contacts = ? WHERE id = ?",
                            (json.dumps(contacts), id))
        self.connection.commit()

    def remove_contact(self, id: int, contact_id: int):
        self.cursor.execute("SELECT contacts FROM users WHERE id = ?", (id,))
        contacts = self.cursor.fetchone()[0]
        if contacts is None:
            contacts = []
        else:
            contacts = json.loads(contacts)
        contacts.remove(contact_id)
        self.cursor.execute("UPDATE users SET contacts = ? WHERE id = ?",
                            (json.dumps(contacts), id))
        self.connection.commit()

    def get_messages(self, id: int, other_id: int = None):
        if other_id is None:
            self.cursor.execute("SELECT * FROM messages WHERE ids LIKE ?", (f'%{id}%',))
            ids = self.cursor.fetchall()
            newdata = list()
            for entry in ids:
                entry = list(entry)
                entry[0] = json.loads(entry[0])
                newdata.append(entry)
            return newdata
        else:
            self.cursor.execute("SELECT * FROM messages WHERE ids LIKE ?", (f'%{id}%',))
            ids = self.cursor.fetchall()
            newdata = list()
            for entry in ids:
                entry = list(entry)
                entry[0] = json.loads(entry[0])
                if other_id in entry[0]:
                    newdata.append(entry)
            return newdata

    def add_message(self, ids: list[int], message: str):
        # get linux timestamp
        timestamp = int(time.time())

        ids_json = json.dumps(ids)

        # make message not harmful to the database
        message = message.replace("'", "''")

        self.cursor.execute("INSERT INTO messages ( ids, message, timestamp) VALUES (?, ?, ?)",
                            (ids_json, message, timestamp))
        self.connection.commit()

    def change_password(self, id: int, password: str, new_password_hash: str):
        self.cursor.execute("SELECT password FROM users WHERE id = ?", (id,))
        old_password = self.cursor.fetchone()[0]
        if compare_digest(old_password, password):
            self.cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password_hash,
                                                                               id))
            self.connection.commit()
            return True
        return new_password_hash

    def close(self):
        self.connection.close()
