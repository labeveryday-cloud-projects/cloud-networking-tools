import os
import json
import boto3

from dotenv import load_dotenv

from pprint import pprint


load_dotenv()

REGION = os.getenv("REGION")
AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN=os.getenv("AWS_SESSION_TOKEN")


# Authenticate to AWS
boto3.setup_default_session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name='us-east-1'
)

network_manager = boto3.client('networkmanager')

def get_global_networks():
    response = network_manager.describe_global_networks()
    return response['GlobalNetworks']

def get_core_networks():
    response = network_manager.list_core_networks()
    return response['CoreNetworks']

def get_core_network_details(core_network_id):
    response = network_manager.get_core_network(CoreNetworkId=core_network_id)
    return response['CoreNetwork']

def get_valid_segment_edge_combinations(core_network_id):
    core_network = get_core_network_details(core_network_id)
    valid_combinations = []
    segments = [segment['Name'] for segment in core_network.get('Segments', [])]
    edge_locations = [edge['EdgeLocation'] for edge in core_network.get('Edges', [])]
    
    for segment in segments:
        for edge_location in edge_locations:
            valid_combinations.append((segment, edge_location))
    
    return valid_combinations

def get_shared_segments(core_network_id):
    core_network = get_core_network_details(core_network_id)
    shared_segments = []
    for segment in core_network.get('Segments', []):
        if segment.get('SharedSegments'):
            shared_segments.append({
                'name': segment['Name'],
                'shared_with': segment['SharedSegments']
            })
    return shared_segments


def get_core_network_policy(core_network_id, policy_version_id=None, alias='LIVE'):
    params = {
        'CoreNetworkId': core_network_id,
        'Alias': alias
    }
    if policy_version_id:
        params['PolicyVersionId'] = policy_version_id

    response = network_manager.get_core_network_policy(**params)
    return response['CoreNetworkPolicy']


def get_routes_for_segment_and_location(global_network_id, core_network_id, segment_name, edge_location):
    route_table_identifier = {
        'CoreNetworkSegmentEdge': {
            'CoreNetworkId': core_network_id,
            'SegmentName': segment_name,
            'EdgeLocation': edge_location
        }
    }
    try:
        response = network_manager.get_network_routes(
            GlobalNetworkId=global_network_id,
            RouteTableIdentifier=route_table_identifier
        )
        return response.get('NetworkRoutes', [])
    except network_manager.exceptions.ValidationException:
        return []

def get_all_routes_for_core_network(global_network_id, core_network_id):
    valid_combinations = get_valid_segment_edge_combinations(core_network_id)
    all_routes = []
    
    for segment_name, edge_location in valid_combinations:
        routes = get_routes_for_segment_and_location(
            global_network_id,
            core_network_id,
            segment_name,
            edge_location
        )
        for route in routes:
            all_routes.append({
                'segment': segment_name,
                'edge_location': edge_location,
                'route': route
            })
    
    return all_routes

def lambda_handler(event, context):
    global_networks = get_global_networks()
    if not global_networks:
        return {"statusCode": 404, "body": "No global networks found."}

    all_network_routes = {}
    core_networks = get_core_networks()

    for global_network in global_networks:
        global_network_id = global_network['GlobalNetworkId']
        all_network_routes[global_network_id] = {}

        for core_network in core_networks:
            if core_network['GlobalNetworkId'] == global_network_id:
                core_network_id = core_network['CoreNetworkId']
                all_network_routes[global_network_id][core_network_id] = {
                    "routes": get_all_routes_for_core_network(global_network_id, core_network_id),
                    "shared_segments": get_shared_segments(core_network_id)
                }
    
    # output all_network_routes to json
    with open('all_network_routes.json', 'w') as f:
        json.dump(all_network_routes, f, indent=4)

    return {
        "statusCode": 200,
        "body": all_network_routes
    }

if __name__ == "__main__":
    pprint(lambda_handler(None, None))
