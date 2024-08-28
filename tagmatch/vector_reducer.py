from sklearn.decomposition import PCA
import pandas as pd
from sklearn.preprocessing import normalize

class PcaReducer:
    def __init__(self, n_components=100):
        self.pca = PCA(n_components=n_components)
        self.fitted = False
        
    def fit(self, dataframe:pd.DataFrame):
        if dataframe.ndim == 1:
            dataframe = dataframe.reshape(1, -1)
        normalized_vectors = normalize(dataframe)
        self.pca.fit(normalized_vectors)
        self.fitted = True
        
    def transform(self, dataframe:pd.DataFrame):
        if not self.fitted:
            return
        if dataframe.ndim == 1:
            dataframe = dataframe.reshape(1, -1)
            dataframe = normalize(dataframe)
        transformed_vectors = self.pca.transform(dataframe)
        if transformed_vectors.shape[0] == 1:
            return transformed_vectors.flatten()
        return transformed_vectors