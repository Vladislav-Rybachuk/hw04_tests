from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from django.contrib.auth.decorators import login_required
from .forms import PostForm

QUANTITY = 10


def paginated_context(queryset, request):
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }


def index(request):
    context = paginated_context(
        Post.objects.all().order_by('pub_date'), request
    )
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts_list = group.posts.all()
    context = {
        'group': group,
        'group_posts_list': group_posts_list,
    }
    context.update(paginated_context(
        group.posts.all().order_by('pub_date'), request)
    )
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    count_post = author_posts.count()
    context = {
        'author': author,
        'count_post': count_post,

    }
    context.update(paginated_context(
        author.posts.all().order_by('pub_date'), request)
    )
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.filter(author_id=post.author.id).count()
    context = {
        'post_count': post_count,
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user)
        return render(request, 'posts/post_create.html',
                      {'form': form})
    context = {
        'form': form,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    selected_post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        instance=selected_post
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post_id=post.pk)
    context = {
        'form': form,
        'title': 'Редактировать пост',
        'is_edit': True
    }
    return render(request, 'posts/post_create.html', context)
