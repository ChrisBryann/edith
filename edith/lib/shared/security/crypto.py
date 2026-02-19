import base64, secrets, hashlib

def generate_code_challlenge():
    """
    Generates a code challenge for PKCE in OAuth2
    
    Returns verifier and the code_challenge
    """
    # generate base64 url encoded string from random bytes
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32))
    
    # hash the verifier to create the code challenge
    return verifier, hashlib.sha256(verifier).hexdigest()

def generate_state():
    """
    Generates a unqiue token session to maintain state between
    the request and callback
    """
    
    return secrets.token_urlsafe(32)