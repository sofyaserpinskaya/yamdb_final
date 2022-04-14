from datetime import datetime as dt

from django.shortcuts import get_object_or_404

from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User

YEAR_VALIDATION_ERROR = 'Год выпуска не может быть больше текущего.'
CATEGORY_VALIDATION_ERROR = (
    'Данной категории {category} нет в БД.'
)
GENRE_VALIDATION_ERROR = 'Данного жанра {genre} нет в БД.'
USERNAME_VALIDATION_ERROR = 'Нельзя использовать "me".'
REVIEW_VALIDATION_ERROR = (
    'Нельзя добавлять больше одного отзыва на произведение.'
)


class NameAndSlugSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CategorySerializer(NameAndSlugSerializer):

    class Meta(NameAndSlugSerializer.Meta):
        model = Category


class GenreSerializer(NameAndSlugSerializer):

    class Meta(NameAndSlugSerializer.Meta):
        model = Genre


class TitleGetSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField()
    category = CategorySerializer(many=False)
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = ('__all__',)

    def get_rating(self, obj):
        return obj.rating or None


class TitlePostPatchDeleteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )

    def validate_year(self, value):
        if value > dt.today().year:
            raise serializers.ValidationError(YEAR_VALIDATION_ERROR)
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        author = self.context['request'].user
        if Review.objects.filter(author=author, title=title):
            raise serializers.ValidationError(REVIEW_VALIDATION_ERROR)
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class ValidateUsernameMixin:

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(USERNAME_VALIDATION_ERROR)
        return value


class UserSerializer(ValidateUsernameMixin, serializers.ModelSerializer):

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class AccountSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        proxy = True
        read_only_fields = ('role',)


class SignupSerializer(ValidateUsernameMixin, serializers.Serializer):
    email = serializers.EmailField(
        required=True
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+',
        required=True
    )


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True, max_length=150
    )
    confirmation_code = serializers.CharField(
        required=True, max_length=150
    )

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
