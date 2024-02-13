import boto3
ec2_client = boto3.client('ec2')

#Create VPC

vpc=ec2_client.create_vpc(CidrBlock='10.0.0.0/16')
vpc_id=vpc['Vpc']['VpcId']

#create public and private Subnet

public_subnet1 = ec2_client.create_subnet(CidrBlock='10.0.0.0/24', Availabilityzone='us-east-1a', VpcId=vpc_id)
public_subnet1_id = public_subnet1['Subnet']['SubnetId']

public_subnet2 = ec2_client.create_subnet(CidrBlock='10.0.1.0/24', Availabilityzone='us-east-1a', VpcId=vpc_id)
public_subnet2_id = public_subnet2['Subnet']['SubnetId']

private_subnet1 = ec2_client.create_subnet(CidrBlock='10.0.11.0/24', Availabilityzone='us-east-1a', VpcId=vpc_id)
private_subnet1_id = private_subnet1['Subnet']['SubnetId']

private_subnet2 = ec2_client.create_subnet(CidrBlock='10.0.12.0/24', Availabilityzone='us-east-1a', VpcId=vpc_id)
private_subnet2_id = private_subnet2['Subnet']['SubnetId']

#create Internet Gateway

igw = ec2_client.create_internet_gateway()
igw_id = igw['InternetGateway']['InternetGatewayId']
vpc.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

#create route table for public subnet1 and public subnet2

route_table_pubsub1 = ec2_client.create_route_table(VpcId=vpc_id)
route_table_pubsub1_id = route_table_pubsub1['RouteTable']['RouteTableId']
route_table_pubsub1.associate_with_subnet(subnetId=public_subnet1_id)
# Add a route to the internet via the IGW
ec2_client.create_route(RouteTableId = route_table_pubsub1_id, DestinationCidrBlock = '0.0.0.0/0', GatewayId = igw_id)

route_table_pubsub2 = ec2_client.create_route_table(VpcId = vpc_id)
route_table_pubsub2_id = route_table_pubsub2['RouteTable']['RouteTableId']
route_table_pubsub2.associate_with_subnet(subnetId = public_subnet2_id)
# Add a route to the internet via the IGW
ec2_client.create_route(RouteTableId = route_table_pubsub2_id, DestinationCidrBlock = '0.0.0.0/0', GatewayId = igw_id)

#create Security group

security_group = ec2_client.create_security_group(
    GroupName = 'my security group',
    Description = 'security group for alb attachment',
    VpcId = vpc_id
)

ec2_client.authorize_security_group_ingress(
        GroupId=security_group.id,
        IpPermissions=[
            {
                'IpProtocol':'tcp',
                'FromPort':80,
                'ToPort':80,
                'IpRanges':[{'CidrIp':'0.0.0.0/0'}]
            }
        ]
)


#create ec2 instance

ec2_client.run_instances(
    ImageId='ami-id',
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    SubnetId=private_subnet1_id,
    SG_ID=security_group.id
)

#create function

create_lambda = boto3.client('lambda')

create_lambda.create_function(
    FunctionName='my_lambda_function',
    Runtime='Python3.11',
    Role='lambda_arn'
)

#create Application Load Balancer

elasticloadbalancerv2=boto3.client('ElasticLoadBalancingv2')

apploadbalancer = elasticloadbalancerv2.create_load_balancer(
        Name='my-apploadbalancer',
        Subnets=[private_subnet1,private_subnet2],
        SecurityGroups=[security_group.id],
        Scheme='internet_facing',
        Tags=[
            {
                'Key': 'Name',
                'Value': 'my_apploadbalancer'
            },
        ],
        Type='application',
        IpAddressType='ipv4'
    )

#create target groups

target_group1=elasticloadbalancerv2.create_target_group(
    Name='target_group_1',
    Protocol='HTTP',
    Port=80,
    VpcId=vpc_id,
    TargetType='instance',
    IpAddressType='ipv4'

    )

 

target_group2=elasticloadbalancerv2.create_target_group(
    Name='target_group_2',
    TargetType='lambda',
    IpAddressType='ipv4'

    )

#create listeners for path based routing

elb_listener1=elasticloadbalancerv2.create_listener(
    LoadBalancerArn='elasticloadbalancerv2_arn',
    Protocol='HTTP',
    Port=80,
    DefaultActions=[
        {
        'Type': 'forward',
        'ForwardConfig': {
                'TargetGroups': [
                    {
                        'TargetGroupArn': 'target_group1_arn',
                    },
                ],
        }
        }
    ]   
    )

 #create rules to distribute traffic based on path

rule1=elasticloadbalancerv2.create_rule(
    ListenerArn='listener1_arn',
    Conditions=[
        {
            'Field':'path-pattern',
            'Values':['/user']
        }
    ],
    Priority=1,
    Actions=[
        {
            'Type': 'forward',
            'TargetGroupArn': 'target_group1_arn'
        }
    ]
)

rule1=elasticloadbalancerv2.create_rule(
    ListenerArn='listener1_arn',
    Conditions=[
        {
            'Field':'path-pattern',
            'Values':['/search']
        }
    ],
    Priority=2,
    Actions=[
        {
            'Type': 'forward',
            'TargetGroupArn': 'target_group2_arn'
        }
    ]
    )
