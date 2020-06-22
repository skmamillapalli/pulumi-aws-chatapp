from pulumi_aws import ec2, config
from pulumi import ResourceOptions, Config

def setup_vpc():
    # Create a VPC
    vpc_config = Config().require_object("vpc_config")
    vpc = ec2.Vpc("chatapp-vpc", 
        cidr_block= vpc_config['cidr'],
        enable_dns_hostnames=True,
        enable_dns_support=True)

    # Create public subnet to place NGW
    public_subnet = ec2.Subnet(
        "PublicSubnet",
        vpc_id=vpc.id,
        cidr_block=vpc_config['public_subnet_cidr'],
        availability_zone="ap-southeast-1a"
    )

    # Create private subnets 1 and 2 for rds and redis clusters
    private_subnet_1 = ec2.Subnet(
        "PrivateSubnet1",
        vpc_id=vpc.id,
        cidr_block=vpc_config['private_subnet_1_cidr'],
        availability_zone="ap-southeast-1b"
    )

    private_subnet_2 = ec2.Subnet(
        "PrivateSubnet2",
        vpc_id=vpc.id,
        cidr_block=vpc_config['private_subnet_2_cidr'],
        availability_zone="ap-southeast-1c"
    )

    # Create internet gateway
    inet_gw = ec2.InternetGateway(
        "inet-gateway",
        vpc_id=vpc.id,
    )

    # create NAT gateway
    elastic_ip = ec2.Eip("eip1", opts=ResourceOptions(delete_before_replace=True))
    nat_gw = ec2.NatGateway(
        "nat-gateway",
        subnet_id=public_subnet.id,
        allocation_id=elastic_ip.id
    )

    # Create private routed route-table
    private_subnet_route_table = ec2.RouteTable(
        "privatesubnetroutetable",
        routes=[
         {
                "cidr_block": "0.0.0.0/0",
                "gateway_id": nat_gw.id
         }
        ],
        vpc_id=vpc.id
    )

    # Create public routed route-table
    public_subnet_route_table = ec2.RouteTable(
        "publicsubnetroutetable",
        routes=[
         {
                "cidr_block": "0.0.0.0/0",
                "gateway_id": inet_gw.id
         }
        ],
        vpc_id=vpc.id
    )

    # Attach route tables to subnets
    ec2.RouteTableAssociation(
        "PrivateSubnetRT1",
        subnet_id=private_subnet_1.id,
        route_table_id=private_subnet_route_table.id
    )
    ec2.RouteTableAssociation(
        "PrivateSubnetRT2",
        subnet_id=private_subnet_2.id,
        route_table_id=private_subnet_route_table.id
    )
    ec2.RouteTableAssociation(
        "PublicSubnetRT",
        subnet_id=public_subnet.id,
        route_table_id=public_subnet_route_table.id
    )
    return dict(vpc=vpc, private_subnets=[private_subnet_1, private_subnet_2])

def create_firewall_rules(vpc):
    # Create lambda, rds, redis security groups to allow traffic between them
    lambda_sg = ec2.SecurityGroup("lambdaSG",
        description="Lambda security group",
        egress=[{
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
            "protocol": -1
        }],
        vpc_id=vpc.id)

    # Create SG for redis, rds
    rds_sg = ec2.SecurityGroup("AllowLambdaToRdsIngress",
        description="Rds Security Group",
        vpc_id=vpc.id,
        ingress=[{
            "from_port": 3306,
            "to_port": 3306,
            "protocol": "tcp",
            "security_groups": [lambda_sg.id],
        }],
        egress=[{
            "from_port": 0,
            "to_port": 0,
            "protocol": -1,
            "cidr_blocks": ["0.0.0.0/0"],
        }],
    )
    redis_sg = ec2.SecurityGroup("AllowLambdaToRedisIngress",
        description="Redis security group",
        vpc_id=vpc.id,
        ingress=[{
            "from_port": 6379,
            "to_port": 6379,
            "protocol": "tcp",
            "security_groups": [lambda_sg.id],
        }],
        egress=[{
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
            "protocol": -1
        }],
    )
    return {
        "lambda_sg": lambda_sg,
        "redis_sg": redis_sg,
        "rds_sg": rds_sg
    }