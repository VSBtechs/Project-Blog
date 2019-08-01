import os


from flask import Flask
from flask import request
from flask_mysqldb import MySQL
from werkzeug import generate_password_hash, check_password_hash

from flask import render_template, json , redirect

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'root'
    app.config['MYSQL_DB'] = 'GoBlog'
  
    mysql = MySQL(app)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    def add_user(_firstname,_lastname, _email, _password , _username):
        
        cursor = mysql.connection.cursor()
        _hashed_password = generate_password_hash(_password)
        cursor.callproc('createUser',(_firstname,_lastname,_username, _email,_password))
        data = cursor.fetchall()
        print('---data----')
        print(data)
        print('---data----')
        if len(data) is 0:
           mysql.connection.commit(),
           cursor.close()
           print("done commit")
           return "done commit user created"
        else:
           return json.dumps({'error':str(data[0])})
        
    @app.route('/showSignUp')  
    def showSignUp():
        return render_template('signup.html')
    

    @app.route('/signup',methods=['POST','GET'])
    def signup():
        try:
           print(request.args)
           _firstname = request.form['inputFirstName']
           _lastname = request.form['inputLastName']
           _username = request.form['inputUserName']
           _email = request.form['inputEmail']
           _password = request.form['inputPassword']
    
           if _firstname and _lastname and _email and _password and _username:
        
                print('-------')
                print(_firstname,_lastname, _email, _password , _username)
                print('-------')
                add_user(_firstname,_lastname, _email, _password, _username )     
                return redirect('/showSignUp')
           else:
                return json.dumps({'html':'<span>Enter the required fields</span>'})
     
        except Exception as e:
           return json.dumps({'error':str(e)})

    return app
