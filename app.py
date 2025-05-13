#gemini
from flask import Flask,request,render_template
app = Flask(__name__)
@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/gemini",methods=["GET","POST"])
def gemini():
    return(render_template("gemini.html"))

@app.route("/gemini_reply",methods=["GET","POST"])
def gemini_reply():
    q = request.form.get("q")
    print(q)
    #gemini
    r=q
    return(render_template("gemini_reply.html",r=r))


if __name__ == "__main__":
    app.run()
