from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)
API = "http://localhost:8000/api"
USER_ID = 1  # utilisateur simulé


@app.route("/")
def index():
    needs = requests.get(f"{API}/needs/").json()
    return render_template("index.html", needs=needs)


@app.route("/needs/create", methods=["GET", "POST"])
def create_need():
    if request.method == "POST":
        requests.post(f"{API}/needs/", json={
            "title": request.form["title"],
            "description": request.form["description"],
            "creator": USER_ID,
        })
        return redirect(url_for("index"))
    return render_template("create_need.html")


@app.route("/needs/<int:need_id>")
def need_detail(need_id):
    need = requests.get(f"{API}/needs/{need_id}/").json()
    return render_template("need_detail.html", need=need)


@app.route("/needs/<int:need_id>/join", methods=["POST"])
def join_need(need_id):
    requests.post(f"{API}/needs/{need_id}/join/", json={"user_id": USER_ID})
    return redirect(url_for("need_detail", need_id=need_id))


@app.route("/needs/<int:need_id>/offers/create", methods=["GET", "POST"])
def create_offer(need_id):
    if request.method == "POST":
        requests.post(f"{API}/needs/{need_id}/offers/", json={
            "seller_name": request.form["seller_name"],
            "price": request.form["price"],
            "description": request.form["description"],
        })
        return redirect(url_for("need_detail", need_id=need_id))
    return render_template("create_offer.html", need_id=need_id)


@app.route("/offers/<int:offer_id>/vote", methods=["POST"])
def vote(offer_id):
    need_id = request.form["need_id"]
    requests.post(f"{API}/offers/{offer_id}/vote/", json={
        "user_id": USER_ID,
        "choice": request.form["choice"],
    })
    return redirect(url_for("need_detail", need_id=need_id))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
