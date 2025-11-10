This repository represents my independent work from a group project investigating different hypotheses based on Bureau of Labor Statistics (BLS) data.

Data was taken frome the BLS, and the full process of data processing and cleaning is detailed in the "BLS Data" folder.

After cleaning the data, it was then uilized in analyzing trends in "hypo2.py". To assess correlations between past and future data, XGBoost was used for temporal modeling across sectors, leveraging two-period lag features. Performance was assessed using normalized RMSE with 5-fold cross-validation and benchmarked against a simple lagged baseline (Xₜ = Xₜ₋₂).

Based on the results, it was found that across many industries, past employment data meaningfully predicts future job openings, partially rejecting the hypothesis of no correlation.
The data visualizations show that a predictive XGBoost model using past data achieved low normalized root-mean-square error in sectors like private education (0.011) and professional services (0.011). While error reduction over the baseline is modest or negative (mean = –0.003), both XGBoost and the baseline relied on lagged predictors, suggesting that past data contains a meaningful signal for predicting future outcomes, though the added value of machine learning varies by sector.

For more detail, graph visualizations can be found in the "visualizations" folder.
