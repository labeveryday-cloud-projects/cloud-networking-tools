# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html
import os
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

# Create a Network Manager client
nm = boto3.client('networkmanager')


def get_global_networks() -> list:
    """
    Returns a list of global networks.
    Args:
        None
    Returns:
        A list of global networks.
    """
    response = nm.describe_global_networks()
    global_networks = response.get("GlobalNetworks")
    return global_networks


def get_core_networks() -> list:
    """
    Returns a list of owned and shared core networks.
    Args:
        None
    Returns:
        A list of core networks.
    """
    response = nm.list_core_networks()
    core_networks  = response.get("CoreNetworks")
    return core_networks


def get_core_network_segments(core_network_id: str) -> list:
    """
    Returns list of segments for the specified core network.
    Args:
        core_network_id: The ID of the core network.
    Returns:
        A list containing the segments of the core network.
    """
    response = nm.get_core_network(CoreNetworkId=core_network_id)
    core_network = response.get("CoreNetwork")
    return core_network["Segments"]

def get_network_routes(global_network_id: str, core_network_id: str, segment_name: str, edge_location: str=None):
    core_network_segments = get_core_network_segments(core_network_id)
    for item in core_network_segments:
        if item["Name"] == segment_name:
            if edge_location.lower() in item["EdgeLocations"]:
                route_table_identifier = {
                    'CoreNetworkSegmentEdge': {
                        'CoreNetworkId': core_network_id,
                        'SegmentName': item["Name"],
                        'EdgeLocation': edge_location.lower()
                    }
                }
    if route_table_identifier:
        response = nm.get_network_routes(GlobalNetworkId=global_network_id, RouteTableIdentifier=route_table_identifier)
        response.pop("ResponseMetadata")
        return response
    else:
        return None
    


# Get global networks
result = get_global_networks()
# pprint(result)

# Get Core networks
result = get_core_networks()
# pprint(result)

# Get core network
cn_id = "core-network-02c7742c8fa6ffc6c"
result = get_core_network_segments(cn_id)
# pprint(result)


global_network_id = 'global-network-0bcc75e2e6968c9fe'

result = get_network_routes(global_network_id=global_network_id, core_network_id=cn_id, segment_name="Production", edge_location="us-east-1")
pprint(result)
