from flask import request, jsonify
from flask_restful import Resource
from extensions import db
from models.payment import Payment
import requests
import base64
import json
from datetime import datetime
from decouple import config
import uuid

class MpesaService:
    """Service class to handle M-Pesa API operations"""
    
    @staticmethod
    def get_access_token():
        """Get M-Pesa access token"""
        try:
            consumer_key = config('MPESA_CONSUMER_KEY')
            consumer_secret = config('MPESA_CONSUMER_SECRET')
            environment = config('MPESA_ENVIRONMENT', default='sandbox')
            
            if not consumer_key or not consumer_secret:
                raise ValueError("M-Pesa consumer key and secret must be set in environment variables")
            
            # Encode credentials
            credentials = base64.b64encode(
                f"{consumer_key}:{consumer_secret}".encode()
            ).decode()
            
            # Set API URL based on environment
            if environment == 'production':
                url = 'https://api.safaricom.co.ke/oauth/v1/generate'
            else:
                url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate'
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
            
            params = {'grant_type': 'client_credentials'}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('access_token')
            
        except Exception as e:
            print(f"Error getting M-Pesa access token: {str(e)}")
            raise e
    
    @staticmethod
    def generate_password(shortcode, passkey, timestamp):
        """Generate M-Pesa password"""
        password_string = f"{shortcode}{passkey}{timestamp}"
        return base64.b64encode(password_string.encode()).decode()
    
    @staticmethod
    def initiate_stk_push(phone_number, amount, account_reference, transaction_desc, checkout_request_id):
        """Initiate STK Push with M-Pesa API"""
        try:
            # Get configuration
            environment = config('MPESA_ENVIRONMENT', default='sandbox')
            shortcode = config('MPESA_SHORTCODE', default='174379')
            passkey = config('MPESA_PASSKEY')
            callback_url = config('MPESA_CALLBACK_URL')
            
            if not passkey:
                raise ValueError("M-Pesa passkey must be set in environment variables")
            
            if not callback_url:
                raise ValueError("M-Pesa callback URL must be set in environment variables")
            
            # Get access token
            access_token = MpesaService.get_access_token()
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = MpesaService.generate_password(shortcode, passkey, timestamp)
            
            # Set API URL based on environment
            if environment == 'production':
                url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            else:
                url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            
            # Prepare request payload
            payload = {
                "BusinessShortCode": shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            print(f"Making STK Push request to: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Make the request
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"M-Pesa API Response Status: {response.status_code}")
            print(f"M-Pesa API Response: {response.text}")
            
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request error in STK Push: {str(e)}")
            raise e
        except Exception as e:
            print(f"Error in STK Push: {str(e)}")
            raise e

class STKPushResource(Resource):
    def post(self):
        """Initiate STK Push payment"""
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'success': False,
                    'message': 'No data provided'
                }, 400
            
            # Validate required fields
            required_fields = ['phoneNumber', 'amount']
            for field in required_fields:
                if not data.get(field):
                    return {
                        'success': False,
                        'message': f'{field} is required'
                    }, 400
            
            phone_number = str(data['phoneNumber']).strip()
            amount = data['amount']
            
            # Validate amount
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError("Amount must be greater than 0")
            except ValueError:
                return {
                    'success': False,
                    'message': 'Invalid amount provided'
                }, 400
            
            # Format phone number to international format
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif phone_number.startswith('+254'):
                phone_number = phone_number[1:]
            elif phone_number.startswith('7') or phone_number.startswith('1'):
                phone_number = '254' + phone_number
            
            # Validate phone number format
            if not phone_number.startswith('254') or len(phone_number) != 12:
                return {
                    'success': False,
                    'message': 'Invalid phone number format. Use format: 0712345678 or 254712345678'
                }, 400
            
            # Generate unique identifiers
            checkout_request_id = str(uuid.uuid4())
            account_reference = data.get('accountReference', 'EduHive Payment')
            transaction_desc = data.get('transactionDesc', 'Payment for EduHive services')
            
            # Create payment record
            payment = Payment(
                checkout_request_id=checkout_request_id,
                phone_number=phone_number,
                amount=amount,
                account_reference=account_reference,
                transaction_desc=transaction_desc,
                status='pending'
            )
            
            db.session.add(payment)
            db.session.commit()
            
            try:
                # Initiate STK Push with M-Pesa
                mpesa_response = MpesaService.initiate_stk_push(
                    phone_number=phone_number,
                    amount=amount,
                    account_reference=account_reference,
                    transaction_desc=transaction_desc,
                    checkout_request_id=checkout_request_id
                )
                
                # Update payment record with M-Pesa response
                if mpesa_response.get('ResponseCode') == '0':
                    # Success
                    payment.merchant_request_id = mpesa_response.get('MerchantRequestID')
                    payment.status = 'sent_to_phone'
                    db.session.commit()
                    
                    return {
                        'success': True,
                        'message': 'STK Push sent successfully',
                        'data': {
                            'checkout_request_id': checkout_request_id,
                            'payment_id': payment.id,
                            'customer_message': mpesa_response.get('CustomerMessage', 
                                f'Please check your phone ({phone_number}) to complete the payment of KES {amount}'),
                            'merchant_request_id': mpesa_response.get('MerchantRequestID'),
                            'response_code': mpesa_response.get('ResponseCode'),
                            'response_description': mpesa_response.get('ResponseDescription')
                        }
                    }, 200
                else:
                    # M-Pesa API returned an error
                    payment.status = 'failed'
                    payment.result_desc = mpesa_response.get('ResponseDescription', 'Unknown error')
                    db.session.commit()
                    
                    return {
                        'success': False,
                        'message': mpesa_response.get('ResponseDescription', 'Failed to initiate payment'),
                        'error_code': mpesa_response.get('ResponseCode')
                    }, 400
                    
            except Exception as mpesa_error:
                # M-Pesa API call failed
                payment.status = 'failed'
                payment.result_desc = f'API Error: {str(mpesa_error)}'
                db.session.commit()
                
                return {
                    'success': False,
                    'message': f'Failed to connect to M-Pesa: {str(mpesa_error)}'
                }, 500
            
        except Exception as e:
            print(f"Error in STK Push endpoint: {str(e)}")
            return {
                'success': False,
                'message': f'Internal server error: {str(e)}'
            }, 500

