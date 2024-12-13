import os
from pathlib import Path
from shutil import copyfile, rmtree
from PIL import Image
from deepface import DeepFace

# Directories for known persons, test images, and runtime processing
train_folder = "know_persons"
test_folder = "for_test"
runtime_train_folder = "runtime/know"
runtime_test_folder = "runtime/for_test"
models = ["VGG-Face", "Facenet", "OpenFace", "ArcFace"]
output_file = "results.txt"
max_dimension = (1548, 1032)

os.makedirs(runtime_train_folder, exist_ok=True)
os.makedirs(runtime_test_folder, exist_ok=True)

def copy_and_downscale_image(src_path, dest_path, max_dim):
    """
    Copy the image to the runtime folder and downscale it if it exceeds the maximum dimensions.
    """
    try:
        with Image.open(src_path) as img:
            if img.width > max_dim[0] or img.height > max_dim[1]:
                scaling_factor = min(max_dim[0] / img.width, max_dim[1] / img.height)
                new_width = int(img.width * scaling_factor)
                new_height = int(img.height * scaling_factor)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                img.save(dest_path)
                print(f"Изображение {src_path} загруженно#")
            else:
                copyfile(src_path, dest_path)
                print(f"Изображение {src_path} загруженно.")
    except Exception as e:
        print(f"Ошибка при обработке {src_path}: {e}")

print("\nЗагрузка известных лиц...")
known_faces = {}
for img in Path(train_folder).glob("*"):
    dest_path = Path(runtime_train_folder) / img.name
    copy_and_downscale_image(str(img), str(dest_path), max_dimension)
    known_faces[img.stem] = str(dest_path)

print("\nСписок известных лиц:")
for name in known_faces.keys():
    print(f"  - {name}")

print("\nЗагрузка тестовых изображений...")
test_files = []
for test_img in Path(test_folder).glob("*"):
    dest_path = Path(runtime_test_folder) / test_img.name
    copy_and_downscale_image(str(test_img), str(dest_path), max_dimension)
    test_files.append(dest_path)

print("\nСписок тестовых изображений:")
for test_file in test_files:
    print(f"  - {test_file.name}")

print("\nНачинается обработка тестовых изображений...")
results = []

for test_img in test_files:
    print(f"\nОбрабатывается файл: {test_img.name}")
    best_conf = -1.0
    best_id = "Неизвестная личность"
    best_model = None
    stop_search = False
    for face_id, face_path in known_faces.items():
        if stop_search:
            break
        for model in models:
            try:
                res = DeepFace.verify(img1_path=str(test_img), img2_path=face_path, model_name=model, enforce_detection=False)
                if res.get("verified"):
                    conf = 1 - res.get("distance", 1.0)
                    if conf > best_conf:
                        best_conf = conf
                        best_id = face_id
                        best_model = model[0]
                        if best_conf > 0.84:
                            stop_search = True
                            break
            except Exception as e:
                print(f"Ошибка при обработке {test_img.name} с моделью {model}: {e}")
    confidence_display = f"{best_conf:.2f}" if best_conf > 0 else "1.0"
    result_line = f"Файл: {test_img.name} | Распознан: {best_id} ({best_model}) | Вероятность: {confidence_display}"
    results.append(result_line)
    print(result_line)

print("\nЗапись результатов в файл...")
with open(output_file, "w", encoding="utf-8") as f:
    f.write("===== ИТОГ =====\n")
    f.write("\n".join(results))

print("\n===== ИТОГ =====\n")
for line in results:
    print(line)
print(" ")

rmtree("runtime")
