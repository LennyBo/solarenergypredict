from http.cookiejar import Cookie
import random,string
from base64 import urlsafe_b64encode
import requests as r
import re

def  random_string(size):
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(size))


    
code_verifier = random_string(86)
code_challenge = urlsafe_b64encode(code_verifier.encode('utf-8')).decode('utf-8')



# with open("response.html", "r") as f:
#     responseStr = f.read()

# with open("header.txt","r") as f:
#     headerStr = f.read()

# hiddenInputs = set(re.findall(r'type="hidden" ?name="([a-zA-Z_]+)" ?value="([a-zA-Z\-1-9]+)"', responseStr))
# tokens = {k:v for k,v in hiddenInputs}

# cookie = re.findall(r"Set-Cookie': ?'(.+)',", headerStr)[0]

# print(cookie)

# print(tokens)

# keys = ["_csrf","_phase","_process","transaction_id","cancel"]

# if not all(k in tokens for k in keys):
#     print(f"Didn't find all keys: Found keys: {tokens.keys()}")
    

# exit()

response = r.get(f"https://auth.tesla.com/oauth2/v3/authorize?"\
                    "client_id=ownerapi&"\
                    "code_challenge={code_challenge}&"\
                    "code_challenge_method=S256&"\
                    "redirect_uri=https://auth.tesla.com/void/callback&"\
                    "response_type=code&"\
                    "scope=openid email offline_access&"\
                    "state=12345&"\
                    "login_hint=lenny.boegli@moosvolk.ch")

if response.status_code == 200:
    responseStr = response.text
    cookie = response.headers["Set-Cookie"]
else:
    print(f"Error {response.status_code}")


hiddenInputs = set(re.findall(r'type="hidden" ?name="([a-zA-Z_]+)" ?value="([a-zA-Z\-1-9]+)"', responseStr))
tokens = {k:v for k,v in hiddenInputs}

print(cookie)

print(tokens)

keys = ["_csrf","_phase","_process","transaction_id","cancel"]

if not all(k in tokens for k in keys):
    print(f"Didn't find all keys: Found keys: {tokens.keys()}")

headerBody = {
    "Cookie": cookie
}

postBody = {k:v for k,v in tokens.items() if k in keys} # Filter keys to only those we need
postBody["identity"] = "lenny.boegli@moosvolk.ch"
postBody["credential"] = "Jathupalc#Te1"


autResponse = r.post(f"https://auth.tesla.com/oauth2/v3/authorize?"\
                        "client_id=ownerapi&"\
                        "code_challenge={code_challenge}&"\
                        "code_challenge_method=S256&"\
                        "redirect_uri=https://auth.tesla.com/void/callback&"\
                        "response_type=code&"\
                        "scope=openid email offline_access&"\
                        "state=12345&",
                        data=postBody,
                        headers=headerBody
                    )

print(autResponse.text)

print(autResponse)