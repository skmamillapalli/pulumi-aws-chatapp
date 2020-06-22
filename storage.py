from pulumi_aws import elasticache, rds
from pulumi import Config

def create_storage_nodes(subnets, security_groups):

    rds_config = Config().require_object("rds_config")
    redis_sg = security_groups['redis_sg']
    rds_sg = security_groups['rds_sg']

    # Create a redis Subnet Group
    redis_subnet_group = elasticache.SubnetGroup("RedisSubGroup", subnet_ids=[subnet.id for subnet in subnets])

    # To-do: Auth and encryption support

    # Create a redis cluster
    redis_cluster = elasticache.Cluster("redisnode",
        engine="redis",
        engine_version="3.2.10",
        node_type="cache.t2.micro",
        num_cache_nodes=1,
        parameter_group_name="default.redis3.2",
        port=6379,
        subnet_group_name=redis_subnet_group.id,
        security_group_ids=[redis_sg.id]
    )

    rds_subnet_group = rds.SubnetGroup("rdssubgroup", subnet_ids=[subnet.id for subnet in subnets])

    # To-do: Secret managment and get from Config
    rds_username=rds_config["username"]
    rds_password=rds_config["password"]
    rds_database_name=rds_config["database_name"]

    # Create a rds instance
    rds_instance = rds.Instance("default",
        allocated_storage=20,
        engine="mysql",
        engine_version="5.7",
        instance_class="db.t2.micro",
        name=rds_database_name,
        parameter_group_name="default.mysql5.7",
        password=rds_password,
        storage_type="gp2",
        username=rds_username,
        storage_encrypted=True,
        db_subnet_group_name=rds_subnet_group.id,
        vpc_security_group_ids=[rds_sg.id],
        skip_final_snapshot=True
    )
    return {
        "rds": rds_instance,
        "redis": redis_cluster
        }
