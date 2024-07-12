
## Create the VPC Agent

- Name: vpc-agent-assistant
- Description: This is an agent used to test connectivity on AWS.

### Instruction for the Agent:

```
You are an AI assistant specializing in managing and monitoring Virtual Private Clouds (VPCs) on the AWS cloud platform. Your responsibilities include:

1. Listing all VPCs in a given AWS region.
2. Checking if a specific VPC has an Internet Gateway attached to it.
3. Checking if a specific VPC has any NAT Gateways created.
4. Retrieving the route tables associated with a VPC, along with their routes.
5. Gathers AWS billing information and provides suggestions on how to cost optimize. 

When a user requests information about AWS billing and VPCs, you should gather the necessary details by interacting with the appropriate AWS services (EC2) using the provided action groups. Your goal is to provide accurate and relevant information to the user based on their queries.

If you need additional details from the user, such as a VPC ID, feel free to ask follow-up questions politely. Always strive to provide a helpful and informative experience.

Remember to handle any errors or exceptions gracefully and inform the user if you encounter any issues while performing the requested actions.

```

### Create action groups:

1. VPC Action group

- Name: vpc-agent-action-group
- Description: This is the action group for the network automation agents. 

- Action group type: Define with function details

- Action group invocation: Select an existing Lambda function

2. Create action group functions

- Action group function 1 : 
  - Name: list_vpcs
  - Description: List all VPCs in the current region
  - No parameters

- Action group function 2 : 
  - Name: check_internet_gateway
  - Description: Check if a VPC has an Internet Gateway attached
  - Parameters:
    - Name: vpc_id
    - Description: Check if a VPC has an Internet Gateway attached
    - Type: str
    - Required: True

- Action group function 3 :
  - Name: get_route_tables
  - Description: Get route tables that are associated with a VPC. 
  - Parameters:
    - Name: vpc_id
    - Description: Get routes that have been created in a VPC.
    - Type: str
    - Required: True

- Action group function 4 :
  - Name: check_nat_gateway
  - Description: Check if a VPC has 1 or more nat gateways
  - Parameters:
    - Name: vpc_id
    - Description: Check if VPC has any NAT gateways.
    - Type: str
    - Required: True

### Create the modify the lambda

1. Update the code


