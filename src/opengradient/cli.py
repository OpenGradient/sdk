import click
import opengradient
import json
import ast
from pathlib import Path
import logging
from pprint import pformat
import webbrowser
import sys

from .client import Client
from .defaults import *
from .types import InferenceMode
from .account import EthAccount, generate_eth_account

OG_CONFIG_FILE = Path.home() / '.opengradient_config.json'


def load_og_config():
    if OG_CONFIG_FILE.exists():
        with OG_CONFIG_FILE.open('r') as f:
            return json.load(f)
    return {}

def save_og_config(ctx):
    with OG_CONFIG_FILE.open('w') as f:
        json.dump(ctx.obj, f)

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
    "VANILLA": InferenceMode.VANILLA,
    "ZKML": InferenceMode.ZKML,
    "TEE": InferenceMode.TEE,
}


def initialize_config(ctx):
    """Interactively initialize OpenGradient config"""
    if ctx.obj:  # Check if config data already exists
        click.echo("A config already exists. Please run 'opengradient config clear' first if you want to reinitialize.")
        click.echo("You can view your current config with 'opengradient config show'.")

    click.echo("Initializing OpenGradient config...")
    click.secho(f"Config will be stored in: {OG_CONFIG_FILE}", fg='cyan')

    # Check if user has an existing account
    has_account = click.confirm("Do you already have an OpenGradient account?", default=True)

    if not has_account:
        eth_account = create_account_impl()
        if eth_account is None:
            click.echo("Account creation cancelled. Config initialization aborted.")
            return
        ctx.obj['private_key'] = eth_account.private_key
    else:
        ctx.obj['private_key'] = click.prompt("Enter your OpenGradient private key", type=str)

    # Make email and password optional
    email = click.prompt("Enter your OpenGradient Hub email address (optional, press Enter to skip)", 
                         type=str, default='', show_default=False)
    ctx.obj['email'] = email if email else None
    password = click.prompt("Enter your OpenGradient Hub password (optional, press Enter to skip)", 
                            type=str, hide_input=True, default='', show_default=False)
    ctx.obj['password'] = password if password else None

    ctx.obj['rpc_url'] = DEFAULT_RPC_URL
    ctx.obj['contract_address'] = DEFAULT_INFERENCE_CONTRACT_ADDRESS
    
    save_og_config(ctx)
    click.echo("Config has been saved.")
    click.secho("You can run 'opengradient config show' to see configs.", fg='green')


@click.group()
@click.pass_context
def cli(ctx):
    """CLI for OpenGradient SDK. Visit https://docs.opengradient.ai/developers/python_sdk/ for more documentation."""
    # Load existing config 
    ctx.obj = load_og_config()

    no_client_commands = ['config', 'create-account', 'version']

    # Only create client if this is not a config management command
    if ctx.invoked_subcommand in no_client_commands:
        return

    if all(key in ctx.obj for key in ['private_key', 'rpc_url', 'contract_address']):
        try:
            ctx.obj['client'] = Client(private_key=ctx.obj['private_key'], 
                                        rpc_url=ctx.obj['rpc_url'],
                                        contract_address=ctx.obj['contract_address'],
                                        email=ctx.obj.get('email'),
                                        password=ctx.obj.get('password'))
        except Exception as e:
            click.echo(f"Failed to create OpenGradient client: {str(e)}")
            ctx.exit(1)
    else:
        click.echo("Insufficient information to create client. Some commands may not be available.")
        click.echo("Please run 'opengradient config clear' and/or 'opengradient config init' and to reinitialize your configs.")
        ctx.exit(1)


@cli.group()
def config():
    """Manage your OpenGradient configuration (credentials etc)"""
    pass


@config.command()
@click.pass_context
def init(ctx):
    """Initialize or reinitialize the OpenGradient config"""
    initialize_config(ctx)


