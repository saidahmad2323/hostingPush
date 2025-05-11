import firebase_admin
from firebase_admin import credentials, messaging, firestore
import threading

# Инициализация Firebase
cred = credentials.Certificate("C:/Users/user/Desktop/service-account.json")
firebase_admin.initialize_app(cred)

# Используем уже инициализированный клиент Firestore из firebase_admin
db = firestore.client()
def send_push_to_all(body: str):
    users_ref = db.collection("users").stream()
    for user_doc in users_ref:
        user_data = user_doc.to_dict()
        token = user_data.get("token")
        if token:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="📩 Новое сообщение",
                    body=body,
                ),
                token=token
            )
            try:
                response = messaging.send(message)
                print(f"✅ Отправлено пользователю {user_doc.id}: {response}")
            except Exception as e:
                print(f"❌ Ошибка при отправке пользователю {user_doc.id}:", e)

def send_push(token: str, body: str):
    if token == "all":
        send_push_to_all(body)
    else:
        message = messaging.Message(
            notification=messaging.Notification(
                title="📩 Новое сообщение",
                body=body,
            ),
            token=token
        )
        try:
            response = messaging.send(message)
            print("✅ Отправлено:", response)
        except Exception as e:
            print("❌ Ошибка отправки:", e)

def on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            doc = change.document
            data = doc.to_dict()
            token = data.get("token")
            body = data.get("message")

            if token and body:
                print(f"📨 Найдено новое сообщение -> Token: {token}")
                send_push(token, body)

                # После отправки удалить или пометить как отправленное
                doc.reference.delete()  # или .update({"sent": True})
            else:
                print("⚠️ Неполные данные в документе:", data)

def listen_for_pushes():
    col_query = db.collection("push")
    col_query.on_snapshot(on_snapshot)

# Запуск
print("👂 Ожидание новых пуш-сообщений...")
listen_thread = threading.Thread(target=listen_for_pushes, daemon=True)
listen_thread.start()

# Удержание программы в рабочем состоянии
try:
    while True:
        pass
except KeyboardInterrupt:
    print("🛑 Остановлено пользователем.")
