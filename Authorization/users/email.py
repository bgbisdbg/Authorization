from time import time

from django.core.mail import send_mail
from djoser.email import BaseDjoserEmail

from poker_elite.settings import EMAIL_HOST_USER


class ActivationEmail(BaseDjoserEmail):
    template_name = "email/activation.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get('user')
        if user:
            if not user.activation_code:
                user.generate_activation_code()
            context['activation_code'] = user.activation_code
        else:
            raise ValueError("User is not provided in the context")
        return context



class CustomPasswordResetEmail(BaseDjoserEmail):
    template_name = "email/password_reset.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get('user')
        if user:
            user.generate_activation_code()
            user.is_active = False
            user.save()
            context['activation_code'] = user.activation_code
        else:
            raise ValueError("User is not provided in the context")
        return context

    def send(self, to, *args, **kwargs):
        context = self.get_context_data()
        if 'activation_code' not in context:
            raise ValueError("Activation code is not in the context")
        subject = 'Код активации'
        message = f'Ваш код активации: {context["activation_code"]}'
        from_email = EMAIL_HOST_USER
        recipient_list = to
        send_mail(subject, message, from_email, recipient_list)