# universal_django_analyzer.py
import os
import glob

def discover_django_structure():
    """Автоматически обнаруживает структуру Django проекта"""
    structure_lines = ["АРХИТЕКТУРА DJANGO ПРОЕКТА:", "=" * 50]
    
    # Ищем manage.py для определения корня проекта
    manage_py = glob.glob('manage.py')
    if not manage_py:
        structure_lines.append("❌ Не найден manage.py - возможно, это не Django проект")
        return "\n".join(structure_lines)
    
    structure_lines.append("📁 КОРЕНЬ ПРОЕКТА:")
    
    # Файлы в корне проекта
    root_files = [
        'manage.py', 'requirements.txt', 'requirements-dev.txt', 
        'Pipfile', 'pyproject.toml', 'setup.py', 'env.example', '.env',
        'Dockerfile', 'docker-compose.yml', 'README.md'
    ]
    
    for file in root_files:
        if glob.glob(file):
            structure_lines.append(f"├── {file}")
    
    # Ищем папки с приложениями (те, что содержат apps.py)
    app_folders = []
    for folder in glob.glob('*/'):
        if os.path.isdir(folder):
            apps_py = glob.glob(os.path.join(folder, 'apps.py'))
            if apps_py:
                app_folders.append(folder.rstrip('/'))
    
    # Ищем папку config/settings (типичная структура)
    config_folders = []
    for folder in glob.glob('*/'):
        folder_name = folder.rstrip('/')
        settings_py = glob.glob(os.path.join(folder, 'settings.py'))
        urls_py = glob.glob(os.path.join(folder, 'urls.py'))
        if settings_py or urls_py:
            config_folders.append(folder_name)
    
    # Выводим конфигурационные папки
    if config_folders:
        structure_lines.append("\n📁 КОНФИГУРАЦИЯ:")
        for config_folder in sorted(config_folders):
            structure_lines.append(f"├── {config_folder}/")
            config_files = glob.glob(f"{config_folder}/*.py")
            for file_path in sorted(config_files):
                file_name = os.path.basename(file_path)
                structure_lines.append(f"│   ├── {file_name}")
    
    # Выводим приложения
    if app_folders:
        structure_lines.append("\n📁 ПРИЛОЖЕНИЯ:")
        for app_folder in sorted(app_folders):
            structure_lines.append(f"├── {app_folder}/")
            
            # Стандартные Django файлы в приложении
            django_files = []
            patterns = [
                'models.py', 'views.py', 'urls.py', 'admin.py', 
                'apps.py', 'serializers.py', 'forms.py', 'tests.py',
                'signals.py', 'managers.py', 'constants.py', 'tasks.py'
            ]
            
            for pattern in patterns:
                found_files = glob.glob(f"{app_folder}/{pattern}")
                django_files.extend(found_files)
            
            # Добавляем папки migrations, templates, static если они есть
            migrations_dir = glob.glob(f"{app_folder}/migrations")
            templates_dir = glob.glob(f"{app_folder}/templates")
            static_dir = glob.glob(f"{app_folder}/static")
            
            for file_path in sorted(django_files):
                file_name = os.path.basename(file_path)
                structure_lines.append(f"│   ├── {file_name}")
            
            if migrations_dir:
                structure_lines.append("│   ├── migrations/")
                migration_files = glob.glob(f"{app_folder}/migrations/*.py")
                # Показываем только несколько миграций для краткости
                for i, mig_file in enumerate(sorted(migration_files)[:3]):
                    mig_name = os.path.basename(mig_file)
                    prefix = "│   │   ├──" if i < len(migration_files) - 1 else "│   │   └──"
                    structure_lines.append(f"{prefix} {mig_name}")
                if len(migration_files) > 3:
                    structure_lines.append(f"│   │   └── ... и еще {len(migration_files) - 3} файлов")
            
            if templates_dir:
                structure_lines.append("│   ├── templates/")
            
            if static_dir:
                structure_lines.append("│   ├── static/")
    
    # Дополнительные папки
    extra_folders = ['static', 'media', 'templates', 'docs', 'scripts']
    found_extra = []
    for folder in extra_folders:
        if glob.glob(folder):
            found_extra.append(folder)
    
    if found_extra:
        structure_lines.append("\n📁 ДОПОЛНИТЕЛЬНЫЕ ПАПКИ:")
        for folder in sorted(found_extra):
            structure_lines.append(f"├── {folder}/")
    
    return "\n".join(structure_lines)

def find_django_files():
    """Находит все важные Django файлы в проекте"""
    target_patterns = [
        'manage.py',
        'requirements*.txt',
        '*/settings.py',
        '*/urls.py', 
        '*/celery.py',
        '*/models.py',
        '*/views.py', 
        '*/admin.py',
        '*/apps.py',
        '*/serializers.py',
        '*/tasks.py',
        '*/forms.py',
        '*/signals.py'
    ]
    
    found_files = []
    for pattern in target_patterns:
        found_files.extend(glob.glob(pattern, recursive=True))
    
    # Убираем дубликаты и сортируем
    return sorted(list(set(found_files)))

def create_universal_dump():
    """Создает универсальный дамп Django проекта"""
    
    with open('django_analysis.txt', 'w', encoding='utf-8') as f:
        # 1. Структура проекта
        structure = discover_django_structure()
        f.write(structure)
        f.write("\n\n" + "=" * 60 + "\n\n")
        
        # 2. Содержимое файлов
        f.write("СОДЕРЖИМОЕ ВАЖНЫХ ФАЙЛОВ:\n")
        f.write("=" * 60 + "\n\n")
        
        django_files = find_django_files()
        files_processed = 0
        
        for file_path in django_files:
            if not os.path.isfile(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                
                # Пропускаем почти пустые файлы
                lines = [line for line in content.split('\n') if line.strip()]
                if len(lines) <= 2 and all(line.strip().startswith('#') for line in lines if line.strip()):
                    continue
                
                f.write(f"🚀 ФАЙЛ: {file_path}\n")
                f.write("-" * 40 + "\n")
                f.write(content)
                f.write("\n\n" + "═" * 60 + "\n\n")
                files_processed += 1
                
            except Exception as e:
                print(f"⚠️ Ошибка чтения {file_path}: {e}")
                continue
        
        # 3. Статистика
        f.write(f"📊 СТАТИСТИКА:\n")
        f.write("-" * 30 + "\n")
        f.write(f"• Обработано файлов: {files_processed}\n")
        f.write(f"• Всего найдено Django файлов: {len(django_files)}\n")
        
        # Подсчет приложений
        app_folders = [f for f in glob.glob('*/') if glob.glob(os.path.join(f, 'apps.py'))]
        f.write(f"• Обнаружено приложений: {len(app_folders)}\n")
        
        if app_folders:
            f.write(f"• Приложения: {', '.join(sorted([app.rstrip('/') for app in app_folders]))}\n")
    
    print(f"✅ Анализ завершен! Результат сохранен в django_project_analysis.txt")
    print(f"📁 Обработано {files_processed} файлов")

if __name__ == "__main__":
    print("🔍 Анализирую структуру Django проекта...")
    create_universal_dump()