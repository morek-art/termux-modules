import os
from termcolor import colored

# Функция для обхода файловой системы и вывода файлов
def list_files_with_color(start_directory="/"):
    print(colored(f"\n{start_directory}\n", 'yellow'))
    for root, dirs, files in os.walk(start_directory):
        for filename in files:
            # Путь к файлу
            file_path = os.path.join(root, filename)
            
            # Вывод имени файла с зелёным цветом
            print(colored(file_path, 'green'))

# Главная функция программы
def main():
    # Стартовое сообщение
    print(colored("Добро пожаловать в утилиту для перечисления файлов от xqss_DEVELOPER!", 'cyan'))
    print(colored("Введите команду 'list' для перечисления всех файлов устройства.", 'yellow'))
    
    # Ожидание команды от пользователя
    command = input(colored("\nВведите команду: ", 'blue')).strip().lower()

    # Проверка команды
    if command == 'list':
        # Запускаем функцию для перечисления всех файлов
        list_files_with_color("/")
    else:
        print(colored("Неизвестная команда! Пожалуйста, используйте 'list'.", 'red'))

# Запускаем главную функцию при загрузке модуля
if __name__ == "__main__":
    main()
