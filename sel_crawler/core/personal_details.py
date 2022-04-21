from dataclasses import dataclass

@dataclass
class ContactDetails:
    """
    Contact Details for filling out payment forms.
    """
    f_name: str
    l_name: str
    email: str
    number: str
    post_code: str
    street_num: str
    street_name: str
    county: str
    town: str
    country: str = "UK"

@dataclass
class PaymentDetails:
    """
    Payment Details for filling out payment forms.
    """
    card_type: str
    card_number: str
    name_on_card: str
    expiry_date: str
    cv2: str

@dataclass
class LoginDetails:
    """
    Some pages require logging in before proceeding to checkout.
    """
    user: str
    pw: str
    