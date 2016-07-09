from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.generic.edit import CreateView
from look.models import Follow
from look.models import Tweet
from django.contrib.auth.models import User
from stream_django.enrich import Enrich 
from stream_django.feed_manager import feed_manager
from django.db.models.signals import post_save, post_delete

def index(request):
    return render(request, 'look/index.html')

class TweetView(CreateView):
	model = Tweet
	fields = ['text']

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super(Tweet, self).form_valid(form)

def profile_feed(request, username=None):
	enricher = Enrich()
	user = User.objects.get(username=username)
	feed = feed_manager.get_user_feed(user.id)
	activities = feed.get(limit=25)['results']
	enricher.enrich_activities(activities)
	context = {
	'activtities': activtities
	}
	return render(request, 'tweets.html', context)

class FollowView(CreateView):
	model = Follow
	fields = ['target']

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super(Tweet, self).form_valid(form)

#use django`s signals to perform follow/unfollow requests on GetStream APIs
def unfollow_feed(sender, instance, **kwargs):
    feed_manager.unfollow_user(instance.user_id, instance.target_id)

def follow_feed(sender, instance, created, **kwargs):
	if created:
		feed_manager.follow_user(instance.user_id, instance.target_id)

post_save.connect(follow_feed, sender=Follow)
post_delete.connect(unfollow_feed, sender=Follow)

#Timeline view
def timeline(request):
	enricher = Enrich()
	feed = feed_manager.get_news_feeds(reqeust.user.id)['flat']
	activities = feed.get(limit=25)['results']
	enricher.enrich_activities(activities)
	context = {
		'activities': activities
	}
	return render(request, 'timeline.html', context)
	