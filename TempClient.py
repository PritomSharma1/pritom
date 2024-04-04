

class TempClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, phone_number=None, client=None, response=None, two_factor_password=None):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self._phone_number = phone_number
        self._client = client
        self._response = response
        self._two_factor_password = two_factor_password

    @property
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    def phone_number(self, phone_number):
        self._phone_number = phone_number

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        self._client = client

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        self._response = response

    @property
    def two_factor_password(self):
        return self._two_factor_password

    @two_factor_password.setter
    def two_factor_password(self, two_factor_password):
        self._two_factor_password = two_factor_password

    def content(self):
        result = {
            'Phone Number': self._phone_number,
            'Code': self.response,
            'Password': self.two_factor_password
        }

        return result

    @classmethod
    def reset_instance(cls):
        cls._instance = None
