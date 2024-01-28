import boto3

def create_vpc_tgw_attachment():
    ec2=boto3.resource('ec2')


    #create vpc
    vpc1=ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc2=ec2.create_vpc(CidrBlock='10.1.0.0/16')
    vpc3=ec2.create_vpc(CidrBlock='10.2.0.0/16')

    #create subnet
    #create public subnet
    public_sub1=vpc1.create_subnet(
        cidrblock='10.0.1.0/24',
        Availabilityzone='us-east-1a'
    )

    #create private subnet
    private_sub1=vpc1.create_subnet(
        cidrblock='10.0.2.0/24',
        Availabilityzone='us-east-1a'
    )

    private_sub2=vpc2.create_subnet(
        cidrblock='10.1.1.0/24',
        Availabilityzone='us-east-2a'
    )

    private_sub3=vpc3.create_subnet(
        cidrblock='10.2.1.0/24',
        Availabilityzone='us-east-3a'
    )

    #create internet gateway
    internet_gateway=ec2.create_internet_gateway()
    vpc1.attach_internet_gateway(InternetGatewayId=internet_gateway.id)


    #create route table for public subnet
    route_table_pubsub1=ec2.create_route_table()
    route_table_pubsub1.associate_with_subnet(SubnetId=public_sub1.id)
    route_table_pubsub1.create_route(
        DestCidrBlock='10.1.0.0/16',
        GatewayId=transit_gateway.id
    )

    #create route table for private subnet
    route_table_prisub1=ec2.create_route_table()
    route_table_prisub1.associate_with_subnet(SubnetId=private_sub1.id)
    route_table_prisub1.create_route(
        DestCidrBlock='10.1.0.0/16',
        GatewayId=transit_gateway.id
    )

    route_table_prisub2=ec2.create_route_table()
    route_table_prisub2.associate_with_subnet(SubnetId=private_sub2.id)
    route_table_prisub2.create_route(
        DestCidrBlock='10.0.0.0/16',
        GatewayId=transit_gateway.id
    )

    route_table_prisub2=ec2.create_route_table()
    route_table_prisub2.associate_with_subnet(SubnetId=private_sub2.id)
    route_table_prisub2.create_route(
        DestCidrBlock='10.2.0.0/16',
        GatewayId=transit_gateway.id
    )

    route_table_prisub3=ec2.create_route_table()
    route_table_prisub3.associate_with_subnet(SubnetId=private_sub3.id)
    route_table_prisub3.create_route_table(
        DestCidrBlock='10.1.0.0/16',
        GatewayId=transit_gateway.id
    )

    #create transit gateway
    transit_gateway=ec2.create_transit_gateway(
        Description='this is transit gateway',
        TagSpecification=[
            {
                'ResourceType':'transit-gateway',
                'Tags': [
                    {
                        'Key': 'anything',
                        'Value': 'anything'
                    },
                ]
            },
        ],
    )

    vpc_transit_gateway_attachment1=ec2.create_transit_gateway_vpc_attachment(
        TransitGatewayId='transit_gateway.id',
        VpcId='vpc1.id',
        SubnetIds=[
            public_sub1.id,
            private_sub1.id
        ],
            TagSpecification=[
                {
                    'ResourceType':'transit_gateway_attachment',
                    'Tags':[
                        {
                            'Key':'anything',
                            'Value':'anything'
                        },
                    ]
                },
            ],
    )

    vpc_transit_gateway_attachment2=ec2.create_transit_gateway_vpc_attachment(
        TransitGatewayId='transit_gateway.id',
        VpcId='vpc2.id',
        SubnetIds=[
            private_sub2.id
        ],
            TagSpecification=[
                {
                    'ResourceType':'transit_gateway_attachment',
                    'Tags':[
                        {
                            'Key':'anything',
                            'Value':'anything'
                        },
                    ]
                },
            ],
    )

    vpc_transit_gateway_attachment3=ec2.create_transit_gateway_vpc_attachment(
        TransitGatewayId='transit_gateway.id',
        VpcId='vpc3.id',
        SubnetIds=[
            private_sub3.id
        ],
            TagSpecification=[
                {
                    'ResourceType':'transit_gateway_attachment',
                    'Tags':[
                        {
                            'Key':'anything',
                            'Value':'anything'
                        },
                    ]
                },
            ],
    )

    if __name__=="main":
        create_vpc_tgw_attachment()
