import graphene
from posts.queries import Query as PostsQuery
from posts.mutations import Mutation as PostsMutations
from users.mutations import Mutation as UsersMutations


class Query(PostsQuery, graphene.ObjectType):
    """Root Query"""

    pass


class Mutation(UsersMutations, PostsMutations, graphene.ObjectType):
    """Root Mutation"""

    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
