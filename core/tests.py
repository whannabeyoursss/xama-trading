from django.test import TestCase
from django.urls import reverse

from .forms import SignUpForm
from .models import Order, PasswordResetCode, Product, User


class DashboardTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer',
            password='pass12345',
            phone_number='09171234567',
            role=User.CUSTOMER,
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='pass12345',
            phone_number='09170000000',
            role=User.ADMIN,
        )
        self.product = Product.objects.create(
            name='Canned Goods',
            sku='CG-001',
            price=50,
            quantity=20,
            reorder_level=5,
        )

    def test_user_roles_split_admin_and_customer(self):
        self.assertFalse(self.customer.is_admin_user())
        self.assertTrue(self.admin.is_admin_user())

    def test_signup_requires_number_only_phone(self):
        form = SignUpForm(
            data={
                'username': 'badphone',
                'first_name': 'Bad',
                'last_name': 'Phone',
                'phone_number': '0917-123-4567',
                'password1': 'pass12345ABC',
                'password2': 'pass12345ABC',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

    def test_customer_can_place_order(self):
        self.client.login(username='customer', password='pass12345')
        response = self.client.post(reverse('order_create'), {'product': self.product.id, 'quantity': 2})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('orders'))
        self.assertEqual(Order.objects.filter(customer=self.customer).count(), 1)

    def test_phone_reset_code_flow(self):
        response = self.client.post(reverse('forgot_password'), {'phone_number': '09171234567'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('reset_password'))
        code = PasswordResetCode.objects.get(user=self.customer).code
        response = self.client.post(
            reverse('reset_password'),
            {'code': code, 'new_password': 'newpass12345', 'confirm_password': 'newpass12345'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.check_password('newpass12345'))

# Create your tests here.
