import datetime as dt

from django.contrib.auth import get_user_model
from django.db import models

from blogicum.settings import IMAGE_CONST

User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено',)

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок',)
    description = models.TextField(verbose_name='Описание',)
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; разрешены '
                   'символы латиницы, цифры, дефис и подчёркивание.'),
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title


class Location(PublishedModel):
    name = models.CharField(max_length=256,
                            verbose_name='Название места',)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name


class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'category', 'author', 'location',
        ).filter(
            pub_date__lte=dt.datetime.utcnow(),
            is_published=True,
            category__is_published=True,
        )


class Post(PublishedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок',)
    text = models.TextField(verbose_name='Текст',)
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем'
                   ' — можно делать отложенные публикации.'),
    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации',
                               related_name='posts',)
    location = models.ForeignKey(Location, blank=True,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name='Местоположение',
                                 related_name='posts',)
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name='Категория',
                                 related_name='posts',)
    image = models.ImageField('Фото', upload_to=IMAGE_CONST, blank=True)
    objects = models.Manager()
    post_objects = PostManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    text = models.TextField('Комментарий')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True,)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
