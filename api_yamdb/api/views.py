import random

from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

import api_yamdb.settings as settings
from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import (
    AdminOnly, AdminOrReadOnly, AuthorModeratorAdminOrReadOnly
)
from .serializers import (
    AccountSerializer, CategorySerializer, CommentSerializer, GenreSerializer,
    GetTokenSerializer, ReviewSerializer, SignupSerializer, TitleGetSerializer,
    TitlePostPatchDeleteSerializer, UserSerializer
)

SIGNUP_ERROR = '{value} уже занят. Используйте другой {field}.'


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class NameAndSlugViewSet(CreateListDestroyViewSet):
    permission_classes = (AdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(NameAndSlugViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(NameAndSlugViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (AdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return TitleGetSerializer
        return TitlePostPatchDeleteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorModeratorAdminOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorModeratorAdminOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminOnly,)
    serializer_class = UserSerializer
    lookup_field = 'username'
    queryset = User.objects.all()
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = AccountSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        serializer = AccountSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


def generate_code():
    random.seed()
    return str(random.randint(10000, 99999))


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user = User.objects.get_or_create(
                username=username, email=email
            )[0]
        except IntegrityError:
            if User.objects.filter(username=username).exists():
                return Response(
                    SIGNUP_ERROR.format(value=username, field='username'),
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                SIGNUP_ERROR.format(value=email, field='email'),
                status=status.HTTP_400_BAD_REQUEST
            )
        code = generate_code()
        user.confirmation_code = code
        user.save()
        send_mail(
            'confirmation code', code,
            settings.DEFAULT_FROM_EMAIL,
            [email], fail_silently=False
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


def get_tokens_for_user(user):
    access = AccessToken.for_user(user)
    return {
        'access': str(access),
    }


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=request.data.get('username'))
    if user.confirmation_code == request.data.get('confirmation_code'):
        return Response(
            get_tokens_for_user(user), status=status.HTTP_200_OK
        )
    return Response(status=status.HTTP_400_BAD_REQUEST)
