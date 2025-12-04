from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
)
from constructs import Construct

class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB Table for Events
        events_table = dynamodb.Table(
            self, "EventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # Change to RETAIN for production
            point_in_time_recovery=True,
        )
        
        # Lambda Layer for dependencies
        dependencies_layer = lambda_.LayerVersion(
            self, "DependenciesLayer",
            code=lambda_.Code.from_asset(
                "../backend",
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_12.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output/python"
                    ],
                }
            ),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_12],
            description="FastAPI and dependencies",
            compatible_architectures=[lambda_.Architecture.ARM_64]
        )
        
        # Lambda Function for FastAPI
        api_lambda = lambda_.Function(
            self, "EventsApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="main.handler",
            code=lambda_.Code.from_asset("../backend"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(30),
            memory_size=512,
            architecture=lambda_.Architecture.ARM_64,
            environment={
                "EVENTS_TABLE_NAME": events_table.table_name,
            }
        )
        
        # Grant Lambda permissions to access DynamoDB
        events_table.grant_read_write_data(api_lambda)
        
        # API Gateway REST API
        api = apigateway.LambdaRestApi(
            self, "EventsApi",
            handler=api_lambda,
            proxy=True,
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["*"],
                allow_credentials=True,
            ),
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            )
        )
