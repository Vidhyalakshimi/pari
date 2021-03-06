from __future__ import unicode_literals

from django.db import models
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, \
    MultiFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from core.edit_handlers import M2MFieldPanel


@python_2_unicode_compatible
class Face(Page):
    image = models.ForeignKey("core.AffixImage",
                              related_name="face_for_image", null=True,
                              on_delete=models.SET_NULL)
    location = models.ForeignKey("location.Location", null=True,
                                  on_delete=models.SET_NULL)
    description = RichTextField(blank=True,
                                default=render_to_string("face/new_face_placeholder.html"))
    language = models.CharField(max_length=7, choices=settings.LANGUAGES)

    def __str__(self):
        return "{0} {1}".format(self.title, self.location.district)

    @property
    def featured_image(self):
        return self.image

    search_fields = Page.search_fields + (
        index.FilterField('image'),
        index.SearchField('description', partial_match=True, boost=2),
        index.FilterField('location'),
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel('image'),
        M2MFieldPanel('location'),
        FieldPanel('description'),
        FieldPanel('language'),
    ]

    def get_absolute_url(self):
        name = "face-detail-single"
        return reverse(name, kwargs={
            "alphabet": self.location.district[0].lower(),
            "slug": self.slug
        })

    def get_context(self, request, *args, **kwargs):
        return {
            'faces': [self],
            'alphabet': self.location.district[0].lower(),
            'request': request
        }
