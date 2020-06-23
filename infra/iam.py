from pulumi_aws import iam

def create_lambda_execution_roles(region, account):
    # Create lambda execution role
    lambda_assume_role_policy = iam.get_policy_document(statements=[{
        "actions": ["sts:AssumeRole"],
        "principals": [{
            "identifiers": ["lambda.amazonaws.com"],
            "type": "Service",
        }],
    }])
    
    lambda_execution_role = iam.Role("sendMessagelambda",
        assume_role_policy=lambda_assume_role_policy.json)
        
    iam.RolePolicy("RolePolicyAttachment",
        role=lambda_execution_role.id,
        policy=f"""{{
        "Version": "2012-10-17",
        "Statement": [
            {{
                "Effect": "Allow",
                "Action": [
                    "ec2:CreateNetworkInterface",
                    "logs:CreateLogStream",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DeleteNetworkInterface",
                    "logs:CreateLogGroup",
                    "logs:PutLogEvents"
                ],
                "Resource": "*"
            }},
            {{
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:{region.name}:{account}:log-group:*"
            }},
            {{
                "Effect": "Allow",
                "Action": "logs:CreateLogGroup",
                "Resource": "arn:aws:logs:{region.name}:{account}:*"
            }},
            {{
                "Effect": "Allow",
                "Action": [
                    "execute-api:ManageConnections",
                    "execute-api:Invoke"
                ],
                "Resource": [
                    "arn:aws:execute-api:{region.name}:{account}:*"
                ]
            }},
            {{
                "Action": "ec2:*",
                "Effect": "Allow",
                "Resource": "*"
            }}
        ]
    }}
    
    """)
    return {
        "role": lambda_execution_role
    }