import numpy as np
import statsmodels.api as sm
from statsmodels.tools.eval_measures import rmse

def mlr_array(Y, X, MASK=None, MASKnodata=None, Ynodata=None, Xnodata=None):

    if MASK is not None:
        X = [np.where(MASK == MASKnodata, np.NaN, x) for x in X]
        Y = np.where(MASK == MASKnodata, np.NaN, Y)

    # also mask array's nodata (X's must have same nodata value!):
    if Ynodata is not None:
        Y = np.where(Y == Ynodata, np.NaN, Y)
    if Xnodata is not None:
        X = [np.where(X == Xnodata, np.NaN, x) for x in X]

    # reshape arrays:
    Y = np.reshape(Y, (Y.shape[0] * Y.shape[1]))
    X = [np.reshape(x, (x.shape[0] * x.shape[1])) for x in X]

    # mask NaNs:
    mask = 0
    for x in X:
        mask = np.where(np.isnan(x), 1, mask)

    mask = np.where(np.isnan(Y), 1, mask)

    X = [np.where(mask == 1, np.NaN, x) for x in X]
    Y = np.where(mask == 1, np.NaN, Y)

    # retrieve valid values:
    X = [x[~np.isnan(x)] for x in X]
    Y = Y[~np.isnan(Y)]

    # prepare predictors
    X = np.array(X).T
    X = sm.add_constant(X)

    model = sm.OLS(Y, X).fit()
    m_predict = model.predict(X)
    print('Model', 'RMSE', 'Predict', 'Y', 'X')
    m_list = [model, rmse(Y, m_predict), m_predict, Y, X]
    return m_list