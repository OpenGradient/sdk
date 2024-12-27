Module opengradient.llm.chat
============================

Classes
-------

`OpenGradientChatModel(private_key: str, model_cid: str, max_tokens: int = 300)`
:   OpenGradient adapter class for LangChain chat model

    ### Ancestors (in MRO)

    * langchain_core.language_models.chat_models.BaseChatModel
    * langchain_core.language_models.base.BaseLanguageModel[BaseMessage]
    * langchain_core.language_models.base.BaseLanguageModel
    * langchain_core.runnables.base.RunnableSerializable[Union[PromptValue, str, Sequence[Union[BaseMessage, list[str], tuple[str, str], str, dict[str, Any]]]], TypeVar]
    * langchain_core.runnables.base.RunnableSerializable
    * langchain_core.load.serializable.Serializable
    * pydantic.main.BaseModel
    * langchain_core.runnables.base.Runnable
    * typing.Generic
    * abc.ABC

    ### Class variables

    `client: opengradient.client.Client`
    :

    `max_tokens: int`
    :

    `model_cid: str`
    :

    `model_computed_fields`
    :

    `model_config`
    :

    `model_fields`
    :

    `tools: List[Dict]`
    :

    ### Methods

    `bind_tools(self, tools: Sequence[langchain_core.tools.base.BaseTool | Dict]) ‑> opengradient.llm.chat.OpenGradientChatModel`
    :   Bind tools to the model.