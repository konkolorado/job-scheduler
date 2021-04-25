import aws_cdk.aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticache as ec
from aws_cdk import core as cdk


class JobSchedulerStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "VPC", max_azs=1)
        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)
        fargate_task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef", memory_limit_mib=512, cpu=256
        )

        api = fargate_task_definition.add_container(
            "api",
            image=ecs.ContainerImage.from_asset("."),
            command=["make api"],
            port_mappings=[{"containerPort": 8000}],
            logging=ecs.LogDrivers.aws_logs(stream_prefix="api"),
        )
        scheduler = fargate_task_definition.add_container(
            "scheduler",
            image=ecs.ContainerImage.from_asset("."),
            command=["make scheduler"],
            logging=ecs.LogDrivers.aws_logs(stream_prefix="scheduler"),
        )
        runner = fargate_task_definition.add_container(
            "runner",
            image=ecs.ContainerImage.from_asset("."),
            command=["make runner"],
            logging=ecs.LogDrivers.aws_logs(stream_prefix="runner"),
        )
        service = ecs.FargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=fargate_task_definition,
            desired_count=1,
            circuit_breaker={"rollback": True},
        )
        redis = ec.CfnCacheCluster(
            self,
            "Redis",
            cache_node_type="cache.t2.micro",
            engine="redis",
            num_cache_nodes=1,
        )


"""
pain med - 1 capsule evey 8 to 10 hours
    - she got one dose at 1230 / 45 next is about at 8

muscle relaxant
    - 1 / 2 table every 8 hours
    
anti inflammatory
    - safe for dogs ibruprofen
    - with food
    - might not eat or vomit, discontinue
    - if shes eating she can have this one

potato + sweet potato
chicken + rice
"""
