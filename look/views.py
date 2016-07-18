from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.generic.edit import CreateView
from look.models import Follow
from look.models import Tweet
from django.contrib.auth.models import User
from stream_django.enrich import Enrich 
from stream_django.feed_manager import feed_manager
from django.shortcuts import render_to_response, render, get_object_or_404, redirect
from django.conf import settings

enricher = Enrich()
#current_user = request.user.first_name

def index(request):
	if not request.user.is_authenticated():
		return render(request, 'look/index.html')
	user = get_object_or_404(User, username=request.user.username)
	feeds = feed_manager.get_user_feed(user.id)
	activities = feeds.get(limit=25)['results']
	activities = enricher.enrich_activities(activities)
	context = {
        'activities': activities,
        'user': user,
        'login_user': request.user
    }
	return render(request, 'look/user.html', context)

class TweetView(CreateView):
	model = Tweet
	fields = ['text']

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super(Tweet, self).form_valid(form)

def profile_feed(request, username=None):
	user = User.objects.get(username=username)
	feed = feed_manager.get_user_feed(user.id)
	activities = feed.get(limit=25)['results']
	enricher.enrich_activities(activities)
	context = {
		'activtities': activtities
	}
	return render(request, 'activity/tweets.html', context)

def user(request, user_name):
    if not request.user.is_authenticated():
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    user = get_object_or_404(User, username=user_name)
    feeds = feed_manager.get_user_feed(user.id)
    activities = feeds.get(limit=25)['results']
    activities = enricher.enrich_activities(activities)
    context = {
        'activities': activities,
        'user': user,
        'login_user': request.user
    }
    return render(request, 'look/user.html', context)

class FollowView(CreateView):
	model = Follow
	fields = ['target']

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super(Tweet, self).form_valid(form)


#Timeline view
def timeline(request):
	feed = feed_manager.get_news_feeds(reqeust.user.id)['flat']
	activities = feed.get(limit=25)['results']
	enricher.enrich_activities(activities)
	context = {
		'activities': activities
	}
	return render(request, 'timeline.html', context)