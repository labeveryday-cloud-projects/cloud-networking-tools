# tool_handler.py



from tools.vpc_tools import list_vpcs, check_internet_gateway, check_nat_gateway, get_route_tables
from tools.network_tools import list_subnets, describe_network_acls


def handle_tool_use(tool_use):
    """
    Handle tool use requests from Claude.
    
    :param tool_use: Dictionary containing tool use details
    :return: Dictionary with the tool result in the format expected by Claude
    """
    tool_name = tool_use['name']
    input_data = tool_use['input']
    
    # Default to us-west-2 if region is not specified
    region = input_data.get('region', 'us-west-2')
    
    if tool_name == "list_vpcs":
        result = list_vpcs(region=region)
    elif tool_name == "check_internet_gateway":
        result = check_internet_gateway(input_data['vpc_id'], region=region)
    elif tool_name == "check_nat_gateway":
        result = check_nat_gateway(input_data['vpc_id'], region=region)
    elif tool_name == "get_route_tables":
        result = get_route_tables(input_data['vpc_id'], region=region)
    elif tool_name == "list_subnets":
        result = list_subnets(input_data['vpc_id'], region=region)
    elif tool_name == "describe_network_acls":
        result = describe_network_acls(input_data['vpc_id'], region=region)
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return {
        "role": "user",
        "content": [
            {
                "toolResult": {
                    "toolUseId": tool_use['toolUseId'],
                    "content": [{"json": result}],
                    "status": "success"
                }
            }
        ]
    }