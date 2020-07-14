import razorpay
from decouple import config
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.
from accounts.models import UserProfile
from payment.models import RazorPayTransactions, UserPurchases
from product.models import Product, ProductFeatures, ProductPackages


def plansPage(request):
    products = Product.objects.filter(active=True).filter(is_package=False)
    features = ProductFeatures.objects.all()
    packages = Product.objects.filter(active=True).filter(is_package=True)
    context = {'products': products, 'packages': packages, 'features': features}
    return render(request, 'accounts/plans.html', context)


# Payment functions
def initPaymentClient():
    rpay_id = config('RazorPay_ID')
    rpay_id = 'rzp_test_EvjFaOqxyfaPP8'
    # rpay_seceret = config('RazorPay_Secret')
    rpay_secret = 'y5fv2iktTLJdMfVtXskRaJ4G'
    client = razorpay.Client(auth=(rpay_id, rpay_secret))
    return client


def paymentStatus(razorpay_payment_id, razorpay_order_id, razorpay_signature):
    params_dict = {
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_signature': razorpay_signature
    }
    # VERIFYING SIGNATURE
    try:
        client = initPaymentClient()
        client.utility.verify_payment_signature(params_dict)
        return True
    except Exception as e:
        return False


@login_required(login_url='login')
def createOrder(request):
    if request.method == "POST":
        if not request.user.customer:
            messages.warning(request, 'You cannot purchase products!')
            return redirect('dashboard')
        product_id = request.POST.get('product')
        product = Product.objects.filter(active=True).get(pk=product_id)
        try:
            user_profile = UserProfile.objects.get(user_id=request.user.id)
        except UserProfile.DoesNotExist:
            user_profile = None
        if product:
            if product.is_package:
                products_in_package = ProductPackages.objects.filter(package_id=product.id)
                for pdt in products_in_package:
                    try:
                        check_product_status = UserPurchases.objects.filter(user_id=request.user.id).filter(
                            product_id=pdt.product.id).get(status=True)
                        messages.warning(request, 'Product already purchased.')
                        return redirect('plans')
                    except UserPurchases.DoesNotExist:
                        pass
                try:
                    in_progress = UserPurchases.objects.filter(user_id=request.user.id).filter(
                        payment_progress=True).get(product_id=product.id)
                    invoice = in_progress.invoice
                except UserPurchases.DoesNotExist:
                    purchase = UserPurchases.objects.create(
                        user=request.user,
                        product=product,
                    )
                    invoice = purchase.invoice
                    for pdt in products_in_package:
                        purchase = UserPurchases.objects.create(
                            user=request.user,
                            product=pdt.product,
                            invoice=invoice,
                        )
                client = initPaymentClient()
                order_amount = (product.amount - product.active_discount) * 100
                order_currency = 'INR'
                order_receipt = invoice
                notes = {'Product': product.name}
                product_name = product.name
                response = client.order.create(
                    dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes,
                         payment_capture='0'))
                order_id = response['id']
                order_status = response['status']
                if order_status == 'created':
                    context = {'order_id': order_id, 'product': product, 'amount': order_amount,
                               'profile': user_profile, 'invoice': invoice}
                    return render(request, 'accounts/payment.html', context)
                else:
                    messages.error(request, 'Some error occured, please try again!')
                    return redirect('plans')

            else:
                # Check if user already has the product
                try:
                    check_product_status = UserPurchases.objects.filter(user_id=request.user.id).filter(
                        product_id=product.id).get(status=True)
                    messages.warning(request, 'Product already purchased.')
                    return redirect('plans')
                except UserPurchases.DoesNotExist:
                    try:
                        in_progress = UserPurchases.objects.filter(user_id=request.user.id).filter(
                            payment_progress=True).get(product_id=product.id)
                        invoice = in_progress.invoice
                    except UserPurchases.DoesNotExist:
                        purchase = UserPurchases.objects.create(
                            user=request.user,
                            product=product,
                        )
                        invoice = purchase.invoice
                    client = initPaymentClient()
                    order_amount = (product.amount - product.active_discount) * 100
                    order_currency = 'INR'
                    order_receipt = invoice
                    notes = {'Product': product.name}
                    product_name = product.name
                    response = client.order.create(
                        dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes,
                             payment_capture='0'))
                    order_id = response['id']
                    order_status = response['status']
                    if order_status == 'created':
                        context = {'order_id': order_id, 'product': product, 'amount': order_amount,
                                   'profile': user_profile, 'invoice': invoice}
                        return render(request, 'accounts/payment.html', context)
                    else:
                        messages.error(request, 'Some error occured, please try again!')
                        return redirect('plans')


@login_required(login_url='login')
def paymentSuccessPage(request):
    if request.method == "POST":
        response = request.POST
        try:
            response['razorpay_payment_id']
            razorpay_payment_id = response['razorpay_payment_id']
            razorpay_order_id = response['razorpay_order_id']
            razorpay_signature = response['razorpay_signature']
            status = paymentStatus(razorpay_payment_id, razorpay_order_id, razorpay_signature)
            if status:

                items = UserPurchases.objects.filter(invoice=response['invoice'])
                if not items.count() > 1:
                    purchase = UserPurchases.objects.get(invoice=response['invoice'])
                    user_id = purchase.user_id
                    try:
                        check_saved = RazorPayTransactions.objects.get(purchase_id=purchase.id)
                    except  RazorPayTransactions.DoesNotExist:
                        RazorPayTransactions.objects.create(
                            razorpay_payment_id=razorpay_payment_id,
                            razorpay_order_id=razorpay_order_id,
                            razorpay_signature=razorpay_signature,
                            status=1,
                            purchase=purchase
                        )
                        UserPurchases.objects.filter(invoice=response['invoice']).update(payment_progress=0, status=1)
                else:
                    try:
                        check_saved = RazorPayTransactions.objects.get(purchase_id=items[0].id)
                    except  RazorPayTransactions.DoesNotExist:
                        RazorPayTransactions.objects.create(
                            razorpay_payment_id=razorpay_payment_id,
                            razorpay_order_id=razorpay_order_id,
                            razorpay_signature=razorpay_signature,
                            status=1,
                            purchase=items[0]
                        )
                        user_id = items[0].user_id
                        for item in items:
                            if not item.product.is_package:
                                UserPurchases.objects.filter(pk=item.id).update(payment_progress=0, status=1)
                            else:
                                UserPurchases.objects.filter(pk=item.id).update(payment_progress=0)
                try:
                    user_profile = UserProfile.objects.get(user_id=user_id)
                    UserProfile.objects.filter(pk=user_profile.id).update(
                        mobile=response['mobile'],
                        address=response['address'],
                        state=response['state'],
                        pincode=response['pincode'],
                    )
                except UserProfile.DoesNotExist:
                    UserProfile.objects.create(
                        mobile=response['mobile'],
                        address=response['address'],
                        state=response['state'],
                        pincode=response['pincode'],
                        user=request.user
                    )

                context = {'payment': True}
            else:
                context = {'payment': False}
        except:
            context = {'payment': False}

        return render(request, 'accounts/success.html', context)