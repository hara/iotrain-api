import graphene
import responder
from graphql import GraphQLError

from halalabs.iotrain import controllers, entities, gateways, motor, usecases

api = responder.API()

loco = entities.Locomotive()
gateway = gateways.MotorGateway(motor.motor())
interactor = usecases.LocomotiveOperateInteractor(loco, gateway)
controller = controllers.LocomotiveController(interactor)


class Direction(graphene.Enum):
    STOP = 0
    FORWARD = 1
    BACKWARD = 2


class Locomotive(graphene.ObjectType):
    direction = Direction()
    speed = graphene.Int()


class OperateLocomotive(graphene.Mutation):
    direction = Direction(required=True)
    speed = graphene.Int(required=True)

    class Arguments:
        direction = Direction()
        speed = graphene.Int()

    def mutate(self, info, direction, speed):
        if speed < 0 or speed > 100:
            raise GraphQLError('speed must be integer between 0 and 100')

        controller.operate({
            'direction': Direction.get(direction).name,
            'speed': speed
        })
        loco.operate(
            direction=entities.Direction(direction),
            speed=entities.Speed(speed))
        return OperateLocomotive(
            direction=loco.direction, speed=loco.speed.value)


class Query(graphene.ObjectType):
    locomotive = graphene.Field(Locomotive)


class Mutation(graphene.ObjectType):
    operate_locomotive = OperateLocomotive.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
view = responder.ext.GraphQLView(api=api, schema=schema)

api.add_route("/graph", view)
