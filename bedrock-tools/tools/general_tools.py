# tools/general_tools.py
from datetime import datetime
import pytz
import math
from typing import Dict, Any, Union


def get_current_datetime(timezone_str: str = "UTC") -> Dict[str, str]:
    """
    Get the current date and time in the specified timezone.

    This function returns the current date and time for a given timezone.
    If no timezone is specified, it defaults to UTC.

    Args:
    timezone_str (str): The timezone to use (e.g., "America/New_York", "Europe/London").

    Returns:
    Dict[str, str]: A dictionary containing the formatted datetime and the timezone used.
                    If an error occurs, it returns a dictionary with an error message.

    Raises:
    pytz.exceptions.UnknownTimeZoneError: If an invalid timezone is provided.
    """
    try:
        tz = pytz.timezone(timezone_str)
        current_time = datetime.now(tz)
        return {
            "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "timezone": timezone_str
        }
    except pytz.exceptions.UnknownTimeZoneError:
        return {"error": f"Unknown timezone: {timezone_str}"}


def perform_calculation(expression: str) -> Dict[str, Union[float, str]]:
    """
    Perform a simple mathematical calculation.

    This function evaluates a given mathematical expression and returns the result.
    It uses a restricted environment to prevent execution of arbitrary code.

    Args:
    expression (str): The mathematical expression to evaluate.

    Returns:
    Dict[str, Union[float, str]]: A dictionary containing either the result of the calculation
                                  or an error message if the calculation fails.

    Raises:
    Exception: If there's an error in evaluating the expression.
    """
    try:
        result = eval(expression, {"__builtins__": None}, {"math": math})
        return {"result": result}
    except Exception as e:
        return {"error": f"Calculation error: {str(e)}"}


def convert_units(value: float, from_unit: str, to_unit: str) -> Dict[str, Union[float, str]]:
    """
    Convert between common units of measurement.

    This function converts a value from one unit to another. It currently supports
    a limited set of conversions and should be expanded for more comprehensive use.

    Args:
    value (float): The numeric value to convert.
    from_unit (str): The unit to convert from.
    to_unit (str): The unit to convert to.

    Returns:
    Dict[str, Union[float, str]]: A dictionary containing either the converted value
                                  or an error message if the conversion is unsupported.
    """
    conversions = {
        "m_to_ft": lambda x: x * 3.28084,
        "ft_to_m": lambda x: x / 3.28084,
        "kg_to_lb": lambda x: x * 2.20462,
        "lb_to_kg": lambda x: x / 2.20462,
        # Add more conversions as needed
    }
    key = f"{from_unit}_to_{to_unit}"
    if key in conversions:
        return {"result": conversions[key](value)}
    return {"error": f"Unsupported conversion: {from_unit} to {to_unit}"}


def get_aws_region_info(region_code: str) -> Dict[str, Any]:
    """
    Provide information about AWS regions.

    This function returns details about a specified AWS region, including its name
    and available Availability Zones.

    Args:
    region_code (str): The AWS region code (e.g., "us-east-1", "us-west-2").

    Returns:
    Dict[str, Any]: A dictionary containing region information or an error message
                    if the region code is unknown.
    """
    regions = {
        "us-east-1": {"name": "US East (N. Virginia)", "zones": ["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1e", "us-east-1f"]},
        "us-west-2": {"name": "US West (Oregon)", "zones": ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"]},
        # Add more regions as needed
    }
    return regions.get(region_code, {"error": f"Unknown region code: {region_code}"})

def calculate_cidr_range(cidr: str) -> Dict[str, Any]:
    """
    Calculate the range of IP addresses for a given CIDR notation.

    This function takes a CIDR notation and returns details about the IP range,
    including the network address, broadcast address, number of addresses, and netmask.

    Args:
    cidr (str): The CIDR notation (e.g., "192.168.1.0/24").

    Returns:
    Dict[str, Any]: A dictionary containing CIDR range details or an error message
                    if the CIDR notation is invalid.

    Raises:
    ValueError: If the CIDR notation is invalid.
    """
    try:
        from ipaddress import ip_network
        network = ip_network(cidr)
        return {
            "network_address": str(network.network_address),
            "broadcast_address": str(network.broadcast_address),
            "num_addresses": network.num_addresses,
            "netmask": str(network.netmask)
        }
    except ValueError as e:
        return {"error": f"Invalid CIDR notation: {str(e)}"}


general_tools = [
    {
        "toolSpec": {
            "name": "get_current_datetime",
            "description": "Get the current date and time in a specified timezone"
        }
    },
    {
        "toolSpec": {
            "name": "perform_calculation",
            "description": "Perform a simple mathematical calculation"
        }
    },
    {
        "toolSpec": {
            "name": "convert_units",
            "description": "Convert between common units of measurement"
        }
    },
    {
        "toolSpec": {
            "name": "get_aws_region_info",
            "description": "Get information about an AWS region"
        }
    },
    {
        "toolSpec": {
            "name": "calculate_cidr_range",
            "description": "Calculate the range of IP addresses for a given CIDR notation"
        }
    }
]


def handle_general_tool(tool_use: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle general tool use requests.

    Args:
    tool_use (Dict[str, Any]): A dictionary containing the tool use request details.

    Returns:
    Dict[str, Any]: The result of the tool operation or an error message.
    """
    tool_name = tool_use['name']
    input_data = tool_use['input']

    try:
        if tool_name == "get_current_datetime":
            result = get_current_datetime(input_data.get('timezone', 'UTC'))
        elif tool_name == "perform_calculation":
            result = perform_calculation(input_data['expression'])
        elif tool_name == "convert_units":
            result = convert_units(input_data['value'], input_data['from_unit'], input_data['to_unit'])
        elif tool_name == "get_aws_region_info":
            result = get_aws_region_info(input_data['region_code'])
        elif tool_name == "calculate_cidr_range":
            result = calculate_cidr_range(input_data['cidr'])
        else:
            return {"error": f"Unknown general tool: {tool_name}"}

        return {
            "toolResult": {
                "toolUseId": tool_use['toolUseId'],
                "content": [{"json": result}],
                "status": "success"
            }
        }
    except Exception as e:
        return {
            "toolResult": {
                "toolUseId": tool_use['toolUseId'],
                "content": [{"json": {"error": str(e)}}],
                "status": "error"
            }
        }