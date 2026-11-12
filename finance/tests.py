from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

from django.test import SimpleTestCase

from finance import views


class WhatsAppFlowTests(SimpleTestCase):
    def build_payment(self):
        student = SimpleNamespace(
            fullName='Jane Student',
            contact='0712345678',
            guardian_information=None,
            sponsor_information=None,
        )
        fee = SimpleNamespace(fee_name='Tuition')
        payment = SimpleNamespace(
            id=10,
            student=student,
            fee=fee,
            amount_paid='15000.00',
            payment_method='cash',
            payment_reference='REF-123',
            date_paid=date(2026, 3, 20),
            whatsapp_messages=MagicMock(),
        )
        payment.get_payment_method_display = lambda: 'Cash'
        return payment

    def test_format_phone_normalizes_tanzanian_numbers(self):
        self.assertEqual(views.format_phone('255712345678'), '+255712345678')
        self.assertEqual(views.format_phone('0712345678'), '+255712345678')
        self.assertEqual(views.format_phone('+255712345678'), '+255712345678')

    def test_get_student_phone_uses_contact_only(self):
        student = SimpleNamespace(contact=255770036452)

        self.assertEqual(views.get_student_phone(student), '255770036452')

    def test_get_latest_whatsapp_message_returns_none_safely(self):
        payment = self.build_payment()
        payment.whatsapp_messages.order_by.return_value.last.return_value = None

        self.assertIsNone(views._get_latest_whatsapp_message(payment))

    @patch('finance.views.send_message')
    @patch('finance.views.WhatsAppMessage.objects.create')
    @patch('finance.views._get_whatsapp_setting')
    def test_notify_payment_saves_msg_id_and_sent_status(self, get_setting, create_message, send_message):
        request = SimpleNamespace(user=SimpleNamespace(username='accountant'))
        payment = self.build_payment()
        get_setting.return_value = SimpleNamespace(api_key='secret', base_url='https://example.com/api')
        send_message.return_value = {'success': True, 'data': {'msgId': 'abc123'}}

        success, message = views._notify_payment_via_whatsapp(request, payment)

        self.assertTrue(success)
        create_message.assert_called_once()
        self.assertEqual(create_message.call_args.kwargs['phone_number'], '+255712345678')
        self.assertEqual(create_message.call_args.kwargs['msg_id'], 'abc123')
        self.assertEqual(create_message.call_args.kwargs['status'], 'sent')
        self.assertIn('sent successfully', message)

    @patch('finance.views.update_message')
    @patch('finance.views._get_latest_whatsapp_message')
    @patch('finance.views._get_whatsapp_setting')
    def test_update_payment_marks_update_failed_on_api_failure(self, get_setting, get_latest_message, update_message):
        payment = self.build_payment()
        request = SimpleNamespace(user=SimpleNamespace(username='accountant'))
        message_obj = Mock(msg_id='abc123', message='old', status='sent', api_response={})
        get_latest_message.return_value = message_obj
        get_setting.return_value = SimpleNamespace(api_key='secret', base_url='https://example.com/api')
        update_message.return_value = {'success': False, 'message': 'not updated'}

        success, message = views._update_payment_whatsapp_message(request, payment)

        self.assertFalse(success)
        self.assertEqual(message_obj.status, 'update_failed')
        message_obj.save.assert_called()
        self.assertIn('update failed', message.lower())

    @patch('finance.views.delete_message')
    @patch('finance.views._get_latest_whatsapp_message')
    @patch('finance.views._get_whatsapp_setting')
    def test_delete_payment_marks_deleted_on_api_success(self, get_setting, get_latest_message, delete_message):
        payment = self.build_payment()
        request = SimpleNamespace(user=SimpleNamespace(username='accountant'))
        message_obj = Mock(msg_id='abc123', status='sent', api_response={})
        get_latest_message.return_value = message_obj
        get_setting.return_value = SimpleNamespace(api_key='secret', base_url='https://example.com/api')
        delete_message.return_value = {'success': True}

        success, message = views._delete_payment_whatsapp_message(request, payment)

        self.assertTrue(success)
        self.assertEqual(message_obj.status, 'deleted')
        message_obj.save.assert_called()
        self.assertIn('deleted successfully', message.lower())
