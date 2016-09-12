from django.forms import ModelForm
from look.models import Tweet, Follow
from django import forms
from django.utils.translation import ugettext_lazy as _

class TweetForm(ModelForm):
	class Meta:
		model = Tweet
		fields = '__all__'
		#override the text label
		labels = {
			'text': _('Anything on your mind?')
		}
		error_messages = {
			'text': {
				'required': 'Why not wait until you actually have something to tweet.'
			}
		}

	def __init__(self, *args, **kwargs):
		super(TweetForm, self).__init__(*args, **kwargs)
		self.fields["text"].initial = "Anything on your mind?"



class FollowForm(ModelForm):
	class Meta:
		model = Follow
		fields = '__all__'