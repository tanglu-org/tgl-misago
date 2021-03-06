from django.utils import timezone
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
import floppyforms as forms
from misago.conf import settings
from misago.utils.strings import slugify

class FloodProtectionMixin(object):
    def clean(self):
        cleaned_data = super(FloodProtectionMixin, self).clean()
        if self.request.block_flood_requests and self.request.user.last_post:
            diff = timezone.now() - self.request.user.last_post
            diff = diff.seconds + (diff.days * 86400)
            wait_for = settings.FLOOD_DELAY - diff
            if wait_for > 0:
                if wait_for < 5:
                    raise forms.ValidationError(_("You can't post one message so quickly after another. Please wait a moment and try again."))
                else:
                    raise forms.ValidationError(ungettext_lazy(
                            "You can't post one message so quickly after another. Please wait %(seconds)d second and try again.",
                            "You can't post one message so quickly after another. Please wait %(seconds)d seconds and try again.",
                        wait_for) % {
                            'seconds': wait_for,
                        })
        return cleaned_data


class ValidateThreadNameMixin(object):
    def clean_thread_name(self):
        data = self.cleaned_data['thread_name']
        slug = slugify(data)
        if len(slug) < settings.thread_name_min:
            raise forms.ValidationError(ungettext_lazy(
                                                  "Thread name must contain at least one alpha-numeric character.",
                                                  "Thread name must contain at least %(count)d alpha-numeric characters.",
                                                  settings.thread_name_min
                                                  ) % {'count': settings.thread_name_min})
        if len(data) > settings.thread_name_max:
            raise forms.ValidationError(ungettext_lazy(
                                                  "Thread name cannot be longer than %(count)d character.",
                                                  "Thread name cannot be longer than %(count)d characters.",
                                                  settings.thread_name_max
                                                  ) % {'count': settings.thread_name_max})
        return data


class ValidatePostLengthMixin(object):
    def clean_post(self):
        data = self.cleaned_data['post']
        if len(data) < settings.post_length_min:
            raise forms.ValidationError(ungettext_lazy(
                                                  "Post content cannot be empty.",
                                                  "Post content cannot be shorter than %(count)d characters.",
                                                  settings.post_length_min
                                                  ) % {'count': settings.post_length_min})
        return data