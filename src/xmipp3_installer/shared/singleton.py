"""### Contains a generic singleton class."""

class Singleton:
  """### Generic singleton class."""

  __instance = None

  def __new__(cls, *args, **kwrgs) -> "Singleton":
    """
    ### Singleton instancer.

    #### Params:
    - cls (self): Current class.
    - *args (any): Positional params.
    - **kwargs (any): Argument params.

    #### Returns:
    - (self): Instance of current class.
    """
    if not cls.__instance:
      cls.__instance = super().__new__(cls)
    return cls.__instance
