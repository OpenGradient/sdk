import click
import opengradient
import json
import ast
from pathlib import Path
import logging
from pprint import pformat

from .client import Client
from .defaults import *
from .types import InferenceMode

# Environment variable names
PRIVATE_KEY_ENV = 'OPENGRADIENT_PRIVATE_KEY'
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
    "VANILLA": InferenceMode.VANILLA,
    "ZKML": InferenceMode.ZKML,
    "TEE": InferenceMode.TEE,
}

# TODO (Kyle): Once we're farther into development, we should remove the defaults for these options
@click.group()
@click.option('--private_key', 
              envvar=PRIVATE_KEY_ENV, 
              help='Your OpenGradient private key', 
              default=DEFAULT_PRIVATE_KEY)
@click.option('--rpc_url', 
              envvar=RPC_URL_ENV, 
              help='OpenGradient RPC URL address', 
              default=DEFAULT_RPC_URL)
@click.option('--contract_address', 
              envvar=CONTRACT_ADDRESS_ENV, 
              help='OpenGradient inference contract address', 
              default=DEFAULT_INFERENCE_CONTRACT_ADDRESS)
@click.option('--email', 
              envvar=EMAIL_ENV,
              help='Your OpenGradient Hub email address -- not required for inference', 
              required=True)
@click.option('--password', 
              envvar=PASSWORD_ENV, 
              help='Your OpenGradient Hub password -- not required for inference', 
              required=True)
@click.pass_context
def cli(ctx, private_key, rpc_url, contract_address, email, password):
    """CLI for OpenGradient SDK. Visit https://docs.opengradient.ai/developers/python_sdk/ for more documentation."""

    if not private_key:
        click.echo("Please provide a private key via flag or setting environment variable OPENGRADIENT_PRIVATE_KEY")
    if not rpc_url:
        click.echo("Please provide a RPC URL via flag or setting environment variable OPENGRADIENT_RPC_URL")
    if not contract_address:
        click.echo("Please provide a contract address via flag or setting environment variable OPENGRADIENT_CONTRACT_ADDRESS")
    if not email:
        click.echo("Please provide an email via flag or setting environment variable OPENGRADIENT_EMAIL")
    if not password:
        click.echo("Please provide a password via flag or setting environment variable OPENGRADIENT_PASSWORD")
    if not private_key or not rpc_url or not contract_address or not email or not password:
        ctx.exit(1)
        return

    try:
        ctx.obj = Client(private_key=private_key, 
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
    click.echo(f"\tPrivate key ({PRIVATE_KEY_ENV}): {client.private_key}")
    click.echo(f"\tRPC URL ({RPC_URL_ENV}): {client.rpc_url}")
    click.echo(f"\tContract address ({CONTRACT_ADDRESS_ENV}): {client.contract_address}")
    if client.user:
        click.echo(f"\tEmail ({EMAIL_ENV}): {client.user["email"]}")
    else:
        click.echo(f"\tEmail: not set")

@cli.command()
@click.option('--repo', '-r', '--name', 'repo_name', required=True, help='Name of the new model repository')
@click.option('--description', '-d', required=True, help='Description of the model')
@click.pass_obj
def create_model_repo(client: Client, repo_name: str, description: str):
    """
    Create a new model repository.

    This command creates a new model repository with the specified name and description.
    The repository name should be unique within your account.

    Example usage:

    \b
    opengradient create-model-repo --name "my_new_model" --description "A new model for XYZ task"
    opengradient create-model-repo -n "my_new_model" -d "A new model for XYZ task"
    """
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
def create_version(client: Client, repo_name: str, notes: str, major: bool):
    """Create a new version in an existing model repository.

    This command creates a new version for the specified model repository. 
    You can optionally provide version notes and indicate if it's a major version update.

    Example usage:

    \b
    opengradient create-version --repo my_model_repo --notes "Added new feature X" --major
    opengradient create-version -r my_model_repo -n "Bug fixes"
    """
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
def upload_file(client: Client, file_path: Path, repo_name: str, version: str):
    """
    Upload a file to an existing model repository and version.

    FILE_PATH: Path to the file you want to upload (e.g., model.onnx)

    Example usage:

    \b
    opengradient upload-file path/to/model.onnx --repo my_model_repo --version 0.01
    opengradient upload-file path/to/model.onnx -r my_model_repo -v 0.01
    """
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
    client: Client = ctx.obj
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