from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from cats.models import Cat
from trips.models import Trip, Stop

User = get_user_model()


class BaseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass123')
        self.other = User.objects.create_user('otheruser', password='pass123')
        self.token = Token.objects.create(user=self.user)
        self.other_token = Token.objects.create(user=self.other)
        self.cat = Cat.objects.create(
            name='Барсик', color='orange', birth_year=2020, owner=self.user
        )
        self.other_cat = Cat.objects.create(
            name='Мурка', color='gray', birth_year=2019, owner=self.other
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')


class TripListCreateTest(BaseTestCase):
    def test_list_trips_anonymous(self):
        """Гость может просматривать список поездок."""
        self.client.credentials()
        response = self.client.get('/api/trips/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_trip_authenticated(self):
        """Авторизованный пользователь создаёт поездку для своего кота."""
        data = {'cat': self.cat.id, 'title': 'Тестовая поездка'}
        response = self.client.post('/api/trips/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'planned')
        self.assertEqual(response.data['owner'], 'testuser')

    def test_create_trip_anonymous_forbidden(self):
        """Гость не может создать поездку."""
        self.client.credentials()
        data = {'cat': self.cat.id, 'title': 'Тест'}
        response = self.client.post('/api/trips/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_trip_with_foreign_cat(self):
        """Нельзя создать поездку для чужого кота."""
        data = {'cat': self.other_cat.id, 'title': 'Чужой кот'}
        response = self.client.post('/api/trips/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cat', response.data)


class TripDetailTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.trip = Trip.objects.create(
            owner=self.user, cat=self.cat, title='Моя поездка'
        )
        self.other_trip = Trip.objects.create(
            owner=self.other, cat=self.other_cat, title='Чужая поездка'
        )

    def test_retrieve_trip_with_stops(self):
        """Детали поездки содержат список остановок."""
        Stop.objects.create(trip=self.trip, title='Стоп 1', order=1)
        response = self.client.get(f'/api/trips/{self.trip.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('stops', response.data)
        self.assertEqual(len(response.data['stops']), 1)

    def test_update_own_trip(self):
        """Владелец может обновить поездку."""
        response = self.client.patch(
            f'/api/trips/{self.trip.id}/',
            {'title': 'Обновлённое название'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Обновлённое название')

    def test_update_foreign_trip_forbidden(self):
        """Нельзя редактировать чужую поездку."""
        response = self.client.patch(
            f'/api/trips/{self.other_trip.id}/',
            {'title': 'Взлом'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_trip(self):
        """Владелец может удалить поездку."""
        response = self.client.delete(f'/api/trips/{self.trip.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TripStartCompleteTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.trip = Trip.objects.create(
            owner=self.user, cat=self.cat, title='Поездка'
        )

    def test_start_trip(self):
        """Владелец начинает поездку: статус planned -> active."""
        response = self.client.post(f'/api/trips/{self.trip.id}/start/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'active')
        self.assertIsNotNone(response.data['started_at'])

    def test_start_already_active_trip(self):
        """Нельзя начать уже активную поездку."""
        self.trip.status = 'active'
        self.trip.save()
        response = self.client.post(f'/api/trips/{self.trip.id}/start/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_trip_without_stops(self):
        """Нельзя завершить поездку без остановок."""
        self.trip.status = 'active'
        self.trip.save()
        response = self.client.post(f'/api/trips/{self.trip.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_complete_trip_with_stops(self):
        """Поездка с остановками завершается успешно."""
        self.trip.status = 'active'
        self.trip.save()
        Stop.objects.create(trip=self.trip, title='Стоп', order=1)
        response = self.client.post(f'/api/trips/{self.trip.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertIsNotNone(response.data['completed_at'])

    def test_complete_planned_trip(self):
        """Нельзя завершить поездку со статусом planned."""
        Stop.objects.create(trip=self.trip, title='Стоп', order=1)
        response = self.client.post(f'/api/trips/{self.trip.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TripFilterTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        Trip.objects.create(
            owner=self.user, cat=self.cat,
            title='Поездка 1', status='planned'
        )
        Trip.objects.create(
            owner=self.user, cat=self.cat,
            title='Поездка 2', status='active'
        )

    def test_filter_by_status(self):
        """Фильтрация поездок по статусу."""
        response = self.client.get('/api/trips/?status=planned')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for trip in response.data['results']:
            self.assertEqual(trip['status'], 'planned')

    def test_filter_by_cat(self):
        """Фильтрация поездок по ID кота."""
        response = self.client.get(f'/api/trips/?cat={self.cat.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for trip in response.data['results']:
            self.assertEqual(trip['cat'], self.cat.id)

    def test_pagination(self):
        """Ответ содержит поля пагинации."""
        response = self.client.get('/api/trips/')
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('results', response.data)


class StopTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.trip = Trip.objects.create(
            owner=self.user, cat=self.cat,
            title='Поездка', status='active'
        )

    def test_add_stop_to_active_trip(self):
        """Можно добавить остановку к активной поездке."""
        data = {'title': 'Остановка 1', 'order': 1}
        response = self.client.post(
            f'/api/trips/{self.trip.id}/stops/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Остановка 1')

    def test_add_stop_to_completed_trip(self):
        """Нельзя добавить остановку к завершённой поездке."""
        self.trip.status = 'completed'
        self.trip.save()
        data = {'title': 'Лишняя', 'order': 1}
        response = self.client.post(
            f'/api/trips/{self.trip.id}/stops/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_stops(self):
        """Список остановок поездки доступен без авторизации."""
        Stop.objects.create(trip=self.trip, title='А', order=1)
        Stop.objects.create(trip=self.trip, title='Б', order=2)
        self.client.credentials()
        response = self.client.get(f'/api/trips/{self.trip.id}/stops/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_delete_stop(self):
        """Владелец может удалить остановку."""
        stop = Stop.objects.create(trip=self.trip, title='Стоп', order=1)
        response = self.client.delete(
            f'/api/trips/{self.trip.id}/stops/{stop.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
