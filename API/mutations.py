import graphene
from API.authentication import AuthMutation,RefreshMutation



class Mutation(graphene.ObjectType):
    auth = AuthMutation.Field()
    refresh = RefreshMutation.Field()
