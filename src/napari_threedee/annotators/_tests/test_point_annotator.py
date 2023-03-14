from unittest.mock import MagicMock

import napari.layers
import numpy as np

from napari_threedee.annotators.points import Points, PointAnnotator


def test_points_data_model():
    pts = Points(data=[])
    assert pts.data.ndim == 2


def test_point_annotator_instantiation(viewer_with_plane_and_points_3d):
    viewer = viewer_with_plane_and_points_3d
    plane_layer = viewer.layers['blobs_3d']
    points_layer = viewer.layers['Points']
    annotator = PointAnnotator(
        viewer=viewer,
        image_layer=plane_layer,
        points_layer=points_layer
    )
    assert isinstance(annotator, PointAnnotator)


def test_point_annotator_auto_creation_of_points_layer(viewer_with_plane_and_points_3d):
    viewer = viewer_with_plane_and_points_3d
    plane_layer = viewer.layers['blobs_3d']
    annotator = PointAnnotator(
        viewer=viewer,
        image_layer=plane_layer,
        points_layer=None
    )
    assert isinstance(annotator.points_layer, napari.layers.Points)
    assert annotator.points_layer.ndim == 3


def test_point_annotator_mouse_callback(viewer_with_plane_and_points_3d):
    # setup
    viewer = viewer_with_plane_and_points_3d
    plane_layer = viewer.layers['blobs_3d']
    points_layer = viewer.layers['Points']
    annotator = PointAnnotator(
        viewer=viewer,
        image_layer=plane_layer,
        points_layer=points_layer,
        enabled=True
    )

    class DummyMouseEvent:
        modifiers = ['Alt']
        position = np.array([14, 14, 14])
        view_direction = np.array([1, 0, 0])

    event = DummyMouseEvent()

    # actual test
    assert annotator.data_model.data.shape == (1, 0)
    assert len(points_layer.data) == 0
    annotator._mouse_callback(viewer=viewer, event=event)
    assert len(annotator.data_model.data) == 1
    assert len(points_layer.data) == 1


def test_point_annotator_two_way_communication(viewer_with_plane_and_points_3d):
    """Is there two-way communication between data model and layer data?"""
    # setup
    viewer = viewer_with_plane_and_points_3d
    plane_layer = viewer.layers['blobs_3d']
    points_layer = viewer.layers['Points']
    annotator = PointAnnotator(
        viewer=viewer,
        image_layer=plane_layer,
        points_layer=points_layer,
        enabled=True,
    )

    # updating data model should update the points layer
    assert len(points_layer.data) == 0
    annotator.data_model.data = [14, 14, 14]
    assert len(points_layer.data) == 1

    # updating the points layer should update the data model
    points_layer.selected_data = {0}
    points_layer.remove_selected()
    assert annotator.data_model.data.shape == points_layer.data.shape


def test_point_annotator_changing_points_layer(viewer_with_plane_and_points_3d):
    """Annotator should work after changing points layer."""
    # setup
    viewer = viewer_with_plane_and_points_3d
    plane_layer = viewer.layers['blobs_3d']
    initial_points_layer = viewer.layers['Points']
    new_points_layer = viewer.add_points(data=[], ndim=3)
    annotator = PointAnnotator(
        viewer=viewer,
        image_layer=plane_layer,
        points_layer=initial_points_layer,
    )
    annotator.data_model.events.data.disconnect = MagicMock()
    initial_points_layer.events.data.disconnect = MagicMock()

    # events should be disconnected from the old points layer
    annotator.points_layer = new_points_layer
    annotator.data_model.events.data.disconnect.assert_called_once_with(
        annotator.update_layer_data_from_data_model
    )
    initial_points_layer.events.data.disconnect.assert_called_once_with(
        annotator.update_data_model_from_layer_data
    )

    # check two way communication with new points layer works
    # updating data model should update the points layer
    assert len(new_points_layer.data) == 0
    annotator.data_model.data = np.random.random(size=(1, 3))
    assert len(new_points_layer.data) == 1

    # updating the points layer should update the data model
    new_points_layer.selected_data = {0}
    new_points_layer.remove_selected()
    assert annotator.data_model.data.shape == new_points_layer.data.shape
