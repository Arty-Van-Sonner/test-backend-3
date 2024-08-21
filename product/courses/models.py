from django.db import models
from users.models import *

# Savchenko AD 20.08.2024 +
from datetime import datetime

from exceptions import *
from users.models import *
# Savchenko AD 20.08.2024 -


class Course(models.Model):
    """Модель продукта - курса."""
    # Savchenko AD 20.08.2024 +
    # author = models.CharField(
    #     max_length=250,
    #     verbose_name='Автор',
    # )
    author = models.ForeignKey(
        CustomUser, on_delete = models.CASCADE,         default = 1
    )
    # Savchenko AD 20.08.2024 -
    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    start_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Дата и время начала курса',
    )

    # TODO
    # Savchenko AD 20.08.2024 +
    course_access = models.BooleanField(default = True)
    creation_date = models.DateTimeField(auto_now_add = True, db_column = 'creation_date', null = True)
    last_update_date = models.DateField(auto_now = True, db_column = 'last_update_date', null = True)

    def get_course_data(self):
        lessons_list = Lesson.objects.filter(course = self)
        count_of_lessons = len(lessons_list)
        course_data = {
            'name': self.title,
            'start_date': self.start_date,
            'count_of_lessons': count_of_lessons,
        }
        return course_data
    # Savchenko AD 20.08.2024 -

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('-id',)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока."""

    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    link = models.URLField(
        max_length=250,
        verbose_name='Ссылка',
    )

    # TODO
    # Savchenko AD 20.08.2024 +
    course = models.ForeignKey(Course, on_delete = models.CASCADE,      default = 1)
    creation_date = models.DateTimeField(auto_now_add = True, db_column = 'creation_date', null = True)
    last_update_date = models.DateField(auto_now = True, db_column = 'last_update_date', null = True)
    # Savchenko AD 20.08.2024 -

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('id',)

    def __str__(self):
        return self.title


class Group(models.Model):
    """Модель группы."""

    # TODO
    # Savchenko AD 20.08.2024 +
    name = models.CharField(max_length = 255,       default = '')
    number = models.PositiveIntegerField(default = 0)
    course = models.ForeignKey(Course, on_delete = models.CASCADE,      default = 1)
    # Savchenko AD 20.08.2024 -

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('-id',)

# Savchenko AD 20.08.2024 +
class UserGroup(models.Model):
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE,        default = 1)
    group = models.ForeignKey(Group, on_delete = models.CASCADE,            default = 1)
    
    @staticmethod
    def assign_user_to_group(user, course):
        groups = Group.objects.filter(course = course)
        min_in_group = 9999999
        group_dict = {}
        group = None
        for group in groups:
            count_users = len(UserGroup.objects.filter(group = group))
            min_in_group = min(min_in_group, count_users) 
            group_dict.update(id(group), count_users)
        for group_id in group_dict:
            if min_in_group == group_dict[group_id]:
                group = object(group_id)
        UserGroup.objects.create(
            user = user,
            group = group,
        )
        return group

class Accesses(models.Model):
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    read_access_open = models.BooleanField(default = False)
    write_access_open = models.BooleanField(default = False)
    start_access_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Дата и время начала доступа',
        null = True
    )
    end_access_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Дата и время окончания доступа',
        null = True
    )
    creation_date = models.DateTimeField(auto_now_add = True, db_column = 'creation_date')
    last_update_date = models.DateField(auto_now = True, db_column = 'last_update_date')

class AccessReasons(models.Model):
    payment = models.ForeignKey(Balance, on_delete = models.CASCADE)
    name = models.CharField(max_length = 255)
    description = models.TextField(null = True)
    access = models.ForeignKey(Accesses, on_delete = models.CASCADE)

class PricesTypes(models.Model):
    '''
    Типы цен. На пример:
    Розничная
    Оптовая
    Специальная
    ...
    '''
    name = models.CharField(max_length = 255)
    description = models.TextField(null = True)

class PriceList(models.Model):
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    price_type = models.ForeignKey(PricesTypes, on_delete = models.CASCADE)
    period = models.DateTimeField(
        auto_now_add = True,
        auto_now = False,
    )
    price = models.FloatField()
    creation_date = models.DateTimeField(auto_now_add = True, db_column = 'creation_date')
    last_update_date = models.DateField(auto_now = True, db_column = 'last_update_date')

    @staticmethod
    def get_price(course, price_type, period = None):
        if period is None:
            period = datetime.now()
        prices = PriceList.objects.filter(
            course = course,
            price_type = price_type, 
        )
        prices.order_by('-period')
        if len(prices) > 0:
            for price_dict in prices.values('period', 'price'):         
                if price_dict['period'] <= period:
                    return price_dict['price']
            raise DataBaseSearchError(f'Ошибка! Цена "{price_type.name}" за продукт "{course.title}" на дату "{period}" в безе на задана')
        else:
            raise DataBaseSearchError(f'Ошибка! Цена "{price_type.name}" за продукт "{course.title}" в безе на задана')
# Savchenko AD 20.08.2024 -
