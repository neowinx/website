"""Various utility functions used across the website"""
import romkan
from xpinyin import Pinyin
from django.contrib.auth import get_user_model
from django.utils.text import slugify as django_slugify
SLUG_MAX_LENGTH = 50


def slugify(text):
    """Version of slugify that supports Japanese characters"""
    if not text:
        return ""
    slug = django_slugify(text)
    if not slug:
        # Title may be in Japanese
        slug = django_slugify(romkan.to_roma(text))
    if not slug:
        # Title may be in Chinese
        pinyin = Pinyin()
        slug = django_slugify(pinyin.get_pinyin(text))
    return slug[:50]


def get_auto_increment_slug(model, instance, text, slug=None):
    """Return a slug of `text` while keeping it unique within a given model.
    If the slug exists, a number will be appended to it until it is made unique
    The slug field must be named `slug`.

    :param model: Class of the Model the object belongs to
    :param instance: Instance of object the slug belongs to
    :param text: The string to slugify
    :param slug: Optional initial slug
    :return: Unique slug for the model
    """
    text = str(text)
    if not slug:
        original_slug = slugify(text)[:SLUG_MAX_LENGTH]
        slug = original_slug
    else:
        original_slug = slug
    slug_exists = True
    counter = 1
    while slug_exists:
        pk = instance.pk if instance else 0
        slug_exists = (
            model.objects
            .exclude(pk=pk)
            .filter(slug=slug)
            .exists()
        )
        if slug_exists:
            suffix = "-%d" % counter
            slug = original_slug[:SLUG_MAX_LENGTH - len(suffix)] + suffix
            counter += 1
    return slug


def create_admin(username='admin', password='admin'):
    user = get_user_model().objects.create(username=username,
                                           is_superuser=True,
                                           is_staff=True,
                                           is_active=True)
    user.set_password(password)
    user.save()
    return user


def create_user(username='user', password='password'):
    user = get_user_model().objects.create(username=username,
                                           is_active=True)
    user.set_password(password)
    user.save()
    return user


def get_client_ip(request):
    """Return the user's IP address from a Django request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return ip_address
