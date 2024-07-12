import boto3
import json
import os

def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    
    # Extracting values from parameters
    param_dict = {param["name"].lower(): str(param["value"]) for param in parameters if param["type"] == "string"}
    region = param_dict.get("region", "us-west-2")
    
    # Check the function name and execute the corresponding action
    if function == "list_vpcs":
        region = param_dict.get("region", "us-west-2")
        result = list_vpcs(region)
    elif function == "check_internet_gateway":
        vpc_id = param_dict.get("vpc_id")
        result = check_internet_gateway(vpc_id, region)
    elif function == "check_nat_gateway":
        vpc_id = param_dict.get("vpc_id")
        result = check_nat_gateway(vpc_id, region)
    elif function == "get_route_tables":
        vpc_id = param_dict.get("vpc_id")
        result = get_route_tables(vpc_id, region)
    else:
        result = f"The function {function} is not supported."
    
    responseBody = {
        "TEXT": {
            "body": json.dumps(result, indent=2)
        }
    }

    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }
    }

    lambda_response = {'response': action_response, 'messageVersion': event['messageVersion']}
    print(f"Response: {json.dumps(lambda_response, indent=2)}")

    return lambda_response

def list_vpcs(region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_vpcs()
    vpcs = [{'VpcId': vpc['VpcId'], 'CidrBlock': vpc['CidrBlock'], 'IsDefault': vpc['IsDefault']} for vpc in response['Vpcs']]
    return {
        'vpcs': vpcs,
        "region": region
    }

def check_internet_gateway(vpc_id, region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_internet_gateways(
        Filters=[
            {
                'Name': 'attachment.vpc-id',
                'Values': [vpc_id]
            }
        ]
    )
    internet_gateways = [
        {
            'InternetGatewayId': ig['InternetGatewayId'],
            'AttachedToVpc': vpc_id in [att['VpcId'] for att in ig['Attachments']]
        } for ig in response['InternetGateways']
    ]
    return {
        'vpc_id': vpc_id,
        'internetGateways': internet_gateways
    }

def check_nat_gateway(vpc_id, region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_nat_gateways(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]
            }
        ]
    )
    nat_gateways = [
        {
            'NatGatewayId': natgw['NatGatewayId'],
            'SubnetId': natgw['SubnetId'],
            'State': natgw['State'],
            'PublicIp': natgw['NatGatewayAddresses'][0]['PublicIp'] if natgw['NatGatewayAddresses'] else None
        } for natgw in response['NatGateways']
    ]
    return {
        'vpc_id': vpc_id,
        'NatGateways': nat_gateways
    }

def get_route_tables(vpc_id, region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
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
                'GatewayId': route.get('GatewayId'),
                'NatGatewayId': route.get('NatGatewayId'),
                'InstanceId': route.get('InstanceId'),
                'VpcPeeringConnectionId': route.get('VpcPeeringConnectionId'),
                'NetworkInterfaceId': route.get('NetworkInterfaceId')
            }
            routes.append({k: v for k, v in route_data.items() if v is not None})
        
        route_tables.append({
            'RouteTableId': rt['RouteTableId'],
            'IsMain': any(assoc['Main'] for assoc in rt.get('Associations', [])),
            'Routes': routes
        })
    
    return {
        'vpc_id': vpc_id,
        'routeTables': route_tables
    }


if __name__ == "__main__":
    event = {
        "agent": "agent",
        "actionGroup": "actionGroup",
        "function": "list_vpcs",
        "parameters": [
            {
                "name": "param1",
                "type": "string",
                "value": "value1"
            }
        ],
        "messageVersion": "demo"
    }
    context = None
    print(lambda_handler(event, context))