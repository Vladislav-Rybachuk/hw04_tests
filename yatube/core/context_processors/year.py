import datetime


def year(request):
    """Добавляем переменную с текущим годом"""
    date = datetime.datetime.today()
    return {
        'year': date.year
    }
