import boto3

def create_vpc_tgw_attachment():
    ec2=boto3.client('ec2')

    #create vpc

    vpc1=ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc2=ec2.create_vpc(CidrBlock='10.1.0.0/16')
    vpc3=ec2.create_vpc(CidrBlock='10.2.0.0/16')


    #create internet gateway

    internet_gateway=ec2.create_internet_gateway()
    vpc1.attach_internet_gateway(InternetGatewayId=internet_gateway.id)


    #create subnet

    public_subnet1=ec2.create_subnet(CidrBlock='10.0.1.0/24',
                                     Availabilityzone='us-east-1a',
                                     VpcId=vpc1.id)
    private_subnet1=ec2.create_subnet(CidrBlock='10.0.2.0/24'
                                      ,Availabilityzone='us-east-1a',
                                      VpcId=vpc1.id)
    private_subnet2=ec2.create_subnet(CidrBlock='10.1.1.0/24'
                                      ,Availabilityzone='us-east-1a',
                                      VpcId=vpc2.id)
    private_subnet3=ec2.create_subnet(CidrBlock='10.2.1.0/24',
                                      Availabilityzone='us-east-1a'
                                      ,VpcId=vpc3.id)


    #Create Transit Gateway

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



    #create vpc routing table and associate it with subnet

    vpc1_route_table=ec2.create_route_table()
    vpc1_route_table.associate_with_subnet(SubnetId=public_subnet1.id)
    vpc1_route_table.create_route(
        DestinationCidrBlock='10.1.0.0/16',
        GatewayId=transit_gateway.id
    )

    vpc2_route_table=ec2.create_route_table()
    vpc2_route_table.associate_with_subnet(SubnetId=private_subnet2.id)
    vpc2_route_table.create_route(
        DestinationCidrBlock='10.0.0.0/16',
        GatewayId=transit_gateway.id
    )
    vpc2_route_table.create_route(
        DestinationCidrBlock='10.2.0.0/16',
        GatewayId=transit_gateway.id
    )

    vpc3_route_table=ec2.create_route_table()
    vpc3_route_table.associate_with_subnet(SubnetId=private_subnet3.id)
    vpc3_route_table.create_route(
        DestinationCidrBlock='10.1.0.0/16',
        GatewayId=transit_gateway.id
    )

    #transit gateway routetable,attachment creation and association of attachment with routetable

    transit_gateway_routetable_vpc1 = ec2.create_transit_gateway_route_table(
        TransitGatewayId='transit_gateway.id',
        TagSpecifications=[
            {
                'ResourceType': 'transit-gateway_route_table',
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
                public_subnet1.id,
                private_subnet1.id
            ],
                TagSpecification=[
                    {
                        'ResourceType':'transit_gateway-attachment',
                        'Tags':[
                            {
                                'Key':'anything',
                                'Value':'anything'
                            },
                        ]
                    },
                ],
        )
    associate_routetable_with_attachment1=transit_gateway_routetable_vpc1.associate_transit_gateway_route_table(
        TransitGatewayRouteTableId='transit_gateway_routetable_vpc1.id',
        TransitGatewayAttachmentId='vpc_transit_gateway_attachment1.id',
    )



    transit_gateway_routetable_vpc2 = ec2.create_transit_gateway_route_table(
        TransitGatewayId='transit_gateway.id',
        TagSpecifications=[
            {
                'ResourceType': 'transit-gateway_route_table',
                'Tags': [
                    {
                        'Key': 'anything',
                        'Value': 'anything'
                    },
                ]
            },
        ],
        
    )

    vpc_transit_gateway_attachment2=ec2.create_transit_gateway_vpc_attachment(
            TransitGatewayId='transit_gateway.id',
            VpcId='vpc2.id',
            SubnetIds=[
                private_subnet2.id
            ],
                TagSpecification=[
                    {
                        'ResourceType':'transit_gateway-attachment',
                        'Tags':[
                            {
                                'Key':'anything',
                                'Value':'anything'
                            },
                        ]
                    },
                ],
        )
    associate_routetable_with_attachment2=transit_gateway_routetable_vpc2.associate_transit_gateway_route_table(
        TransitGatewayRouteTableId='transit_gateway_routetable_vpc2.id',
        TransitGatewayAttachmentId='vpc_transit_gateway_attachment2.id',
    )



    transit_gateway_routetable_vpc3 = ec2.create_transit_gateway_route_table(
        TransitGatewayId='transit_gateway.id',
        TagSpecifications=[
            {
                'ResourceType': 'transit-gateway_route_table',
                'Tags': [
                    {
                        'Key': 'anything',
                        'Value': 'anything'
                    },
                ]
            },
        ],
        
    )

    vpc_transit_gateway_attachment3=ec2.create_transit_gateway_vpc_attachment(
            TransitGatewayId='transit_gateway.id',
            VpcId='vpc3.id',
            SubnetIds=[
                private_subnet3.id
            ],
                TagSpecification=[
                    {
                        'ResourceType':'transit_gateway-attachment',
                        'Tags':[
                            {
                                'Key':'anything',
                                'Value':'anything'
                            },
                        ]
                    },
                ],
        )
    associate_routetable_with_attachment3=transit_gateway_routetable_vpc3.associate_transit_gateway_route_table(
        TransitGatewayRouteTableId='transit_gateway_routetable_vpc3.id',
        TransitGatewayAttachmentId='vpc_transit_gateway_attachment3.id',
    )


    #propagation of vpc to tgw
    ec2.enable_transit_gateway_route_table_propagation(
        TransitGatewayRoutetableId='transit_gateway_route_table.id',
        TransitGatewayAttachmentId='vpc_transit_gateway_attachment1.id',
    )

    ec2.enable_transit_gateway_route_table_propagation(
        TransitGatewayRoutetableId='transit_gateway_route_table.id',
        TransitGatewayAttachmentId='vpc_transit_gateway_attachment2.id',
    )

    ec2.enable_transit_gateway_route_table_propagation(
        TransitGatewayRoutetableId='transit_gateway_route_table.id',
        TransitGatewayAttachmentId='vpc_transit_gateway_attachment3.id',
    )

    if __name__=="main":
        create_vpc_tgw_attachment()






















