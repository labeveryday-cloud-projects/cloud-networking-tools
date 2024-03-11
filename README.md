# Cloud Networking Automation Tools

This repo consists of several Python scripts that uses the boto3 library to interact with the Amazon Web Services (AWS) Elastic Compute Cloud (EC2) service. 

## SCRIPT_1: AWS Unallocated IP Address Remover

This Python script is designed to get all unallocated IP addresses across all AWS regions and remove them. It utilizes the `boto3` library to interact with the AWS API and perform the necessary operations.

### Features

- Retrieves a list of all available AWS regions
- Identifies unallocated Elastic IP addresses in each region
- Releases (removes) unallocated Elastic IP addresses
- Provides status reporting for each IP address removal operation
- Includes error handling for failed removal operations

### Prerequisites

Before running this script, ensure that you have the following:

- Python 3.x installed
- `boto3` library installed (`pip install boto3`)
- AWS credentials configured with appropriate permissions to describe and release Elastic IP addresses

### Usage

1. Clone or download the repository containing the script.
2. Open a terminal or command prompt and navigate to the directory containing the script.
3. Run the script with `python get_remove_unassociated_eip.py`.

### Functions

The script contains the following functions:

- `get_all_regions()`: This function retrieves a list of all available AWS regions using the `boto3` library.

- `get_unallocated_ids(region: str)`: This function takes a region name as input and returns a list of unallocated IP address allocation IDs for that region.

- `remove_unassigned_ips(region: str, allocated_id: str)`: This function takes a region name and an allocation ID as input. It attempts to release (remove) the specified IP address using the `boto3` library. It returns a dictionary containing the status of the operation (success or failure), the allocation ID, and an error message (if applicable).

- `main()`: This is the main function that orchestrates the execution of the script. It calls the other functions to retrieve the list of regions, get unallocated IP addresses for each region, and remove them.

## Note

This script assumes that you have the necessary AWS credentials configured and permissions to describe and release Elastic IP addresses. Make sure to review and comply with AWS best practices and security guidelines before running this script in a production environment.

___

## SCRIPT_2: EC2 Instance Security Group Analyzer

This Python script uses the boto3 library to interact with the Amazon Web Services (AWS) Elastic Compute Cloud (EC2) service. It retrieves information about all EC2 instances across all AWS regions and their associated security groups, along with the inbound and outbound rules for each security group.

### Features

- Lists all available AWS regions
- Retrieves all EC2 instances in each region
- Retrieves security group IDs associated with each instance
- Retrieves inbound and outbound rules for each security group
- Prints the instance ID, security group ID, and rules for each security group

### Usage

1. Clone or download the repository.
2. Run the script using `python script.py`.

The script will output the following information:

```
Region: <region_name>
Instance: <instance_id> SG: <security_group_id>
<security_group_rule_1>
<security_group_rule_2>
...

Instance: <instance_id> SG: <security_group_id>
<security_group_rule_1>
<security_group_rule_2>
...

...
```

### Functions

- `main()`: The main function that coordinates the execution of the script.
- `get_all_regions()`: Retrieves a list of all available AWS regions.
- `get_all_instances(region)`: Retrieves a list of all EC2 instances in the specified region.
- `get_instance_sg(instance_id, region)`: Retrieves the security group IDs associated with the specified instance in the specified region.
- `get_sg_rules(security_group_id, region)`: Retrieves the inbound and outbound rules for the specified security group in the specified region.

## Notes

- Make sure you have the appropriate AWS credentials configured on your system or in the script.
- The script assumes that you have the necessary permissions to access EC2 instances and security groups across all regions.
- Modify the script as needed to fit your specific use case or requirements.
