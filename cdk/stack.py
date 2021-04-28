import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticache as ec
from aws_cdk import core as cdk
from aws_cdk.aws_logs import RetentionDays


class JobSchedulerStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "VPC", max_azs=2)

        # Create a single node ElastiCache cluster and resources:
        # The subnet group is used to choose a subnet and IP addresses for the
        # cache nodes
        # The security group creates a network ACL to prevent all inbound and
        # outbound connections
        cache_subnet_group = ec.CfnSubnetGroup(
            self,
            "ElasticCacheSubnetGroup",
            subnet_ids=[ps.subnet_id for ps in vpc.private_subnets],
            description="ElasticCache Subnet Group",
        )
        ec_security_group = ec2.SecurityGroup(
            self, "ElastiCacheSG", vpc=vpc, allow_all_outbound=False
        )
        redis = ec.CfnCacheCluster(
            self,
            "Redis",
            cache_node_type="cache.t2.micro",
            auto_minor_version_upgrade=True,
            engine="redis",
            num_cache_nodes=1,
            cache_subnet_group_name=cache_subnet_group.ref,
            vpc_security_group_ids=[ec_security_group.security_group_id],
        )

        # Create a Task definition that configures the running application,
        # including the containers, their images, their start commands, and the
        # container's environment variables. Only the API container exposes any
        # ports.
        fargate_task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef", memory_limit_mib=512, cpu=256
        )
        api = fargate_task_definition.add_container(
            "api",
            image=ecs.ContainerImage.from_asset("."),
            command=["make", "api"],
            port_mappings=[{"containerPort": 8000}],
            environment={
                "APP_API_HOST": "0.0.0.0",
                "APP_API_PORT": "8000",
                "APP_DATABASE_URL": f"redis://{redis.attr_redis_endpoint_address}",
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="api", log_retention=RetentionDays.ONE_WEEK
            ),
        )
        scheduler = fargate_task_definition.add_container(
            "scheduler",
            image=ecs.ContainerImage.from_asset("."),
            command=["make", "scheduler"],
            environment={
                "APP_DATABASE_URL": f"redis://{redis.attr_redis_endpoint_address}",
                "APP_BROKER_URL": f"redis://{redis.attr_redis_endpoint_address}",
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="scheduler", log_retention=RetentionDays.ONE_WEEK
            ),
        )
        runner = fargate_task_definition.add_container(
            "runner",
            image=ecs.ContainerImage.from_asset("."),
            command=["make", "runner"],
            environment={
                "APP_DATABASE_URL": f"redis://{redis.attr_redis_endpoint_address}",
                "APP_BROKER_URL": f"redis://{redis.attr_redis_endpoint_address}",
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="runner", log_retention=RetentionDays.ONE_WEEK
            ),
        )

        # Create the ECS cluster on which the service will run. Create the ECS
        # service which will instantiate the task definition, manage rolling
        # updates, and associate the Task with the LoadBalancer. Provide the
        # service inbound access to the ElastiCache cluster nodes.
        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)
        service = ecs.FargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=fargate_task_definition,
            desired_count=1,
            circuit_breaker={"rollback": True},
        )
        service.connections.allow_to(ec_security_group, ec2.Port.tcp(6379))

        # Create a LoadBalancer which makes the API container publicly
        # accessible. The LB listens for connections on port 80 and forwards
        # requests onto the API container's exposed port. If there are multiple
        # task definition's the health check gets used to route requests to
        # healthy instances.
        lb = elbv2.ApplicationLoadBalancer(
            self,
            "LB",
            vpc=vpc,
            internet_facing=True,
        )
        listener = lb.add_listener("Listener", port=80)
        target_group = listener.add_targets(
            "ECS2",
            port=80,
            targets=[
                service.load_balancer_target(container_name="api", container_port=8000)
            ],
            health_check=elbv2.HealthCheck(path="/health"),
        )

        # Print the LoadBalancer's public DNS name in the CDK deploy output
        cdk.CfnOutput(
            self,
            "LBDNSName",
            value=lb.load_balancer_dns_name,
            description="DNS Name for the ALB",
        )
