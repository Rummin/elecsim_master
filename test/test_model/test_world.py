"""
File name: test_world
Date created: 01/12/2018
Feature: # Tests the model
"""
from unittest import TestCase
from model.world import World
from src.scenario import scenario_data
import logging
__author__ = "Alexander Kell"
__copyright__ = "Copyright 2018, Alexander Kell"
__license__ = "MIT"
__email__ = "alexander@kell.es"

logging.basicConfig(level=logging.DEBUG)


class TestWorld(TestCase):
    def test_world_initialization(self):
        world = World(scenario=scenario_data, initialization_year=1990)

        for i in range(20):
            world.step()

        assert 1 == 1
