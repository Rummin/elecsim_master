import logging
from src.data_manipulation.data_modifications.linear_regression import linear_regression
from src.plants.fuel.fuel_registry.fuel_registry import plant_type_to_fuel, fuel_registry
from src.plants.plant_costs.estimate_costs.estimate_costs import create_power_plant
from src.plants.plant_registry import PlantRegistry

from src.plants.plant_type.fuel_plant import FuelPlant

import src.scenario.scenario_data as scenario
logger = logging.getLogger(__name__)

"""
File name: current_market_data
Date created: 29/12/2018
Feature: # Data which collates market information for generator companies when making decisions about investments.
"""

__author__ = "Alexander Kell"
__copyright__ = "Copyright 2018, Alexander Kell"
__license__ = "MIT"
__email__ = "alexander@kell.es"


class LatestMarketData:

    def __init__(self, model):
        self.model = model
        self.demand = self.model.demand


    def get_predicted_marginal_cost(self, power_plant, look_back_years):

        variable_o_m_cost = power_plant.variable_o_and_m_per_mwh

        if isinstance(power_plant, FuelPlant):

            co2_price = self.agent_forecast_value("co2", look_back_years)
            fuel_price = self.agent_forecast_value(power_plant.fuel.fuel_type, look_back_years)
            demand_level = self.agent_forecast_value("demand", look_back_years)

            co2_cost = power_plant.fuel.mwh_to_co2e_conversion_factor * (1 / power_plant.efficiency) * co2_price
            fuel_cost = fuel_price/power_plant.efficiency
            logger.debug("predicted co2: {}, fuel price: {}, demand: {}".format(co2_price, fuel_price, demand_level))
            logger.debug("co2_cost: {}, fuel_cost: {}, variable o_m cost: {}, efficiency: {}".format(co2_cost, fuel_cost, variable_o_m_cost, power_plant.efficiency))
            short_run_marginal_cost = variable_o_m_cost + co2_cost + fuel_cost
        else:
            short_run_marginal_cost = variable_o_m_cost

        return short_run_marginal_cost




    def agent_forecast_value(self, value_required, years_to_look_back):
        years_for_regression = list(range(self.model.step_number-years_to_look_back-1, self.model.step_number-1))
        value_data = self._get_variable_data(value_required)
        regression = self._get_yearly_change_for_regression(value_data, years_for_regression)

        logger.debug(regression)

        next_value = linear_regression(regression, years_to_look_back)
        return next_value

    @staticmethod
    def _get_yearly_change_for_regression(value_required, years_for_regression):
        regression = [value_required[i] if i > 0 else value_required[0] for i in years_for_regression]
        return regression


    @staticmethod
    def _get_variable_data(values_required):
        try:
            values_required = values_required.lower()
        except:
            raise ValueError("Price required must be a string, not a {}".format(type(values_required)))
        if values_required == "coal":
            return scenario.coal_price
        elif values_required == "gas":
            return scenario.gas_price
        elif values_required == "uranium":
            return scenario.uranium_price
        elif values_required == "co2":
            return scenario.carbon_price_scenario
        elif values_required == "demand":
            return scenario.yearly_demand_change
        else:
            raise ValueError("Could not find {}".format(values_required))



