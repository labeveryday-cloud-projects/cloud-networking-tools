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

def get_all_regions() -> list:
    """
    Gets all available AWS regions.

    Args:
    None:           This function takes no arguments.
    
    Returns:
    list:           A list containing the name of each region as a string
    """
    ec2 = boto3.client('ec2')
    regions = []
    for region in ec2.describe_regions()['Regions']:
        regions.append(region['RegionName'])
    return regions

def get_unallocated_ids(region: str) -> list:
    """
    Gets unallocated Elastic IP addresses for a region.

    Args:
    region (str):   The AWS region to check for unallocated EIPs

    Returns: 
    list:           A list containing the allocation IDs of any unassociated EIPs  
    """
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_addresses()

    unallocated_ids = []

    for id in response['Addresses']:
        if not id.get('NetworkInterfaceId'):
            unallocated_ids.append(id['AllocationId'])

    return unallocated_ids

def remove_unassigned_ips(region: str, allocated_id: str) -> dict:
    """
    Releases an unallocated Elastic IP address for a region.

    Args:
    region (str):           The AWS region containing the EIP 
    allocated_id (str):     The allocation ID of the EIP to release
    
    Returns:
    dict:                   A dictionary containing either:
        - 'status':         'removed' and 'id': allocation_id if successful  
        - 'status':         'failed', 'id': allocation_id, 'message': error if failed
    """
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
