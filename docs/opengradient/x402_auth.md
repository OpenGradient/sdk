---
outline: [2,3]
---

  

# Package opengradient.x402_auth

X402 Authentication handler for httpx streaming requests.

This module provides an httpx Auth class that handles x402 payment protocol
authentication for streaming responses.

## Classes
    

###  X402Auth

<code>class <b>X402Auth</b>(account: [local](docs/signers.md#local), max_value: Optional[int] = None, network_filter: Optional[str] = None, scheme_filter: Optional[str] = None)</code>

  

  
httpx Auth handler for x402 payment protocol.

This class implements the httpx Auth interface to handle 402 Payment Required
responses by automatically creating and attaching payment headers.
  

**Arguments**

* **`account`**: eth_account LocalAccount instance for signing payments
* **`max_value`**: Optional maximum allowed payment amount in base units
* **`network_filter`**: Optional network filter for selecting payment requirements
* **`scheme_filter`**: Optional scheme filter for selecting payment requirements
  

  

### Auth flow 

```python
def auth_flow(self, request: httpx.Request) ‑> Generator[httpx.Request, httpx.Response, None]
```

  

  
Implement the auth flow for x402 payment handling.

This method yields the initial request, and if a 402 response is received,
it creates a payment header and retries the request.
  

**Arguments**

* **`request`**: The initial httpx Request

  

#### Variables

  
    
* static `requires_response_body` - The type of the None singleton.