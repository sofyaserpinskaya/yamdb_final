from datetime import date
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


def year():
    return date.today().year


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(
        choices=ROLE_CHOICES,
        default=USER,
        max_length=max(len(role) for role, _ in ROLE_CHOICES)
    )
    confirmation_code = models.CharField(
        blank=True, null=True, max_length=150
    )

    @property
    def is_admin(self):
        return (
            self.is_active
            and self.role == ADMIN
            or self.is_staff
        )

    @property
    def is_moderator(self):
        return (
            self.is_active
            and self.role == MODERATOR
        )

    class Meta():
        ordering = ('username',)


class CategoryGenreModel(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta():
        abstract = True
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Category(CategoryGenreModel):
    pass


class Genre(CategoryGenreModel):
    pass


class Title(models.Model):
    name = models.TextField()
    year = models.IntegerField(
        validators=[
            MaxValueValidator(limit_value=year)
        ]
    )
    description = models.TextField(null=True, blank=True)
    genre = models.ManyToManyField(
        Genre,
        related_name="titles"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles"
    )

    class Meta():
        ordering = ('name',)

    def __str__(self):
        return self.name


class ReviewCommentModel(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='%(class)s'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta():
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return (f'{self.text[:15]} {self.author.username} {self.pub_date}')


class Review(ReviewCommentModel):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta(ReviewCommentModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]


class Comment(ReviewCommentModel):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
