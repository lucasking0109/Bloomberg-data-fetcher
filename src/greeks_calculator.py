#!/usr/bin/env python3
"""
Greeks Calculator - Black-Scholes計算器
當Bloomberg不提供Greeks時，使用此模組自行計算
"""

import numpy as np
from scipy.stats import norm
from typing import Optional
import pandas as pd


class GreeksCalculator:
    """使用Black-Scholes模型計算選擇權Greeks"""

    def __init__(self, risk_free_rate: float = 0.05):
        """
        初始化計算器

        Args:
            risk_free_rate: 無風險利率（預設5%）
        """
        self.risk_free_rate = risk_free_rate

    def calculate_d1_d2(self, S: float, K: float, T: float, r: float, sigma: float):
        """計算Black-Scholes的d1和d2參數"""
        if T <= 0 or sigma <= 0:
            return np.nan, np.nan

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return d1, d2

    def calculate_delta(self, S: float, K: float, T: float, r: float, sigma: float,
                       option_type: str = 'C') -> float:
        """
        計算Delta

        Args:
            S: 標的價格
            K: 履約價
            T: 到期時間（年）
            r: 無風險利率
            sigma: 隱含波動率
            option_type: 'C' for call, 'P' for put

        Returns:
            Delta值
        """
        d1, _ = self.calculate_d1_d2(S, K, T, r, sigma)

        if np.isnan(d1):
            return np.nan

        if option_type.upper() == 'C':
            return norm.cdf(d1)
        else:
            return norm.cdf(d1) - 1

    def calculate_gamma(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        計算Gamma（Call和Put相同）

        Returns:
            Gamma值
        """
        d1, _ = self.calculate_d1_d2(S, K, T, r, sigma)

        if np.isnan(d1) or T <= 0 or sigma <= 0:
            return np.nan

        return norm.pdf(d1) / (S * sigma * np.sqrt(T))

    def calculate_theta(self, S: float, K: float, T: float, r: float, sigma: float,
                       option_type: str = 'C') -> float:
        """
        計算Theta（每天的時間價值衰減）

        Returns:
            Theta值（每天）
        """
        d1, d2 = self.calculate_d1_d2(S, K, T, r, sigma)

        if np.isnan(d1) or T <= 0:
            return np.nan

        if option_type.upper() == 'C':
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
                    - r * K * np.exp(-r * T) * norm.cdf(d2))
        else:
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
                    + r * K * np.exp(-r * T) * norm.cdf(-d2))

        return theta / 365  # 轉換為每天

    def calculate_vega(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        計算Vega（對隱含波動率的敏感度）

        Returns:
            Vega值（每1%波動率變化）
        """
        d1, _ = self.calculate_d1_d2(S, K, T, r, sigma)

        if np.isnan(d1) or T <= 0:
            return np.nan

        return S * norm.pdf(d1) * np.sqrt(T) / 100  # 轉換為每1%變化

    def calculate_rho(self, S: float, K: float, T: float, r: float, sigma: float,
                     option_type: str = 'C') -> float:
        """
        計算Rho（對利率的敏感度）

        Returns:
            Rho值（每1%利率變化）
        """
        _, d2 = self.calculate_d1_d2(S, K, T, r, sigma)

        if np.isnan(d2) or T <= 0:
            return np.nan

        if option_type.upper() == 'C':
            rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        else:
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)

        return rho / 100  # 轉換為每1%變化

    def calculate_all_greeks(self, S: float, K: float, T: float,
                           sigma: float, option_type: str = 'C') -> dict:
        """
        計算所有Greeks

        Args:
            S: 標的價格
            K: 履約價
            T: 到期時間（年）
            sigma: 隱含波動率
            option_type: 'C' for call, 'P' for put

        Returns:
            包含所有Greeks的字典
        """
        r = self.risk_free_rate

        return {
            'DELTA': self.calculate_delta(S, K, T, r, sigma, option_type),
            'GAMMA': self.calculate_gamma(S, K, T, r, sigma),
            'THETA': self.calculate_theta(S, K, T, r, sigma, option_type),
            'VEGA': self.calculate_vega(S, K, T, r, sigma),
            'RHO': self.calculate_rho(S, K, T, r, sigma, option_type)
        }

    def add_greeks_to_dataframe(self, df: pd.DataFrame,
                               spot_col: str = 'OPT_UNDL_PX',
                               strike_col: str = 'strike',
                               expiry_col: str = 'expiry',
                               ivol_col: str = 'IVOL_MID',
                               type_col: str = 'option_type') -> pd.DataFrame:
        """
        為DataFrame添加計算的Greeks

        Args:
            df: 包含選擇權資料的DataFrame
            spot_col: 標的價格欄位名
            strike_col: 履約價欄位名
            expiry_col: 到期日欄位名
            ivol_col: 隱含波動率欄位名
            type_col: 選擇權類型欄位名

        Returns:
            添加了Greeks的DataFrame
        """
        from datetime import datetime

        df = df.copy()

        # 初始化Greeks欄位
        for greek in ['DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO']:
            df[greek] = np.nan

        # 計算每一行的Greeks
        for idx, row in df.iterrows():
            try:
                # 取得必要參數
                S = float(row.get(spot_col, np.nan))
                K = float(row.get(strike_col, np.nan))
                sigma = float(row.get(ivol_col, np.nan))
                opt_type = str(row.get(type_col, 'C'))

                # 計算到期時間（年）
                if expiry_col in row:
                    if isinstance(row[expiry_col], str):
                        expiry = datetime.strptime(row[expiry_col], "%Y%m%d")
                    else:
                        expiry = row[expiry_col]

                    T = (expiry - datetime.now()).days / 365.0
                else:
                    T = 30 / 365.0  # 預設30天

                # 確保所有參數有效
                if np.isnan(S) or np.isnan(K) or np.isnan(sigma) or T <= 0:
                    continue

                # 隱含波動率需要從百分比轉換為小數
                if sigma > 1:
                    sigma = sigma / 100

                # 計算Greeks
                greeks = self.calculate_all_greeks(S, K, T, sigma, opt_type)

                # 更新DataFrame
                for greek, value in greeks.items():
                    df.at[idx, greek] = value

            except Exception as e:
                # 如果計算失敗，保持NaN
                continue

        return df


