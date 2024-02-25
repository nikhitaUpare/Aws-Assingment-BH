import boto3

def route53():

    ec2 = boto3.client('ec2')

    # Create a VPC
    vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc['Vpc']['VpcId']

    # Create an Internet Gateway
    igw = ec2.create_internet_gateway()
    igw_id = igw['InternetGateway']['InternetGatewayId']

    # Attach the Internet Gateway to the VPC
    ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

    # Create Public Subnet
    public_subnet = ec2.create_subnet(CidrBlock='10.0.0.0/24', VpcId=vpc_id ,  AvailabilityZone='us-east-1a')
    public_subnet_id = public_subnet['Subnet']['SubnetId']

    # Create Private Subnets
    private_subnet1 = ec2.create_subnet(CidrBlock='10.0.10.0/24', VpcId=vpc_id, AvailabilityZone='us-east-1a')
    private_subnet_id1 = private_subnet1['Subnet']['SubnetId']

    private_subnet2 = ec2.create_subnet(CidrBlock='10.0.11.0/24', VpcId=vpc_id, AvailabilityZone='us-east-1a')
    private_subnet_id2 = private_subnet2['Subnet']['SubnetId']

    # Create Route Table for Public Subnet
    public_subnet_routetable = ec2.create_route_table(VpcId=vpc_id)
    public_route_table_id = public_subnet_routetable['RouteTable']['RouteTableId']

    # Add Routes to Public Route Table
    public_subnet_routetable.create_route(RouteTableId=public_route_table_id, DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)


    # Create Route Table for Private Subnets1
    private_subnet_routetable1 = ec2.create_route_table(VpcId=vpc_id)
    private_route_table_id = private_subnet_routetable1['RouteTable']['RouteTableId']

    # Create Route Table for Private Subnets2
    private_subnet_routetable2 = ec2.create_route_table(VpcId=vpc_id)
    private_route_table_id = private_subnet_routetable2['RouteTable']['RouteTableId']

    # Associate Public Subnet with Public Route Table
    ec2.associate_route_table(RouteTableId=public_route_table_id, SubnetId=public_subnet_id)

    # Associate Private Subnets with Private Route Table
    ec2.associate_route_table(RouteTableId=private_route_table_id, SubnetId=private_subnet_id1)
    ec2.associate_route_table(RouteTableId=private_route_table_id, SubnetId=private_subnet_id2)

    # Create Security Group for App EC2 Instance
    security_group1 = ec2.create_security_group(
        GroupName='MyAppSecurityGroup',
        Description='Security group for App EC2 instance',
        VpcId=vpc_id
    )
    app_security_group_id = security_group1['GroupId']

    # Allow SSH from 0.0.0.0/0
    ec2.authorize_security_group_ingress(
        GroupId=app_security_group_id,
        IpPermissions=[
                {
                    'IpProtocol':'tcp',
                    'FromPort':22,
                    'ToPort':22,
                    'IpRanges':[{'CidrIp':'0.0.0.0/0'}]
                }
            ]
    )

    # Allow ICMP IPv4 from 192.168.0.0/16
    ec2.authorize_security_group_ingress(
        GroupId=app_security_group_id,
        IpPermissions=[
                {
                    'IpProtocol':'icmp',
                    'FromPort':-1,
                    'ToPort':-1,
                    'IpRanges':[{'CidrIp':'192.168.0.0/16'}]
                }
            ]
    )

    #create ec2 instance
    ec2.run_instances(
    ImageId='ami-id',
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    SubnetId=public_subnet.id,
    SG_ID=app_security_group_id
    )

    # Create Virtual Private Gateway
    vgw = ec2.create_vpn_gateway(
        AvailabilityZone='us-east-1a',
        Type='ipsec.1'
        [
        {
            'ResourceType': 'vpn-gateway',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'MyVpnGateway'
                },
            ]
        },
    ],
        )
    vgw_id = vgw['VpnGateway']['VpnGatewayId']

    # Attach Virtual Private Gateway to VPC
    ec2.attach_vpn_gateway(VpcId=vpc_id,
                            VpnGatewayId=vgw_id)

    # Create Customer Gateway
    cgw = ec2.create_customer_gateway(
        BgpAsn=65000,
        PublicIp='11.11.11.11',
        Type='ipsec.1',
        TagSpecifications=[
        {
            'ResourceType': 'customer-gateway',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'MyCustomerGateway'
                },
            ]
        },
    ],
    )
    cgw_id = cgw['CustomerGateway']['CustomerGatewayId']

    # Create Site-to-Site VPN Connection
    vpn_connection = ec2.create_vpn_connection(
        CustomerGatewayId='cgw_id',
        VpnGatewayId='vgw_id',
        Type='ipsec.1',
        Options={
            'StaticRoutesOnly': True,
            'TunnelInsideIpVersion': 'ipv4',
                'TunnelOptions':[
                    {
                        'TunnelInsideCidr':'198.162.0.0/16',
                        'PreSharedKey': 'pre_shared_key'
                    }
                ]
        }
    )
    vpn_connection_id = vpn_connection['VpnConnection']['VpnConnectionId']

    ec2.enable_vgw_route_propagation(
        GatewayId='vgw_id',
        RouteTableId='route_table_pub_subnet_id',
    )
    # Create VPN Connection
    ec2.create_tags(Resources=[vpn_connection_id], Tags=[{'Key': 'Name', 'Value': 'Site-to-Site-VPN'}])

    # Enable DNS resolution and DNS hostname for VPC
    ec2.modify_vpc_attribute(VpcId=vpc_id, 
                             EnableDnsSupport={'Value': True})
    ec2.modify_vpc_attribute(VpcId=vpc_id, 
                             EnableDnsHostnames={'Value': True}, VpcId='vpc_id',)

    # Create Private Hosted Zone
    route53 = boto3.client('route53')
    private_hosted_zone = route53.create_hosted_zone(
        Name='cloud.com',
        VPC={'VPCRegion': 'us-east-1' ,'VPCId': vpc_id, 'SubnetIds': [private_subnet_id1, private_subnet_id2]}
    )
    private_hosted_zone_id = private_hosted_zone['HostedZone']['Id']

    #attach private hosted zone to vpc
    route53.associate_vpc_with_hosted_zone(
        HostedZoneId='string',
        VPC={
            'VPCRegion': 'us-east-1',
            'VPCId': 'vpc_id'
        }
    )


    # Create A record with name app.cloud.com
    record = route53.change_resource_record_sets(
        HostedZoneId=private_hosted_zone_id,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': 'app.cloud.com',
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [{'Value': 'Private IP of EC2 Instance'}]
                    }
                }
            ]
        }
    )

    # Create Security Group for Route 53 Resolver Inbound Endpoint
    security_group_inbound = ec2.create_security_group(
        GroupName='Route53ResolverInboundSG',
        Description='Security group for Route 53 Resolver Inbound Endpoint',
        VpcId=vpc_id
    )
    route53_inbound_sg_id = security_group_inbound['GroupId']

    # Allow DNS (UDP 53) from on-premise network 192.168.0.0/16
    ec2.authorize_security_group_ingress(
        GroupId=route53_inbound_sg_id,
        IpPermissions=[
                {
                    'IpProtocol':'udp',
                    'FromPort':53,
                    'ToPort':53,
                    'IpRanges':[{'CidrIp':'192.168.0.0/16'}]
                }
            ]
    )

    # Create Route 53 Resolver Inbound Endpoint
    route53resolver = boto3.client('route53resolver')
   
    route53resolver.create_resolver_endpoint(
        CreatorRequestId='String',
        SecurityGroupIds=[
            'route53_inbound_sg_id',
        ],
        Direction='INBOUND',
        IpAddresses=[
            {
                'SubnetId': 'private_subnet_id1',
            },
        ],
    )

    route53resolver.create_resolver_endpoint(
        CreatorRequestId='String',
        SecurityGroupIds=[
            'route53_inbound_sg_id',
        ],
        Direction='INBOUND',
        IpAddresses=[
            {
                'SubnetId': 'private_subnet_id2',
            },
        ],
    )


    # Create Security Group for Route 53 Resolver Outbound Endpoint
    security_group_outbound = ec2.create_security_group(
        GroupName='Route53ResolverOutboundSG',
        Description='Security group for Route 53 Resolver Outbound Endpoint',
        VpcId=vpc_id
    )
    route53_outbound_sg_id = security_group_outbound['GroupId']

    # Allow DNS (UDP 53) to on-premise network 192.168.0.0/16
    ec2.authorize_security_group_ingress(
        GroupId=route53_outbound_sg_id,
        IpPermissions=[
                {
                    'IpProtocol':'udp',
                    'FromPort':53,
                    'ToPort':53,
                    'IpRanges':[{'CidrIp':'192.168.0.0/16'}]
                }
            ]
    )

    # Create Route 53 Resolver Outbound Endpoint
    route53resolver.create_resolver_endpoint(
        CreatorRequestId='String',
        SecurityGroupIds=[
            'route53_outbound_sg_id',
        ],
        Direction='OUTBOUND',
        IpAddresses=[
            {
                'SubnetId': 'private_subnet_id1',
            },
        ],
    )

    route53resolver.create_resolver_endpoint(
        CreatorRequestId='String',
        SecurityGroupIds=[
            'route53_outbound_sg_id',
        ],
        Direction='OUTBOUND',
        IpAddresses=[
            {
                'SubnetId': 'private_subnet_id2',
            },
        ],
    )
