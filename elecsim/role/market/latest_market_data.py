import logging
import warnings

from scipy.optimize import curve_fit, OptimizeWarning

from elecsim.data_manipulation.data_modifications.linear_regression import linear_regression

warnings.filterwarnings('error', category=OptimizeWarning)
import numpy as np

from elecsim.plants.plant_type.fuel_plant import FuelPlant

import elecsim.scenario.scenario_data as scenario
import elecsim.scenario.scenario_data

from elecsim.scenario.scenario_data import years_for_agents_to_predict_forward
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

            co2_price = self.agent_forecast_value("co2", look_back_years, years_for_agents_to_predict_forward)
            fuel_price = self.agent_forecast_value(power_plant.fuel.fuel_type, look_back_years, years_for_agents_to_predict_forward)

            co2_cost = power_plant.fuel.mwh_to_co2e_conversion_factor * (1 / power_plant.efficiency) * co2_price
            fuel_cost = fuel_price/power_plant.efficiency
            short_run_marginal_cost = variable_o_m_cost + co2_cost + fuel_cost
        else:
            short_run_marginal_cost = variable_o_m_cost

        return short_run_marginal_cost




    def agent_forecast_value(self, value_required, years_to_look_back,years_to_look_forward=None, demand_linear=False):
        years_for_regression = list(range(self.model.step_number-years_to_look_back-1, self.model.step_number-1))
        variable_data = self._get_variable_data(value_required)

        regression = self._get_yearly_change_for_regression(variable_data, years_for_regression)
        if value_required != "demand"  or demand_linear:
            next_value = linear_regression(regression, years_to_look_back, years_to_look_forward)
        else:
            next_value = self.fit_exponential_function(regression, years_to_look_back, years_to_look_forward, years_for_regression)
        return next_value



    # def agent_forecast_demand(self, years_to_look_back, years_to_predict_forward):
    #     years_for_regression = list(range(self.model.step_number-years_to_look_back-1, self.model.step_number-1))
    #     scenario.yearly_demand_change




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
        elif values_required == "biomass_wood" or values_required == "woodchip":
            return scenario.woodchip_price
        elif values_required == "biomass_poultry_litter" or values_required == "poultry_litter":
            return scenario.poultry_litter_price
        elif values_required == "oil":
            return scenario.oil_price
        elif values_required == "diesel" or values_required == "gas oil":
            return scenario.diesel_price
        elif values_required == "straw":
            return scenario.straw_price
        elif values_required == "meat":
            return scenario.meat_price
        elif values_required == "waste_post_2000":
            return scenario.waste_price_post_2000
        elif values_required == "waste_pre_2000":
            return scenario.waste_price_pre_2000
        elif values_required == "co2":
            return elecsim.scenario.scenario_data.carbon_price_scenario
        elif values_required == "demand":
            return scenario.yearly_demand_change
        else:
            raise ValueError("Could not find {}".format(values_required))


    def _get_yearly_change_for_regression(self, variable_data, years_for_regression):

        regression = [variable_data[i] if i > 0 else variable_data[0] for i in years_for_regression]
        return regression

    def fit_exponential_function(self, regression, years_to_look_back, years_to_look_forward, years_for_regression):
        def exponential_func(x, a, b, c):
            return a * np.exp(b * x) + c

        regression = np.array(regression)

        x = np.array(list(range(1,years_to_look_back+1)))
        y = exponential_func(regression, 2.5, 1.3, 0.5)
        try:
            popt, pcov = curve_fit(exponential_func, x, regression)
        except Warning:
            return self.agent_forecast_value("demand", years_to_look_back, years_to_look_forward, demand_linear=True)

        return exponential_func(np.array(years_to_look_forward), *popt)