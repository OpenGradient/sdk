---
outline: [2,3]
---

  

# Package opengradient.workflow_models.types

Type definitions for models module.

## Classes
    

###  WorkflowModelOutput

```python
class WorkflowModelOutput(result: str, block_explorer_link: str = '')
```

  

  
Output definition for reading from a workflow model.
  

#### Variables

  
    
* static `block_explorer_link  : str` - (Optional) Block explorer link for the smart contract address of the workflow.
    
* static `result  : str` - Result of the workflow formatted as a string.