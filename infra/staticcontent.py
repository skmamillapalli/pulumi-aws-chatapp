from pulumi_aws import s3

bucket = s3.Bucket("static-bucket",
    acl="private",
    tags={
        "Environment": "Test",
        "Name": "Chat App Static Content"
    })