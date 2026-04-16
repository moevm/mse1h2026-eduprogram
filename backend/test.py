from src.rdf.dependencies import get_rdf, repository

# Тестовый код для демонстрации работы RDF
test_data = {
    "Программная инженерия": [
        {
            "программирование": {
                "previousDisciplines": [],
                "topics": [
                    {
                        "Компьютер": [
                            "Мышка",
                            "Клавиатура"
                        ]
                    },
                    {
                        "Принтер:": [
                            "Краска для печати",
                            "Подключение к компу"
                        ]
                    }
                ]
            }
        },
        {
            "алгебра и геометрия": {
                "previousDisciplines": [],
                "topics": [
                    {
                        "Векторы": [
                            "Скалярные",
                            "Умножения векторов"
                        ]
                    },
                    {
                        "Основы матриц": [
                            "Умножение",
                            "Сложение и вычитание",
                            "Транспонирование",
                            "Диагональные матрицы"
                        ]
                    }
                ]
            }
        },
        {
            "C++": {
                "previousDisciplines": ["программирование"],
                "topics": [
                    {
                        "Переменные": [
                            "int, double, std::",
                            "явные неявные преобразования"
                        ]
                    }
                ]
            }
        }
    ]
}

if __name__ == "__main__":
    rdf = get_rdf()
    rdf.open_connection()
    print(rdf.create_repo(repository))
    rdf.open_connection(repository)
    print(rdf.add_program("ЛЭТИ", test_data))
    print(rdf.get_repo_all_data())
    rdf.close_connection()