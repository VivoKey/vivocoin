import random
import json
import secrets
import urllib.request

from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.signing import Signer
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Account, Payment

INITIAL_BALANCE = 10000

class ValidationFailed(Exception):
    pass

def _start_vivokey_validation_fromserver(request, message, our_id):
    """
    We do this while the user waits for the page to load -- a proper implementation
    would do this via AJAX so the user can see some feedback (or use a worker
    thread and redirects)

    Returns the transaction ID or raises ValidationFailed.
    """
    token = request.session['oidc_access_token']
    print('oidc_access_token:', token)
    json_data = json.dumps({
        'message': message,
        'timeout': 30,
        'id': our_id,
        'callback': settings.VALIDATION_CALLBACK,
    }).encode('utf-8')

    request = urllib.request.Request(
        settings.VIVO_VALIDATE,
        data=json_data,
        headers={
            'Authorization': 'Bearer %s' % (token,),
            'Content-Type': 'application/json',
        }
    )

    response = json.loads(urllib.request.urlopen(request).read())
    if not response.get('accepted', False):
        raise ValidationFailed(response.get('message', 'No message supplied'))

    return response['vivo_id']

def _get_signed_payment_token(payment):
    to_sign = '%d:%s' % (payment.id, payment.nonce)
    return Signer().sign(to_sign)

def _get_payment_from_signed_token(signed_token):
    unsigned = Signer().unsign(signed_token)
    payment_id, nonce = unsigned.split(':', 1)
    return Payment.objects.get(pk=payment_id, nonce=nonce)

def index(request):
    # Create the user account if it doesn't exist.
    message = None
    wait_for_payment = None

    if request.user.is_authenticated:
        try:
            account = Account.objects.get(django_user=request.user)
        except Account.DoesNotExist:
            account = Account.objects.create(django_user=request.user, balance=INITIAL_BALANCE)

        # Do actions
        if request.POST.get('action') == 'more_money_pls':
            account.balance += random.randint(0, 100) * 100
            account.save()

        elif request.POST.get('action') == 'spend_money':
            spend_amount_cents = int(request.POST.get('cents'))
            message = 'Pay $%.02f to VivoCoin' % (spend_amount_cents // 100,)
            payment = Payment.objects.create(nonce=secrets.token_hex(8),
                                             status='auth',
                                             from_account=account,
                                             amount_cents=spend_amount_cents)
            try:
                signed_id = _get_signed_payment_token(payment)
                _start_vivokey_validation_fromserver(request, message, signed_id)
            except ValidationFailed as e:
                payment.status = 'failed'
                payment.save()
                message = 'Validation not accepted: %s' % (str(e),)
            else:
                message = 'Validation started for transaction ID %d' % (payment.id,)
                wait_for_payment = payment.id

        balance_dollars = account.balance // 100
    else:
        account = None
        balance_dollars = 0

    context = {
        'account': Account,
        'balance_dollars': balance_dollars,
        'debt': balance_dollars < 0,
        'message': message,
        'wait_for_payment': wait_for_payment
    }

    return render(request, 'coinweb/index.html', context)

def _oidc_userinfo(request):
    """
    Make the /userinfo call to VivoKey.

    mozilla_django_oidc has already made this API call as as part of logging
    in, but unfortunately didn't store the result, so just ask again.
    """
    token = request.session['oidc_access_token']
    print('oidc_access_token:', token)
    json_data = json.dumps({
        'timeout': 30,
    }).encode('utf-8')

    request = urllib.request.Request(
        settings.OIDC_OP_USER_ENDPOINT,
        data=json_data,
        headers={
            'Authorization': 'Bearer %s' % (token,),
            'Content-Type': 'application/json',
        }
    )
    response = urllib.request.urlopen(request).read().decode('utf-8')
    return response

@login_required
@require_POST
def userinfo(request):
    """
    Return some information about the logged-in user.

    This is extra info to help you while working with VivoKey OIDC and isn't
    required to implement any core functionality.
    """


    context = {
        'oidc_access_token': request.session.get('oidc_access_token', ''),  # for debugging
        'oidc_userinfo': _oidc_userinfo(request)
    }

    return render(request,'coinweb/userinfo.html', context)

def validation_complete(request):
    # Callback from VivoKey.
    # Note that we have to ensure that the callback has not been forged. We do
    # that by validating (cryptographically, using the Signer module) that the
    # payment ID we've received is the one we originally sent.
    json_response = json.loads(request.body)

    payment = _get_payment_from_signed_token(json_response.get('id', ''))
    success = json_response.get('success', False)
    if success:
        payment.from_account.balance -= payment.amount_cents
        payment.from_account.save()

    payment.status = 'completed' if success else 'failed'
    payment.save()


    return JsonResponse({})

def auth_status(_request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    return JsonResponse({'status': payment.status})

def logout(request):
    django_logout(request)

    return redirect(index)
