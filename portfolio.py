import numpy as np
import pandas as pd
from scipy.optimize import minimize

def compute_returns(price_df):
    return price_df.pct_change().dropna()

def annualize_returns(returns):
    return returns.mean() * 252

def annualize_covariance(returns):
    return returns.cov() * 252

def portfolio_performance(weights, returns, cov_matrix):
    ret = np.dot(weights, returns)
    vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return ret, vol

def negative_sharpe(weights, returns, cov_matrix, risk_free_rate=0.05):
    p_ret, p_vol = portfolio_performance(weights, returns, cov_matrix)
    if p_vol == 0:
        return 0
    return -(p_ret - risk_free_rate) / p_vol

def minimize_variance(weights, cov_matrix):
    return np.dot(weights.T, np.dot(cov_matrix, weights))

def optimize_portfolio(returns_df, method="sharpe"):
    returns = annualize_returns(returns_df)
    cov = annualize_covariance(returns_df)
    num_assets = len(returns)
    constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
    bounds = tuple((0, 1) for _ in range(num_assets))
    init_guess = [1.0 / num_assets] * num_assets
    if method == "sharpe":
        result = minimize(negative_sharpe, init_guess, args=(returns, cov),
                          method="SLSQP", bounds=bounds, constraints=constraints)
    else:
        result = minimize(minimize_variance, init_guess, args=(cov,),
                          method="SLSQP", bounds=bounds, constraints=constraints)
    return result.x, returns, cov

def efficient_frontier(returns_df, num_points=40):
    returns = annualize_returns(returns_df)
    cov = annualize_covariance(returns_df)
    num_assets = len(returns)
    results = []
    for target in np.linspace(returns.min(), returns.max(), num_points):
        constraints = [
            {"type": "eq", "fun": lambda x: np.sum(x) - 1},
            {"type": "eq", "fun": lambda x, t=target: np.dot(x, returns) - t}
        ]
        bounds = tuple((0, 1) for _ in range(num_assets))
        init_guess = [1.0 / num_assets] * num_assets
        result = minimize(minimize_variance, init_guess, args=(cov,),
                          method="SLSQP", bounds=bounds, constraints=constraints)
        if result.success:
            w = result.x
            ret, vol = portfolio_performance(w, returns, cov)
            results.append({"Volatility": vol * 100, "Return": ret * 100})
    return pd.DataFrame(results) if results else pd.DataFrame(columns=["Volatility", "Return"])
