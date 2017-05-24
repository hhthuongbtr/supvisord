from __future__ import unicode_literals

from django.db import models


class Log(models.Model):
	datetime = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	user = models.TextField(blank=True, null=True)
	action = models.TextField(blank=True, null=True)
	msg = models.TextField(blank=True, null=True)