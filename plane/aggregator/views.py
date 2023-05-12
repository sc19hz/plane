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
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['user_id'] = user.user_id
            request.session['real_name'] = user.real_name
            return HttpResponseRedirect('/')
        else:
            print(form.errors)
            messages.error(request, '注册失败，请检查您的输入。')
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

    url = 'http://sc192jl.pythonanywhere.com/api/Airline/findflight'
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
    api_url = 'http://sc192jl.pythonanywhere.com/api/Airline/order'
    json_data = {
        "payer_name": request.user.real_name,
        "payer_id": 7
    }
    print(json_data)
    response = requests.post(api_url, json=json_data)
    print(response)
    if response.status_code == 200:
        orders = response.json()['data']

        return render(request, 'order.html', {'orders': orders})
    else:
        messages.error(request, 'There was an issue retrieving your orders. Please try again later.')
        return render(request, 'order.html')

@login_required
def order_detail(request, order_id):
    api_url = 'http://sc192jl.pythonanywhere.com/api/Airline/order/{}'.format(order_id)
    json_data = {
        "payer_name": request.user.real_name,
        "payer_id": request.user.user_id
    }
    response = requests.post(api_url, json=json_data)

    if response.status_code == 200:
        order = response.json()
        print(order)
        return render(request, 'order_detail.html', {'order': order})
    else:
        return HttpResponseNotFound('Order not found')

@login_required
@csrf_exempt
def book_flight(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        flight_id = data['flight_id']

        payer_name = request.session['real_name']
        payer_id = request.session['user_id']
        # Call the external API with the required data
        api_url = 'http://sc192jl.pythonanywhere.com/api/Airline/bookflight'
        api_data = {
            'flight_id': flight_id,
            'payer_name': payer_name,
            'payer_id': payer_id,
        }

        response = requests.post(api_url, json=api_data)

        if response.status_code == 201:
            order_id = response.json().get('order_id', None)
            if order_id:
                print(f'order_id={order_id}')
                payment_url = reverse('payment', args=[order_id])
                return JsonResponse({"redirect_url": payment_url})
            else:
                return JsonResponse({"error": "Error in booking flight."})
        else:
            return JsonResponse({"error": f"Error in booking flight. Status code: {response.status_code}"})

def cancel_order(request, order_id):
    if request.method == 'POST':
        api_url = 'http://sc192jl.pythonanywhere.com/api/Airline/cancelbooking'
        json_data = {"order_id": order_id}

        response = requests.post(api_url, json=json_data)

        if response.status_code == 200:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to cancel order'})
def payment(request, order_id):
    return render(request, 'payment.html', {'order_id': order_id})
def process_payment(request):
    if request.method == 'POST':
        payment_provider = request.POST['paymentprovider']
        order_id = request.POST['order_id']
        api_url = 'http://sc192jl.pythonanywhere.com/api/Airline/paymentMethod'
        api_data = {
            "payment_provider": payment_provider,
            "order_id": order_id,
        }

        response = requests.post(api_url, json=api_data)

        if response.status_code == 200:
            login_payment_url = reverse('login_payment', args=[order_id])
            return HttpResponseRedirect(login_payment_url)
        else:
            return JsonResponse({"error": f"Error in selecting payment method. Status code: {response.status_code}"})
    return JsonResponse({"error": "Invalid request method."})

def login_payment(request, order_id):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Call the external API with the required data
        api_url = 'https://ccty.pythonanywhere.com/Payment_WS/signin/'
        api_data = {
            'username': username,
            'password': password,
        }

        response = requests.post(api_url, json=api_data)

        if response.status_code == 200:
            user_id = response.json().get('msg', None)
            if user_id:
                print(f'uid={user_id}')
                request.session['user_id'] = user_id
                request_key_url = reverse('request_key', args=[order_id])
                return HttpResponseRedirect(request_key_url)
            else:
                return JsonResponse({"error": "Error in login payment."})
        else:
            return JsonResponse({"error": f"Error in login payment. Status code: {response.status_code}"})
    else:
        return render(request, 'login_payment.html', {'order_id': order_id})

def request_key(request, order_id):
    if request.method == 'GET':
        user_id = request.session.get('user_id', None)
        if user_id:
            # Call the external API with the required data
            api_url = 'https://ccty.pythonanywhere.com/Payment_WS/Payment_order/'
            api_data = {
                'uid': user_id,
                'Airline_order': order_id,
            }

            response = requests.post(api_url, json=api_data)

            if response.status_code == 200:

                secret_key = response.json().get('msg', None)
                print(f'key:{secret_key}')
                if secret_key:

                    request.session['secret_key'] = secret_key
                    pay_url = reverse('pay', args=[order_id])
                    return HttpResponseRedirect(pay_url)
                else:
                    return JsonResponse({"error": "Error in request key."})
            else:
                return JsonResponse({"error": f"Error in request key. Status code: {response.status_code}"})
        else:
            return JsonResponse({"error": "User ID not found in session."})
    else:
        return JsonResponse({"error": "Invalid request method."})

@login_required
def pay(request, order_id):
    secret_key = request.session.get('secret_key', None)
    if secret_key:
        # Call the external API with the required data
        api_url = 'http://sc192jl.pythonanywhere.com/api/Airline/checkBookingState'
        api_data = {
            'secret_key': secret_key,
            'order_id': order_id,
        }

        response = requests.post(api_url, json=api_data)

        if response.status_code == 200:
            state = response.json().get('state', None)
            if state:
                # Show a success message and redirect to the index page
                messages.success(request, "Your payment has been finished.")

                return redirect('index')
            else:
                messages.error(request, "Error in processing payment.")

                return redirect('index')
        else:
            messages.error(request, f"Error in processing payment. Status code: {response.status_code}")
            print("err")
            return redirect('index')
    else:
        messages.error(request, "Secret key not found in session.")

        return redirect('index')