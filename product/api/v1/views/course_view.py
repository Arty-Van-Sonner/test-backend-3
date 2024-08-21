from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
# Savchenko AD 20.08.2024 +
# from courses.models import Course
from courses.models import *
from users.models import *
from django.db import transaction

from datetime import datetime

import json
# Savchenko AD 20.08.2024 -
from users.models import Subscription


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""

        # TODO

        # Savchenko AD 20.08.2024 +
        data_dict = json.loads(request.body)
        price_type = data_dict['price_type']
        course = data_dict['course']
        
        amount = data_dict['amount']
        payment_id = data_dict['payment_id']
        payment_type = data_dict['payment_type']
        payment_description = data_dict['payment_description']
        is_bonus = data_dict['is_bonus']
        accrual_write_off = AccrualWriteOff.objects.get(dev_code = (1 if payment_type == 'CA' else (0 if payment_type == 'NC' else 2)))

        payment = Balance.objects.create(
            user = request.user,
            accrual_write_off = accrual_write_off,
            amount = amount,
            description = payment_description,
            is_bonus = is_bonus,
            payment_id = payment_id,
        )
        ex = 'Ошибка при оплате курса'
        try:
            with transaction.atomic():
                # this request processing 
                Balance.get_balance(user = request.user)
                price = PriceList.get_price(course, price_type)
                if amount < price:
                    raise PaymentError('Ошибка! Суммы на вашем балансе не хватает для получения курса, даже с учётом текущего платежа')
                
                # при изменении правил и добавлении ограничений по дате, здесь будет задаватся дата доступа к курсу
                start_access_date = None
                end_access_date = None

                accesses = Accesses.objects.filter(course = course, user = request.user)
                access = None
                if len(accesses) > 0:
                    access = accesses[0]
                    access.read_access_open = True
                    access.start_access_date = start_access_date
                    access.end_access_date = end_access_date
                    access.save()
                else:
                    access = Accesses.objects.create(
                        course = course,
                        user = request.user,
                        read_access_open = True,
                        start_access_date = start_access_date,
                        end_access_date = end_access_date,
                    )    
                list_of_payments = Balance.write_off_for_course(request.user, amount, course)
                list_of_resonce = []
                for payment in list_of_payments:
                    list_of_resonce.append(AccessReasons.objects.create(
                        payment = payment,
                        name = payment.description,
                        access = access,
                    ))
                UserGroup.assign_user_to_group(request.user, course)
                data = json.dumps({
                    'messege': f'Вам предоставлен доступ к курсу "{course.title}"',
                })
            # Savchenko AD 20.08.2024 -
            return Response(
                data=data,
                status=status.HTTP_201_CREATED
            )
        # Savchenko AD 20.08.2024 +
        except Exception as ex:
            pass

        data = json.dumps({
            'messege': ex,
        })  
        return Response(
            data=data,
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
        # Savchenko AD 20.08.2024 -

    # Savchenko AD 20.08.2024 +
    @action(
        methods=['get'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def available_purchases_list(self, request, pk):
        now = datetime.now()
        list_access_course = Accesses.objects.filter(
            models.Q(end_access_date__isnull = True) | models.Q(end_access_date__lte = now),
            user = request.user, 
            read_access_open = True,    
        )
        courses = Course.objects.filter(course_access = True)
        courses_for_sale = []
        courses_dict_for_sale = []
        for course in courses:
            if not (course in list_access_course):
                courses_for_sale.append(course)
                courses_dict_for_sale.append(course.get_course_data())
        data_for_return = {
            'courses': courses_dict_for_sale,
        }
        return Response(
            data = json.dumps(data_for_return),
            status=status.HTTP_201_CREATED
        )
    # Savchenko AD 20.08.2024 -
