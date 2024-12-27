Module opengradient.llm.openai
==============================

Classes
-------

`OGChat(client: opengradient.client.Client)`
:   

    ### Class variables

    `completions: opengradient.llm.openai.OGCompletions`
    :

`OGCompletions(client: opengradient.client.Client)`
:   

    ### Class variables

    `client: opengradient.client.Client`
    :

    ### Static methods

    `convert_to_abi_compatible(messages)`
    :

    ### Methods

    `create(self, model: str, messages: List[object], tools: List[object], tool_choice: str, stream: bool = False, parallel_tool_calls: bool = False) ‑> openai.types.chat.chat_completion.ChatCompletion`
    :

`OpenGradientOpenAIClient(private_key: str)`
:   

    ### Class variables

    `chat: opengradient.llm.openai.OGChat`
    :

    `client: opengradient.client.Client`
    :