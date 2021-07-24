import aws_cdk.aws_elasticloadbalancingv2 as elbv2
import aws_cdk.aws_route53 as route53
import aws_cdk.aws_route53_targets as route53_targets
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticache as ec
from aws_cdk import core as cdk


class RedisCluster(cdk.Construct):
    # Create a single node ElastiCache cluster and resources:
    # The subnet group is used to choose a subnet and IP addresses for the
    # cache nodes
    # The security group creates a network ACL to prevent all inbound and
    # outbound connections. Later allow connections from the Fargate Service.

    def __init__(self, scope: cdk.Construct, id: str, *, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, id)

        self.subnet_group = ec.CfnSubnetGroup(
            self,
            "ElastiCacheSubnetGroup",
            subnet_ids=[ps.subnet_id for ps in vpc.private_subnets],
            description="ElastiCache Subnet Group",
        )
        self.security_group = ec2.SecurityGroup(
            self, "ElastiCacheSecurityGroup", vpc=vpc, allow_all_outbound=False
        )
        self.redis = ec.CfnCacheCluster(
            self,
            "ElastiCacheCluster",
            cache_node_type="cache.t2.micro",
            auto_minor_version_upgrade=True,
            engine="redis",
            num_cache_nodes=1,
            cache_subnet_group_name=self.subnet_group.ref,
            vpc_security_group_ids=[self.security_group.security_group_id],
        )
        self.endpoint_address = self.redis.attr_redis_endpoint_address


class DNS(cdk.Construct):
    # Create a hosted zone for this project, under which multiple subdomains
    # may live i.e. api.job-scheduler... app.job-scheduler... For this to
    # work the parent zone must exist already and have a valid registered
    # domain name. This allows the API to be hit via a 'friendly' web URL
    # such as api.job-scheduler.uriel.globuscs.info
    # Docs:
    # https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-routing-traffic-for-subdomains.html#dns-routing-traffic-for-subdomains-creating-records
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        *,
        lb: elbv2.ApplicationLoadBalancer,
        **kwargs,
    ):
        super().__init__(scope, id)
        parent_zone_name = kwargs.get("parent_zone_name", "uriel.globuscs.info")
        parent_zone_id = kwargs.get("parent_zone_id", "Z07538033GFYDX485PZSC")
        project_subdomain_name = kwargs.get("project_subdomain_name", "job-scheduler")
        api_subdomain_name = kwargs.get("api_subdomain_name", "api")
        zone_name = f"{project_subdomain_name}.{parent_zone_name}"

        zone = route53.PublicHostedZone(self, "HostedZone", zone_name=zone_name)
        parent_zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            "ParentHostedZone",
            zone_name=parent_zone_name,
            hosted_zone_id=parent_zone_id,
        )
        # Create a record in the parent zone telling it to forward traffic for
        # the job-scheduler domain to the new zone
        route53.ZoneDelegationRecord(
            self,
            "NS",
            zone=parent_zone,
            record_name=project_subdomain_name,
            name_servers=zone.hosted_zone_name_servers or [],
        )
        route53.ARecord(
            self,
            "ARecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(
                route53_targets.LoadBalancerTarget(lb)
            ),
            record_name=api_subdomain_name,
            ttl=cdk.Duration.seconds(300),
        )

        self.api_domain = f"{api_subdomain_name}.{zone_name}"
