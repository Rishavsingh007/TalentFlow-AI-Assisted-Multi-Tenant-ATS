from django.utils.text import slugify

from .models import Company


def generate_company_slug(name: str) -> str:
    base = slugify(name) or "company"
    slug = base
    counter = 1
    while Company.objects.filter(slug=slug).exists():
        counter += 1
        slug = f"{base}-{counter}"
    return slug
