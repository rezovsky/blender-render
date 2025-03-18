# blender_script_template.py

import bpy
import json
import sys

import os
import hashlib

try:
    # Открываем переданный .blend-файл
    bpy.ops.wm.open_mainfile(filepath=r"{file_path}")

    scene = bpy.context.scene
    engine = scene.render.engine

    if engine == 'CYCLES':
        # В Blender 4.x tile_x и tile_y заменили на tile_size
        tile_size = scene.cycles.tile_size
        samples = scene.cycles.samples
    else:
        tile_size = 0
        samples = 0

    # Заполняем первоначальные данные о файле
    data = {
        "resolution_x": scene.render.resolution_x,
        "resolution_y": scene.render.resolution_y,
        "samples": samples,
        "tile_size": tile_size,
        "engine": engine,
        "frame_current": scene.frame_current,
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "render_filepath": scene.render.filepath
    }

    # -----------------------------
    #     Работа с превью
    # -----------------------------
    try:
        # Определяем папку для превью (папка "previews" в той же директории, где лежит этот скрипт)
        this_dir = os.path.dirname(os.path.abspath(__file__))
        preview_folder = os.path.join(this_dir, "previews")

        # Создаём папку, если её ещё нет
        if not os.path.exists(preview_folder):
            os.makedirs(preview_folder)

        # Генерируем хэш от полного пути к .blend-файлу
        blend_file_path = r"{file_path}"
        file_hash = hashlib.md5(blend_file_path.encode("utf-8")).hexdigest()

        # Формируем путь к будущему превью
        preview_path = os.path.join(preview_folder, file_hash + ".png")

        # Запоминаем текущий движок
        old_engine = scene.render.engine

        # Переключаемся на Workbench — самый быстрый способ получить «превью»
        scene.render.engine = 'BLENDER_WORKBENCH'
        scene.render.filepath = preview_path

        # Делаем быстрый рендер (write_still=True -> сразу сохраняем результат)
        bpy.ops.render.render(write_still=True)

        # Возвращаем исходный движок
        scene.render.engine = old_engine

        # Добавляем путь к превью в итоговые данные
        data["preview_path"] = preview_path

    except Exception as preview_error:
        # Если рендер превью не удался, сохраняем ошибку в данных
        data["preview_error"] = str(preview_error)

    # Выводим результат в формате JSON
    print(json.dumps(data))

except Exception as e:
    # Если при работе со сценой возникла ошибка, выводим её
    print(json.dumps({"error": str(e)}))

# Завершаем Blender
sys.exit(0)
