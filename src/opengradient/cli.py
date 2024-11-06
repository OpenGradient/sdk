import ast
import json
import logging
import webbrowser
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum
from . import types

import click

import opengradient

from .account import EthAccount, generate_eth_account
from .client import Client
from .defaults import (
    DEFAULT_BLOCKCHAIN_EXPLORER,
    DEFAULT_HUB_SIGNUP_URL,
    DEFAULT_INFERENCE_CONTRACT_ADDRESS,
    DEFAULT_OG_FAUCET_URL,
    DEFAULT_RPC_URL,
)
from .types import InferenceMode

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

# Supported inference modes
InferenceModes = {
    "VANILLA": InferenceMode.VANILLA,
    "ZKML": InferenceMode.ZKML,
    "TEE": InferenceMode.TEE,
}

# Supported LLMs
LlmModels = {
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3"
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
    """
    CLI for OpenGradient SDK. 

    Run 'opengradient config show' to make sure you have configs set up.
    
    Visit https://docs.opengradient.ai/developers/python_sdk/ for more documentation.
    """
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
                                        contract_address=DEFAULT_INFERENCE_CONTRACT_ADDRESS,
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
            if (key == 'password' or key == 'private_key') and value is not None:
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
            
        click.echo(f"Running {inference_mode} inference for model \"{model_cid}\"")
        tx_hash, model_output = client.infer(model_cid=model_cid, inference_mode=InferenceModes[inference_mode], model_input=model_input)

        click.echo()  # Add a newline for better spacing
        click.secho("✅ Transaction successful", fg="green", bold=True)
        click.echo("──────────────────────────────────────")
        click.echo("Transaction hash: ", nl=False)
        click.secho(tx_hash, fg="cyan", bold=True)

        block_explorer_link = f"{DEFAULT_BLOCKCHAIN_EXPLORER}0x{tx_hash}"
        click.echo("Block explorer link: ", nl=False)
        click.secho(block_explorer_link, fg="blue", underline=True)
        click.echo()

        click.secho("Inference result:", fg="green")
        formatted_output = json.dumps(model_output, indent=2, default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x))
        click.echo(formatted_output)
    except json.JSONDecodeError as e:
        click.echo(f"Error decoding JSON: {e}", err=True)
        click.echo(f"Error occurred on line {e.lineno}, column {e.colno}", err=True)
    except Exception as e:
        click.echo(f"Error running inference: {str(e)}")

@cli.command()
@click.option('--model', '-m', 'model_cid', type=click.Choice(LlmModels), required=True, help='CID of the LLM model to run inference on')
@click.option('--prompt', '-p', required=True, help='Input prompt for the LLM completion')
@click.option('--max-tokens', type=int, default=100, help='Maximum number of tokens for LLM completion output')
@click.option('--stop-sequence', multiple=True, help='Stop sequences for LLM')
@click.option('--temperature', type=float, default=0.0, help='Temperature for LLM inference (0.0 to 1.0)')
@click.pass_context
def completion(ctx, model_cid: str, prompt: str, max_tokens: int, stop_sequence: List[str], temperature: float):
    """
    Run completion inference on an LLM model.

    This command runs a completion inference on the specified LLM model using the provided prompt and parameters.

    Example usage:

    \b
    opengradient completion --model meta-llama/Meta-Llama-3-8B-Instruct --prompt "Hello, how are you?" --max-tokens 50 --temperature 0.7
    opengradient completion -m meta-llama/Meta-Llama-3-8B-Instruct -p "Translate to French: Hello world" --stop-sequence "." --stop-sequence "\n"
    """
    client: Client = ctx.obj['client']
    try:
        click.echo(f"Running LLM completion inference for model \"{model_cid}\"\n")
        tx_hash, llm_output = client.llm_completion(
            model_cid=model_cid,
            prompt=prompt,
            max_tokens=max_tokens,
            stop_sequence=list(stop_sequence),
            temperature=temperature
        )

        print_llm_completion_result(model_cid, tx_hash, llm_output)
    except Exception as e:
        click.echo(f"Error running LLM completion: {str(e)}")

def print_llm_completion_result(model_cid, tx_hash, llm_output):
    click.secho("✅ LLM completion Successful", fg="green", bold=True)
    click.echo("──────────────────────────────────────")
    click.echo("Model CID: ", nl=False)
    click.secho(model_cid, fg="cyan", bold=True)
    click.echo("Transaction hash: ", nl=False)
    click.secho(tx_hash, fg="cyan", bold=True)
    block_explorer_link = f"{DEFAULT_BLOCKCHAIN_EXPLORER}0x{tx_hash}"
    click.echo("Block explorer link: ", nl=False)
    click.secho(block_explorer_link, fg="blue", underline=True)
    click.echo("──────────────────────────────────────")
    click.secho("LLM Output:", fg="yellow", bold=True)
    click.echo()
    click.echo(llm_output)
    click.echo()


