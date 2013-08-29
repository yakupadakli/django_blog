from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from unidecode import unidecode
from ckeditor.fields import RichTextField

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=100)
    body = RichTextField()
    # author = models.CharField(max_length=50)
    author = models.ForeignKey(User, related_name="author")
    pub_date = models.DateTimeField(
        auto_now_add=True,
        editable=False)
    image = models.ImageField(upload_to="blog",
                              blank=True,
                              default="blog/not-found.png")
    categories = models.ManyToManyField(Category,
                                        related_name='categories')
    tags = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120,
                            unique=True,
                            editable=False)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        i = 1
        articles = Article.objects.order_by('slug')

        self.slug = slugify(unidecode(self.title))
        for article in articles:
            if self.slug == article.slug:
                articles = Article.objects.order_by('slug')
                self.slug = slugify(unidecode(self.title)) + "-" + str(i)
                i += 1
        super(Article, self).save(*args, **kwargs)
