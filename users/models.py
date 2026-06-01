from django.db import models


class UserAccess(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ('access_users_module', 'Can access users module'),
        ]
        verbose_name = 'User access'
        verbose_name_plural = 'User access'

    def __str__(self):
        return f'User access {self.pk}'