@config.command()
@click.pass_context
def show(ctx):
    """Display current config information"""
    click.secho(f"Config file location: {OG_CONFIG_FILE}", fg='cyan')

    if not ctx.obj:
        click.echo("Config is empty. Run 'opengradient config init' to initialize it.")
        return

    click.echo("Current config:")
    for key, value in ctx.obj.items():
        if key != 'client':  # Don't display the client object
            if key == 'password' and value is not None:
                click.echo(f"{key}: {'*' * len(value)}")  # Mask the password
            elif value is None:
                click.echo(f"{key}: Not set")
            else:
                click.echo(f"{key}: {value}") 


@config.command()
@click.pass_context
def clear(ctx):
    """Clear all saved configs"""
    if not ctx.obj:
        click.echo("No configs to clear.")
        return

    if click.confirm("Are you sure you want to clear all configs? This action cannot be undone.", abort=True):
        ctx.obj.clear()
        save_og_config(ctx)
        click.echo("Configs cleared.")
    else:
        click.echo("Config clear cancelled.")


@cli.command()
@click.option('--repo', '-r', '--name', 'repo_name', required=True, help='Name of the new model repository')
@click.option('--description', '-d', required=True, help='Description of the model')
@click.pass_obj
def create_model_repo(obj, repo_name: str, description: str):
    """
    Create a new model repository.

    This command creates a new model repository with the specified name and description.
    The repository name should be unique within your account.

    Example usage:

    \b
    opengradient create-model-repo --name "my_new_model" --description "A new model for XYZ task"
    opengradient create-model-repo -n "my_new_model" -d "A new model for XYZ task"
    """
    client: Client = obj['client']

    try:
        result = client.create_model(repo_name, description)
        click.echo(f"Model repository created successfully: {result}")
    except Exception as e:
        click.echo(f"Error creating model: {str(e)}")


@cli.command()
@click.option('--repo', '-r', 'repo_name', required=True, help='Name of the existing model repository')
@click.option('--notes', '-n', help='Version notes (optional)')
@click.option('--major', '-m', is_flag=True, default=False, help='Flag to indicate a major version update')
@click.pass_obj
def create_version(obj, repo_name: str, notes: str, major: bool):
    """Create a new version in an existing model repository.

    This command creates a new version for the specified model repository. 
    You can optionally provide version notes and indicate if it's a major version update.

    Example usage:

    \b
    opengradient create-version --repo my_model_repo --notes "Added new feature X" --major
    opengradient create-version -r my_model_repo -n "Bug fixes"
    """
    client: Client = obj['client']

    try:
        result = client.create_version(repo_name, notes, major)
        click.echo(f"New version created successfully: {result}")
    except Exception as e:
        click.echo(f"Error creating version: {str(e)}")


@cli.command()
@click.argument('file_path', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path),
                metavar='FILE_PATH')
@click.option('--repo', '-r', 'repo_name', required=True, help='Name of the model repository')
@click.option('--version', '-v', required=True, help='Version of the model (e.g., "0.01")')
@click.pass_obj
def upload_file(obj, file_path: Path, repo_name: str, version: str):
    """
    Upload a file to an existing model repository and version.

    FILE_PATH: Path to the file you want to upload (e.g., model.onnx)

    Example usage:

    \b
    opengradient upload-file path/to/model.onnx --repo my_model_repo --version 0.01
    opengradient upload-file path/to/model.onnx -r my_model_repo -v 0.01
    """
    client: Client = obj['client']

    try:
        result = client.upload(file_path, repo_name, version)
        click.echo(f"File uploaded successfully: {result}")
    except Exception as e:
        click.echo(f"Error uploading model: {str(e)}")


@cli.command()
@click.option('--model', '-m', 'model_cid', required=True, help='CID of the model to run inference on')
@click.option('--mode', 'inference_mode', type=click.Choice(InferenceModes.keys()), default="VANILLA", 
              help='Inference mode (default: VANILLA)')
@click.option('--input', '-d', 'input_data', type=Dict, help='Input data for inference as a JSON string')
@click.option('--input-file', '-f', 
              type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path),
              help="JSON file containing input data for inference")
