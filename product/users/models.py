from django.contrib.auth.models import AbstractUser
from django.db import models

# Savchenko AD 20.08.2024 +
from datetime import datetime

from exceptions import *
from courses.models import *
# Savchenko AD 20.08.2024 -

class CustomUser(AbstractUser):
    """Кастомная модель пользователя - студента."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    # Savchenko AD 20.08.2024 +
    dev_code = models.PositiveIntegerField(null = True, unique = True)
    # Savchenko AD 20.08.2024 -

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()

# Savchenko AD 20.08.2024 +
class AccrualWriteOff(models.Model):
    cash = 'CA'
    non_cash = 'NC'
    bonus = 'BO'
    gift = 'GI'
    course_pay = 'CP'
    penalty = 'PE'
    other = 'OT'

    TYPES = (
        (cash, 'Наличные'),
        (non_cash, 'Безналичный'),
        (bonus, 'Бонус'),
        (gift, 'Подарок'),
        (course_pay, 'Покупка курса'),
        (penalty, 'Штраф'),
        (other, 'Другое'),
    )

    accrual = '+'
    write_off = '-'
    PROCESSING_TYPES = (
        (accrual, 'Приход'),
        (write_off, 'Расход'),
    )

    _type = models.CharField(max_length = 2, db_column = 'type', choices = TYPES)
    name = models.CharField(max_length = 255)
    dev_code = models.PositiveIntegerField(null = True, unique = True)
    processing_type = models.CharField(max_length = 1, choices = PROCESSING_TYPES)
    is_bonus = models.BooleanField(null = True)
    description = models.TextField(null = True)
    creation_date = models.DateTimeField(auto_now_add = True, db_column = 'creation_date', null = True)
    last_update_date = models.DateField(auto_now = True, db_column = 'last_update_date', null = True)
# Savchenko AD 20.08.2024 -
class Balance(models.Model):
    """Модель баланса пользователя."""

    # TODO
    # Savchenko AD 20.08.2024 +
    '''
    Баланс пользователя - сумма всех начислений и списаний пользователя. Проверка на отрицательный баланс происходит 
    '''
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    accrual_write_off = models.ForeignKey(AccrualWriteOff, on_delete = models.CASCADE)
    amount = models.FloatField(default = 0.0)
    description = models.TextField(null = True)
    is_bonus = models.BooleanField(default = False)
    payment_id = models.PositiveIntegerField(null = True)
    period = models.DateTimeField(
        auto_now_add = True,
    )
    creation_date = models.DateTimeField(auto_now_add = True, db_column = 'creation_date')

    @staticmethod
    def get_balance(user, amount_type = 0, period = None):
        '''
        amount_type - это тип суммы. Допустимые значения:
            0 - Сумма с учётом бонусов
            1 - Сумма бонусов
            2 - Сумма без учёта бонусов
        '''
        if period is None:
            period = datetime.now()
        is_bonus = None
        if amount_type == 1:
            is_bonus = False
        elif amount_type == 2:
            is_bonus = True
        balance_list = None  
        if is_bonus is None: 
            balance_list = Balance.objects.filter(
                user = user, 
                period__lte = period,
            )
        else:
            balance_list = Balance.objects.filter(
                user = user,
                period__lte = period,
                is_bonus = is_bonus, 
            )
        amounts = balance_list.values('amount')
        balance_amount = 0
        for amount_dict in amounts:
            balance_amount += amount_dict['amount']
        return balance_amount

    @staticmethod
    def write_off_for_course(user, amount, course, bonus_first = True):
        dev_code_of_write_off_for_course = 3
        accrual_write_off = AccrualWriteOff.objects.get(dev_code = dev_code_of_write_off_for_course)
        list_of_payments = []
        if bonus_first:
            balances = Balance.objects.filter(user = user, is_bonus = True)
            bonus_amount = 0
            for balance_dict in balances.values('amount'):
                bonus_amount += balance_dict['amount']
            if bonus_amount > 0:
                list_of_payments.append(Balance.objects.create(
                    user = user,
                    accrual_write_off = accrual_write_off,
                    amount = -bonus_amount,
                    description = f'Платёж за курс "{course.title}" бонусами, от {user.email}',
                    is_bonus = True,
                ))
                amount -= bonus_amount 

        list_of_payments.append(Balance.objects.create(
            user = user,
            accrual_write_off = accrual_write_off,
            amount = -amount,
            description = f'Платёж за курс "{course.title}", от {user.email}',
            is_bonus = False,
        ))
        return list_of_payments
    # Savchenko AD 20.08.2024 -

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'
        ordering = ('-id',)


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""

    # TODO

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)