def demo_calculation():
    """示範Greeks計算"""
    print("="*60)
    print("📊 Black-Scholes Greeks 計算示範")
    print("="*60)

    calculator = GreeksCalculator(risk_free_rate=0.05)

    # 範例參數
    S = 500      # QQQ價格
    K = 505      # 履約價
    T = 30/365   # 30天到期
    sigma = 0.20 # 20%隱含波動率
    opt_type = 'C'  # Call option

    print(f"\n輸入參數：")
    print(f"標的價格 (S): ${S}")
    print(f"履約價 (K): ${K}")
    print(f"到期時間 (T): {T*365:.0f} 天")
    print(f"隱含波動率 (σ): {sigma*100:.1f}%")
    print(f"無風險利率 (r): {calculator.risk_free_rate*100:.1f}%")
    print(f"選擇權類型: {opt_type}")

    # 計算Greeks
    greeks = calculator.calculate_all_greeks(S, K, T, sigma, opt_type)

    print(f"\n計算結果：")
    for greek, value in greeks.items():
        if not np.isnan(value):
            print(f"{greek:8s}: {value:8.4f}")
        else:
            print(f"{greek:8s}: N/A")

    # 解釋意義
    print(f"\n意義說明：")
    print(f"Delta: 標的價格變化$1，選擇權價格變化${greeks['DELTA']:.2f}")
    print(f"Gamma: Delta變化率 = {greeks['GAMMA']:.4f}")
    print(f"Theta: 每天時間價值損失${greeks['THETA']:.2f}")
    print(f"Vega: 波動率變化1%，選擇權價格變化${greeks['VEGA']:.2f}")
    print(f"Rho: 利率變化1%，選擇權價格變化${greeks['RHO']:.2f}")


if __name__ == "__main__":
    demo_calculation()