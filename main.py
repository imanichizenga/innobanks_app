from snippe_payment import SnippePaymentClient

client = SnippePaymentClient()

# Create payment request
payment_response = client.create_dynamic_qr_payment(
    amount=500,
    phone_number="255770036452",
    first_name="Akila",
    last_name="Gwimo",
    email="akilainnocent@gmail.com",
    order_id="ORDER-1003",
    redirect_url="https://schoolsoft.online/payment-success",
    cancel_url="https://schoolsoft.online/payment-cancel",
    webhook_url="https://schoolsoft.online/webhook/snippe"
)

# from snippe_payment import SnippePaymentClient
# import os
# client = SnippePaymentClient(timeout=90)

# push_response = client.create_mobile_payment(
#     amount=500,
#     phone_number="255770036452",
#     first_name="Akila",
#     last_name="Gwimo",
#     email="akilainnocent@gmail.com",
#     order_id="ORDER-1007",
#     webhook_url="https://schoolsoft.online/webhook/snippe",
# )

print(payment_response)

