from typing import Optional

import napari.layers
import numpy as np
from psygnal import evented
from pydantic import BaseModel, validator

from napari_threedee._backend.threedee_model import N3dComponent
from napari_threedee.geometry_utils import point_in_bounding_box
from napari_threedee.utils.napari_utils import add_mouse_callback_safe, \
    remove_mouse_callback_safe, mouse_event_to_plane_position_nd


@evented
class Points(BaseModel):
    data: np.ndarray

    class Config:
        arbitrary_types_allowed = True

    @validator('data', pre=True)
    def at_least_2d(cls, v):
        return np.atleast_2d(np.asarray(v))


class PointAnnotator(N3dComponent):
    ANNOTATION_TYPE: str = "points"
    _data_model: Points

    def __init__(
        self,
        viewer: napari.Viewer,
        data_model: Points = Points(data=[]),
        image_layer: Optional[napari.layers.Image] = None,
        points_layer: Optional[napari.layers.Points] = None,
        enabled: bool = False,
    ):
        self.viewer = viewer
        self._points_layer = None
        self._data_model = data_model
        self.image_layer = image_layer
        self.points_layer = points_layer
        if points_layer is None and image_layer is not None:
            self.points_layer = napari.layers.Points(
                data=[], ndim=image_layer.data.ndim
            )
            self.viewer.add_layer(self.points_layer)
        self.enabled = enabled

    def _mouse_callback(self, viewer, event):
        if (self.image_layer is None) or (self.points_layer is None):
            return
        if 'Alt' not in event.modifiers:
            return
        new_point_nd = mouse_event_to_plane_position_nd(
            event=event, viewer=viewer, plane_layer=self.image_layer
        )
        point_in_layer_bbox = point_in_bounding_box(
            new_point_nd, self.image_layer.extent.data
        )
        if point_in_layer_bbox is False:
            return
        new_point_nd = np.atleast_2d(new_point_nd)
        new_points_data = np.concatenate(
            [self.points_layer.data, new_point_nd], axis=0
        )
        print('updating data model')
        self.data_model.data = new_points_data
        # layer update is triggered on changes in the data model

    def update_layer_data_from_data_model(self):
        if self.points_layer is None:
            return
        print('updating layer data')
        self.points_layer.events.data.block()
        self.points_layer.data = self.data_model.data
        self.points_layer.events.data.unblock()

    def update_data_model_from_layer_data(self, event=None):
        print('updating data model')
        with self.data_model.events.blocked():
            self.data_model.data = self.points_layer.data

    def set_layers(
        self,
        image_layer: napari.layers.Image,
        points_layer: napari.layers.Points
    ):
        self.image_layer = image_layer
        self.points_layer = points_layer

    @property
    def points_layer(self) -> napari.layers.Points:
        return self._points_layer

    @points_layer.setter
    def points_layer(self, value: napari.layers.Points):
        if value is None:
            self._points_layer = None
            return
        self.enabled = False  # force event disconnection
        self._points_layer = value
        self.enabled = True  # force event connection

    def _on_enable(self):
        add_mouse_callback_safe(
            self.viewer.mouse_drag_callbacks, self._mouse_callback
        )
        self.points_layer.events.data.connect(self.update_data_model_from_layer_data)
        self.data_model.events.data.connect(self.update_layer_data_from_data_model)

    def _on_disable(self):
        remove_mouse_callback_safe(
            self.viewer.mouse_drag_callbacks, self._mouse_callback
        )
        if self.points_layer is not None:
            self.points_layer.events.data.disconnect(self.update_data_model_from_layer_data)
            self.data_model.events.data.disconnect(self.update_layer_data_from_data_model)

