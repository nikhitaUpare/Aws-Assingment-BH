import boto3
ec2 = boto3.resource('ec2')

#create vpc

vpc = ec2.create_vpc(CidrBlock = '10.0.0.0/16')

#create subnet

pub_sub1=ec2.create_subnet(CidrBlock='10.0.1.0/24',AvailabiltyZone='us-east-1a')
pub_sub2=ec2.create_subnet(CidrBlock='10.0.2.0/24',AvailabiltyZone='us-east-1a')
pri_sub1=ec2.create_subnet(CidrBlock='10.0.3.0/24',AvailabiltyZone='us-east-1a')


#create an internet gateway and attach to vpc

internetgateway = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayID = internetgateway.id)

#create nat gateway

nat_gateway=ec2.create_nat_gateway(subnetID=pub_sub1.id)

#create a route table and a public route and associate with subnet

route_table_pub1 = vpc.create_route_table()
route_table_pub1.create_route(DestinationCidrBlock='0.0.0.0/0',GatewayID=internetgateway.id)
route_table_pub1.associate_with_subnet(subnetId=pub_sub1.id)

route_table_pub2 = vpc.create_route_table()
route_table_pub2.create_route(DestinationCidrBlock='0.0.0.0/0',GatewayID=internetgateway.id)
route_table_pub2.associate_with_subnet(subnetId=pub_sub2.id)


route_table_pri1 = vpc.create_route_table()
route_table_pri1.create_route(DestinationCidrBlock='0.0.0.0/0',GatewayID=nat_gateway.id)
route_table_pri1.associate_with_subnet(subnetId=pri_sub1.id)


#create ec2 instance associated with security group

pri_instance=ec2.create_instances(ImageId='ami-id', InstanceType='t2.micro', MaxCount=1 ,MinCount=1 ,
                    NetworkInterfaces=[{
                        'SubnetId':pub_sub1.id,
                        'Groups':['security_group_id']
                    }])




pub_intance=ec2.create_instances(ImageId='ami-id', InstanceType='t2.micro', MaxCount=2 ,MinCount=1 ,
                    NetworkInterfaces=[{
                        'SubnetId':pri_sub1.id,
                        'Groups':['security_group_id']
                    }])

sec_group=ec2.create_security_group(GroupName='VPC_DEMO_SG',Description='MY_SG_GROUP')
ec2.authorize_security_group_ingress(GroupID='security_group_id' , 
                                     IpPermissions=[{'IpProtocal' : 'tcp' , 'FromPort' :80 , 'ToPort' :80 , 'IpRanges' :[{'CidrIp':'0.0.0.0/0'}]}])

if __name__=="main":
    create_vpc()
    