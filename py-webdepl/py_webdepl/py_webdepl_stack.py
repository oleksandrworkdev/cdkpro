import os
from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins,
    aws_s3_deployment,
    CfnOutput
)
from constructs import Construct

class PyWebdeplStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        deployment_bucket = s3.Bucket(self, "PyWebDeplBucket")

        ui_dir = os.path.join(os.path.dirname(__file__), "..", "..", "web", "dist")
        if not os.path.exists(ui_dir):
            raise Exception("UI dist folder not found. Please run 'npm run build' in the web directory.")
        
        origin_access_identity = cloudfront.OriginAccessIdentity(self, "PyOriginAccessIdentity")
        deployment_bucket.grant_read(origin_access_identity)
        
        distribution = cloudfront.Distribution(self, "PyWebDeplDistribution",
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=aws_cloudfront_origins.S3Origin(deployment_bucket, origin_access_identity=origin_access_identity)
            )
        )
        
        aws_s3_deployment.BucketDeployment(self, "DeployStaticFiles",
            sources=[aws_s3_deployment.Source.asset(ui_dir)],
            destination_bucket=deployment_bucket
        )
        
        CfnOutput(self, "PyAppURL", value=f"https://{distribution.domain_name}")
        