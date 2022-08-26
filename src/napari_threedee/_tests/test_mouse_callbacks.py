import numpy as np

from ..mouse_callbacks import add_point_on_plane


def test_add_point_on_plane_3d(viewer_with_plane_and_points_3d):
    viewer = viewer_with_plane_and_points_3d
    points_layer = viewer.layers['Points']
    plane_layer = viewer.layers['blobs_3d']

    class DummyMouseEvent:
        position = (14, 14, 14)
        _view_direction = np.array((1, 0, 0))
        modifiers = ['Alt']

    add_point_on_plane(
        viewer=viewer_with_plane_and_points_3d,
        event=DummyMouseEvent,
        points_layer=points_layer,
        plane_layer=plane_layer,
    )
    assert len(points_layer.data) == 1
    np.testing.assert_array_almost_equal(points_layer.data[0], (14, 14, 14))
