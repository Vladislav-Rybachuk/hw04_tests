import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post_to_create = {
            'text': 'Текст поста',
            'group': cls.group.id,
        }
        cls.post = Post.objects.create(
            text='Текст поста 1',
            author=cls.user,
            group=cls.group,
        )
        cls.post_after_edit = {
            'text': 'Текст поста после изменения',
            'group': cls.group.id,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.post_to_create,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.post_to_create['text'],
                group=self.post_to_create['group'],
                author=self.user,
            ).exists()
        )
        self.assertEqual(
            Post.objects.get(
                text=self.post_to_create['text'],
                group=self.post_to_create['group'],
                author=self.user,
            ), Post.objects.latest('pub_date')
        )

    def test_post_edit(self):
        """Валидная форма корректно меняет запись в Post."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    args=[self.post.id]
                    ),
            data=self.post_after_edit,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[self.post.id])
        )
        self.assertEqual(Post.objects.count(), posts_count)

        post_edit = Post.objects.filter(
            text=self.post_after_edit['text'],
            author=self.user,
            group=self.group,
        )
        self.assertTrue(post_edit.exists())
