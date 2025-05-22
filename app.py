from flask import Flask, redirect, render_template, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user

app = Flask(__name__)
app.secret_key = "rans"
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Where to redirect if not logged in
login_manager.login_message_category = "info"

db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
    id = db.Column("id",db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(255), nullable=False)

    notes = db.relationship("Notes", backref = "user", lazy = True)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return f"<User {self.name}>"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(1000), nullable = False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False )

    def __init__(self, note, user_id):
        self.note = note
        self.user_id = user_id

    def __repr__(self):
        return f"<Note {self.id} for user {self.user_id}>"
    

@app.route("/")
@login_required
def home():
    return(render_template("base.html"))

@app.route("/view")
@login_required
def view():
    info = Users.query.all()
    return (render_template('view.html', info=info))

@app.route("/notes")
@login_required
def viewnotes():
    notes = Notes.query.filter_by(user_id = current_user.id).all()
    return (render_template('notes.html', notes = notes))

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nme"]
        password = request.form.get("password")

        user_found=Users.query.filter_by(name=user).first()
        
        if user_found:
            if check_password_hash(user_found.password, password):
                login_user(user_found)
                flash(f"Welcome {user_found.name}", "success")
                return redirect(url_for("acct"))
            else:
                flash("Wrong password", "danger")
                return render_template("login.html")    
        else:
            flash("User doesn't exist, please register first", "danger")
            return redirect(url_for("register"))
    
    else:
        if current_user.is_authenticated:
            flash("You are already logged in gee", "info")
            return redirect(url_for("acct"))
        return(render_template("login.html"))

@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        user_exists = Users.query.filter_by(name = name).first()
        
        if user_exists:
            flash("User already exists, please pick another name", "danger")
            return render_template("register.html")
        
        new = Users(name, None, hashed_password)
        db.session.add(new)
        db.session.commit()
        login_user(new)
        flash("Account created")
        return redirect(url_for("acct"))
    return(render_template("register.html"))

@app.route("/user", methods = ["POST", "GET"])
@login_required
def acct():
    email = None
    user_found = current_user
        
    # email = session.get("email", user_found.email) #To get the existing email if there is one

    if request.method == "POST":
        # email = request.form.get("email")
        action = request.form.get("action")
        note_text = request.form.get("note") #to get the information from the form
        
        # session["email"] = email
        #user_found.email = email #Update the email in the session and database
        
        # flash("Email saved", "info")

        if action == "Save":
            note_id = request.form.get("note_id")
            if not note_text:
                 flash("Note cannot be empty")
            elif note_id:                    
                selected_note = Notes.query.filter_by(id=note_id,user_id=user_found.id).first()
                if selected_note:
                    selected_note.note = note_text
                    flash("Note updated successfully", "success")
                    db.session.commit()
                    return redirect(url_for("acct"))
            else:
                new_note = Notes(note=note_text, user_id = user_found.id) #to save the new note, filing up the required arguments for the class
                db.session.add(new_note)
                flash("Note saved", "info")
                db.session.commit()
                return redirect(url_for("acct", new = new_note.id))        

        elif action == "Delete": 
            note_id = request.form.get("note_id")
            if note_id:
                note_delete = Notes.query.filter_by(id=note_id, user_id=user_found.id).first()
                if note_delete:
                    db.session.delete(note_delete)
                    db.session.commit()
                    flash("Note deleted", "Success")
                else:
                    flash("Note does not exist", "warning")    
            else: 
                flash("Note not found", "warning")
            return redirect(url_for("acct"))    

        elif action == "Edit":
            note_id = request.form.get("note_id")
            if note_id:
                note_to_edit = Notes.query.filter_by(id = note_id, user_id = user_found.id).first()
                return (render_template("index.html", selected_note = note_to_edit, notes = user_found.notes))
            else:
                flash("Note does not exist", "warning")        
            
    db.session.commit()
        
    notes = user_found.notes #retrieving notes from the users notes          
    return (render_template("index.html", notes = notes)) # email=email was removed

@app.route("/logout", methods = ["POST", "GET"])
@login_required    
def logout():
    flash(f"You've been logged out {current_user.name}", "info")
    logout_user()
    return redirect(url_for("login"))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)