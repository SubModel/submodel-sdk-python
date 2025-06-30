import click
import json
import sys
import logging
from typing import Optional

from submodel import __version__
from submodel.sdk.client import create_client
from submodel.sdk.exceptions import SubModelError, AuthenticationError, APIError
from submodel.sdk.utils import set_log_level

def handle_error(func):
    """Handle errors during command execution"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SubModelError as e:
            click.echo(f"Error: {str(e)}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Unknown error: {str(e)}", err=True)
            sys.exit(1)
    return wrapper

@click.group()
@click.option('--token', help='API access token')
@click.option('--api-key', help='API key')
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.pass_context
def cli(ctx, token: Optional[str], api_key: Optional[str], debug: bool):
    """SubModel CLI tool"""
    logger = logging.getLogger("submodel")
    
    if debug:
        set_log_level(logging.DEBUG)
        logger.debug("Debug mode enabled")
    else:
        set_log_level(logging.INFO)
        
    ctx.ensure_object(dict)
    try:
        ctx.obj['client'] = create_client(token=token, api_key=api_key)
        logger.debug("Client created successfully")
    except ValueError as e:
        logger.debug(f"Client creation failed: {str(e)}")
        raise click.ClickException("Authentication required")

@cli.group()
def auth():
    """Authentication commands"""
    pass

@auth.command()
@click.argument('username')
@click.argument('password')
@click.pass_context
@handle_error
def register(ctx, username: str, password: str):
    """Register new account"""
    result = ctx.obj['client'].auth.register(username, password)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))

@auth.command()
@click.argument('username')
@click.argument('password')
@click.pass_context
def login(ctx, username: str, password: str):
    """Login and get access token"""
    try:
        result = ctx.obj['client'].auth.login(username, password)
        click.echo(f"Login successful! Token: {result['data']['token']}")
    except AuthenticationError as e:
        raise click.ClickException(f"Authentication failed: {str(e)}")
    except APIError as e:
        raise click.ClickException(f"API error: {str(e)}")

@auth.command()
@click.pass_context
@handle_error
def info(ctx):
    """Get current user info"""
    result = ctx.obj['client'].auth.get_user_info()
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))

@cli.group()
def instance():
    """Instance management commands"""
    pass

@instance.command()
@click.option('--billing-method', required=True, type=click.Choice(['payg', 'monthly']),
              help='Billing method: payg(Pay As You Go) or monthly')
@click.option('--mode', required=True, type=click.Choice(['pod', 'baremetal']),
              help='Instance mode: pod or baremetal')
@click.option('--plan', help='Instance plan')
@click.option('--image', help='Image name')
@click.option('--pod-num', type=int, default=1, help='Number of pods')
@click.pass_context
def create(ctx, billing_method: str, mode: str, plan: Optional[str],
          image: Optional[str], pod_num: int):
    """Create new instance"""
    try:
        result = ctx.obj['client'].instance.create(
            billing_method=billing_method,
            mode=mode,
            plan=plan,
            image=image,
            pod_num=pod_num
        )
        click.echo(f"Instance created successfully! Instance ID: {result['data']['inst_id']}")
    except (AuthenticationError, APIError) as e:
        raise click.ClickException(str(e))

@instance.command(name='list')
@click.option('--page', type=int, default=1, help='Page number')
@click.option('--limit', type=int, default=10, help='Items per page')
@click.pass_context
@handle_error
def list_instances(ctx, page: int, limit: int):
    """Get instance list"""
    result = ctx.obj['client'].instance.list_instances(
        page=page,
        limit=limit
    )
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))

@instance.command()
@click.argument('instance-id')
@click.pass_context
@handle_error
def get(ctx, instance_id):
    """Get instance details"""
    result = ctx.obj['client'].instance.get_instance(instance_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))

@instance.command()
@click.argument('instance-id')
@click.argument('action', type=click.Choice(['run', 'stop', 'release', 'restart']))
@click.pass_context
@handle_error
def control(ctx, instance_id, action):
    """Control instance status"""
    result = ctx.obj['client'].instance.control_instance(action, instance_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))

@cli.group()
def device():
    """Device management commands"""
    pass

@device.command(name='list')
@click.option('--page', type=int, default=1, help='Page number')
@click.option('--limit', type=int, default=10, help='Items per page')
@click.pass_context
def list_devices(ctx, page: int, limit: int):
    """List all devices"""
    try:
        result = ctx.obj['client'].device.list_devices(page=page, limit=limit)
        devices = result['data']['items']
        if not devices:
            click.echo("No devices found")
            return
            
        for dev in devices:
            click.echo(f"ID: {dev['id']}, Status: {dev['status']}")
    except (AuthenticationError, APIError) as e:
        raise click.ClickException(str(e))

@device.command()
@click.argument('device-id')
@click.pass_context
@handle_error
def get(ctx, device_id):
    """Get device details"""
    result = ctx.obj['client'].device.get_device(device_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))

@cli.command()
def version():
    """Show the SubModel SDK version."""
    click.echo(f"submodel=={__version__}")

if __name__ == '__main__':
    cli()
