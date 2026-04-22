from functools import wraps
from django.shortcuts import render, redirect
import requests

API = "http://localhost:5000/api"


def login_required(f):
    @wraps(f)
    def decorated(request, *args, **kwargs):
        if 'token' not in request.session:
            return redirect(f'/login?next={request.path}')
        return f(request, *args, **kwargs)
    return decorated


def auth_headers(request):
    return {'Authorization': f'Token {request.session["token"]}'}


# ── AUTH ──────────────────────────────────────────────

def register(request):
    error = None
    if request.method == 'POST':
        res = requests.post(f'{API}/auth/register/', json={
            'username': request.POST['username'],
            'password': request.POST['password'],
            'email': request.POST.get('email', ''),
        })
        data = res.json()
        if res.ok:
            request.session['token'] = data['token']
            request.session['user_id'] = data['user_id']
            request.session['username'] = data['username']
            return redirect('/')
        error = data.get('error', "Erreur lors de l'inscription.")
    return render(request, 'register.html', {'error': error})


def login_view(request):
    error = None
    if request.method == 'POST':
        res = requests.post(f'{API}/auth/login/', json={
            'username': request.POST['username'],
            'password': request.POST['password'],
        })
        data = res.json()
        if res.ok:
            request.session['token'] = data['token']
            request.session['user_id'] = data['user_id']
            request.session['username'] = data['username']
            return redirect(request.GET.get('next', '/'))
        error = data.get('error', 'Identifiants invalides.')
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    request.session.flush()
    return redirect('/')


# ── PROFILE ───────────────────────────────────────────

@login_required
def profile(request):
    h = auth_headers(request)
    profile_data = requests.get(f'{API}/profile/', headers=h).json()
    my_needs = requests.get(f'{API}/profile/needs/', headers=h).json()
    my_collabs = requests.get(f'{API}/profile/collabs/', headers=h).json()
    profile_data['total_activities'] = profile_data.get('needs_count', 0) + profile_data.get('collabs_count', 0)
    return render(request, 'profile.html', {
        'profile': profile_data, 'my_needs': my_needs, 'my_collabs': my_collabs
    })


@login_required
def edit_profile(request):
    h = auth_headers(request)
    error = None
    if request.method == 'POST':
        res = requests.patch(f'{API}/profile/update/', json={
            'username': request.POST['username'],
            'email': request.POST.get('email', ''),
            'bio': request.POST.get('bio', ''),
            'location': request.POST.get('location', ''),
        }, headers=h)
        if res.ok:
            request.session['username'] = res.json()['username']
            return redirect('/profile')
        error = res.json().get('detail', 'Erreur lors de la mise à jour.')
    profile_data = requests.get(f'{API}/profile/', headers=h).json()
    return render(request, 'edit_profile.html', {'profile': profile_data, 'error': error})


# ── NEEDS ─────────────────────────────────────────────

def index(request):
    needs = requests.get(f'{API}/needs/').json()
    return render(request, 'index.html', {'needs': needs})


@login_required
def create_need(request):
    if request.method == 'POST':
        requests.post(f'{API}/needs/', json={
            'title': request.POST['title'],
            'description': request.POST['description'],
        }, headers=auth_headers(request))
        return redirect('/')
    return render(request, 'create_need.html')


def need_detail(request, need_id):
    need = requests.get(f'{API}/needs/{need_id}/').json()
    return render(request, 'need_detail.html', {'need': need})


@login_required
def edit_need(request, need_id):
    h = auth_headers(request)
    need = requests.get(f'{API}/needs/{need_id}/').json()
    if need.get('creator') != request.session.get('username'):
        return redirect(f'/needs/{need_id}')
    if request.method == 'POST':
        requests.patch(f'{API}/needs/{need_id}/', json={
            'title': request.POST['title'],
            'description': request.POST['description'],
        }, headers=h)
        return redirect(f'/needs/{need_id}')
    return render(request, 'edit_need.html', {'need': need})


@login_required
def delete_need(request, need_id):
    if request.method == 'POST':
        requests.delete(f'{API}/needs/{need_id}/', headers=auth_headers(request))
    return redirect('/profile')


@login_required
def archive_need(request, need_id):
    if request.method == 'POST':
        requests.post(f'{API}/needs/{need_id}/archive/', headers=auth_headers(request))
    return redirect('/profile')


@login_required
def join_need(request, need_id):
    requests.post(f'{API}/needs/{need_id}/join/', headers=auth_headers(request))
    return redirect(f'/needs/{need_id}')


# ── OFFERS ────────────────────────────────────────────

@login_required
def create_offer(request, need_id):
    if request.method == 'POST':
        requests.post(f'{API}/needs/{need_id}/offers/', json={
            'seller_name': request.POST['seller_name'],
            'price': request.POST['price'],
            'description': request.POST['description'],
        }, headers=auth_headers(request))
        return redirect(f'/needs/{need_id}')
    return render(request, 'create_offer.html', {'need_id': need_id})


@login_required
def vote(request, offer_id):
    need_id = request.POST['need_id']
    requests.post(f'{API}/offers/{offer_id}/vote/', json={
        'choice': request.POST['choice'],
    }, headers=auth_headers(request))
    return redirect(f'/needs/{need_id}')
