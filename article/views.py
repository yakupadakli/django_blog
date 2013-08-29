# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from unidecode import unidecode
from account import tasks
from article.forms import ArticleForm
from comment.forms import CommentForm
from comment.models import Comment, Activation
from models import Article, Category
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.cache import get_cache


def caching():
    """
        Find articles and adding them into
        cache if cache is empty
    :param articles: All articles want to be
        listed in the index page
    :return:
        result: articles in the cache
    """
    cache_key = 'articles'
    cache_time = 60 * 60  # time to live in seconds
    cache = get_cache("default")
    result = cache.get(cache_key)
    if not result:
        articles = Article.objects.select_related().order_by(
            '-pub_date'
        ).prefetch_related(
            'categories'
        )
        print articles
        # if articles has no image
        for article in articles:
            if article.image == "":
                article.image = "blog/not-found.png"
                article.save()
        cache.set(cache_key, articles, cache_time)
        result = cache.get(cache_key)
    return result


def delete_cache():
    cache_key = 'articles'
    cache = get_cache("default")
    cache.delete(cache_key)


def index(request):
    """
        Showing all articles in the site
        Articles are putting into cache and
        sending template
    :param request:
    :return:
    """
    # taking values from cache if exist
    articles = caching()

    c = {'articles': articles}
    return render(request, "index.html", c)


def find_all_comments(article):
    """
        Finding all comments belongs to the article
    :param article: is looking for comments
    :return:
        comments: all comments are belongs the article
        comments_of_comments : all comments belongs to comments
        type_article : Content type of article
        type_comment : Content type of comment
    """
    type_article = ContentType.objects.get_for_model(Article)
    comments = Comment.objects.filter(
        object_id=article.id
    ).filter(
        content_type=type_article.id
    ).filter(
        is_active=True
    ).filter(
        article_id=article.id
    )

    type_comment = ContentType.objects.get_for_model(Comment)
    comments_of_comments = Comment.objects.filter(
        content_type=type_comment.id
    ).filter(
        is_active=True
    ).filter(
        article_id=article.id
    )
    return comments, comments_of_comments, type_article, type_comment


def check_user(email, new_comment, request):
    """
        finding user who is comment on the article or
        comments and if user is not registered and logged in
        he or she needs to confirm the comment via email adress

    :param email: users who comments
    :param new_comment: comment comes from user
    :param request:
    :raise:
    """
    try:
        user = request.user
        comment = Comment.objects.get(id=new_comment.id)
        if user.is_authenticated():
            comment.is_active = True
            comment.name = str(
                user.first_name
            ) + " " + str(
                unidecode(
                    user.last_name
                )
            )
            comment.save()
            messages.success(
                request,
                _('Comment added successfully. It will show as soon as possible.'),
                fail_silently=True
            )
        else:
            activation_key = tasks.generate_activation_key(
                email
            )
            key_expires = tasks.generate_key_expires_date()
            activation = Activation(
                comment=new_comment,
                activation_key=activation_key,
                key_expires=key_expires
            )
            activation.save()
            messages.success(
                request,
                _('Comment add successfully but you need to confirm it by confirmation code is sent .'),
                fail_silently=True
            )
            tasks.send_activation_code.delay(
                activation_key,
                email, "comment_activation"
            )
    except Comment.DoesNotExist:
        raise Http404


