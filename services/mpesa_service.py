import requests
import base64
import json
from datetime import datetime
from decouple import config
import re


class MpesaService:
    def __init__(self):
        self.consumer_key = config('MPESA_CONSUMER_KEY')
        self.consumer_secret = config('MPESA_CONSUMER_SECRET')
        self.passkey = config('MPESA_PASSKEY')
        self.shortcode = config('MPESA_SHORTCODE', default='174379')
        self.environment = config('MPESA_ENVIRONMENT', default='sandbox')
        self.shortcode_type = config('MPESA_SHORTCODE_TYPE', default='CustomerPayBillOnline')
        
        # API URLs
        self.base_url = (
            'https://api.safaricom.co.ke' if self.environment == 'production'
            else 'https://sandbox.safaricom.co.ke'
        )
        
        self.callback_url = config('MPESA_CALLBACK_URL')
        self.timeout_url = config('MPESA_TIMEOUT_URL')

    def generate_access_token(self):
        """Generate access token for Daraja API"""
        try:
            api_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            
            # Create credentials
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'access_token': result['access_token']
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error generating access token: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to generate access token: {str(e)}'
            }

    def generate_password(self):
        """Generate password for STK Push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode('utf-8')
        
        return {
            'password': password,
            'timestamp': timestamp
        }

    def format_phone_number(self, phone):
        """Format phone number to required format (254XXXXXXXXX)"""
        # Remove any non-digit characters
        cleaned = re.sub(r'\D', '', phone)
        
        # Handle different formats
        if cleaned.startswith('0'):
            cleaned = '254' + cleaned[1:]
        elif cleaned.startswith('+254'):
            cleaned = cleaned[1:]
        elif cleaned.startswith('254'):
            pass  # Already in correct format
        else:
            cleaned = '254' + cleaned
            
        return cleaned

    def validate_phone_number(self, phone):
        """Validate if phone number is a valid Safaricom number"""
        formatted_phone = self.format_phone_number(phone)
        
        # Check if it's a valid Safaricom number (starts with 2547 or 2541)
        pattern = r'^254[17]\d{8}$'
        return re.match(pattern, formatted_phone) is not None

    def initiate_stk_push(self, phone_number, amount, account_reference='Payment', transaction_desc='Payment Description'):
        """Initiate STK Push request"""
        try:
            # Generate access token
            token_result = self.generate_access_token()
            if not token_result['success']:
                return token_result

            access_token = token_result['access_token']
            
            # Generate password and timestamp
            password_data = self.generate_password()
            
            # Format phone number
            formatted_phone = self.format_phone_number(phone_number)
            
            # Validate phone number
            if not self.validate_phone_number(phone_number):
                return {
                    'success': False,
                    'error': 'Invalid phone number format. Use Safaricom numbers only.'
                }

            # Prepare request body
            request_body = {
                "BusinessShortCode": self.shortcode,
                "Password": password_data['password'],
                "Timestamp": password_data['timestamp'],
                "TransactionType": self.shortcode_type,
                "Amount": int(amount),
                "PartyA": formatted_phone,
                "PartyB": self.shortcode,
                "PhoneNumber": formatted_phone,
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }

            # Prepare headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Make STK Push request
            api_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            response = requests.post(api_url, json=request_body, headers=headers)
            response.raise_for_status()

            result = response.json()
            
            return {
                'success': True,
                'data': result,
                'checkout_request_id': result.get('CheckoutRequestID'),
                'customer_message': result.get('CustomerMessage'),
                'response_code': result.get('ResponseCode'),
                'response_description': result.get('ResponseDescription')
            }

        except requests.exceptions.RequestException as e:
            print(f"STK Push Error: {str(e)}")
            return {
                'success': False,
                'error': f'STK Push failed: {str(e)}'
            }
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def query_stk_push_status(self, checkout_request_id):
        """Query STK Push status"""
        try:
            # Generate access token
            token_result = self.generate_access_token()
            if not token_result['success']:
                return token_result

            access_token = token_result['access_token']
            
            # Generate password and timestamp
            password_data = self.generate_password()

            # Prepare request body
            request_body = {
                "BusinessShortCode": self.shortcode,
                "Password": password_data['password'],
                "Timestamp": password_data['timestamp'],
                "CheckoutRequestID": checkout_request_id
            }

            # Prepare headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Make query request
            api_url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            response = requests.post(api_url, json=request_body, headers=headers)
            response.raise_for_status()

            result = response.json()
            
            return {
                'success': True,
                'data': result
            }

        except requests.exceptions.RequestException as e:
            print(f"STK Push Query Error: {str(e)}")
            return {
                'success': False,
                'error': f'Query failed: {str(e)}'
            }

    def process_callback(self, callback_data):
        """Process M-Pesa callback data"""
        try:
            body = callback_data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            
            if result_code == 0:
                # Payment successful
                callback_metadata = stk_callback.get('CallbackMetadata', {})
                items = callback_metadata.get('Item', [])
                
                payment_data = {}
                for item in items:
                    name = item.get('Name')
                    value = item.get('Value')
                    
                    if name == 'Amount':
                        payment_data['amount'] = value
                    elif name == 'MpesaReceiptNumber':
                        payment_data['mpesa_receipt_number'] = value
                    elif name == 'TransactionDate':
                        payment_data['transaction_date'] = value
                    elif name == 'PhoneNumber':
                        payment_data['phone_number'] = value

                return {
                    'success': True,
                    'result_code': result_code,
                    'result_desc': stk_callback.get('ResultDesc'),
                    'checkout_request_id': stk_callback.get('CheckoutRequestID'),
                    'payment_data': payment_data
                }
            else:
                # Payment failed or cancelled
                return {
                    'success': False,
                    'result_code': result_code,
                    'result_desc': stk_callback.get('ResultDesc'),
                    'checkout_request_id': stk_callback.get('CheckoutRequestID')
                }

        except Exception as e:
            print(f"Error processing callback: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to process callback data: {str(e)}'
            }


# Global instance
mpesa_service = MpesaService()