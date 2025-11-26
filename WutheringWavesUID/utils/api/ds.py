# import base64
# import json
#
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import unpad
#
#
# def decrypt(value):
#     key_base64 = "XSNLFgNCth8j8oJI3cNIdw=="
#     key = base64.b64decode(key_base64)
#     encrypted_data = base64.b64decode(value)
#     cipher = AES.new(key, AES.MODE_ECB)
#     decrypted_data = cipher.decrypt(encrypted_data)
#     plaintext = unpad(decrypted_data, AES.block_size, style='pkcs7')
#     return json.loads(plaintext.decode('utf-8'))