@cli.command()
@click.option('--model', '-m', 'model_cid', 
              type=click.Choice([e.value for e in types.LLM]), 
              required=True, 
              help='CID of the LLM model to run inference on')
@click.option('--messages', 
              type=str,
              required=False, 
              help='Input messages for the chat inference in JSON format')
@click.option('--messages-file', 
              type=click.Path(exists=True, path_type=Path),
              required=False, 
              help='Path to JSON file containing input messages for the chat inference')
@click.option('--max-tokens', 
              type=int,
              default=100, 
              help='Maximum number of tokens for LLM output')
@click.option('--stop-sequence',
              type=str,
              default=None,
              multiple=True,
              help='Stop sequences for LLM')
@click.option('--temperature', 
              type=float,
              default=0.0,
              help='Temperature for LLM inference (0.0 to 1.0)')
@click.option('--tools',
              type=str,
              default="[]",
              help='Tool configurations in JSON format')
@click.option('--tools-file',
              type=click.Path(exists=True, path_type=Path),
              required=False,
              help='Path to JSON file containing tool configurations')
@click.option('--tool-choice',
              type=str,
              default='',
              help='Specific tool choice for the LLM')
@click.pass_context
def chat(
    ctx,
    model_cid: str,
    messages: Optional[str],
    messages_file: Optional[Path],
    max_tokens: int,
    stop_sequence: List[str],
    temperature: float,
    tools: Optional[str],
    tools_file: Optional[Path],
    tool_choice: Optional[str]): 
    """
    Run chat inference on an LLM model.

    This command runs a chat inference on the specified LLM model using the provided messages and parameters.

    Example usage:

    \b
    opengradient chat --model meta-llama/Meta-Llama-3-8B-Instruct --messages '[{"role":"user","content":"hello"}]' --max-tokens 50 --temperature 0.7
    opengradient chat -m mistralai/Mistral-7B-Instruct-v0.3 --messages-file messages.json --stop-sequence "." --stop-sequence "\n"
    """
    # TODO (Kyle): ^^^^^^^ Edit description with more examples using tools
    client: Client = ctx.obj['client']
    try:
        click.echo(f"Running LLM chat inference for model \"{model_cid}\"\n")
        if not messages and not messages_file:
            click.echo("Must specify either messages or messages-file")
            ctx.exit(1)
            return
        if messages and messages_file:
            click.echo("Cannot have both messages and messages_file")
            ctx.exit(1)
            return

        if messages:
            try:
                messages = json.loads(messages)
            except Exception as e:
                click.echo(f"Failed to parse messages: {e}")
                ctx.exit(1)
        else:
            with messages_file.open('r') as file:
                messages = json.load(file)

        # Parse tools if provided
        if (tools or tools != "[]") and tools_file:
            click.echo("Cannot have both tools and tools_file")
            click.exit(1)
            return
        
        parsed_tools=[]
        if tools:
            try:
                parsed_tools = json.loads(tools)
                if not isinstance(parsed_tools, list):
                    click.echo("Tools must be a JSON array")
                    ctx.exit(1)
                    return
            except json.JSONDecodeError as e:
                click.echo(f"Failed to parse tools JSON: {e}")
                ctx.exit(1)
                return

        if tools_file:
            try:
                with tools_file.open('r') as file:
                    parsed_tools = json.load(file)
                if not isinstance(parsed_tools, list):
                    click.echo("Tools must be a JSON array")
                    ctx.exit(1)
                    return
            except Exception as e:
                click.echo("Failed to load JSON from tools_file: %s" % e)
                ctx.exit(1)
                return
            
        if not tools and not tools_file:
            parsed_tools = None

        tx_hash, finish_reason, llm_chat_output = client.llm_chat(
            model_cid=model_cid,
            messages=messages,
            max_tokens=max_tokens,
            stop_sequence=list(stop_sequence),
            temperature=temperature,
            tools=parsed_tools,
            tool_choice=tool_choice,
        )

        # TODO (Kyle): Make this prettier
        print("TX Hash: ", tx_hash)
        print("Finish reason: ", finish_reason)
        print("Chat output: ", llm_chat_output)
    except Exception as e:
        click.echo(f"Error running LLM chat inference: {str(e)}")

def print_llm_chat_result():
    pass

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

    click.echo("Please create an account on the OpenGradient Hub")
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
    click.echo("Please fund your account clicking 'Request' on the Faucet website")
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