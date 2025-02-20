from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import SecretMessage
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode

# Generate or load a secure encryption key
ENCRYPTION_KEY = os.environ.get('DJANGO_ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = os.urandom(32)  # AES-256 requires 32 bytes
    print(f"Generated Encryption Key: {b64encode(ENCRYPTION_KEY).decode()}")

def encrypt_message(message):
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    return b64encode(cipher.iv + ct_bytes).decode()

def decrypt_message(encrypted_message):
    encrypted_data = b64decode(encrypted_message)
    iv = encrypted_data[:AES.block_size]
    ct = encrypted_data[AES.block_size:]
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()

def send_message(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        encrypted_content = encrypt_message(content)
        message = SecretMessage.objects.create(content=encrypted_content)
        link = request.build_absolute_uri(f'/receive/{message.id}/')
        return render(request, 'send_success.html', {'link': link})
    return render(request, 'send_message.html')

def receive_message(request, message_id):
    try:
        message = get_object_or_404(SecretMessage, id=message_id)
        decrypted_content = decrypt_message(message.content)
        message.delete()
        return render(request, 'receive_message.html', {'content': decrypted_content})
    except (ValueError, AttributeError):
        return HttpResponse("Invalid ID", status=400)

def bulk_action(request):
    if request.method == 'POST':
        contents = request.POST.get('contents').splitlines()
        links = []
        for content in contents:
            encrypted_content = encrypt_message(content.strip())
            message = SecretMessage.objects.create(content=encrypted_content)
            link = request.build_absolute_uri(f'/receive/{message.id}/')
            links.append(link)
        return render(request, 'bulk_success.html', {'links': links})
    return render(request, 'bulk_action.html')
