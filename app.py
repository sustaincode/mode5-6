from flask import Flask,request,render_template
import google.generativeai as genai
import os
import sqlite3
import datetime


gemini_api_key = os.getenv("gemini_api_key")
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))


@app.route("/main", methods=["GET", "POST"])
def main():
    uname = request.form.get("q")
    print(uname)
    t = datetime.datetime.now()
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("insert into users(name,timestamp) values(?,?)", (uname, t))
    conn.commit()
    c.close()
    conn.close()
    return render_template("main.html")  # Ensure this file exists

@app.route("/gemini",methods=["GET","POST"])
def gemini():
    return(render_template("gemini.html"))
@app.route("/gemini_reply",methods=["GET","POST"])
def gemini_reply():
    q = request.form.get("q")
    print(q)
    r = model.generate_content(q)
    return(render_template("gemini_reply.html",r=r.text))

@app.route("/user_log",methods=["GET","POST"])
def user_log():
    #read
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("select * from users")
    r=""
    for row in c:
        print(row)
        r= r+str(row)
    c.close()
    conn.close()
    return(render_template("user_log.html",r=r))

@app.route("/delete_log",methods=["GET","POST"])
def delete_log():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("delete from users")
    conn.commit()
    c.close()
    conn.close()
    return(render_template("delete_log.html"))

if __name__ == "__main__":
    app.run()