def detail(request, slug):
    """
        This views gives us detail of article
        which has same slug with slug
        and also user can comments article or comments

    :param request:
    :param slug:
    :return:
    """
    article = get_object_or_404(Article, slug=slug)
    new_comment_form = CommentForm()
    # displaying comment form to the user
    show_comment_form = True
    if request.method == "POST":
        # create comment form
        new_comment_form = CommentForm(request.POST)
        if new_comment_form.is_valid():
            # if valid taking values in the form by variables
            name = request.POST.get("name")
            email = request.POST.get("email")
            comment = request.POST.get("comment")
            content_type_id = request.POST.get("content_type_id")
            object_id = request.POST.get("object_id")

            type = ContentType.objects.get_for_id(
                content_type_id
            )
            # saving comment
            new_comment = Comment(
                comment=comment,
                email=email,
                name=name,
                content_type=type,
                object_id=object_id,
                article=article
            )
            new_comment.save()
            delete_cache()
            # controlling user is registered or not and
            # if s/he are not registered or logged in,
            # s/he needs to confirm comment
            check_user(email, new_comment, request)
             # not displaying comment form to the user
            return redirect(
                "/articles/" + slug + "/#comment-" + str(
                    new_comment.id
                )
            )
        else:

            show_comment_form = False
    comments, comments_of_comments, type_article, type_comment = \
        find_all_comments(
            article
        )

    c = {"article": article,
         "comments": comments,
         "comments_of_comments": comments_of_comments,
         "form": new_comment_form,
         "content_type_article": type_article.id,
         "content_type_comment": type_comment.id,
         "show_comment_form": show_comment_form}
    return render(request, "detail.html", c)


def search(request):
    """
        Simple search into articles
    :param request:
    :return:
    """
    query = request.GET['search']
    results = Article.objects.filter(body__icontains=query)
    c = {'results': results, "query": query}
    return render(request, "search.html", c)


@login_required(login_url='/accounts/login/')
def add_article(request):
    """
        Adding new article by user who is logged in
    :param request:
    :return:
    """
    # create article form
    article_form = ArticleForm()
    if request.method == "POST":
        # taking form data into variables to use later
        data = request.POST.copy()
        # adding author for th article
        author_id = request.user.id
        data["author"] = author_id
        article_form = ArticleForm(data, request.FILES)
        if article_form.is_valid():
            article_form = ArticleForm(data, request.FILES)
            instance = article_form.save()
            # if article has highlighted image, it will be re-size
            if request.FILES.get("image") is not None:
                tasks.resize_image.delay(instance.image)

            delete_cache()
            return redirect(reverse("articles:my_article"))

    c = {"form": article_form}
    return render(request, "add_article.html", c)


@login_required(login_url='/accounts/login/')
def my_article(request):
    """
        Showing logged users articles
    :param request:
    :return:
    """
    articles = Article.objects.filter(
        author=request.user
    ).order_by(
        "-pub_date"
    )
    c = {"articles": articles}
    return render(request, "my_articles.html", c)


@login_required(login_url='/accounts/login/')
def edit_article(request, slug):
    """
        Editing articles which are users have
    :param request:
    :param slug:
    :return:
    """

    # find article if it exists
    article = get_object_or_404(Article, slug=slug)

    if article.author_id == request.user.id:
        if request.method == "POST":
            # taking form data into variables to use later
            data = request.POST.copy()
            # adding author
            author_id = request.user.id
            data["author"] = author_id
            article_form = ArticleForm(data, request.FILES)
            if article_form.is_valid():
                # changing new value with the new value
                article.title = data["title"]
                article.body = data["body"]
                image = request.FILES.get("image")
                # if there is  a new image, old image will change
                if image is not None:
                    article.image = request.FILES.get("image")

                # categories can be list because of this,
                # i get categories with getlist()
                article.categories = request.POST.getlist("categories")
                article.tags = data["tags"]

                # save edited article
                article.save()
                # determining success message
                messages.success(
                    request,
                    _('Article updated successfully.'),
                    fail_silently=True
                )
                tasks.resize_image.delay(article.image)

                return redirect(reverse("articles:edit_article", kwargs={'slug': article.slug}))
            else:
                messages.error(
                    request,
                    _('Article update failed.'),
                    fail_silently=True
                )

        image = article.image
        # send data to the template with initial data
        article_form = ArticleForm(
            initial={
                "title": article.title,
                "body": article.body,
                "image": article.image,
                "categories": article.categories.all(),
                "tags": article.tags
            }
        )
        c = {"form": article_form, "image": image}
        return render(request, "edit_article.html", c)
    else:
        messages.error(
            request,
            _('You cannot edit this article because it is not yours.'),
            fail_silently=True
        )
        return redirect(reverse("index"))