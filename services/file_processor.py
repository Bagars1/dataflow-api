import csv

from email_validator import EmailNotValidError, validate_email
from sqlalchemy.orm import Session

from models.import_error import ImportError
from models.import_job import ImportJob


REQUIRED_COLUMNS = {"name", "email", "age"} # «Вот список колонок, которые обязательно должны быть в CSV».


def process_import( # в этом блоке это входные данные функции Вот тебе база данных, вот информация об импорте и вот путь к файлу. Работай с ними
    db: Session,
    import_job: ImportJob,
    file_path: str,
) -> ImportJob:

    import_job.status = "processing"
    db.commit()
    # «У этого импорта сейчас началась обработка».
    # Помнишь, что import_job — это наш объект из модели ImportJob. У него есть поле: status
    # Статус показывает, на каком этапе находится импорт:
# queued      — импорт создан и ждёт обработки
# processing  — файл сейчас обрабатывается
# completed   — обработка успешно завершена
# failed      — обработка завершилась с ошибкой


    processed_rows = 0
    failed_rows = 0
# сколько строк CSV успешно прошли проверку.
# Мы создаём два счётчика, и в начале оба равны 0.
    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        # Этот блок отвечает за открытие нашего CSV-файла, чтобы программа могла его читать.

        reader = csv.DictReader(file)    # читаем CSV по колонкам

        columns = set(reader.fieldnames or [])    # получаем колонки из файла

        missing_columns = REQUIRED_COLUMNS - columns     # ищем отсутствующие обязательные колонки

        if missing_columns:         # если в CSV не хватает обязательных колонок
            import_job.status = "failed"       # помечаем импорт как неудачный
            db.commit()           # сохраняем статус в базе данных


            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing_columns))}"
            )    # останавливаем обработку и показываем, каких колонок не хватает
# этот блок означает: «если каких-то обязательных колонок нет — остановить импорт и сообщить, каких именно».
        for row_number, row in enumerate(reader, start=2):
            # «Бери строки CSV по одной и проверяй каждую».

            row_has_error = False
            #«Пока считаем, что в этой строке ошибки нет».

            name = row.get("name", "").strip()
            #Здесь мы достаём из текущей строки значение из колонки:

            email = row.get("email", "").strip()
            # Берём значение из: email

            age = row.get("age", "").strip()
            # Получаем значение из: age


            # Проверяем name
            if not name:
                # Если пользователь не указал имя — выполняем код ниже.
                db.add(
                    # То есть мы сейчас хотим записать информацию об ошибке.
                    ImportError(
                        import_job_id=import_job.id,
                        row_number=row_number,
                        field="name",
                        message="Name is required",
                    )
                )
                row_has_error = True
                # ПРАВДА  в этой строке есть ошибка.

            # Проверяем email
            if not email:
                db.add(
                    ImportError(
                        import_job_id=import_job.id,
                        row_number=row_number,
                        field="email",
                        message="Email is required",
                    )
                )
                row_has_error = True
            # если email НЕ пустой, тогда переходим к следующей проверке.
            else:
                try:
                    validate_email( # пришло из библиотеки
                        email,   # наша переменная
                        check_deliverability=False,  # настройка функции из библиотеки.
                    )
                except EmailNotValidError:
                    # «Если проверка email выбросила именно такую ошибку — выполни код ниже».
                    db.add(
                        ImportError(
                            import_job_id=import_job.id,
                            row_number=row_number,
                            field="email",
                            message="Invalid email",
                        )
                    )
                    row_has_error = True

            # Проверяем age
            if not age.isdigit():
                db.add(
                    ImportError(
                        import_job_id=import_job.id,
                        row_number=row_number,
                        field="age",
                        message="Age must be an integer",
                    )
                )
                row_has_error = True

            if row_has_error:
                failed_rows += 1
            else:
                processed_rows += 1

    import_job.processed_rows = processed_rows
    import_job.failed_rows = failed_rows
    import_job.status = "completed"

    db.commit()
    db.refresh(import_job)

    return import_job