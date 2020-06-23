# pulumi-aws-chatapp
A serverless chat app deployed on aws with pulumi

# How to run
*venv is only to faciliate easy setup with below steps. It avoids setting up new pulumi project and integration with changes in this repo. Without venv, please setup pulumi project and update files with changes in this repository*
1. ## Install pulumi and setup aws config
    Follow instructions [here](https://www.pulumi.com/docs/get-started/install/)

2. ## Set up project
   ```
    git clone https://github.com/skmamillapalli/pulumi-aws-chatapp.git
    cd pulumi-aws-chatapp
   ```
    
3. ## Setup config details
   ```
    pulumi config set --path vpc_config.cidr 172.3.0.0/16
    pulumi config set --path vpc_config.pub_subnet_cidr 172.3.9.0/24
    pulumi config set --path vpc_config.private_subnet_1_cidr 172.3.10.0/24 
    pulumi config set --path vpc_config.private_subnet_2_cidr 172.3.11.0/24
    pulumi config set --secret --path rds_config.password password
    pulumi config set --path rds_config.username admin
    pulumi config set --path rds_config.database_name chatapp
    pulumi config set --path stage_config.stage dev
   ```
4. ## Deploy stack
   ```
    pulumi up
   ```
   
   *or if you are doing a standalone installation, run*
   ```pulumi new aws-python``` *then setup config as in #3, copy changes in this repo to your project followed by* ```pulumi up```
# Using App
### Use the websocket url(from pulumi Outputs) to connect to API(use a client like wscat)
   ```
   wscat -c wss://randomid9.execute-api.ap-southeast-1.amazonaws.com/Dev -H "username:Sid"
   ````
### Once connection is established, messages can be sent/received over connection
   ```
   {"action":"send", "to":"Sid", "message":"Hey!!"}
   "Hey!!"
   ```
## Errors
   If you run into 4xx, please watch out for header string "username:Sid". 
   
    
    
    