class PaymentStatusResource(Resource):
    def get(self, checkout_request_id):
        """Check payment status"""
        try:
            payment = Payment.query.filter_by(checkout_request_id=checkout_request_id).first()
            
            if not payment:
                return {
                    'success': False,
                    'message': 'Payment not found'
                }, 404
            
            return {
                'success': True,
                'data': {
                    'checkout_request_id': payment.checkout_request_id,
                    'status': payment.status,
                    'amount': payment.amount,
                    'phone_number': payment.phone_number,
                    'mpesa_receipt_number': payment.mpesa_receipt_number,
                    'result_desc': payment.result_desc,
                    'created_at': payment.created_at.isoformat() if payment.created_at else None,
                    'updated_at': payment.updated_at.isoformat() if payment.updated_at else None
                }
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error checking payment status: {str(e)}'
            }, 500

class MpesaCallbackResource(Resource):
    def post(self):
        """Handle M-Pesa callback"""
        try:
            data = request.get_json()
            
            # Log the callback for debugging
            print(f"M-Pesa Callback received: {json.dumps(data, indent=2)}")
            
            # Extract callback data
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            if not checkout_request_id:
                return {'success': False, 'message': 'Invalid callback data'}, 400
            
            # Find the payment record by merchant request ID if checkout request ID doesn't match
            payment = Payment.query.filter_by(checkout_request_id=checkout_request_id).first()
            
            if not payment:
                # Try to find by merchant request ID
                merchant_request_id = stk_callback.get('MerchantRequestID')
                if merchant_request_id:
                    payment = Payment.query.filter_by(merchant_request_id=merchant_request_id).first()
            
            if not payment:
                print(f"Payment not found for checkout_request_id: {checkout_request_id}")
                return {'success': False, 'message': 'Payment not found'}, 404
            
            # Update payment status based on result code
            if result_code == 0:
                # Payment successful
                payment.status = 'completed'
                payment.result_desc = result_desc
                payment.result_code = result_code
                
                # Extract additional data from callback
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in callback_metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        payment.mpesa_receipt_number = item.get('Value')
                    elif item.get('Name') == 'TransactionDate':
                        try:
                            payment.transaction_date = datetime.strptime(
                                str(item.get('Value')), '%Y%m%d%H%M%S'
                            )
                        except:
                            pass
            else:
                # Payment failed or cancelled
                payment.status = 'failed'
                payment.result_desc = result_desc
                payment.result_code = result_code
            
            payment.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {'success': True, 'message': 'Callback processed successfully'}, 200
            
        except Exception as e:
            print(f"Error processing M-Pesa callback: {str(e)}")
            return {
                'success': False,
                'message': f'Error processing callback: {str(e)}'
            }, 500

class MpesaTimeoutResource(Resource):
    def post(self):
        """Handle M-Pesa timeout"""
        try:
            data = request.get_json()
            
            print(f"M-Pesa Timeout received: {json.dumps(data, indent=2)}")
            
            checkout_request_id = data.get('CheckoutRequestID')
            
            if checkout_request_id:
                payment = Payment.query.filter_by(checkout_request_id=checkout_request_id).first()
                if payment:
                    payment.status = 'timeout'
                    payment.result_desc = 'Transaction timed out'
                    payment.updated_at = datetime.utcnow()
                    db.session.commit()
            
            return {'success': True, 'message': 'Timeout processed successfully'}, 200
            
        except Exception as e:
            print(f"Error processing M-Pesa timeout: {str(e)}")
            return {
                'success': False,
                'message': f'Error processing timeout: {str(e)}'
            }, 500

class PaymentsListResource(Resource):
    def get(self):
        """Get list of payments"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            status = request.args.get('status')
            
            query = Payment.query
            
            if status:
                query = query.filter_by(status=status)
            
            payments = query.order_by(Payment.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'success': True,
                'data': {
                    'payments': [{
                        'id': payment.id,
                        'checkout_request_id': payment.checkout_request_id,
                        'phone_number': payment.phone_number,
                        'amount': payment.amount,
                        'status': payment.status,
                        'mpesa_receipt_number': payment.mpesa_receipt_number,
                        'created_at': payment.created_at.isoformat() if payment.created_at else None,
                        'updated_at': payment.updated_at.isoformat() if payment.updated_at else None
                    } for payment in payments.items],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': payments.total,
                        'pages': payments.pages,
                        'has_next': payments.has_next,
                        'has_prev': payments.has_prev
                    }
                }
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching payments: {str(e)}'
            }, 500