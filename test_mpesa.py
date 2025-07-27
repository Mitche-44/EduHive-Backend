import requests
import json
import time
from decouple import config

# Test configuration
BASE_URL = 'http://localhost:5000/api'
TEST_PHONE = '254708374149'  # Sandbox test number
TEST_AMOUNT = 1


def test_stk_push():
    """Test STK Push initiation"""
    print("Testing STK Push initiation...")
    
    url = f"{BASE_URL}/mpesa/stk-push"
    payload = {
        "phoneNumber": TEST_PHONE,
        "amount": TEST_AMOUNT,
        "accountReference": "Test Payment",
        "transactionDesc": "Testing M-Pesa integration"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                checkout_request_id = data['data']['checkout_request_id']
                print(f"✅ STK Push initiated successfully!")
                print(f"Checkout Request ID: {checkout_request_id}")
                return checkout_request_id
            else:
                print(f"❌ STK Push failed: {data.get('message')}")
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
    
    return None


def test_payment_status(checkout_request_id):
    """Test payment status check"""
    print(f"\nTesting payment status for: {checkout_request_id}")
    
    url = f"{BASE_URL}/mpesa/status/{checkout_request_id}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                payment_status = data['data']['status']
                print(f"✅ Payment status: {payment_status}")
                return payment_status
            else:
                print(f"❌ Status check failed: {data.get('message')}")
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
    
    return None


def test_get_payments():
    """Test getting all payments"""
    print("\nTesting get all payments...")
    
    url = f"{BASE_URL}/mpesa/payments"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                payments = data['data']['payments']
                print(f"✅ Found {len(payments)} payments")
                for payment in payments[:3]:  # Show first 3
                    print(f"  - ID: {payment['id']}, Amount: {payment['amount']}, Status: {payment['status']}")
            else:
                print(f"❌ Get payments failed: {data.get('message')}")
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")


def main():
    print("🚀 Starting M-Pesa Integration Tests")
    print("="*50)
    
    # Test 1: STK Push
    checkout_request_id = test_stk_push()
    
    if checkout_request_id:
        # Wait a bit before checking status
        print("\nWaiting 3 seconds before checking status...")
        time.sleep(3)
        
        # Test 2: Payment Status
        test_payment_status(checkout_request_id)
    
    # Test 3: Get all payments
    test_get_payments()
    
    print("\n" + "="*50)
    print("🏁 Tests completed!")


if __name__ == "__main__":
    main()