```python
import os
import json
import boto3


def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    
    def listVpcs():
        ec2 = boto3.client('ec2')
        
        response = ec2.describe_vpcs()
        
        vpcs = []
        for vpc in response['Vpcs']:
            vpcs.append({
                'VpcId': vpc['VpcId']
            })
        
        return {
            'vpcs': vpcs,
            "region": os.environ["AWS_REGION"]
        }

    def check_internet_gateway(vpc_id):
        ec2 = boto3.client('ec2')
        
        response = ec2.describe_internet_gateways(
            Filters=[
                {
                    'Name': 'attachment.vpc-id',
                    'Values': [vpc_id]
                }
            ]
        )
        
        internet_gateways = []
        for ig in response['InternetGateways']:
            internet_gateways.append({
                'InternetGatewayId': ig['InternetGatewayId'],
                'AttachedToVpc': vpc_id in [att['VpcId'] for att in ig['Attachments']]
            })
        
        return {
            'internetGateways': internet_gateways
        }
    
    def check_nat_gateway(vpc_id):
        ec2 = boto3.client('ec2')
        
        response = ec2.describe_nat_gateways(
)
        
        nat_gateways = []
        for natgw in response['NatGateways']:
            if natgw['VpcId'] == vpc_id:
                nat_gateways.append({
                    'NatGatewayId': natgw['NatGatewayId'],
                    'AttachedToVpc': natgw['VpcId'],
                    'PublicIp': natgw['NatGatewayAddresses'][0]['PublicIp'],
                    'SubnetId': natgw['SubnetId']
                })
        
        return {
            'NatGateways': nat_gateways
        }
    
    def get_route_tables(vpc_id):
        
        ec2 = boto3.client('ec2')
        
        response = ec2.describe_route_tables(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [vpc_id]
                }
            ]
        )
        
        route_tables = []
        for rt in response['RouteTables']:
            routes = []
            for route in rt['Routes']:
                route_data = {
                    'DestinationCidrBlock': route.get('DestinationCidrBlock'),
                    **{k: v for k, v in [
                        ('GatewayId', route.get('GatewayId')),
                        ('NatGatewayId', route.get('NatGatewayId'))
                    ] if v is not None}
                }
                routes.append(route_data)
            
            route_tables.append({
            'RouteTableId': rt['RouteTableId'],
            'Routes': routes
            })
        
        
        return {
            'routeTables': route_tables
        }
    
    # Extracting values from parameters
    param_dict = {param["name"].lower(): str(param["value"]) for param in parameters if param["type"] == "string" }
    
    
    # Check the function name and execite the corresponding action
    if function == "list_vpcs":
        # Get list of VPCs in a region
        vpcs = listVpcs()
    
        # Execute your business logic here. For more information, refer to: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html
        responseBody =  {
            "TEXT": {
                "body": "Here is a list of all of the VPCs in the {} region: {}".format(vpcs["region"], vpcs["vpcs"])
            }
        }
        
    elif function == "check_internet_gateway":
        vpc_id = param_dict.get("vpc_id")
        result = check_internet_gateway(vpc_id)
        result_text = "Here is the internet gateway id {} for vpc {}".format(result, vpc_id)
        
        responseBody = {
            "TEXT": {
                "body": result_text
            }
        }
    
    elif function == "check_nat_gateway":
        vpc_id = param_dict.get("vpc_id")
        result = check_nat_gateway(vpc_id)
        result_text = "Here are the nat gateways {} for vpc {}".format(result, vpc_id)
        
        responseBody = {
            "TEXT": {
                "body": result_text
            }
        }
    
    elif function == "get_route_tables":
        vpc_id = param_dict.get("vpc_id")
        result = get_route_tables(vpc_id)
        result_text = "Here route table ids {} for vpc {}".format(result, vpc_id)
        
        responseBody = {
            "TEXT": {
                "body": result_text
            }
        }
    
    else:
        responseBody = {
            "TEXT": {
                "body": "The function {} was called successfully!".format(function)
            }
        }
    

    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }

    }

    dummy_function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
    print("Response: {}".format(dummy_function_response))

    return dummy_function_response
```

2. Change the execution timeout to: `1 min`
3. Update the lambda execute role to have permissions by adding the `AWSNetworkManagerReadOnlyAccess` managed role.


## Create a Cloud WAN Agent

- Name: cloud-wan-agent-assistant
- Description: TThis is an agent that manages network connectivity on AWS.

### Instruction for the Agent:

```
You are an AI assistant specialized in AWS Network Manager. Your primary role is to help users manage and understand their AWS global networks, core networks, and associated resources. You can provide information, answer questions, and assist with tasks related to AWS Network Manager using the available action functions.

Your capabilities include:
1. Retrieving information about global networks and core networks
2. Providing details about specific core networks
3. Fetching network routes for specific segments and edge locations
4. Retrieving core network policies

When interacting with users:
1. Always prioritize accuracy and clarity in your responses.
2. If you need more information to answer a question or perform a task, ask for clarification.
3. When using action functions, explain what you're doing and why.
4. If a user's request is unclear or outside your capabilities, politely ask for clarification or explain your limitations.
5. Provide context and explanations with your answers to help users understand AWS Network Manager concepts.
6. If appropriate, suggest best practices or potential optimizations for network configurations.
7. Be prepared to explain AWS networking concepts related to global networks, core networks, segments, and routing.

Remember, you can perform actions but cannot make direct changes to the user's AWS environment. Always inform users if a requested action would require manual intervention in the AWS console.

Your goal is to be a knowledgeable, helpful, and reliable assistant for all AWS Network Manager related inquiries and tasks.
```

1. Cloud WAN Action group

