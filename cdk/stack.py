import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_ec2 as ec2
from aws_cdk import core as cdk
from aws_cdk.aws_logs import LogGroup, RetentionDays

from cdk.resources import DNS, RabbitMQ, RedisCluster

# from aws_cdk import aws_ecr as ecr


class JobSchedulerStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cdk.Tags.of(self).add("StackName", construct_id)
        vpc = ec2.Vpc(self, "VPC", max_azs=2)
        redis = RedisCluster(self, "RedisCluster", vpc=vpc)
        rabbitmq = RabbitMQ(self, f"{construct_id}RabbitMQ", vpc=vpc)

        # Create the image repository that will hold our private images
        # Notice that this creates a bootstrap problem - we need the registry
        # to exist before we can push images to it, but we can't push images if
        # if doesn't exist
        # repository = ecr.Repository(
        #    self,
        #    "ImageRepository",
        #    image_scan_on_push=True,
        #    image_tag_mutability=ecr.TagMutability.IMMUTABLE,
        # )
        # repository.add_lifecycle_rule(max_image_age=cdk.Duration.days(30))

        # Create a Task definition that configures the running application,
        # including the containers, their images, their start commands, and the
        # container's environment variables. Only the API container exposes any
        # ports.

        log_group = LogGroup(
            self,
            construct_id,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            retention=RetentionDays.ONE_WEEK,
            log_group_name=f"{construct_id}LogGroup",
        )
        fargate_task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef", memory_limit_mib=512, cpu=256
        )
        api = fargate_task_definition.add_container(
            "api",
            image=ecs.ContainerImage.from_asset(".", target="prod"),
            command=["just", "api"],
            port_mappings=[ecs.PortMapping(container_port=8000)],
            environment={
                "APP_API_HOST": "0.0.0.0",
                "APP_API_PORT": "8000",
                "APP_DATABASE_URL": f"redis://{redis.endpoint_address}",
                "APP_LOGGING_LEVEL": "debug",
                "APP_LOGGING_FORMAT": "json",
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="api", log_group=log_group),
        )
        scheduler = fargate_task_definition.add_container(
            "scheduler",
            image=ecs.ContainerImage.from_asset(".", target="prod"),
            command=["just", "scheduler"],
            environment={
                "APP_DATABASE_URL": f"redis://{redis.endpoint_address}",
                "APP_CACHE_URL": f"redis://{redis.endpoint_address}",
                "APP_BROKER_URL": f"{rabbitmq.endpoint_address}",
                "APP_BROKER_USERNAME": rabbitmq.templated_secret.secret_value_from_json(
                    "username"
                ).to_string(),
                "APP_BROKER_PASSWORD": rabbitmq.templated_secret.secret_value_from_json(
                    "password"
                ).to_string(),
                "APP_LOGGING_LEVEL": "debug",
                "APP_LOGGING_FORMAT": "json",
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="scheduler", log_group=log_group
            ),
        )
        runner = fargate_task_definition.add_container(
            "runner",
            image=ecs.ContainerImage.from_asset(".", target="prod"),
            command=["just", "runner"],
            environment={
                "APP_DATABASE_URL": f"redis://{redis.endpoint_address}",
                "APP_BROKER_URL": f"{rabbitmq.endpoint_address}",
                "APP_BROKER_USERNAME": rabbitmq.templated_secret.secret_value_from_json(
                    "username"
                ).to_string(),
                "APP_BROKER_PASSWORD": rabbitmq.templated_secret.secret_value_from_json(
                    "password"
                ).to_string(),
                "APP_LOGGING_LEVEL": "debug",
                "APP_LOGGING_FORMAT": "json",
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="runner", log_group=log_group
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
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
        )
        service.connections.allow_to(redis.security_group, ec2.Port.tcp(6379))
        service.connections.allow_to(rabbitmq.security_group, ec2.Port.tcp(5671))

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
            health_check=elbv2.HealthCheck(
                path="/health", interval=cdk.Duration.minutes(2)
            ),
        )

        # Configure the DNS records for the project. This is optional, but if
        # used we can publish a static URL for the service rather than relying
        # on the gross-looking ALB's DNS name
        dns = DNS(self, "Route53DNS", lb=lb)

        cdk.CfnOutput(
            self,
            "APISubdomain",
            value=dns.api_domain,
            description="ALB Hostname for the API",
        )
        cdk.CfnOutput(
            self,
            "LBDNSName",
            value=lb.load_balancer_dns_name,
            description="DNS Name for the ALB",
        )
