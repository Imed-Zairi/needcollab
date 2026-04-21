from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'needcollab-secret-key'
API = "http://localhost:8000/api"


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def auth_headers():
    return {'Authorization': f'Token {session["token"]}'}


# ── AUTH ──────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        res = requests.post(f"{API}/auth/register/", json={
            "username": request.form["username"],
            "password": request.form["password"],
            "email": request.form.get("email", ""),
        })
        data = res.json()
        if res.ok:
            session['token'] = data['token']
            session['user_id'] = data['user_id']
            session['username'] = data['username']
            return redirect(url_for('index'))
        error = data.get('error', "Erreur lors de l'inscription.")
    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        res = requests.post(f"{API}/auth/login/", json={
            "username": request.form["username"],
            "password": request.form["password"],
        })
        data = res.json()
        if res.ok:
            session['token'] = data['token']
            session['user_id'] = data['user_id']
            session['username'] = data['username']
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        error = data.get('error', 'Identifiants invalides.')
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


# ── PROFILE ───────────────────────────────────────────

@app.route("/profile")
@login_required
def profile():
    h = auth_headers()
    profile_data = requests.get(f"{API}/profile/", headers=h).json()
    my_needs = requests.get(f"{API}/profile/needs/", headers=h).json()
    my_collabs = requests.get(f"{API}/profile/collabs/", headers=h).json()
    return render_template("profile.html", profile=profile_data, my_needs=my_needs, my_collabs=my_collabs)


@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    h = auth_headers()
    error = None
    if request.method == "POST":
        res = requests.patch(f"{API}/profile/update/", json={
            "username": request.form["username"],
            "email": request.form.get("email", ""),
            "bio": request.form.get("bio", ""),
            "location": request.form.get("location", ""),
        }, headers=h)
        if res.ok:
            data = res.json()
            session['username'] = data['username']
            return redirect(url_for('profile'))
        error = res.json().get('detail', 'Erreur lors de la mise à jour.')
    profile_data = requests.get(f"{API}/profile/", headers=h).json()
    return render_template("edit_profile.html", profile=profile_data, error=error)


# ── NEEDS ─────────────────────────────────────────────

@app.route("/")
def index():
    needs = requests.get(f"{API}/needs/").json()
    return render_template("index.html", needs=needs)


@app.route("/needs/create", methods=["GET", "POST"])
@login_required
def create_need():
    if request.method == "POST":
        requests.post(f"{API}/needs/", json={
            "title": request.form["title"],
            "description": request.form["description"],
        }, headers=auth_headers())
        return redirect(url_for("index"))
    return render_template("create_need.html")


@app.route("/needs/<int:need_id>")
def need_detail(need_id):
    need = requests.get(f"{API}/needs/{need_id}/").json()
    return render_template("need_detail.html", need=need)


@app.route("/needs/<int:need_id>/join", methods=["POST"])
@login_required
def join_need(need_id):
    requests.post(f"{API}/needs/{need_id}/join/", headers=auth_headers())
    return redirect(url_for("need_detail", need_id=need_id))


# ── OFFERS ────────────────────────────────────────────

@app.route("/needs/<int:need_id>/offers/create", methods=["GET", "POST"])
@login_required
def create_offer(need_id):
    if request.method == "POST":
        requests.post(f"{API}/needs/{need_id}/offers/", json={
            "seller_name": request.form["seller_name"],
            "price": request.form["price"],
            "description": request.form["description"],
        }, headers=auth_headers())
        return redirect(url_for("need_detail", need_id=need_id))
    return render_template("create_offer.html", need_id=need_id)


@app.route("/offers/<int:offer_id>/vote", methods=["POST"])
@login_required
def vote(offer_id):
    need_id = request.form["need_id"]
    requests.post(f"{API}/offers/{offer_id}/vote/", json={
        "choice": request.form["choice"],
    }, headers=auth_headers())
    return redirect(url_for("need_detail", need_id=need_id))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
