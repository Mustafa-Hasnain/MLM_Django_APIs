from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment

class PayPalClient:
    def __init__(self):
        self.client_id = "AcfZegwsJHjZkBYFKkSAsNWTRDS3xF_7jjEr-bjMTxROkAj6Nlg1HVXyzIWIFb7Iujtex-uSMM_yTA1H"
        self.client_secret = "EBytr5RbE3xIWcirROf1I48hUcp9FP4IlNs-EQff4a3e2jEZ7JQMHqNnvCZKgg5JrLEc_tbZ7qnSQxHy"

        self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)
        self.client = PayPalHttpClient(self.environment)
