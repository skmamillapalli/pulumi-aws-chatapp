# pulumi-aws-chatapp
A serverless chat app deployed on aws with pulumi

# How to run
1. ## Set up project
   ```
    git clone https://github.com/skmamillapalli/pulumi-aws-chatapp.git
    cd pulumi-aws-chatapp
   ```
    
2. ## Setup config details
   ```
    pulumi config set --path vpc_config.cidr 172.3.0.0/16
    pulumi config set --path vpc_config.pub_subnet_cidr 172.3.9.0/24
    pulumi config set --path vpc_config.private_subnet_1_cidr 172.3.10.0/24 
    pulumi config set --path vpc_config.private_subnet_2_cidr 172.3.11.0/24 
    pulumi config set --secret --path rds_config.password <password>
    pulumi config set --path rds_config.username admin              
    pulumi config set --path rds_config.database_name chatapp
    pulumi config set --path stage_config.stage dev
   ```
3. ## Deploy stack
   ```
    pulumi up
   ```

*venv is only to faciliate easy setup. Avoids setting up new pulumi project and integration with these changes.*
    
