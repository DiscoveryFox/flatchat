from flask import Flask
from flask import request
from werkzeug.security import check_password_hash, generate_password_hash
import database.tools

app = Flask(__name__)

database = database.tools.Database('testdb.db')


@app.route('/auth', methods=['POST'])
def auth():
    id = request.form.get('id')
    password = request.form.get('password')

    database_password = database.get_password(id)

    print(database_password)

    if check_password_hash(password, database_password):
        return database.generate_api_key(id)


if __name__ == '__main__':
    app.run(host='0.0.0.0.', port=6000)
