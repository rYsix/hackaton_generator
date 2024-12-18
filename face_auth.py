from deepface import DeepFace
import numpy as np

class FaceAuth:
    def __init__(self, model_name='Facenet'):
        self.model_name = model_name

    def get_embedding(self, image):
        """Получает эмбеддинг для изображения."""
        try:
            # Передаем массив пикселей вместо пути к файлу
            embedding = DeepFace.represent(img_path=image, model_name=self.model_name, enforce_detection=False)
            return embedding[0]["embedding"]
        except Exception as e:
            print(f"[ERROR FaceAuth] Failed to get embedding: {e}")
            return None

    def compare_embeddings(self, embedding1, embedding2, threshold=0.6):
        """Сравнивает два эмбеддинга."""
        try:
            distance = np.linalg.norm(np.array(embedding1) - np.array(embedding2))
            return distance < threshold
        except Exception as e:
            print(f"[ERROR FaceAuth] Failed to compare embeddings: {e}")
            return False

    def compare_photos(self, photo1, photo2):
        """
        Сравнивает две фотографии и проверяет, один ли это человек.
        - photo1, photo2: изображения в формате numpy array.
        Возвращает True, если фотографии принадлежат одному человеку, иначе False.
        """
        try:
            result = DeepFace.verify(img1_path=photo1, img2_path=photo2, model_name=self.model_name, enforce_detection=False)
            return result["verified"]
        except Exception as e:
            print(f"[ERROR FaceAuth] Failed to compare photos: {e}")
            return False

    def detect_face(self, image):
        """
        Проверяет, есть ли лицо на фотографии.
        - image: numpy array (изображение).
        Возвращает:
            bool: True, если лицо найдено, иначе False.
        """
        try:
            # Используем DeepFace для детекции лиц
            analysis = DeepFace.analyze(img_path=image, actions=['gender'], enforce_detection=True)
            return True  # Если анализ успешен, лицо обнаружено
        except Exception as e:
            print(f"[ERROR FaceAuth] No face detected: {e}")
            return False
