import click
import os
import opengradient
# from opengradient import init, upload, create_model, create_version, infer, sign_in_with_email_and_password
from opengradient.types import InferenceMode, ModelInput

@click.group()
@click.option('--private_key', envvar='OG_PRIVATE_KEY', help='Your OpenGradient private key')
@click.option('--rpc_url', envvar='OG_RPC_URL', help='OpenGradient RPC URL address')
@click.option('--contract_address', envvar='OG_CONTRACT_ADDRESS', help='OpenGradient contract address')
@click.pass_context
def cli(ctx, private_key, rpc_url, contract_address):
    """CLI for OpenGradient SDK"""
    if not private_key or not rpc_url or not contract_address:
        click.echo("Please provide private key, rpc url, and contract address via options or environment variables.")
        ctx.exit(1)
    # Debugging
    print("Private key: ", private_key)
    print("RPC URL: ", rpc_url)
    print("contract address: ", contract_address)
    opengradient.init(private_key=private_key, rpc_url=rpc_url, contract_address=contract_address)

@cli.command()
@click.argument('model_path')
@click.argument('model_id')
@click.argument('version_id')
def upload(model_path, model_id, version_id):
    """Upload a model"""
    try:
        result = opengradient.upload(model_path, model_id, version_id)
        click.echo(f"Model uploaded successfully: {result}")
    except Exception as e:
        click.echo(f"Error uploading model: {str(e)}")

@cli.command()
@click.argument('model_name')
@click.argument('model_desc')
def create_model(model_name, model_desc):
    """Create a new model"""
    try:
        result = opengradient.create_model(model_name, model_desc)
        click.echo(f"Model created successfully: {result}")
    except Exception as e:
        click.echo(f"Error creating model: {str(e)}")

@cli.command()
@click.argument('model_id')
@click.option('--notes', help='Version notes')
@click.option('--is-major', is_flag=True, help='Is this a major version')
def create_version(model_id, notes, is_major):
    """Create a new version of a model"""
    try:
        result = opengradient.create_version(model_id, notes, is_major)
        click.echo(f"Version created successfully: {result}")
    except Exception as e:
        click.echo(f"Error creating version: {str(e)}")

@cli.command()
@click.argument('model_id')
@click.argument('inference_mode')
@click.argument('input_data')
def infer(model_id, inference_mode, input_data):
    """Run inference on a model"""
    try:
        # mode = InferenceMode(inference_mode)
        # model_input = ModelInput(input_data)
        result = opengradient.infer(model_id=model_id, inference_mode=inference_mode, model_input=input_data)
        click.echo(f"Inference result: {result}")
    except Exception as e:
        click.echo(f"Error running inference: {str(e)}")

@cli.command()
@click.argument('email')
@click.argument('password')
def sign_in(email, password):
    """Sign in with email and password"""
    try:
        result = opengradient.sign_in_with_email_and_password(email, password)
        click.echo(f"Sign in successful: {result}")
    except Exception as e:
        click.echo(f"Error signing in: {str(e)}")

if __name__ == '__main__':
    cli()