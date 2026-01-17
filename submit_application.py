#!/usr/bin/env python3
"""
B12 Application Submission Script
Executes via GitHub Actions to submit application data to B12
"""

import json
import hmac
import datetime
import hashlib
import urllib.request
import urllib.error
import sys
import os


def create_payload(name, email, resume_link, repository_link, action_run_link):
    """Create the canonicalized JSON payload"""
    # Create ISO 8601 timestamp
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    
    # Create payload dictionary with keys sorted alphabetically
    payload = {
        "action_run_link": action_run_link,
        "email": email,
        "name": name,
        "repository_link": repository_link,
        "resume_link": resume_link,
        "timestamp": timestamp
    }
    
    # Convert to JSON with no extra whitespace (compact separators)
    return json.dumps(payload, separators=(',', ':'), ensure_ascii=False)


def calculate_signature(payload, secret):
    """Calculate HMAC-SHA256 signature for the payload"""
    # Encode payload as UTF-8
    payload_bytes = payload.encode('utf-8')
    secret_bytes = secret.encode('utf-8')
    
    # Calculate HMAC-SHA256
    hmac_digest = hmac.new(secret_bytes, payload_bytes, hashlib.sha256).hexdigest()
    
    return f"sha256={hmac_digest}"


def submit_application(payload, signature):
    """Submit the application to B12 endpoint"""
    url = "https://b12.io/apply/submission"
    
    # Create request
    req = urllib.request.Request(url, data=payload.encode('utf-8'))
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('X-Signature-256', signature)
    
    try:
        # Make POST request
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            
            if result.get('success'):
                print(f"Submission successful! Receipt: {result['receipt']}")
                return result['receipt']
            else:
                print(f"Submission failed: {response_data}")
                return None
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(e.read().decode('utf-8'))
        return None
    except Exception as e:
        print(f"Error submitting application: {e}")
        return None


def main():
    # Application data - replace with your actual information
    application_data = {
        "name": "Ioan Zicu",
        "email": "ioan.zicu94+b12@gmail.com",
        "resume_link": "https://www.linkedin.com/in/%E2%98%80-ioan-z-29109b161/",
        "repository_link": "https://github.com/ioanzicu",
        "action_run_link": os.environ.get('GITHUB_RUN_URL', 'https://github.com/ioanzicu/b12-application/actions/runs/placeholder')
    }
    
    # Signing secret
    signing_secret = "hello-there-from-b12"
    
    # Create payload
    payload = create_payload(
        name=application_data["name"],
        email=application_data["email"],
        resume_link=application_data["resume_link"],
        repository_link=application_data["repository_link"],
        action_run_link=application_data["action_run_link"]
    )
    
    print("Created payload:")
    print(payload)
    print()
    
    # Calculate signature
    signature = calculate_signature(payload, signing_secret)
    print(f"Calculated signature: {signature}")
    print()
    
    # Submit application
    receipt = submit_application(payload, signature)
    
    if receipt:
        # For GitHub Actions, set output
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
                print(f'receipt={receipt}', file=fh)
        
        # Exit successfully
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

