import os
import json
from deepface import DeepFace
from pathlib import Path

train_folder = "know_persons"
test_folder = "for_test"
models = ["VGG-Face", "Facenet", "OpenFace", "ArcFace"]
output_file = "results.txt"

print("\nЗагрузка известных лиц...")
known_faces = {}
for img in Path(train_folder).glob("*"):
    known_faces[img.stem] = str(img)

print("\nСписок файлов для обучения:")
for name in known_faces.keys():
    print(f"  - {name}")

print(f"\nНайдено {len(known_faces)} известных лиц.\n")

test_files = list(Path(test_folder).glob("*"))
print("Список файлов для тестирования:")
for test_file in test_files:
    print(f"  - {test_file.name}")

results = []
print("\nНачинается обработка тестовых изображений...\n")
for test_img in test_files:
    print(f"Обрабатывается файл: {test_img.name}")
    best_conf = -1.0
    best_id = "Неизвестная личность"
    for face_id, face_path in known_faces.items():
        for model in models:
            try:
                res = DeepFace.verify(img1_path=str(test_img), img2_path=face_path, model_name=model, enforce_detection=False)
                if res.get("verified"):
                    conf = 1 - res.get("distance", 1.0)
                    if conf > best_conf:
                        best_conf = conf
                        best_id = face_id
            except Exception as e:
                print(f"Ошибка при обработке {test_img.name}: {e}")
    confidence_display = f"{best_conf:.2f}" if best_conf > 0 else "Неизвестно"
    result_line = f"Файл: {test_img.name} | Распознан: {best_id} | Вероятность: {confidence_display}"
    results.append(result_line)
    print(result_line)

print("\nЗапись результатов в файл...")
with open(output_file, "w", encoding="utf-8") as f:
    f.write("===== ИТОГ =====\n")
    f.write("\n".join(results))

print("\n===== ИТОГ =====")
for line in results:
    print(line)
