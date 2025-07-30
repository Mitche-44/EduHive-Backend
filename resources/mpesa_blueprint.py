from flask import Blueprint
from flask_restful import Api

# Import M-Pesa resources
from .mpesa_resources import (
    STKPushResource,
    PaymentStatusResource,
    MpesaCallbackResource,
    MpesaTimeoutResource,
    PaymentsListResource
)

# Create M-Pesa blueprint
mpesa_bp = Blueprint('mpesa', __name__)
mpesa_api = Api(mpesa_bp)

# Add M-Pesa API routes
mpesa_api.add_resource(STKPushResource, '/stk-push')
mpesa_api.add_resource(PaymentStatusResource, '/status/<string:checkout_request_id>')
mpesa_api.add_resource(MpesaCallbackResource, '/callback')
mpesa_api.add_resource(MpesaTimeoutResource, '/timeout')
mpesa_api.add_resource(PaymentsListResource, '/payments')

# Temporary test route to verify the blueprint is working
from flask import jsonify

@mpesa_bp.route('/test')
def mpesa_test():
    return jsonify({
        'message': 'M-Pesa blueprint is working!',
        'status': 'success'
    })