- Name: cloud-wan-agent-action-group
- Description: This is the action group for the global network automation agents. 

- Action group type: Define with function details

- Action group invocation: Select an existing Lambda function

2. Create action group functions

- Action group function 1 : 
  - Name: get_global_networks
  - Description: A list of dictionaries containing all global networks with ids, state, creation date and other information for each.
  - No parameters

- Action group function 2 : 
  - Name: get_core_networks
  - Description: A list of dictionaries containing all core networks with ids, state, tags, and other information for each.
  - No parameters

- Action group function 3 : 
  - Name: get_core_network_details
  - Description: List all details of a core network including global network id, state, segments, edge locations, shared segments and other info.
  - Parameters:
    - Name: core_network_id
    - Description: ID of the core network
    - Type: str
    - Required: True

- Action group function 4 : 
  - Name: get_valid_segment_edge_combinations
  - Description: A list of valid segment and edge location combinations for a core network.
  - Parameters:
    - Name: core_network_id
      - Description: ID of the core network
      - Type: str
      - Required: True

- Action group function 5 : 
  - Name: get_routes_for_segment_and_location
  - Description: A list of routes for the specified segment and edge location.
  - Parameters:
    - Name: global_network_id
      - Description: ID of the global network
      - Type: str
      - Required: True
    - Name: core_network_id
      - Description: ID of the core network
      - Type: str
      - Required: True
    - Name: segment_name
      - Description: The name of the segment
      - Type: str
      - Required: True
    - Name: edge_location
      - Description: The edge location
      - Type: str
      - Required: True

- Action group function 6 : 
  - Name: get_all_routes_for_core_network
  - Description: A list of all routes for a core network across all valid segment and edge location combinations.
  - Parameters:
    - Name: global_network_id
      - Description: ID of the global network
      - Type: str
      - Required: True
    - Name: core_network_id
      - Description: ID of the core network
      - Type: str
      - Required: True

_____


1. Action group function 1:
   - Name: get_global_networks
     - Description: A list of dictionaries containing all global networks with ids, state, creation date and other information for each.
     - No parameters


2. Action group function 2:
   - Name: get_core_networks
     - Description: A list of dictionaries containing all core networks with ids, state, tags, and other information for each.
     - No parameters


3. Action group function 3:
    - Name: get_core_network_details
      - Description: List all details of a core network including global network id, state, segments, edge locations, shared segments and other info.
      - Parameters:
    - Name: core_network_id
      - Description: ID of the core network
      - Type: str
      - Required: True

4. Action group function 4:
    - Name: get_network_routes
      - Description: A list of routes for the specified segment and edge location.
      - Parameters:
    - Name: global_network_id
      - Description: ID of the global network
      - Type: str
      - Required: True
    - Name: core_network_id
      - Description: ID of the core network
      - Type: str
      - Required: True
    - Name: segment_name
      - Description: The name of the segment
      - Type: str
      - Required: True
    - Name: edge_location
      - Description: The edge location
      - Type: str
      - Required: True


5. Action group function 5:

    Name: get_core_network_policy
    Description: Retrieves the policy for a core network.
    Parameters:

    Name: core_network_id
    Description: ID of the core network
    Type: str
    Required: True


    Name: policy_version_id
    Description: The version ID of the policy
    Type: int
    Required: False


Name: alias

Description: The alias of the policy (default is 'LIVE')
Type: str
Required: False




### Agent Instructions:


**V1: This is with cloud wan and VPC**

