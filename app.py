from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import datetime as dt
from dateutil import parser



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brukere.db'
app.config['SECRET_KEY'] = 'asdasdas1$$34asld34KDKAMF€@42LASLasdDLAS€€@AASD'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    joinedDate = db.Column(db.DateTime(timezone=True), default=dt.datetime.now())
    password_hash = db.Column(db.String(120), nullable=False)
    days = db.Column(db.PickleType, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)




    def addDays(self):
        self.days = []
        for i in range(51):
            dag = Day(id=i)
            self.days.append(dag)
            

class Day:
    def __init__(self, id ,wakeUp=False,mourningRoutine=False,excercise=False,readPages=False,newSkill=False):
        self.id = int(id)
        self.wakeUp = wakeUp
        self.mourningRoutine = mourningRoutine
        self.excercise = excercise
        self.readPages = readPages
        self.newSkill = newSkill
    
    def __repr(self):
        return self.id
  
    def isFalse(self):
        counter=0
        for a in [self.wakeUp,self.mourningRoutine,self.excercise,self.readPages,self.newSkill]:
            if not a:
                counter+=1
        return counter


#@app.before_first_request
def before_first_request():
    with app.app_context():
        db.drop_all()
        db.create_all()
    
    """
    user1 = User(email="marius.bakken.berg@gmail.com",firstName="Marius",lastName="Berg",days=[])
    user1.set_password("marius")
    db.session.add(user1)

    user1.addDays()
    dager = list(user1.days)
    print(dager[1].id)
    db.session.commit()
    """
def loginFunction(user):
    if user and user.check_password(request.form['password']):
        session['email'] = user.email
        session['id'] = user.id

        return True

def registerFunction():
    
        # create new user with email and password from form
        user = User(email=request.form['email'],firstName=request.form['firstName'],lastName=request.form['lastName'],days=[])
        user.set_password(request.form['password'])
        user.addDays()

        # set user's role to default value of 'user'

        # add user to database
        db.session.add(user)
        db.session.commit()

        # log in user
        session['email'] = user.email
        session['id'] = user.id

def is_logged_in():
    if 'email' in session:
        return True
    return False

    
def showCorrectDay(user):
    x = dt.datetime.now()
    day = int((x-user.joinedDate).days)

    return day

def userActivities(user,day):
    temp = list(user.days)
    return temp[day]

def updateactivity(user,day,a):
    d = list(user.days)
    a = int(a)
    if a==0:
        d[day].wakeUp = True
    elif a==1:
        d[day].mourningRoutine = True
    elif a==2:
        d[day].excercise = True
    elif a==3:
        d[day].readPages = True
    elif a==4:
        d[day].newSkill = True



    User.query.filter_by(id=session['id']).update(dict(days = d))
    db.session.commit()

def skippedActivites(user):
    today = showCorrectDay(user)

    counter = 0
    for a in user.days[1:today+1]: #First day-object in list doesnt count for some reason (Have to fix), so from object 1 to the actudalday + 1 to offset for the first day that doesnt count and we dont want to count today
        counter += a.isFalse()

    return counter


@app.route('/', methods=['GET','POST'])
def home():
    if request.method=='POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            return render_template('index.html', error='Email already exists')
        registerFunction()
        return redirect('/profile')
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not is_logged_in():
        if request.method == 'POST':
            # get user from database
            user = User.query.filter_by(email=request.form['email']).first()
            # if user exists and password is correct, log in user
            if loginFunction(user):
                return redirect('/profile')

            # if user does not exist or password is incorrect, show error message
            return render_template('login.html', error='Invalid email or password')

        # if method is GET, show login page
        return render_template('login.html')
    else:
        return redirect('/profile')

@app.route('/logout')
def logout():
    # remove user from session
    for s in ['email','id']:
        session.pop(s)

    return redirect('/')

@app.route('/profile', methods=['GET','POST'])
def profile():
    if session.get('id')==False:
        return redirect('/')
    
    day = request.args.get('day')
    if day:
        day = int(day)
        if day>50:
            day = 50
    id = session['id']
    user = User.query.filter_by(id=session['id']).first()
    if not day:
        day = showCorrectDay(user)+1
    tasks = request.form.getlist('actv')

    if tasks:
        print('hello')
        updateactivity(user,day,tasks[0])
    activities = userActivities(user, day)
    print(skippedActivites(user))
    return render_template('profile.html',user=user, day = day, actualDay = showCorrectDay(user) ,activities = activities, skippedActivities = skippedActivites(user))


if __name__ == '__main__':
    app.run(debug=True)