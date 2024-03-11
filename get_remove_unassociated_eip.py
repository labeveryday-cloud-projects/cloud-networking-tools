import boto3
from pprint import pprint


def main():
    regions = get_all_regions()
    
    # Get a list of all unallocated IP addresses in each region
    for region in regions:
        for id in get_unallocated_ids(region):
            result = input(f"Do you want to remove {id} from region {region}? (y/n) ")
            if result.lower() == "y" or result.lower() == "yes":
                pprint(remove_unassigned_ips(region, id))
            else:
                continue

# Function that gets all regions
def get_all_regions():
    ec2 = boto3.client('ec2')
    regions = []
    for region in ec2.describe_regions()['Regions']:
        regions.append(region['RegionName'])
    return regions

# Create a function that returns a list of unallocated IDs
def get_unallocated_ids(region: str):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_addresses()

    unallocated_ids = []

    for id in response['Addresses']:
        if not id.get('NetworkInterfaceId'):
            unallocated_ids.append(id['AllocationId'])

    return unallocated_ids


# Create a function that removes ip addresses that are not allocated.
def remove_unassigned_ips(region: str, allocated_id: str):
    ec2 = boto3.client('ec2', region_name=region)
    
    try:
        ec2.release_address(AllocationId=allocated_id)
        return {
            "status": "removed", 
            "id": allocated_id
            }
    except Exception as e:

        return {
            "status": "failed",
            "id": allocated_id,
            "message": str(e)
            }


if __name__ == '__main__':
    main()
