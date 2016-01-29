from __future__ import unicode_literals

from django.db import models
from django.contrib import auth
from django.core.urlresolvers import reverse

# Create your models here.
class Patch(models.Model):
    submitter = models.ForeignKey(auth.models.User)
    pid = models.TextField(max_length=10)
    info = models.TextField(max_length=1024)
    status = models.TextField(max_length=50)
    time = models.DateTimeField()

    def get_absolute_url(self):
        return reverse('patch_detail', args=[str(self.id)])
