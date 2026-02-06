---
outline: [2,3]
---

  

# Package opengradient.client.alpha

Alpha Testnet features for OpenGradient SDK.

This module contains features that are only available on the Alpha Testnet,
including workflow management and ML model execution.

## Classes
    

###  Alpha

<code>class <b>Alpha</b>(blockchain: `Web3`, wallet_account: `LocalAccount`)</code>

  

  
Alpha Testnet features namespace.

This class provides access to features that are only available on the Alpha Testnet,
including workflow deployment and execution.
  

  

### New workflow 

```python
def new_workflow(self, model_cid: str, input_query: opengradient.types.HistoricalInputQuery, input_tensor_name: str, scheduler_params: Optional[opengradient.types.SchedulerParams] = None) ‑> str
```

  

  
Deploy a new workflow contract with the specified parameters.

This function deploys a new workflow contract on OpenGradient that connects
an AI model with its required input data. When executed, the workflow will fetch
the specified model, evaluate the input query to get data, and perform inference.

The workflow can be set to execute manually or automatically via a scheduler.
  

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
  

**Returns**

List[ModelOutput]: List of historical inference results

  

### Read workflow result 

```python
def read_workflow_result(self, contract_address: str) ‑> opengradient.types.ModelOutput
```

  

  
Reads the latest inference result from a deployed workflow contract.
  

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
  

**Returns**

ModelOutput: The inference result from the contract

**Raises**

* **`ContractLogicError`**: If the transaction fails
* **`Web3Error`**: If there are issues with the web3 connection or contract interaction