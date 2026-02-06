---
outline: [2,3]
---

  

# Package opengradient.client.x402_auth

X402 Authentication handler for httpx streaming requests.

This module provides an httpx Auth class that handles x402 payment protocol
authentication for streaming responses.

## Classes
    

###  X402Auth

<code>class <b>X402Auth</b>(account: Any, max_value: Optional[int] = None, payment_requirements_selector: Optional[Callable[[list[`PaymentRequirements`], Optional[str], Optional[str], Optional[int]], `PaymentRequirements`]] = None, network_filter: Optional[str] = None)</code>

  

  
httpx Auth handler for x402 payment protocol.

This class implements the httpx Auth interface to handle 402 Payment Required
responses by automatically creating and attaching payment headers.
  

**Arguments**

* **`account`**: eth_account LocalAccount instance for signing payments
* **`max_value`**: Optional maximum allowed payment amount in base units
* **`network_filter`**: Optional network filter for selecting payment requirements
* **`scheme_filter`**: Optional scheme filter for selecting payment requirements
  

  

### Async auth flow 

```python
async def async_auth_flow(self, request: httpx.Request) ‑> AsyncGenerator[httpx.Request, httpx.Response]
```

  

  
Handle authentication flow for x402 payment protocol.
  

**Arguments**

* **`request`**: httpx Request object to be authenticated

  

#### Variables

  
    
* static `requires_response_body` - The type of the None singleton.