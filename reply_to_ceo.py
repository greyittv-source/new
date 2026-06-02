import sys
import requests
import time

if len(sys.argv) < 2:
    print("Usage: python reply_to_ceo.py 'Your message here'")
    sys.exit(1)

message_text = sys.argv[1]
payload = {
    "sender": "luna",
    "text": message_text,
    "msgId": str(int(time.time() * 1000))
}

url = "https://dweet.io/dweet/for/greyit-luna-to-ceo-7x9q2w1z"
try:
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print("✅ Message successfully sent to CEO's smartphone!")
    else:
        print("❌ Failed to send:", res.text)
except Exception as e:
    print("❌ Error:", e)
