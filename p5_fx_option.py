"""FX Option Calculator

CPSC 5061, Seattle University, P5

Function to calculate the fair price of a European FX option using Garman Kohlhagen model.
"""
import math
from datetime import date

from scipy.stats import norm

def years_apart(date1, date2):
    """Returns the fractional difference in years between the given dates.
    Assumes a 365-day year for the fractional part.
    >>> years_apart(date(1959, 5, 3), date(1960, 5, 3))
    1.0
    >>> years_apart(date(2004, 1, 1), date(2005, 1, 2)) # 365 days even if a leap year
    1.0027397260273974
    >>> years_apart(date(1959, 5, 1), date(2019, 6, 2))
    60.087671232876716
    >>> years_apart(date(2019, 7, 1), date(2019, 4, 1)) # reversed is ok
    0.2493150684931507
    """
    if date1 > date2:
        date1, date2 = date2, date1
    next_year = date(date1.year + 1, date1.month, date1.day)
    num_years = 0.0
    while next_year <= date2:
        date1 = next_year
        num_years += 1.0
        next_year = date(date1.year + 1, date1.month, date1.day)
    final_year = date2 - date1
    num_years += final_year.days / 365
    return num_years


def discount(rate, term):
    """Calculate the discount factor for given simple interest rate and term.
    present_value = future_value * discount(rate, term)
    >>> discount(0.123, 0.0)
    1.0
    >>> discount(0.03, 2.1)
    0.9389434736891332
    """
    return math.exp(-rate * term)


def fx_option_d1(strike, term, spot, volatility, domestic_rate, foreign_rate):
    """Calculate the d1 statistic for Garman Kohlhagen formula for fx option
    >>> '%.10f' % fx_option_d1(152, 91/365, 150, 0.13, 0.03, 0.04)
    '-0.2100058012'
    """
    numerator = math.log(spot / strike) + (domestic_rate - foreign_rate + volatility ** 2 / 2) * term
    #print('volatility is: ', volatility)
    #print('term is: ', term)
    denominator = volatility * math.sqrt(term)
    return numerator / denominator


def fx_option_d2(term, volatility, d1):
    """Calculate the d2 statistic for Garman Kolhagen formula for fx option
    >>> '%.10f' % fx_option_d2(91/365, 0.13, -0.21000580120118273)
    '-0.2749166990'
    """
    return d1 - volatility * math.sqrt(term)


def fx_option_price(call, strike, expiration, spot_date,
                    spot, volatility, domestic_rate, foreign_rate):
    """
    Calculates the fair price of a currency option.
    :param call:          True if this is a call option, False if this is a put option
    :param strike:        units of domestic currency per unit of foreign currency to be exchanged
    :param expiration:    date on which the exchange would take place if exercised
    :param spot_date:     date of valuation
    :param spot:          market exchange rate for fx exchanged on spot_date (same units as strike)
    :param volatility:    standard deviation of the logarithmic returns of holding this foreign currency (annualized)
    :param domestic_rate: simple risk-free interest rate from spot_date to expiration_date (annualized)
    :param foreign_rate:  simple risk-free interest rate from spot_date to expiration_date (annualized)
    :return:              option value in domestic currency for one unit of foreign currency

    >>> '%.10f' % fx_option_price(True, 152, date(2019,7,1), date(2019,4,1), 150, 0.13, 0.03, 0.04)
    '2.8110445343'
    >>> '%.10f' % fx_option_price(False, 152, date(2019,7,1), date(2019,4,1), 150, 0.13, 0.03, 0.04)
    '5.1668650332'
    """
    t = years_apart(spot_date, expiration)
    #print(t)
    d1 = fx_option_d1(strike, t, spot, volatility, domestic_rate, foreign_rate)
    #print(d1)
    d2 = fx_option_d2(t, volatility, d1)
    #print(d2)
    disc_spot = spot * discount(foreign_rate, t)
    disc_strike = strike * discount(domestic_rate, t)
    if call:
        price = disc_spot * norm.cdf(d1) - disc_strike * norm.cdf(d2)
    else:
        price = disc_strike * norm.cdf(-d2) - disc_spot * norm.cdf(-d1)
    return price

#'%.10f' % fx_option_price(True, 152, date(2019,7,1), date(2019,4,1), 150, 0.13, 0.03, 0.04)
    #'2.8110445343'