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
