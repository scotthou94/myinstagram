from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from stream_django import activity
from django.db.models import signals
from django.template.defaultfilters import slugify
from stream_django import activity
from stream_django.feed_manager import feed_manager
from django.db.models.signals import post_save, post_delete


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

    def __str__(self):
        return self.text

    @property
    def activity_object_attr(self):
        return self

    def parse_mentions(self):
        mentions = [slugify(i) for i in self.text.split() if i.startswith("@")]
        return User.objects.filter(username__in=mentions)

    @property
    def activity_notify(self):
        targets = []
        for user in self.parse_mentions():
            targets.append(feed_manager.get_news_feeds(user.id)['flat'])
        return targets
    
class Follow(models.Model):
    user = models.ForeignKey('auth.User', related_name='friends')
    target = models.ForeignKey('auth.User',related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target')

#use django`s signals to perform follow/unfollow requests on GetStream APIs
def unfollow_feed(sender, instance, **kwargs):
    feed_manager.unfollow_user(instance.user_id, instance.target_id)

def follow_feed(sender, instance, created, **kwargs):
    if created:
        feed_manager.follow_user(instance.user_id, instance.target_id)

post_save.connect(follow_feed, sender=Follow)
post_delete.connect(unfollow_feed, sender=Follow)

