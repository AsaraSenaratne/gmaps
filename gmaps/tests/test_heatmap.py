
import unittest
import pytest

from ..heatmap import (
    _HeatmapOptionsMixin, heatmap_layer, Heatmap, WeightedHeatmap)
from ..geotraitlets import InvalidPointException, InvalidWeightException


class HeatmapLayer(unittest.TestCase):

    def setUp(self):
        self.locations = [(-5.0, 5.0), (10.0, 10.0)]
        self.weights = [0.2, 0.5]

    def test_weighted(self):
        heatmap = heatmap_layer(self.locations, weights=self.weights)
        state = heatmap.get_state()
        assert state['_view_name'] == 'WeightedHeatmapLayerView'
        assert state['_model_name'] == 'WeightedHeatmapLayerModel'
        assert state['weights'] == self.weights
        assert state['locations'] == self.locations

    def test_weighted_numpy_array(self):
        import numpy as np
        locations = np.array(self.locations)
        weights = np.array(self.weights)
        heatmap = heatmap_layer(locations, weights=weights)
        state = heatmap.get_state()
        assert state['weights'] == self.weights
        assert state['locations'] == self.locations

    def test_not_weighted_numpy_array(self):
        import numpy as np
        locations = np.array(self.locations)
        heatmap = heatmap_layer(locations)
        state = heatmap.get_state()
        assert state['_view_name'] == 'SimpleHeatmapLayerView'
        assert state['_model_name'] == 'SimpleHeatmapLayerModel'
        assert state['locations'] == self.locations

    def test_weighted_pandas_df(self):
        pd = pytest.importorskip('pandas')
        df = pd.DataFrame.from_items([
            ('latitude', [loc[0] for loc in self.locations]),
            ('longitude', [loc[1] for loc in self.locations]),
            ('weight', self.weights)
        ])
        heatmap = heatmap_layer(
            df[['latitude', 'longitude']],
            weights=df['weight']
        )
        state = heatmap.get_state()
        assert state['_view_name'] == 'WeightedHeatmapLayerView'
        assert state['_model_name'] == 'WeightedHeatmapLayerModel'
        assert state['weights'] == self.weights
        assert state['locations'] == self.locations

    def test_not_weighted_pandas_df(self):
        pd = pytest.importorskip('pandas')
        df = pd.DataFrame.from_items([
            ('latitude', [loc[0] for loc in self.locations]),
            ('longitude', [loc[1] for loc in self.locations]),
        ])
        heatmap = heatmap_layer(df[['latitude', 'longitude']])
        state = heatmap.get_state()
        assert state['_view_name'] == 'SimpleHeatmapLayerView'
        assert state['_model_name'] == 'SimpleHeatmapLayerModel'
        assert state['locations'] == self.locations

    def test_defaults(self):
        heatmap = heatmap_layer(self.locations)
        state = heatmap.get_state()
        assert state['max_intensity'] is None
        assert state['opacity'] == 0.6
        assert state['point_radius'] is None
        assert state['dissipating']
        assert state['gradient'] is None

    def test_max_intensity(self):
        heatmap = heatmap_layer(self.locations, max_intensity=0.2)
        state = heatmap.get_state()
        assert state['max_intensity'] == 0.2

    def test_point_radius(self):
        heatmap = heatmap_layer(self.locations, point_radius=2)
        state = heatmap.get_state()
        assert state['point_radius'] == 2

    def test_dissipating(self):
        heatmap = heatmap_layer(self.locations, dissipating=False)
        state = heatmap.get_state()
        assert not state['dissipating']

    def test_opacity(self):
        heatmap = heatmap_layer(self.locations, opacity=0.4)
        state = heatmap.get_state()
        assert state['opacity'] == 0.4

    def test_gradient(self):
        heatmap = heatmap_layer(self.locations, gradient=['blue', 'red'])
        state = heatmap.get_state()
        assert state['gradient'] == ['blue', 'red']

    def test_invalid_location(self):
        with self.assertRaises(InvalidPointException):
            heatmap_layer([(1.0, -200.0)])


class TestHeatmapOptionsMixin(unittest.TestCase):

    def test_gradient_default_none(self):
        layer = _HeatmapOptionsMixin()
        assert layer.gradient is None

    def test_gradient_default_values(self):
        layer = _HeatmapOptionsMixin(gradient=['blue', 'red'])
        assert layer.gradient == ['blue', 'red']

    def test_gradient_set_none(self):
        layer = _HeatmapOptionsMixin(gradient=['blue', 'red'])
        layer.gradient = None
        assert layer.gradient is None


class TestHeatmap(unittest.TestCase):

    def setUp(self):
        self.locations = [(-5.0, 5.0), (10.0, 10.0)]

    def test_set_data(self):
        heatmap = Heatmap(data=self.locations)
        assert heatmap.locations == self.locations

    def test_change_data(self):
        heatmap = Heatmap(locations=self.locations)
        heatmap.data = self.locations * 2
        assert heatmap.locations == self.locations * 2


class TestWeightedHeatmap(unittest.TestCase):

    def setUp(self):
        self.locations = [(-5.0, 5.0), (10.0, 10.0)]
        self.weights = [0.2, 0.5]
        self.merged_location_weights = [
            (-5.0, 5.0, 0.2),
            (10.0, 10.0, 0.5),
        ]

    def test_set_data(self):
        heatmap = WeightedHeatmap(data=self.merged_location_weights)
        assert heatmap.locations == self.locations
        assert heatmap.weights == self.weights

    def test_change_data(self):
        heatmap = WeightedHeatmap(
            locations=self.locations, weights=self.weights)
        heatmap.data = self.merged_location_weights * 2
        assert heatmap.locations == self.locations * 2
        assert heatmap.weights == self.weights * 2

    def test_non_float_weights(self):
        with self.assertRaises(InvalidWeightException):
            WeightedHeatmap(locations=self.locations, weights=['not', 'float'])

    def test_negative_weights(self):
        with self.assertRaises(InvalidWeightException):
            WeightedHeatmap(locations=self.locations, weights=[1.0, -2.0])
