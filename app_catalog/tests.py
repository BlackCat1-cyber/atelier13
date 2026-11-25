from django.test import TestCase, Client
from django.db import transaction
from app_catalog.models import Costume, Category


class NegativeTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.category = Category.objects.create(name='Test')
        self.costume = Costume.objects.create(
            name='Test',
            article='T-001',
            category=self.category,
            daily_price=3000,
            deposit_amount=5000,
            status='available'
        )

    def test_404_nonexistent_costume(self):
        r = self.client.get('/catalog/9999/')
        self.assertEqual(r.status_code, 404)

    def test_403_csrf_missing(self):
        r = self.client.post('/fitting/', {
            'fitting_date': '2027-01-01',
            'fitting_time': '10:00',
            'costume_count': '1'
        })
        self.assertEqual(r.status_code, 403)

    def test_form_invalid_no_record_created(self):
        r = self.client.get('/fitting/')
        token = r.cookies['csrftoken'].value
        r2 = self.client.post('/fitting/', {
            'fitting_date': '2027-01-01',
            'fitting_time': '10:00',
            'costume_count': '99',
            'csrfmiddlewaretoken': token
        })
        self.assertNotContains(r2, 'Вы записаны')

    def test_transaction_rollback(self):
        initial_price = self.costume.daily_price
        try:
            with transaction.atomic():
                self.costume.daily_price = 9999
                self.costume.save()
                raise ValueError('error')
        except ValueError:
            pass
        self.costume.refresh_from_db()
        self.assertEqual(self.costume.daily_price, initial_price)

    def test_empty_queryset_no_crash(self):
        r = self.client.get('/catalog/?q=zzzzzzzz')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Под фильтр ничего не попало')