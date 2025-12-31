import base64
import hashlib
import hmac
from datetime import datetime, timezone

gmt_time = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

key_id = "longyuan-common-chat"                # key id
secret_key = b"5b0d907e24926125f5646302e43d0c2f"    # secret key
request_method = "POST"             # HTTP method
request_path = "/digital-artisan-space/file/api/portalBySpace"              # route URI
algorithm= "hmac-sha256"           # can use other algorithms in allowed_algorithms
body = """{
    "spaceId": 2363,
    "sort": 1,
    "userId": "longyuanuser",
    "userToken": "",
    "regionRights": []
}"""

# construct the signing string (ordered)
# the date and any subsequent custom headers should be lowercased and separated by a
# single space character, i.e. `<key>:<space><value>`
# https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures-12#section-2.1.6
signing_string = (
  f"{key_id}\n"
  f"{request_method} {request_path}\n"
  f"date: {gmt_time}\n"
)


# create signature
signature = hmac.new(secret_key, signing_string.encode('utf-8'), hashlib.sha256).digest()
signature_base64 = base64.b64encode(signature).decode('utf-8')

# create the SHA-256 digest of the request body and base64 encode it
body_digest = hashlib.sha256(body.encode('utf-8')).digest()
body_digest_base64 = base64.b64encode(body_digest).decode('utf-8')

# construct the request headers
headers = {
  "Date": gmt_time,
  "Digest": f"SHA-256={body_digest_base64}",
  "Authorization": (
    f'Signature keyId="{key_id}",algorithm="{algorithm}",'
    f'headers="@request-target date",'
    f'signature="{signature_base64}"'
  )
}

# print headers
print(headers)

print(f"""curl -N --no-buffer -X POST -i 'http://10.170.249.86:9901{request_path}' \\
 -H "Date: {headers['Date']}" \\
 -H "Digest: {headers['Digest']}" \\
 -H 'Authorization: {headers['Authorization']}'\\
 -H 'Content-Type: application/json' \\
 -d '{body}'
""")


# curl -i http://127.0.0.1:9900/ip \
# -H "X-HMAC-SIGNED-HEADERS: x-custom-a" \
# -H "X-HMAC-DIGEST: YCkk4yY7qHXuccI5T3165i2WoypyJGN6HPcvLVk/6iY=" \
# -H "x-custom-a: test" \
# -H "User-Agent: curl/7.29.0"


# import base64
# import hashlib
# import hmac

# secret = bytes('my-secret-key', 'utf-8')
# message = bytes("""GET
# /index.html
# age=36&name=james
# user-key
# Tue, 19 Jan 2021 11:33:20 GMT
# User-Agent:curl/7.29.0
# x-custom-a:test
# """, 'utf-8')

# hash = hmac.new(secret, message, hashlib.sha256)

# # to lowercase base64
# print(base64.b64encode(hash.digest()))


# curl -i "http://127.0.0.1:9900/mytest/ip/test" \
# -H "X-HMAC-SIGNATURE: G0GZKj7LOZTWFddn5vh7Cey+7gL8AtQnJd8tJw+dRsc=" \
# -H "X-HMAC-ALGORITHM: hmac-sha256" \
# -H "X-HMAC-ACCESS-KEY: user-key" \
# -H "Date: Sun, 27 Apr 2025 14:27:50 CST" \
# -H "X-HMAC-SIGNED-HEADERS: x-custom-a" \
# -H "x-custom-a: test" \
# -H "User-Agent: curl/7.29.0"


# curl -i "http://127.0.0.1:9900/mytest/ip/test" \
# -H "X-HMAC-SIGNATURE: XlCgEkIzLw+IdnwdhuoqUdgyAXkZQf9uZsxe1XqsvZw=" \
# -H "X-HMAC-ALGORITHM: hmac-sha256" \
# -H "X-HMAC-ACCESS-KEY: user-key-2" \
# -H "Date: Sun, 27 Apr 2025 14:27:50 CST" \
# -H "X-HMAC-SIGNED-HEADERS: x-custom-a" \
# -H "x-custom-a: test" \
# -H "User-Agent: curl/7.29.0"