@click.pass_context
def infer(ctx, model_cid: str, inference_mode: str, input_data, input_file: Path):
    """
    Run inference on a model.

    This command runs inference on the specified model using the provided input data.
    You must provide either --input or --input-file, but not both.

    Example usage:

    \b
    opengradient infer --model Qm... --mode VANILLA --input '{"key": "value"}'
    opengradient infer -m Qm... -i ZKML -f input_data.json
    """
    client: Client = ctx.obj['client']

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
        click.echo(f"Running {inference_mode} inference for model \"{model_cid}\"\n")
        tx_hash, model_output = client.infer(model_cid=model_cid, inference_mode=InferenceModes[inference_mode], model_input=model_input)

        click.secho("Success!", fg="green")
        click.echo(f"Transaction hash: {tx_hash}")
        click.echo(f"Inference result:\n{pformat(model_output, indent=2, width=120)}")
    except json.JSONDecodeError as e:
        click.echo(f"Error decoding JSON: {e}", err=True)
        click.echo(f"Error occurred on line {e.lineno}, column {e.colno}", err=True)
    except Exception as e:
        click.echo(f"Error running inference: {str(e)}")


@cli.command()
def create_account():
    """Create a new test account for OpenGradient inference and model management"""
    create_account_impl()


def create_account_impl() -> EthAccount:
    click.echo("\n" + "=" * 50)
    click.echo("OpenGradient Account Creation Wizard".center(50))
    click.echo("=" * 50 + "\n")

    click.echo("\n" + "-" * 50)
    click.echo("Step 1: Create Account on OpenGradient Hub")
    click.echo("-" * 50)

    click.echo(f"Please create an account on the OpenGradient Hub")
    webbrowser.open(DEFAULT_HUB_SIGNUP_URL, new=2)
    click.confirm("Have you successfully created your account on the OpenGradient Hub?", abort=True)

    click.echo("\n" + "-" * 50)
    click.echo("Step 2: Generate Ethereum Account")
    click.echo("-" * 50)
    eth_account = generate_eth_account()
    click.echo(f"Generated OpenGradient chain account with address: {eth_account.address}")

    click.echo("\n" + "-" * 50)
    click.echo("Step 3: Fund Your Account")
    click.echo("-" * 50)
    click.echo(f"Please fund your account clicking 'Request' on the Faucet website")
    webbrowser.open(DEFAULT_OG_FAUCET_URL + eth_account.address, new=2)
    click.confirm("Have you successfully funded your account using the Faucet?", abort=True)

    click.echo("\n" + "=" * 50)
    click.echo("Account Creation Complete!".center(50))
    click.echo("=" * 50)
    click.echo("\nYour OpenGradient account has been successfully created and funded.")
    click.secho(f"Address: {eth_account.address}", fg='green')
    click.secho(f"Private Key: {eth_account.private_key}", fg='green')
    click.secho("\nPlease save this information for your records.\n", fg='cyan')

    return eth_account


@cli.command()
def version():
    """Return version of OpenGradient CLI"""
    click.echo(f"OpenGradient CLI version: {opengradient.__version__}")


@cli.command()
@click.option('--repo', '-r', 'repo_name', required=True, help='Name of the model repository')
@click.option('--version', '-v', required=True, help='Version of the model (e.g., "0.01")')
@click.pass_obj
def list_files(client: Client, repo_name: str, version: str):
    """
    List files for a specific version of a model repository.

    This command lists all files associated with the specified model repository and version.

    Example usage:

    \b
    opengradient list-files --repo my_model_repo --version 0.01
    opengradient list-files -r my_model_repo -v 0.01
    """
    try:
        files = client.list_files(repo_name, version)
        if files:
            click.echo(f"Files for {repo_name} version {version}:")
            for file in files:
                click.echo(f"  - {file['name']} (Size: {file['size']} bytes)")
        else:
            click.echo(f"No files found for {repo_name} version {version}")
    except Exception as e:
        click.echo(f"Error listing files: {str(e)}")


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARN)
    cli()