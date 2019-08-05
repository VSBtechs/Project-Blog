import os
import logging

#from flask_session.__init__ import Session
from functools import wraps
from flask import Flask
from flask import request, flash, session
from flask_mysqldb import MySQL
from werkzeug import generate_password_hash, check_password_hash

from flask import render_template, json , redirect

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.urandom(24)
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
        
        cursor.callproc('createUser',(_firstname,_lastname,_username, _email,_hashed_password))
        data = cursor.fetchall()

        if len(data) is 0:
           mysql.connection.commit(),
           cursor.close()
           return "done commit user created"
        else:
           return json.dumps({'error':str(data[0])})

    def check_and_do_login(u_name,u_pswd):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE userName =%s", (u_name,))
        if cursor is not None:
          data = cursor.fetchone()

          try:
            password = data[5]
          except Exception:
            print('Invalid Username')
            return False
           
          cursor.close()
          if check_password_hash(password,u_pswd):
            app.logger.info('Password Matched')
            session['username'] = u_name   
            return True
          
          else:
            print('Invalid Password')
            return False
        
        else:
          print('Invalid user or Password')
          return False


    def ensure_logged_in(fn):
      @wraps(fn)
      def wrapper(*args, **kwargs):
          print('session-user  ',session,'   session-user')
          if not session.get('username'):
            print("Please log in first")
            return redirect('/showSignUp')
          return fn(*args, **kwargs)
      return wrapper

    
    @app.route('/dashboard')
    @ensure_logged_in
    def dashboard():
        print('session-user  ',session,'   session-user')
        return render_template('dashboard.html')

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        print('You have been logged out successfully')
        return redirect('/showSignUp')



    @app.route('/showSignUp')  
    def showSignUp():
        return render_template('signup.html')    
    

    @app.route('/signup',methods=['POST','GET'])
    def signup():
        try:
           _firstname = request.form['inputFirstName']
           _lastname = request.form['inputLastName']
           _username = request.form['inputUserName']
           _email = request.form['inputEmail']
           _password = request.form['inputPassword']
    
           if _firstname and _lastname and _email and _password and _username:
        
                add_user(_firstname,_lastname, _email, _password, _username )
                     
                return redirect('/showSignUp')
           else:
                return json.dumps({'html':'<span>Enter the required fields</span>'})
     
        except Exception as e:
           return json.dumps({'error':str(e)})

    @app.route('/signin')
    def signin():
          u_name = request.args.get('u_name')
          u_pswd = request.args.get('u_pswd')

          if u_name and u_pswd:
              log_success = check_and_do_login(u_name,u_pswd)

              if  log_success:
                app.logger.info('login succcesfull')

                return 'LOGGED IN SUCCESSFULLY'
              else:
                app.logger.info('Incorrect Credential')

                return ('Incorrect Credential, Try Again :)')      
          return 'Try Again :)'


    return app
