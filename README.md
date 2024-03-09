# EC2 Instance Security Group Analyzer

This Python script uses the boto3 library to interact with the Amazon Web Services (AWS) Elastic Compute Cloud (EC2) service. It retrieves information about all EC2 instances across all AWS regions and their associated security groups, along with the inbound and outbound rules for each security group.

## Features

- Lists all available AWS regions
- Retrieves all EC2 instances in each region
- Retrieves security group IDs associated with each instance
- Retrieves inbound and outbound rules for each security group
- Prints the instance ID, security group ID, and rules for each security group

## Prerequisites

- Python 3.x
- AWS account with appropriate permissions
- Boto3 library installed (`pip install boto3`)

## Usage

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

## Functions

- `main()`: The main function that coordinates the execution of the script.
- `get_all_regions()`: Retrieves a list of all available AWS regions.
- `get_all_instances(region)`: Retrieves a list of all EC2 instances in the specified region.
- `get_instance_sg(instance_id, region)`: Retrieves the security group IDs associated with the specified instance in the specified region.
- `get_sg_rules(security_group_id, region)`: Retrieves the inbound and outbound rules for the specified security group in the specified region.

## Notes

- Make sure you have the appropriate AWS credentials configured on your system or in the script.
- The script assumes that you have the necessary permissions to access EC2 instances and security groups across all regions.
- Modify the script as needed to fit your specific use case or requirements.

```

This README provides an overview of the script's purpose, features, prerequisites, usage instructions, function descriptions, and notes. It should help users understand the script's functionality and how to run it on their systems.