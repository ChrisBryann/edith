from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import logging, requests
from urllib.parse import urlencode
from redis.asyncio import Redis
from edith.config import EmailAssistantConfig, Environment
from edith.dependencies import get_config, get_redis
from edith.lib.shared.security.crypto import generate_code_challlenge, generate_state


router = APIRouter(prefix='/email', tags=['email'])
logger = logging.getLogger(__name__)

BASE_YAHOO_URL = 'https://api.login.yahoo.com'

@router.get('/connect/yahoo')
async def connect_yahoo_account(config: EmailAssistantConfig = Depends(get_config), redis: Redis = Depends(get_redis)):
    '''
    Redirects user to Yahoo Consent Screen for Authorization
    '''
    verifier, code_challenge = generate_code_challlenge()
    state = generate_state()
    query_params = {
        'client_id': config.yahoo_client_id,
        'redirect_uri': f'{config.base_url}/email/connect/yahoo/callback',
        'response_type': 'code',
        'scope': 'openid,mail-r',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'state': state,
    }
    
    # store verifier in redis
    key = f'pkce:yahoo:{state}'
    await redis.hset(key, mapping={"code_verifier": verifier})
    await redis.expire(key, 600) # 10 min TTL
    
    auth_url = f'{BASE_YAHOO_URL}/oauth2/request_auth?{urlencode(query_params)}'
    return RedirectResponse(auth_url, status.HTTP_302_FOUND)

@router.get('/connect/yahoo/callback')
async def connect_yahoo_callback(code: str, state: str, config: EmailAssistantConfig = Depends(get_config), redis: Redis = Depends(get_redis)):
    '''
    Callback function for Yahoo Authorization to get code
    '''
    # gets the verifier from Redis using the state value
    key = f'pkce:yahoo:{state}'
    data = await redis.hgetall(key)
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid/expired state")
    
    verifier = data['code_verifier']
    
    await redis.delete(key)
    
    query_params = {
        'redirect_uri': f'{config.base_url}/email/connect/yahoo/callback',
        'code': code,
        'grant_type': 'authorization_code',
        'code_verifier': verifier,
    }
    
    headers = {
        'client_id': config.yahoo_client_id,
        'client_secret': config.yahoo_client_secret,
    }
    
    # call the get_token endpoint from Yahoo API
    
    response = requests.get(f'{config.base_url}/oauth2/get_token', params=query_params, headers=headers)
    try:
        response.raise_for_status()
        data = response.json()
        json_response = JSONResponse(content={"User connected with Yahoo successfully!"}, status_code=status.HTTP_200_OK)
        json_response.set_cookie(key="yahoo_access_token", value=data.access_token, expires=data.expires_in, httponly=True, samesite='strict', secure=config.env == Environment.PROD)
        json_response.set_cookie(key="yahoo_refresh_token", value=data.refresh_token, expires=(60 * 60 * 7), httponly=True, samesite='strict', secure=config.env == Environment.PROD)

        return json_response
    except requests.HTTPError as e:
        raise HTTPException(e.response.status_code, e.response.text)