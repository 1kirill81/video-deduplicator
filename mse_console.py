import cv2
import numpy as np
import os
import argparse


def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err


def remove_duplicate_frames_mse(input_video_path, output_video_path, mse_threshold=1000.0,
                                skip_frames=1, new_fps=False):
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Ошибка: не удалось открыть видеофайл")
        return False

    original_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    saved_frames = []
    prev_frame = None
    processed_count = 0
    duplicates_removed = 0

    print(f"Начата обработка видео: {total_frames} кадров")

    while True:
        ret, current_frame = cap.read()
        if not ret:
            break

        processed_count += 1

        # Прогресс
        if processed_count % 100 == 0:
            progress = (processed_count / total_frames) * 100
            print(f"Обработано: {processed_count}/{total_frames} кадров ({progress:.1f}%)")

        if processed_count % skip_frames != 0:
            continue

        current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is None:
            saved_frames.append(current_frame)
            prev_frame = current_gray.copy()
        else:
            current_mse = mse(prev_frame, current_gray)
            if current_mse > mse_threshold:
                saved_frames.append(current_frame)
                prev_frame = current_gray.copy()
            else:
                duplicates_removed += 1

    cap.release()

    if not saved_frames:
        print("Нет кадров для сохранения")
        return False

    if new_fps:
        saved_ratio = len(saved_frames) / (total_frames / skip_frames)
        output_fps = original_fps * saved_ratio
    else:
        output_fps = original_fps

    print(f"Сохранение видео...")
    out = cv2.VideoWriter(output_video_path, fourcc, output_fps, (width, height))
    for i, frame in enumerate(saved_frames):
        out.write(frame)
        if i % 100 == 0:
            print(f"Сохранено кадров: {i}/{len(saved_frames)}")
    out.release()

    print(f"\nОбработка завершена!")
    print(f"Обработано кадров: {processed_count}")
    print(f"Сохранено кадров: {len(saved_frames)}")
    print(f"Удалено дубликатов: {duplicates_removed}")
    print(f"Исходный FPS: {original_fps:.2f}")
    print(f"Выходной FPS: {output_fps:.2f}")
    print(f"Эффективность: {(1 - len(saved_frames) / processed_count) * 100:.1f}% кадров удалено")

    return True


def get_user_input():
    """Функция для интерактивного ввода параметров"""
    print("=== Удаление дубликатов кадров из видео ===")

    # Ввод пути к исходному видео
    while True:
        input_path = input("Введите путь к исходному видеофайлу: ").strip()
        if not input_path:
            print("Ошибка: путь не может быть пустым.")
            continue
        if os.path.exists(input_path):
            break
        print("Ошибка: файл не найден. Попробуйте еще раз.")

    # Ввод пути для сохранения результата
    while True:
        output_path = input("Введите путь для сохранения результата: ").strip()
        if not output_path:
            print("Ошибка: путь не может быть пустым.")
            continue

        # Создаем папку для результата, если её нет
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            create_dir = input(f"Папка '{output_dir}' не существует. Создать? (y/n): ").strip().lower()
            if create_dir in ['y', 'yes', 'да', 'д']:
                os.makedirs(output_dir, exist_ok=True)
                break
            else:
                continue
        break

    # Ввод порога схожести
    while True:
        threshold_str = input("Порог схожести кадров (по умолчанию: 1000): ").strip()
        if not threshold_str:
            threshold = 1000.0
            break
        try:
            threshold = float(threshold_str)
            if threshold >= 0:
                break
            print("Ошибка: порог должен быть неотрицательным числом.")
        except ValueError:
            print("Ошибка: введите число.")

    # Ввод пропуска кадров
    while True:
        skip_str = input("Пропуск кадров (по умолчанию: 1): ").strip()
        if not skip_str:
            skip_frames = 1
            break
        try:
            skip_frames = int(skip_str)
            if skip_frames >= 1:
                break
            print("Ошибка: значение должно быть не менее 1.")
        except ValueError:
            print("Ошибка: введите целое число.")

    # Ввод настройки FPS
    while True:
        new_fps_str = input("Рассчитать новый FPS? (y/n, по умолчанию: n): ").strip().lower()
        if not new_fps_str:
            new_fps = False
            break
        if new_fps_str in ['y', 'yes', 'да', 'д']:
            new_fps = True
            break
        elif new_fps_str in ['n', 'no', 'нет', 'н']:
            new_fps = False
            break
        else:
            print("Ошибка: введите 'y' или 'n'.")

    return input_path, output_path, threshold, skip_frames, new_fps


def main():
    parser = argparse.ArgumentParser(description='Удаление дубликатов кадров из видео')
    parser.add_argument('--input', help='Входной видеофайл')
    parser.add_argument('--output', help='Выходной видеофайл')
    parser.add_argument('--threshold', type=float, help='Порог схожести кадров (по умолчанию: 1000)')
    parser.add_argument('--skip-frames', type=int, help='Пропуск кадров (по умолчанию: 1)')
    parser.add_argument('--new-fps', action='store_true', help='Рассчитать новый FPS')

    args = parser.parse_args()

    # Если не указаны все параметры через аргументы, используем интерактивный ввод
    if not all([args.input, args.output, args.threshold is not None, args.skip_frames is not None,
                args.new_fps is not None]):
        print("Не все параметры указаны. Запускаем интерактивный ввод...")
        input_path, output_path, threshold, skip_frames, new_fps = get_user_input()
    else:
        # Все параметры указаны через аргументы
        input_path, output_path, threshold, skip_frames, new_fps = (
            args.input, args.output, args.threshold, args.skip_frames, args.new_fps
        )

    # Проверка существования входного файла
    if not os.path.exists(input_path):
        print(f"Ошибка: файл '{input_path}' не найден.")
        return

    print(f"\nПараметры обработки:")
    print(f"Входной файл: {input_path}")
    print(f"Выходной файл: {output_path}")
    print(f"Порог схожести: {threshold}")
    print(f"Пропуск кадров: {skip_frames}")
    print(f"Пересчет FPS: {'Да' if new_fps else 'Нет'}")
    print("\nНачинаем обработку...")

    remove_duplicate_frames_mse(
        input_video_path=input_path,
        output_video_path=output_path,
        mse_threshold=threshold,
        skip_frames=skip_frames,
        new_fps=new_fps
    )

if __name__ == "__main__":
    main()