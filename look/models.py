from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from stream_django import activity
from django.db.models import signals
from django.template.defaultfilters import slugify
from stream_django import activity
from stream_django.feed_manager import feed_manager

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name = 'profile')
    
    def __unicode__(self):
        return "{}'s profile".format(self.user.username)
    
    class Meta:
        db_table = 'user_profile'
        
    def acocunt_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email = self.user.email)
            if len(result):
                return result[0].verified
        return False

User.profile = property(lambda u: UserProfile.objects.get_or_create(user = u)[0])

class Tweet(activity.Activity, models.Model):
    user = models.ForeignKey('auth.User')
    text = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def activity_object_attr(self):
        return self
    

class Follow(models.Model):
    user = models.ForeignKey('auth.User', related_name='friends')
    target = models.ForeignKey('auth.User',related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target')

