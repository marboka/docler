from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pandas as pd

class PcaReducer:
    def __init__(self, n_components=100):
        self.pca = PCA(n_components=n_components)
        self.std_scaler = StandardScaler()
        self.fitted = False
        
    def fit(self, dataframe:pd.DataFrame):
        if dataframe.ndim == 1:
            dataframe = dataframe.reshape(1, -1)
        scaled_df = self.std_scaler.fit_transform(dataframe)
        self.pca.fit(scaled_df)
        self.fitted = True
        
    def transform(self, dataframe:pd.DataFrame):
        if not self.fitted:
            return
        if dataframe.ndim == 1:
            dataframe = dataframe.reshape(1, -1)
        scaled_df = self.std_scaler.fit_transform(dataframe)
        return self.pca.transform(scaled_df)