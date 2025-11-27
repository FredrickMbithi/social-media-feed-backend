import graphene
import graphql_jwt
from graphql_jwt.shortcuts import get_token
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from graphql_jwt.decorators import login_required
from django.db import transaction


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "date_joined")


class RegisterUser(graphene.Mutation):
    """Register a new user"""

    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    @transaction.atomic
    def mutate(self, info, username, email, password):
        # Validation
        if User.objects.filter(username=username).exists():
            raise Exception("Username already exists")

        if User.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        if len(password) < 6:
            raise Exception("Password must be at least 6 characters")

        # Create user
        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        # Generate token
        token = get_token(user)

        return RegisterUser(user=user, token=token)


class UpdateUser(graphene.Mutation):
    """Update user profile"""

    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String()
        password = graphene.String()

    @login_required
    @transaction.atomic
    def mutate(self, info, email=None, password=None):
        user = info.context.user

        if email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                raise Exception("Email already in use")
            user.email = email

        if password:
            if len(password) < 6:
                raise Exception("Password must be at least 6 characters")
            user.set_password(password)

        user.save()
        return UpdateUser(user=user)


class Mutation(graphene.ObjectType):
    register = RegisterUser.Field()
    update_user = UpdateUser.Field()

    # JWT mutations
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
