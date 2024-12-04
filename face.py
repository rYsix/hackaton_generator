from deepface import DeepFace
import numpy as np

# Пороговое значение для определения одного и того же человека
THRESHOLD = 0.6

# Словарь для сохранения эталонного пользователя
users_to_find = {}

try:
    # Эталонная фотография для Руслана
    reference_photo = "ruslan.jpeg"
    reference_embedding = DeepFace.represent(img_path=reference_photo, model_name='Facenet')[0]["embedding"]

    # Записываем Руслана в список
    users_to_find["ruslan"] = reference_embedding
    print("[LOG] Эталонный эмбеддинг для Руслана записан.")

    # Список фотографий для проверки
    test_photos = [
        {"name": "image_1", "path": "damir.jpeg"},
        {"name": "image_2", "path": "damir.jpeg"},
        {"name": "image_3", "path": "ruslan.jpeg"},
        {"name": "image_4", "path": "ruslan2.jpeg"},
    ]

    # Проверка каждой фотографии
    for test_photo in test_photos:
        try:
            # Получаем эмбеддинг текущей фотографии
            test_embedding = DeepFace.represent(img_path=test_photo["path"], model_name='Facenet')[0]["embedding"]

            # Сравниваем эмбеддинг с эталоном Руслана
            distance = np.linalg.norm(np.array(users_to_find["ruslan"]) - np.array(test_embedding))
            if distance < THRESHOLD:
                print(f"[RESULT] На {test_photo['name']} Руслан.")
            else:
                print(f"[RESULT] На {test_photo['name']} не Руслан.")
        except Exception as photo_error:
            print(f"[ERROR] Ошибка обработки {test_photo['name']}: {photo_error}")

except Exception as e:
    print(f"Ошибка: {e}")