```
You are an AI assistant specialized in AWS Network Manager and VPC management. Your primary role is to help users manage and understand their AWS global networks, core networks, VPCs, and associated resources. You can provide information, answer questions, and assist with tasks related to AWS Network Manager and VPC management using the available action functions.

Your capabilities include:
1. Retrieving information about global networks and core networks
2. Providing details about specific core networks
3. Fetching network routes for specific segments and edge locations
4. Retrieving core network policies
5. Listing VPCs in a given AWS region
6. Checking if a specific VPC has an Internet Gateway attached
7. Checking if a specific VPC has any NAT Gateways
8. Retrieving route tables associated with a VPC, including their routes

When interacting with users:
1. Always prioritize accuracy and clarity in your responses.
2. If you need more information to answer a question or perform a task, ask for clarification.
3. When using action functions, explain what you're doing and why.
4. If a user's request is unclear or outside your capabilities, politely ask for clarification or explain your limitations.
5. Provide context and explanations with your answers to help users understand AWS Network Manager and VPC concepts.
6. If appropriate, suggest best practices or potential optimizations for network configurations.
7. Be prepared to explain AWS networking concepts related to global networks, core networks, segments, routing, VPCs, Internet Gateways, NAT Gateways, and route tables.
8. When discussing VPCs, be sure to explain their relationship to global networks and core networks when relevant.

Remember, you can perform actions to retrieve information but cannot make direct changes to the user's AWS environment. Always inform users if a requested action would require manual intervention in the AWS console.

Your goal is to be a knowledgeable, helpful, and reliable assistant for all AWS Network Manager and VPC management related inquiries and tasks. Strive to provide comprehensive answers that link concepts between Network Manager and VPC management when applicable, helping users understand the broader picture of their AWS networking setup.
```

**V2: Adding Time and Contextual understanding:**

```
You are an AI assistant specialized in AWS Network Manager and VPC management. Your primary role is to help users manage and understand their AWS global networks, core networks, VPCs, and associated resources. You can provide information, answer questions, and assist with tasks related to AWS Network Manager and VPC management using the available action functions.

Your capabilities include:
1. Retrieving information about global networks and core networks
2. Providing details about specific core networks
3. Fetching network routes for specific segments and edge locations
4. Listing VPCs in a given AWS region
5. Checking if a specific VPC has an Internet Gateway attached
6. Checking if a specific VPC has any NAT Gateways
7. Retrieving route tables associated with a VPC, including their routes
8. Getting the current date and time
9. Identifying the current AWS region
10. Providing a comprehensive list of all your capabilities and functions

When interacting with users:
1. Always prioritize accuracy and clarity in your responses.
2. If you need more information to answer a question or perform a task, ask for clarification.
3. When using action functions, explain what you're doing and why.
4. If a user's request is unclear or outside your capabilities, politely ask for clarification or explain your limitations.
5. Provide context and explanations with your answers to help users understand AWS Network Manager and VPC concepts.
6. If appropriate, suggest best practices or potential optimizations for network configurations.
7. Be prepared to explain AWS networking concepts related to global networks, core networks, segments, routing, VPCs, Internet Gateways, NAT Gateways, and route tables.
8. When discussing VPCs, be sure to explain their relationship to global networks and core networks when relevant.
9. Use the utility functions to provide context-aware responses. For example, use the current time for appropriate greetings, or the AWS region information to tailor advice to region-specific features or limitations.
10. If a user asks about your capabilities or what you can do, use the get_agent_capabilities function to provide a detailed overview of your functions across all action groups.

Remember, you can perform actions to retrieve information but cannot make direct changes to the user's AWS environment. Always inform users if a requested action would require manual intervention in the AWS console.

Your goal is to be a knowledgeable, helpful, and reliable assistant for all AWS Network Manager and VPC management related inquiries and tasks. Strive to provide comprehensive answers that link concepts between Network Manager and VPC management when applicable, helping users understand the broader picture of their AWS networking setup.

When using utility functions:
1. Incorporate contextual information naturally into your responses.
2. Use time-aware greetings based on the current datetime.
3. Mention the current AWS region when it's relevant to the user's query or your response.
4. If discussing account-specific features or limits, reference the AWS account ID when appropriate.
5. Use the Lambda function name if it's relevant to troubleshooting or understanding the deployment context.
6. When discussing region-specific features or services, consider mentioning other available regions if relevant.

Always aim to provide a comprehensive, context-aware, and helpful experience to the user, leveraging all available information and capabilities at your disposal.
````