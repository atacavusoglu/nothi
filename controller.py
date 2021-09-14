
from logging import log
from MySQLdb import cursors
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from werkzeug import useragents
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps


class RegisterForm(Form):
    name = StringField("Name :",validators=[validators.Length(min=2 ,max=25, message ="Min =2 Max =25")])
    username = StringField("Username :",validators=[validators.Length(min=2 ,max=25, message ="Min =2 Max =25")])
    email = StringField("Email :",validators=[validators.Email(message="Must enter your email")])
    password = PasswordField("Password :",validators=[validators.DataRequired(message="Must enter your password")])

class LoginForm(Form):
    username = StringField("Username :")
    password = PasswordField("Password :")


class CommentsForm(Form):
    title = StringField("Title",validators =[validators.Length(min=5 , max =100)])
    content = StringField("Comment",validators =[validators.Length(min=10)])

app = Flask(__name__)

app.config["MYSQL_HOST"]= "localhost"
app.config["MYSQL_USER"] ="root"
app.config["MYSQL_PASSWORD"] =""
app.config["MYSQL_DB"] ="end"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

app.secret_key ="şifre"

mysql = MySQL(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session :
            return f(*args,**kwargs)
        else :
            flash("Login to see this page","danger")
            return redirect(url_for("login"))
    return decorated_function
        




@app.route("/")
def index():
    return render_template("index.html")



@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register",methods = ["POST","GET"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        cursor = mysql.connection.cursor()
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        sorgu = "Insert into users (name,username,mail,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,username,email,password))
        mysql.connection.commit()
        cursor.close()
        flash("Succesfuly Registered","success")
        return redirect(url_for("index"))
        
    else :
        return render_template("register.html",form=form)
# login
@app.route("/login",methods =["POST","GET"])
def login():
    
    form = LoginForm(request.form)
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        username = form.username.data
        password_entered = form.password.data
        sorgu = "Select * From users where username = %s"
        result = cursor.execute(sorgu,(username,))
        if result > 0 :
            data = cursor.fetchone()
            real_password = data["password"]
            if password_entered == real_password:
                flash("Succesfuly Logged In","success")
                session["username"] =username
                session["logged_in"] = True
                return(redirect(url_for("index")))
            else:
                flash("False password","danger")
                return redirect(url_for("login"))

        else :
            flash("There is no username like that","danger")
            return redirect(url_for("login"))


    else :
        return render_template("login.html",form=form)
# about you
@app.route("/about/you")
def about_you():
    return render_template("aboutyou.html")

# add comment
@app.route("/comments",methods =["GET","POST"])
@login_required
def add_comment():
    
    form = CommentsForm(request.form) # yeni form
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data 
        cursor = mysql.connection.cursor()
        sorgu = "Insert into comments(title,username,content) VALUES (%s,%s,%s) "
        cursor.execute(sorgu,(title,session["username"],content))
        mysql.connection.commit()
        cursor.close()
        flash("Your comment has been saved","info")
        return redirect(url_for("add_comment"))

    else :
        cursor = mysql.connection.cursor()
        sorgu = "Select * From comments"
        result = cursor.execute(sorgu)
        
        if result > 0:
            any_comment = cursor.fetchall()
            return render_template("comments.html",any_comment= any_comment,form=form)
        else :

            return render_template("comments.html",form=form)


#logout
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Çıkış yapıldı","success")
    return redirect(url_for("index"))


#search
@app.route("/search",methods=["POST","GET"])
def search():
    if request.method =="POST" :
        cursor = mysql.connection.cursor()
        keyword = request.form.get("keyword")
        sorgu ="Select * From comments where title like '%"+keyword+ "%' "
        result = cursor.execute(sorgu)
        if result == 0 :
            flash("There is no comments like that","danger")
            return redirect(url_for("search"))
        else :
            liste = cursor.fetchall()
            return render_template("search_page.html",liste=liste)
            


    else :
        return render_template("index.html")

@app.route("/comments/<string:id>")
@login_required
def show_comments(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * from comments where id = %s"
    result = cursor.execute(sorgu,(id,))
    if result > 0 :
        comment = cursor.fetchall()
        return render_template("show_comments.html",comment=comment)
    else :
        flash("There is no comment like that bro","info")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)