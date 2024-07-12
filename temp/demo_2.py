import json
import boto3
from typing import List, Dict, Any, Optional


network_manager = boto3.client('networkmanager')


class NetworkManagerActions:
    @staticmethod
    def get_global_networks() -> List[Dict[str, Any]]:
        """
        Retrieves all global networks.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing global network information.
        """
        response = network_manager.describe_global_networks()
        return response['GlobalNetworks']

    @staticmethod
    def get_core_networks() -> List[Dict[str, Any]]:
        """
        Retrieves all core networks.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing core network information.
        """
        response = network_manager.list_core_networks()
        return response['CoreNetworks']

    @staticmethod
    def get_core_network_details(core_network_id: str) -> Dict[str, Any]:
        """
        Retrieves details for a specific core network.

        Args:
            core_network_id (str): The ID of the core network.

        Returns:
            Dict[str, Any]: Details of the specified core network.
        """
        response = network_manager.get_core_network(CoreNetworkId=core_network_id)
        return response['CoreNetwork']

    @staticmethod
    def get_core_network_policy(core_network_id: str, policy_version_id: Optional[int] = None, alias: str = 'LIVE') -> Dict[str, Any]:
        """
        Retrieves the policy for a core network.

        Args:
            core_network_id (str): The ID of the core network.
            policy_version_id (int, optional): The version ID of the policy. Defaults to None.
            alias (str, optional): The alias of the policy. Defaults to 'LIVE'.

        Returns:
            Dict[str, Any]: The core network policy.
        """
        params = {
            'CoreNetworkId': core_network_id,
            'Alias': alias
        }
        if policy_version_id:
            params['PolicyVersionId'] = policy_version_id

        response = network_manager.get_core_network_policy(**params)
        return response['CoreNetworkPolicy']

    @staticmethod
    def get_network_routes(global_network_id: str, core_network_id: str, segment_name: str, edge_location: str) -> List[Dict[str, Any]]:
        """
        Retrieves routes for a specific segment and edge location in a core network.

        Args:
            global_network_id (str): The ID of the global network.
            core_network_id (str): The ID of the core network.
            segment_name (str): The name of the segment.
            edge_location (str): The edge location.

        Returns:
            List[Dict[str, Any]]: A list of routes for the specified segment and edge location.
        """
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

def lambda_handler(event, context):
    """
    AWS Lambda function handler for Bedrock Agent.
    
    This function dispatches to the appropriate NetworkManagerActions method based on the action specified in the event.

    Args:
        event (dict): The event dictionary containing the details of the Lambda function invocation.
        context (object): The context object provided by AWS Lambda.

    Returns:
        dict: The result of the called function, formatted for Bedrock Agent response.
    """
    action = event.get('action')
    parameters = event.get('parameters', {})

    action_map = {
        'GetGlobalNetworks': NetworkManagerActions.get_global_networks,
        'GetCoreNetworks': NetworkManagerActions.get_core_networks,
        'GetCoreNetworkDetails': NetworkManagerActions.get_core_network_details,
        'GetCoreNetworkPolicy': NetworkManagerActions.get_core_network_policy,
        'GetNetworkRoutes': NetworkManagerActions.get_network_routes
    }

    if action not in action_map:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Action {action} not found'})
        }

    try:
        result = action_map[action](**parameters)
        return {
            'statusCode': 200,
            'body': json.dumps(result, default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

if __name__ == "__main__":
    event = {
        "action": "GetCoreNetworks"
    }
    context = None
    print(lambda_handler(event, context))