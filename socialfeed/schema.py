import graphene
from posts.queries import Query as PostsQuery
from posts.mutations import Mutation as PostsMutations
from users.mutations import Mutation as UsersMutations


class Query(PostsQuery, graphene.ObjectType):
    """Root Query"""



class Mutation(UsersMutations, PostsMutations, graphene.ObjectType):
    """Root Mutation"""



schema = graphene.Schema(query=Query, mutation=Mutation)
