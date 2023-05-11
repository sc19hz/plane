from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from django.http import HttpResponseRedirect,HttpResponseNotFound, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.contrib import messages
import json
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id
            request.session['real_name'] = user.real_name
            return HttpResponseRedirect('/index/')
        else:
            form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # 获取并存储real_name到session中
            real_name = user.real_name
            user_id=user.user_id
            request.session['real_name'] = real_name
            request.session['user_id']=user_id
            login(request, user)
            return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def find_flight(request):
    departure_place = request.GET.get('departure_place')
    destin_place = request.GET.get('destin_place')
    departure_time = request.GET.get('departure_time')

    url = 'http://sc192jl.pythonanywhere.com/api/AirlineSichuan/findflight'
    params = {
        'departure_place': departure_place,
        'destin_place': destin_place,
        'departure_time': departure_time
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        flight_data = json.loads(response.text)
        return JsonResponse({'status': response.status_code, 'data': flight_data['data']})
    else:
        return JsonResponse({'status': response.status_code})
def flight_detail(request, flight_id):
    # Fetch flight data based on flight_id, e.g., from an external API or your database
    flight_data = {} # Replace with actual flight data
    return render(request, "detail.html", {"flight": flight_data})
@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

def index(request):
    return render(request, 'index.html')

@login_required
def order(request):
    api_url = 'http://sc192jl.pythonanywhere.com/api/AirlineSichuan/order'
    json_data = {
        "payer_name": request.user.real_name,
        "payer_id": request.user.user_id
    }
    response = requests.post(api_url, json=json_data)

    if response.status_code == 200:
        orders = response.json()
        return render(request, 'order.html', {'orders': orders})
    else:
        messages.error(request, 'There was an issue retrieving your orders. Please try again later.')
        return render(request, 'order.html')

@login_required
def order_detail(request, order_id):
    orders = request.session.get('orders', [])

    order = None
    for o in orders:
        if o['order_id'] == int(order_id):
            order = o
            break

    if order is None:
        return HttpResponseNotFound('Order not found')

    return render(request, 'order_detail.html', {'order': order})

@login_required
@csrf_exempt
def book_flight(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        flight_id = data['flight_id']

        payer_name = request.session['real_name']
        payer_id = request.session['user_id']
        # Call the external API with the required data
        api_url = 'http://sc192jl.pythonanywhere.com/api/AirlineSichuan/bookflight'
        api_data = {
            'flight_id': flight_id,
            'payer_name': payer_name,
            'payer_id': payer_id,
        }

        response = requests.post(api_url, json=api_data)

        if response.status_code == 201:
            order_id = response.json().get('order_id', None)
            if order_id:
                response_json = JsonResponse({"order_id": order_id})
                print("Response JSON:", response_json.content)  # Print response content
                return response_json
            else:
                return JsonResponse({"error": "Error in booking flight."})
        else:
            return JsonResponse({"error": f"Error in booking flight. Status code: {response.status_code}"})
    return JsonResponse({"error": "Invalid request method."})
def cancel_order(request, order_id):
    if request.method == 'POST':
        api_url = 'http://sc192jl.pythonanywhere.com/api/AirlineSichuan/cancelbooking'
        json_data = {"order_id": order_id}

        response = requests.post(api_url, json=json_data)

        if response.status_code == 200:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to cancel order'})