from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from config import MongoDB, db_mongo
import os
import json

mongo_db = MongoDB()

async def insert_applications_to_mongo(decrypted_data, computer_name):
    """Вставляет данные в MongoDB без каких-либо проверок и манипуляций с данными."""
    await mongo_db.connect(db_mongo)

    # Создаем структуру данных
    structured_data = {
        "computer_name": computer_name,
        "big_bit": decrypted_data.get('big_bit', {}),
        "low_bit": decrypted_data.get('low_bit', {})
    }

    try:
        # Вставляем в MongoDB
        await mongo_db.insert_one("apps", structured_data)
        print("Документ успешно вставлен в MongoDB!")
    except Exception as e:
        print(f"Ошибка при вставке документа в MongoDB: {e}")

async def decrypt_aes(encrypted_data: bytes, key: bytes) -> str:
    """Расшифровывает данные с использованием AES."""

    iv = encrypted_data[:16]
    ciphered_data = encrypted_data[16:]

    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Расшифровываем данные и убираем паддинг
    decrypted_data = unpad(cipher.decrypt(ciphered_data), AES.block_size)

    return decrypted_data.decode('utf-8')

async def decrypt(data):
    encrypted_data = data.get("encrypted_data")
    key = b"WiNrmZMISbgmQROi3TncqGGFxbrFkwar"

    # Преобразуем список в bytes
    encrypted_data = bytes(encrypted_data)

    try:
        decrypted_message = await decrypt_aes(encrypted_data, key)

        decrypted_data = json.loads(decrypted_message)
        computer_name = data.get('computer_name')

        print(f"Computer Name: {computer_name}")

        await insert_applications_to_mongo(decrypted_data, computer_name)

    except Exception as e:
        print("Ошибка при расшифровке:", e)