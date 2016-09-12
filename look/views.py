from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.generic.edit import CreateView
from look.models import Follow
from look.models import Tweet
from django.contrib.auth.models import User
from stream_django.enrich import Enrich 
from stream_django.feed_manager import feed_manager
from django.shortcuts import render_to_response, render, get_object_or_404, redirect
from django.conf import settings
from look.forms import TweetForm, FollowForm

enricher = Enrich()

def index(request):
	if not request.user.is_authenticated():
		return render(request, 'look/index.html')
	if request.method == 'POST':
		#create a form instance from post data.the authenticated user is passed only the POST`s text field is needed
		form = TweetForm(
				{
				'user': request.user.pk,
				'text': request.POST['text']
			}
		)
		#validate the form
		if form.is_valid():
			#save a new Tweet object from the form data
			form.save()
	else: #for a GET request, create a blank form
		form = TweetForm()
	user = get_object_or_404(User, username=request.user.username)
	feeds = feed_manager.get_user_feed(user.id)
	activities = feeds.get(limit=25)['results']
	activities = enricher.enrich_activities(activities)
	context = {
        'activities': activities,
        'user': user,
        'login_user': request.user,
        'form': form
    }
	return render(request, 'look/user.html', context)

class TweetView(CreateView):
	model = Tweet
	fields = ['text']

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super(Tweet, self).form_valid(form)


def user(request, user_name):
    if not request.user.is_authenticated():
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    form = TweetForm()
    user = get_object_or_404(User, username=user_name)
    feeds = feed_manager.get_user_feed(user.id)
    activities = feeds.get(limit=25)['results']
    activities = enricher.enrich_activities(activities)
    context = {
        'activities': activities,
        'user': user,
        'login_user': request.user,
        'form': form
    }
    return render(request, 'look/user.html', context)

def follow(request):
	form = FollowForm(request.POST)
	if form.is_valid():
		follow = form.instance
		follow.user = request.user
		follow.save()
	return redirect("/discover/")

def unfollow(request, target_id):
	follow = Follow.objects.filter(user=request.user, target_id=target_id).first()
	if follow is not None:
		follow.delete()
	return redirect("/discover/")

def discover(request):
	users = User.objects.order_by('date_joined')[:50]
	login_user = User.objects.get(username=request.user)
	#generating the user list
	following = []
	for i in users:
		if len(i.followers.filter(user=login_user.id)) == 0:
			if i == request.user:	
				pass  		#user himself shouldn't appear
			else:
				following.append((i, False)) #not followed
		else:
			following.append((i, True)) #followed
	context = {
		'users': users,
		'form': FollowForm,
		'login_user': request.user,
		'following': following
	}
	return render(request, 'look/discover.html', context)

#Timeline view
def timeline(request):
	feed = feed_manager.get_news_feeds(reqeust.user.id)['flat']
	activities = feed.get(limit=25)['results']
	enricher.enrich_activities(activities)
	context = {
		'activities': activities
	}
	return render(request, 'timeline.html', context)

#hashtag view
def hashtag(request, hashtag):
	feed = feed_manager.get_feed('hashtag', hashtag)
	activities = feed.get(limit=25)['results']
	enricher.enrich_activities(activities)
	context = {
		'activities': activities
	}
	return render(request, 'hashtag.html', context)