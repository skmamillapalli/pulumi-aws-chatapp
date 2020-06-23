from pulumi_aws import route53

def create_private_zone(vpc):
    private = route53.Zone("private", vpcs=[{
    "vpc_id": vpc.id
}])
