---
outline: [2,3]
---

  

# Package opengradient.client.alpha

Alpha Testnet features for OpenGradient SDK.

This module contains features that are only available on the Alpha Testnet,
including workflow management and ML model execution.

## Classes
    

###  Alpha

```python
class Alpha(blockchain: `Web3`, wallet_account: `LocalAccount`)
```

  

  
Alpha Testnet features namespace.

This class provides access to features that are only available on the Alpha Testnet,
including workflow deployment and execution.
  

#### Methods

  

### New workflow 

```python
def new_workflow(self, model_cid: str, input_query: opengradient.types.HistoricalInputQuery, input_tensor_name: str, scheduler_params: Optional[opengradient.types.SchedulerParams] = None) ‑> str
```

  

  
Deploy a new workflow contract with the specified parameters.

This function deploys a new workflow contract on OpenGradient that connects
an AI model with its required input data. When executed, the workflow will fetch
the specified model, evaluate the input query to get data, and perform inference.

The workflow can be set to execute manually or automatically via a scheduler.
  

**Arguments**

* **`model_cid (str)`**: CID of the model to be executed from the Model Hub
* **`input_query (HistoricalInputQuery)`**: Input definition for the model inference,
        will be evaluated at runtime for each inference
* **`input_tensor_name (str)`**: Name of the input tensor expected by the model
* **`scheduler_params (Optional[SchedulerParams])`**: Scheduler configuration for automated execution:
        - frequency: Execution frequency in seconds
        - duration_hours: How long the schedule should live for

  
**Returns**

str: Deployed contract address. If scheduler_params was provided, the workflow
     will be automatically executed according to the specified schedule.

**Raises**

* **`Exception`**: If transaction fails or gas estimation fails
  

  

### Read workflow history 

```python
def read_workflow_history(self, contract_address: str, num_results: int) ‑> List[opengradient.types.ModelOutput]
```

  

  
Gets historical inference results from a workflow contract.

Retrieves the specified number of most recent inference results from the contract's
storage, with the most recent result first.
  

**Arguments**

* **`contract_address (str)`**: Address of the deployed workflow contract
* **`num_results (int)`**: Number of historical results to retrieve

  
**Returns**

List[ModelOutput]: List of historical inference results

  

### Read workflow result 

```python
def read_workflow_result(self, contract_address: str) ‑> opengradient.types.ModelOutput
```

  

  
Reads the latest inference result from a deployed workflow contract.
  

**Arguments**

* **`contract_address (str)`**: Address of the deployed workflow contract

  
**Returns**

ModelOutput: The inference result from the contract

**Raises**

* **`ContractLogicError`**: If the transaction fails
* **`Web3Error`**: If there are issues with the web3 connection or contract interaction
  

  

### Run workflow 

```python
def run_workflow(self, contract_address: str) ‑> opengradient.types.ModelOutput
```

  

  
Triggers the run() function on a deployed workflow contract and returns the result.
  

**Arguments**

* **`contract_address (str)`**: Address of the deployed workflow contract

  
**Returns**

ModelOutput: The inference result from the contract

**Raises**

* **`ContractLogicError`**: If the transaction fails
* **`Web3Error`**: If there are issues with the web3 connection or contract interaction