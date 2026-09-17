from flask import Flask, render_template, request, redirect
import time
from math import floor
from os import environ
import kv_redis
import kv_dummy
import db_postgres
import db_dummy
import redis

app = Flask(__name__)

if "KARL_MAIL" in environ:
	karl_mail = environ["KARL_MAIL"]
else:
	karl_mail = "karl@marx.com"

default_text = "Griechischer Wein ist so wie das Blut der Erde"

if "KV_URL" in environ:
	kv_bridge = kv_redis.Bridge(default_text)
else:
	print("Using dummy KV")
	kv_bridge = kv_dummy.Bridge(default_text)

if "DB_URL" in environ:
	db = db_postgres.Database()
else:
	db = db_dummy.Database()

cooldown_minutes = 5

def minutes_since_last_change():
	now = time.time()
	last_change = kv_bridge.get_last_change()
	return floor((now - last_change) / 60)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/newsletter", methods=["POST"])
def newsletter_signup():
	if request.form["email"] == karl_mail:
		return redirect("/karl_marx_very_secret_page")

	db.add_subscriber(request.form["email"])
	return "Sie wurden erfolgreich zum E-Mail-Verteiler hinzugefügt!"

@app.route("/karl_marx_very_secret_page")
def secret_page():
	minutes_to_wait = cooldown_minutes - minutes_since_last_change()
	can_change = minutes_to_wait <= 0

	return render_template(
		"secret.html",
		state_text = kv_bridge.get_text(),
		can_change = can_change,
		minutes_next_change = minutes_to_wait
	)

@app.route("/changetext", methods = ["POST"])
def change_text():
	words = request.form["text"].lower().split(" ")
	if "fdp" in words:
		return "Die FDP ist hier verboten! Wir haben Mitarbeiter zu deinem Haus geschickt die dich beseitigen werden"
	elif "afd" in words:
		return "Das hier ist Münster!!! So eine blaue Scheiße wollen wir hier nicht"

	if minutes_since_last_change() >= cooldown_minutes and len(request.form["text"]) > 1:
		kv_bridge.set_text_and_update_time(request.form["text"])
		db.add_text(request.form["text"])
	
	return redirect("/karl_marx_very_secret_page")

@app.route("/secret_history")
def history():
	return render_template("history.html", history=db.text_history())

if __name__ == "__main__":
	app.run(port = 1234, debug = True)