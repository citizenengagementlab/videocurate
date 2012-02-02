from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_will_be_posted
from django.conf import settings

import akismet

def spam_check(sender, comment, request, **kwargs):
  ak = akismet.Akismet()
  try:
    ak.setAPIKey(settings.AKISMET_API_KEY,"http://www.99percentmedia.org")
    real_key = ak.verify_key()
    if real_key:
      data = {
        'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERER', ''),
        'comment_type': 'comment',
        'comment_author': comment.user_name.encode('utf-8'),
      }
      is_spam = ak.comment_check(comment.comment.encode('utf-8'), data=data, build_data=True)
      if is_spam:
        return False
      else:
        return True
  except akismet.AkismetError, e:
      print 'Something went wrong, allowing comment'
      print e.response, e.statuscode
      return True

comment_will_be_posted.connect(spam_check,sender=Comment,dispatch_uid="comment_spam_check_akismet")
