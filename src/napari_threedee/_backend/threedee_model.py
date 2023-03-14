from abc import ABC, abstractmethod

from pydantic import BaseModel


class N3dComponent(ABC):
    """Base class for n3d components.

    By adhering to the interface defined by this class, widgets can be
    automatically generated for components.

    To implement:
        - the __init__() should take the viewer as the first argument and all
        keyword arguments should have default values.
        - make sure the _data_model attribute is set on instance construction
        - implement the set_layers() method
        - implement the _on_enable() callback
        - implement the _on_disable() callback
    """
    _data_model: BaseModel

    @property
    def data_model(self) -> BaseModel:
        """This property should return a data model for the component."""
        return self._data_model

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._on_enable() if value is True else self._on_disable()
        self._enabled = value

    @abstractmethod
    def _on_enable(self):
        """This method should 'activate' the manipulator/annotator,
        setting state and connecting callbacks.
        """
        pass

    @abstractmethod
    def _on_disable(self):
        """This method should 'deactivate' the manipulator/annotator,
        updating state and disconnecting callbacks.
        """
        pass

    @abstractmethod
    def set_layers(self, *args):
        """This method should set layer attributes on the manipulator/annotator.
        Arguments to this function should be typed as napari layers.
        """
        pass

