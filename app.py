import hashlib
from flask import Flask
from flask import request
import database.tools

app = Flask(__name__)

database = database.tools.Database('testdb.db')


@app.route('/auth', methods=['POST'])
def auth():
    id = int(request.form.get('id'))
    password = request.form.get('password')

    if id is None or password is None:
        return 'Missing id or password', 400

    # todo: need to check if id exists
    # todo: transfer this hashing process to the client so the password wont be transmitted
    #  clearly readable
    hashed_password = hashlib.blake2b(bytes(password, 'utf-8')).hexdigest()

    database_password = database.get_password(id)

    if hashed_password == database_password:
        return database.generate_api_key(id)
    else:
        return 'Wrong Password', 604


if __name__ == '__main__':
    app.run(host='0.0.0.0.', port=6000)
