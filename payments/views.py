from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from properties.models import Property
from django.contrib.auth.decorators import login_required
import time
from django.utils import timezone
from datetime import timedelta
import requests
from django.conf import settings
from django.contrib import messages
from .models import FeaturedPayment
from messaging.models import Notification
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth.models import User

ADMIN = User.objects.filter(is_staff=True).first()


def payment_return(request):
    """User returns from Chapa payment - SHOWS TEMPLATE"""
    tx_ref = request.GET.get('tx_ref')
    context = {}
    property = None 
    print(f"textreference number{tx_ref}")
    
    if tx_ref:
        try:
            print(f"iget the tex ref{tx_ref}")
            payment = FeaturedPayment.objects.get(tx_ref=tx_ref)
            context['payment'] = payment
            property = payment.property
            context['property'] = property
            
            if payment.status == 'success':
                print('Return weld one')
                context['success'] = True
                context['message'] = 'Payment successful! Property is now featured.'
            else:
                context['success'] = False
                context['message'] = 'Payment failed'
                
        except FeaturedPayment.DoesNotExist:
            context['success'] = False
            context['message'] = 'Payment not found'
    else:
        context['success'] = False
        context['message'] = 'No payment reference provided'
    
    # SHOW TEMPLATE, not redirect
    return render(request, 'payments/result.html', context)

@csrf_exempt
def payment_callback(request):
    """Handle BOTH Chapa webhook (POST) AND redirect callback (GET)"""
    if request.method == 'GET':
        # GET request - user returns from Chapa
        print("GET CALLBACK RECEIVED")
        print(f"GET params: {dict(request.GET)}")
        
        # Chapa sends GET with these parameters:
        trx_ref = request.GET.get('trx_ref')  # Note: 'trx_ref' not 'tx_ref' in GET!
        status = request.GET.get('status')
        tx_ref = request.GET.get('tx_ref')  # Sometimes they use tx_ref
        
        # Use whichever is available
        ref = trx_ref or tx_ref
        print(f"Payment reference: {ref}, Status: {status}")
        
        if ref and status == 'success':
            try:
                # Get payment record
                payment = FeaturedPayment.objects.get(tx_ref=ref)
                property_obj = payment.property  # Use property_obj to avoid conflict
                
                # Verify with Chapa API
                verify_url = f'https://api.chapa.co/v1/transaction/verify/{ref}'
                headers = {'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}'}
                
                verify_response = requests.get(verify_url, headers=headers)
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    
                    # Check if payment is actually successful
                    if verify_data.get('status') == 'success' and verify_data.get('data', {}).get('status') == 'success':
                        
                        # Update payment if not already updated
                        if payment.status != 'success':
                            payment.status = 'success'
                            payment.completed_at = timezone.now()
                            payment.save()
                            
                            # Upgrade property
                            days = 30 if payment.plan_type == 'monthly' else 7
                            property_obj.is_featured = True
                            property_obj.featured_until = timezone.now() + timedelta(days=days)
                            property_obj.save()
                            
                            # Send notification to landlord
                            Notification.objects.create(
                                user=property_obj.landlord,
                                message=f"Your property '{property_obj.title}' has been upgraded to featured status for {days} days!",
                                notification_type='featured_upgrade',
                                related_property=property_obj,
                                is_read=False
                            )
                            
                            # Notify admin
                            admin_user = User.objects.filter(is_staff=True).first()
                            if admin_user:
                                Notification.objects.create(
                                    user=admin_user,
                                    message=f"{property_obj.landlord.email} upgraded '{property_obj.title}'. Payment: {payment.amount} ETB.",
                                    notification_type='featured_upgrade',
                                    related_property=property_obj,
                                    is_read=False
                                )
                            
                            print(f"Payment processed successfully in GET callback: {ref}")
                        
                        # Redirect to success page
                        return redirect(f"{reverse('payment_return')}?tx_ref={ref}")
                    else:
                        print(f"Chapa verification failed for {ref}")
                        return redirect(f"{reverse('payment_return')}?tx_ref={ref}&error=verification_failed")
                
                else:
                    print(f"Chapa API error: {verify_response.status_code}")
                    return redirect(f"{reverse('payment_return')}?tx_ref={ref}&error=api_error")
                    
            except FeaturedPayment.DoesNotExist:
                print(f"Payment not found: {ref}")
                return JsonResponse({'error': 'Payment not found'}, status=404)
            except Exception as e:
                print(f"Error in GET callback: {e}")
                return JsonResponse({'error': str(e)}, status=400)
        
        # If payment failed or status not success
        elif ref and status == 'failed':
            print(f"Payment failed: {ref}")
            return redirect(f"{reverse('payment_return')}?tx_ref={ref}&error=payment_failed")
        
        # Just return success if nothing else
        return JsonResponse({'status': 'GET callback received'})
    
    elif request.method == 'POST':
        # POST request - webhook (instant notification)
        try:
            print("POST WEBHOOK RECEIVED")
            data = json.loads(request.body)
            tx_ref = data.get('tx_ref')
            status = data.get('status')
            print(f"Webhook data: tx_ref={tx_ref}, status={status}")
            
            if tx_ref and status == 'successful':
                # Process webhook (you can call a shared function here)
                print(f"Processing webhook for: {tx_ref}")
                # Add your webhook processing logic here
                
            return JsonResponse({'status': 'webhook received'})
            
        except Exception as e:
            print(f"Webhook error: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def upgrade_featured(request, property_id):
    property = get_object_or_404(Property, id=property_id, landlord=request.user)
    
    if request.method == 'POST':
        plan = request.POST.get('plan')
        
        if plan == 'weekly':
            price = 500
            days = 7
            plan_type = 'weekly'
        elif plan == 'monthly':
            price = 1500  
            days = 30
            plan_type = 'monthly'
        else:
            messages.error(request, 'Select a plan')
            return redirect('upgrade_featured', property_id=property.id)
        
        # Generate unique transaction reference
        tx_ref = f"FEATURED_{property.id}_{int(time.time())}"
        
        # Prepare Chapa data
        chapa_data = {
            'amount': str(price),
            'currency': 'ETB',
            'email': request.user.email,
            'first_name': request.user.first_name or 'User',
            'last_name': request.user.last_name or 'Customer',
            'tx_ref': tx_ref,
            'callback_url': request.build_absolute_uri(reverse('payment_callback')),
            'return_url': request.build_absolute_uri(f"{reverse('payment_return')}?tx_ref={tx_ref}"),
            'customization': {
                'title': f'FeaturedProperty',
                'description': 'Property listing upgrade'
            }
        }
        
        # Send to Chapa
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                'https://api.chapa.co/v1/transaction/initialize',
                json=chapa_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Save payment record
                payment = FeaturedPayment.objects.create(
                    property=property,
                    user=request.user,
                    amount=price,
                    tx_ref=tx_ref,
                    plan_type=plan_type,
                    status='pending'
                )
                
                # Redirect to Chapa checkout
                print(f"sucesss debiug: {data}")
                checkout_url = data['data']['checkout_url']
                return redirect(checkout_url)
            
            
            else:
                print(f"failer debiug: {response.json()}")
                messages.error(request, 'Payment initialization failed')
                
        except Exception as e:
            messages.error(request, f'Payment error: {str(e)}')
        
        return redirect('upgrade_featured', property_id=property.id)
    
    # GET request - show plans
    context = {
        'property': property,
        'weekly_price': 500,
        'monthly_price': 1500,
    }
    return render(request, 'payments/upgrade_featured.html', context)
