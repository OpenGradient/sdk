import click
import os
import opengradient
import json
import ast
from pathlib import Path
from .client import Client
from opengradient.types import InferenceMode, ModelInput

# Environment variable names
API_KEY_ENV = 'OPENGRADIENT_API_KEY'
RPC_URL_ENV = 'OPENGRADIENT_RPC_URL'
CONTRACT_ADDRESS_ENV = 'OPENGRADIENT_CONTRACT_ADDRESS'
EMAIL_ENV = 'OPENGRADIENT_EMAIL'
PASSWORD_ENV = 'OPENGRADIENT_PASSWORD'

# Convert string to dictionary click parameter typing
class DictParamType(click.ParamType):
    name = "dictionary"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            # First, try to parse as JSON
            return json.loads(value)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to evaluate as a Python literal
            try:
                # ast.literal_eval is safer than eval as it only parses Python literals
                result = ast.literal_eval(value)
                if not isinstance(result, dict):
                    self.fail(f"'{value}' is not a valid dictionary", param, ctx)
                return result
            except (ValueError, SyntaxError):
                self.fail(f"'{value}' is not a valid dictionary", param, ctx)

Dict = DictParamType()

# Support inference modes
InferenceModes = {
    "VANILLA": opengradient.InferenceMode.VANILLA,
    "ZKML": opengradient.InferenceMode.ZKML,
    "TEE": opengradient.InferenceMode.TEE,
}

# TODO (Kyle): Once we're farther into development, we should remove the defaults for these options
@click.group()
@click.option('--api_key', 
              envvar=API_KEY_ENV, 
              help='Your OpenGradient private key', 
              default="cd09980ef6e280afc3900d2d6801f9e9c5d858a5deaeeab74a65643f5ff1a4c1")
@click.option('--rpc_url', 
              envvar=RPC_URL_ENV, 
              help='OpenGradient RPC URL address', 
              default="http://18.218.115.248:8545")
@click.option('--contract_address', 
              envvar=CONTRACT_ADDRESS_ENV, 
              help='OpenGradient inference contract address', 
              default="0x350E0A430b2B1563481833a99523Cfd17a530e4e")
@click.option('--email', 
              envvar=EMAIL_ENV,
              help='Your OpenGradient Hub email address -- not required for inference', 
              default="test@test.com")
@click.option('--password', 
              envvar=PASSWORD_ENV, 
              help='Your OpenGradient Hub password -- not required for inference', 
              default="Test-123")
@click.pass_context
def cli(ctx, api_key, rpc_url, contract_address, email, password):
    """CLI for OpenGradient SDK"""
    if not api_key:
        click.echo("Please provide an API key via flag or setting environment variable OPENGRADIENT_API_KEY")
    if not rpc_url:
        click.echo("Please provide a RPC URL via flag or setting environment variable OPENGRADIENT_RPC_URL")
    if not contract_address:
        click.echo("Please provide a contract address via flag or setting environment variable OPENGRADIENT_CONTRACT_ADDRESS")
    if not api_key or not rpc_url or not contract_address:
        ctx.exit(1)
        return

    try:
        ctx.obj = Client(private_key=api_key, 
                         rpc_url=rpc_url,
                         contract_address=contract_address,
                         email=email,
                         password=password)
    except Exception as e:
        click.echo(f"Failed to create OpenGradient client: {str(e)}")

@cli.command()
@click.pass_context
def client_settings(ctx):
    """Display OpenGradient client settings"""
    client = ctx.obj
    if not client:
        click.echo("Client not initialized")
        ctx.exit(1)
        
    click.echo("Settings for OpenGradient client:")
    click.echo(f"\tAPI key ({API_KEY_ENV}): {client.private_key}")
    click.echo(f"\tRPC URL ({RPC_URL_ENV}): {client.rpc_url}")
    click.echo(f"\tContract address ({CONTRACT_ADDRESS_ENV}): {client.contract_address}")
    if client.user:
        click.echo(f"\tEmail ({EMAIL_ENV}): {client.user["email"]}")
    else:
        click.echo(f"\tEmail: not set")

@cli.command()
@click.argument('model_path', type=Path)
@click.argument('model_id', type=str)
@click.argument('version_id', type=str)
@click.pass_obj
def upload(client, model_path, model_id, version_id):
    """Upload a model"""
    try:
        result = client.upload(model_path, model_id, version_id)
        click.echo(f"Model uploaded successfully: {result}")
    except Exception as e:
        click.echo(f"Error uploading model: {str(e)}")

@cli.command()
@click.argument('model_name', type=str)
@click.argument('model_desc', type=str)
@click.pass_obj
def create_model(client, model_name, model_desc):
    """Create a new model"""
    try:
        result = client.create_model(model_name, model_desc)
        click.echo(f"Model created successfully: {result}")
    except Exception as e:
        click.echo(f"Error creating model: {str(e)}")

@cli.command()
@click.argument('model_id', type=str)
@click.option('--notes', type=str, default=None, help='Version notes')
@click.option('--is-major', default=False, is_flag=True, help='Is this a major version')
@click.pass_obj
def create_version(client, model_id, notes, is_major):
    """Create a new version of a model"""
    try:
        result = client.create_version(model_id, notes, is_major)
        click.echo(f"Version created successfully: {result}")
    except Exception as e:
        click.echo(f"Error creating version: {str(e)}")

@cli.command()
@click.argument('model_cid', type=str)
@click.argument('inference_mode', type=click.Choice(InferenceModes.keys()), default="VANILLA")
@click.argument('input_data', type=Dict, required=False)
@click.option('--input_file',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path),
              help="Optional file input for model inference -- must be JSON") 
@click.pass_context
def infer(ctx, model_cid, inference_mode, input_data, input_file):
    """Run inference on a model"""
    client = ctx.obj
    try:
        if not input_data and not input_file:
            click.echo("Must specify either input_data or input_file")
            ctx.exit(1)
            return
        
        if input_data and input_file:
            click.echo("Cannot have both input_data and input_file")
            ctx.exit(1)
            return
        
        if input_data:
            model_input = input_data

        if input_file:
            with input_file.open('r') as file:
                model_input = json.load(file)
            
        # Parse input data from string to dict
        click.echo(f"Running {inference_mode} inference for {model_cid}...")
        tx_hash, model_output = client.infer(model_cid=model_cid, inference_mode=InferenceModes[inference_mode], model_input=model_input)
        click.secho("Success!", fg="green")
        click.echo(f"\nTransaction Hash: \n{tx_hash}")
        click.echo(f"\nInference result: \n{model_output}")
    except json.JSONDecodeError as e:
        click.echo(f"Error decoding JSON: {e}", err=True)
        click.echo(f"Error occurred on line {e.lineno}, column {e.colno}", err=True)
    except Exception as e:
        click.echo(f"Error running inference: {str(e)}")


@cli.command()
def version():
    click.echo(f"OpenGradient CLI version: {opengradient.__version__}")

if __name__ == '__main__':
    cli()