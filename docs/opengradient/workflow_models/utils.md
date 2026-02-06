---
outline: [2,3]
---

  

# Package opengradient.workflow_models.utils

Utility functions for the models module.

## Functions

  

### Create block explorer link smart contract 

```python
def create_block_explorer_link_smart_contract(transaction_hash: str) ‑> str
```

  

  
Create block explorer link for smart contract.
  

  

### Create block explorer link transaction 

```python
def create_block_explorer_link_transaction(transaction_hash: str) ‑> str
```

  

  
Create block explorer link for transaction.
  

  

### Read workflow wrapper 

```python
def read_workflow_wrapper(alpha: opengradient.client.alpha.Alpha, contract_address: str, format_function: Callable[..., str]) ‑> opengradient.workflow_models.types.WorkflowModelOutput
```

  

  
Wrapper function for reading from models through workflows.