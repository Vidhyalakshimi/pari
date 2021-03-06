from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, \
    MultiFieldPanel, RichTextFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from modelcluster.fields import M2MField, ParentalKey

from core.edit_handlers import M2MFieldPanel, AudioPanel


@python_2_unicode_compatible
class Album(Page):
    description = RichTextField()
    locations = M2MField("location.Location", related_name="albums_by_location")
    photographers = M2MField("author.Author",
                             related_name="albums_by_photographer", blank=True)
    language = models.CharField(max_length=7, choices=settings.LANGUAGES)

    content_panels = Page.content_panels + [
        FieldPanel('language'),
        FieldPanel('description'),
        M2MFieldPanel('locations'),
        M2MFieldPanel('photographers'),
        InlinePanel('slides', label=_('Slides'), panels=[
            ImageChooserPanel('image'),
            AudioPanel('audio'),
            RichTextFieldPanel('description')
        ]),
    ]

    template = "album/album_detail.html"

    search_fields = Page.search_fields + (
        index.FilterField('photographers'),
        index.SearchField('description', partial_match=True, boost=2),
        index.FilterField('locations'),
        index.FilterField('language'),
    )

    def get_context(self, request, *args, **kwargs):
        return {
            'album': self,
            'request': request
        }

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        name = "album-detail"
        return reverse(name, kwargs={"slug": self.slug})

    @property
    def featured_image(self):
        return self.slides.all()[0].image


@python_2_unicode_compatible
class AlbumSlide(Orderable):
    page = ParentalKey("album.Album", related_name="slides")
    image = models.ForeignKey("core.AffixImage", related_name="album_for_image", null=True, blank=True)
    audio = models.CharField(blank=True, max_length=50)
    description = RichTextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "created_on"]

    def __str__(self):
        if self.image:
            return self.image.title
        return self.description
