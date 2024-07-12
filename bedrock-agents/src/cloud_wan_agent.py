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
    
    This function dispatches to the appropriate NetworkManagerActions method based on the actionGroup and function specified in the event.

    Args:
        event (dict): The event dictionary containing the details of the Lambda function invocation.
        context (object): The context object provided by AWS Lambda.

    Returns:
        dict: The result of the called function, formatted for Bedrock Agent response.
    """
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])

    # Convert parameters to a dictionary
    param_dict = {param['name']: param['value'] for param in parameters}

    action_map = {
        'get_global_networks': NetworkManagerActions.get_global_networks,
        'get_core_networks': NetworkManagerActions.get_core_networks,
        'get_core_network_details': NetworkManagerActions.get_core_network_details,
        'get_core_network_policy': NetworkManagerActions.get_core_network_policy,
        'get_network_routes': NetworkManagerActions.get_network_routes
    }

    if function not in action_map:
        responseBody = {
            "TEXT": {
                "body": f"Invalid function '{function}'"
            }
        }
    else:
        try:
            result = action_map[function](**param_dict)
            result_text = json.dumps(result, indent=2, default=str)
            responseBody = {
                "TEXT": {
                    "body": f"Here is the result for {function}: {result_text}"
                }
            }
        except Exception as e:
            responseBody = {
                "TEXT": {
                    "body": f"Error executing {function}: {str(e)}"
                }
            }

    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }
    }

    response = {'response': action_response, 'messageVersion': event['messageVersion']}
    print(f"Response: {json.dumps(response, indent=2)}")

    return response