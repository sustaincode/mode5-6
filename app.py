from flask import Flask,request,render_template
from google import genai
import google.generativeai as genai1
import os
import sqlite3
import datetime
import requests



gemini_api_key = os.getenv("gemini_api_key")
genai1.configure(api_key=gemini_api_key)
model = genai1.GenerativeModel("gemini-2.0-flash")
telegram_api = os.getenv("telegram_api")
domain_url = os.getenv('WEBHOOK_URL')

### Initialize the Google Gemini client
gemini_client = genai.Client(api_key=gemini_api_key)
gemini_model = "gemini-2.0-flash"


app = Flask(__name__)
@app.route("/",methods=["GET","POST"])
def index():
    return render_template("index.html")



@app.route("/paynow",methods=["GET","POST"])
def paynow():
    return render_template("paynow.html")

@app.route("/start_telegram",methods=["GET","POST"])
def start_telegram():

    domain_url = os.getenv('WEBHOOK_URL')

    # The following line is used to delete the existing webhook URL for the Telegram bot
    delete_webhook_url = f"https://api.telegram.org/bot{telegram_api}/deleteWebhook"
    requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})
    
    # Set the webhook URL for the Telegram bot
    set_webhook_url = f"https://api.telegram.org/bot{telegram_api}/setWebhook?url={domain_url}/telegram"
    webhook_response = requests.post(set_webhook_url, json={"url": domain_url, "drop_pending_updates": True})
    print('webhook:', webhook_response)
    if webhook_response.status_code == 200:
        # set status message
        status = "The telegram bot is running. Please check with the telegram bot. @mod5-6-gemini"
    else:
        status = "Failed to start the telegram bot. Please check the logs."
    
    return(render_template("telegram.html", status=status))

@app.route("/telegram",methods=["GET","POST"])
def telegram():
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        # Extract the chat ID and message text from the update
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        if text == "/start":
            r_text = "Welcome to the Gemini Telegram Bot! You can ask me any finance-related questions."
        else:
            # Process the message and generate a response
            system_prompt = "You are a financial expert.  Answer ONLY questions related to finance, economics, investing, and financial markets. If the question is not related to finance, state that you cannot answer it."
            prompt = f"{system_prompt}\n\nUser Query: {text}"
            r = gemini_client.models.generate_content(
                model=gemini_model,
                contents=prompt
            )
            r_text = r.text
        
        # Send the response back to the user
        send_message_url = f"https://api.telegram.org/bot{telegram_api}/sendMessage"
        requests.post(send_message_url, data={"chat_id": chat_id, "text": r_text})

    return('ok', 200)
@app.route("/stop_telegram", methods=["GET", "POST"])
def stop_telegram():
    domain_url = os.getenv('WEBHOOK_URL')
    # Call Telegram API to delete the webhook
    delete_webhook_url = f"https://api.telegram.org/bot{telegram_api}/deleteWebhook"
    response = requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})
    print('delete webhook:', response.text)
    if response.status_code == 200:
        status = "The telegram bot has been stopped (webhook deleted)."
    else:
        status = "Failed to stop the telegram bot. Please check the logs."
    return render_template("telegram.html", status=status)

@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    prediction = None
    if request.method == "POST":
        sgd_value = request.form.get("q")
        try:
            sgd_value = float(sgd_value)
            prediction = 90.2 + (-50.6 * sgd_value)
        except (TypeError, ValueError):
            prediction = "XXX"
    return render_template("prediction.html", prediction=prediction)


@app.route("/main", methods=["GET", "POST"])
def main():
    if request.method == "GET":
        return render_template("main.html")
    uname = request.form.get("q")
    if not uname or uname.strip() == "":
        return render_template("index.html", error="Please enter a valid username.")
    print(uname)
    t = datetime.datetime.now()
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("insert into users(name,timestamp) values(?,?)", (uname, t))
    conn.commit()
    c.close()
    conn.close()
    return render_template("main.html")

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