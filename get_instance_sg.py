"""
GET EC2 Instance SGs
"""
import boto3

def main():
    regions = get_all_regions()
    for region in regions:
        print("Region: " + region)
        instances = get_all_instances(region)
        for instance in instances:
            instance_id = instance['Instances'][0]['InstanceId']
            sg_ids = get_instance_sg(instance_id, region)
            for sg_id in sg_ids:
                sg_rules = get_sg_rules(sg_id['GroupId'], region)
                print("Instance: " + instance_id + " SG: " + sg_id['GroupId'])
                for rule in sg_rules['SecurityGroups'][0]['IpPermissions']:
                    print(rule)
                print("\n")
        print("\n")
    return 0


# Get a list all regions
def get_all_regions():
    ec2 = boto3.client('ec2')
    regions = []
    for region in ec2.describe_regions()['Regions']:
        regions.append(region['RegionName'])
    return regions

# Get a list of all instances in a region
def get_all_instances(region):
    ec2 = boto3.client('ec2', region_name=region)
    instances = ec2.describe_instances()['Reservations']
    return instances

# Get a list of all security groups attached to an instance
def get_instance_sg(instance_id, region):
    ec2 = boto3.client(service_name='ec2', region_name=region)
    instance_details = ec2.describe_instances(InstanceIds=[instance_id])
    security_group_ids = instance_details['Reservations'][0]['Instances'][0]['SecurityGroups']
    return security_group_ids

# Get a list of rules in a security group
def get_sg_rules(security_group_id, region):
    ec2 = boto3.client(service_name='ec2', region_name=region)
    sg_rules = ec2.describe_security_groups(GroupIds=[security_group_id])
    return sg_rules


if __name__ == "__main__":
    main()
    exit(0)
