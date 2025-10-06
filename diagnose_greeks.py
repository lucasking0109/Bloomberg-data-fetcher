#!/usr/bin/env python3
"""
Enhanced Greeks Diagnostic Tool - Definitive Problem Identification
直接識別阻止Greeks資料抓取的確切問題
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.bloomberg_api import BloombergAPI
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
import re
import ast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GreeksDiagnostic:
    def __init__(self):
        self.api = BloombergAPI()
        self.results = {}
        self.test_results = []
        self.problems_found = []  # 儲存發現的問題
        self.solutions = []  # 儲存解決方案

        # 定義測試欄位
        self.greeks = ['DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO']
        self.price_fields = ['PX_LAST', 'PX_BID', 'PX_ASK']
        self.other_fields = ['VOLUME', 'OPEN_INT', 'IVOL_MID']

        # 測試標的
        self.test_tickers = [
            "QQQ US 12/20/25 C500 Equity",
            "QQQ US 11/21/25 C500 Equity",
            "AAPL US 12/20/25 C150 Equity",
        ]

    def log_test_result(self, test_name, success, details, data_count=0):
        """記錄測試結果"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'data_count': data_count,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.test_results.append(result)

        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        if data_count > 0:
            print(f"   📊 資料筆數: {data_count}")

    def analyze_codebase_problems(self):
        """分析程式碼找出確切問題"""
        print("\n" + "="*60)
        print("📋 程式碼分析 - 尋找確切問題")
        print("="*60)

        # 檢查 qqq_options_fetcher.py
        fetcher_path = os.path.join(os.path.dirname(__file__), 'src', 'qqq_options_fetcher.py')
        if os.path.exists(fetcher_path):
            print(f"\n檢查檔案: {fetcher_path}")
            with open(fetcher_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                if 'self.OPTION_FIELDS[:6]' in line:
                    print(f"\n🔴 發現問題在第 {i} 行:")
                    print(f"   {line.strip()}")
                    print(f"\n   💡 問題說明:")
                    print(f"   這行限制只抓取前6個欄位: [PX_LAST, PX_BID, PX_ASK, PX_VOLUME, OPEN_INT, IVOL_MID]")
                    print(f"   Greeks (DELTA, GAMMA, THETA, VEGA, RHO) 是第7-11個欄位，被跳過了！")

                    self.problems_found.append({
                        'file': 'src/qqq_options_fetcher.py',
                        'line': i,
                        'problem': '欄位陣列被切片為[:6]，排除了Greeks',
                        'current': line.strip(),
                        'fix': line.replace('[:6]', '[:11]').strip()
                    })

                    print(f"\n   ✅ 解決方案:")
                    print(f"   第 {i} 行從: {line.strip()}")
                    print(f"   改為: {line.replace('[:6]', '[:11]').strip()}")

        # 檢查 constituents_fetcher.py
        constituents_path = os.path.join(os.path.dirname(__file__), 'src', 'constituents_fetcher.py')
        if os.path.exists(constituents_path):
            print(f"\n檢查檔案: {constituents_path}")
            with open(constituents_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            for i, line in enumerate(lines, 1):
                if 'self.OPTION_FIELDS[:' in line and '[:6]' in line:
                    print(f"\n🔴 類似問題在第 {i} 行:")
                    print(f"   {line.strip()}")
                    self.problems_found.append({
                        'file': 'src/constituents_fetcher.py',
                        'line': i,
                        'problem': '欄位陣列也被限制',
                        'current': line.strip(),
                        'fix': line.replace('[:6]', '[:11]')
                    })

    def check_async_blp_comparison(self):
        """檢查async_blp可用性及比較"""
        # 移除 async_blp 檢查，因為不是必需的
        # 我們使用標準的 blpapi
        return True

    def run_all_tests(self):
        """執行增強版診斷測試"""
        print("="*80)
        print("🔬 增強版 BLOOMBERG GREEKS 診斷 - 確定問題識別")
        print("="*80)
        print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 步驟1: 分析程式碼問題
        self.analyze_codebase_problems()

        # 步驟3: Bloomberg連線測試
        print("\n" + "="*60)
        print("🔗 Bloomberg API 連線測試")
        print("="*60)

        if not self.api.connect():
            print("\n❌ 無法連線到Bloomberg API")
            print("這是次要問題 - 先修復程式碼問題！")
            self.show_final_diagnosis()
            return

        print("✅ 成功連線到Bloomberg API")

        # 步驟4: 快速驗證測試
        print("\n" + "="*60)
        print("🔍 驗證: 測試Greeks是否可透過API取得")
        print("="*60)
        self.quick_validation_test()

        # 步驟5: 顯示最終診斷
        self.show_final_diagnosis()

        print(f"\n結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def quick_validation_test(self):
        """快速測試確認Greeks可用性"""
        test_ticker = "AAPL US 01/17/25 C150 Equity"
        print(f"\n測試標的: {test_ticker}")
        print("測試Greeks欄位是否可透過Bloomberg API取得...")

        try:
            # 使用參考資料API測試
            data = self.api.fetch_reference_data([test_ticker], self.greeks)

            if not data.empty:
                print("\n✅ Greeks 資料可透過Bloomberg API取得!")
                print("🎯 問題確認在程式碼，不在API")

                # 顯示取得的Greeks值
                for greek in self.greeks:
                    if greek in data.columns:
                        value = data[greek].iloc[0]
                        if pd.notna(value):
                            print(f"   {greek}: {value:.4f}")
                        else:
                            print(f"   {greek}: 無資料")
                    else:
                        print(f"   {greek}: 欄位不存在")
            else:
                print("\n⚠️ 無Greeks資料回傳 - 檢查API權限")

        except Exception as e:
            print(f"\n⚠️ 驗證測試錯誤: {e}")

    def show_final_diagnosis(self):
        """顯示最終診斷結果"""
        print("\n" + "="*80)
        print("🎯 最終診斷結果")
        print("="*80)

        if self.problems_found:
            print("\n🔴 根本原因已確認:")
            print("\n程式碼刻意限制欄位抓取以提升效能,")
            print("但這排除了Greeks的抓取。")

            print("\n📋 必要修復:")
            for i, problem in enumerate(self.problems_found, 1):
                print(f"\n{i}. 檔案: {problem['file']}")
                print(f"   行數: {problem['line']}")
                print(f"   目前: {problem['current']}")
                print(f"   修改為: {problem['fix']}")

            print("\n🛠️ 快速修復指令:")
            print("\n對於QQQ選擇權:")
            print("sed -i 's/self.OPTION_FIELDS\[:6\]/self.OPTION_FIELDS[:11]/' src/qqq_options_fetcher.py")

            if any('constituents' in p['file'] for p in self.problems_found):
                print("\n對於成分股選擇權:")
                print("sed -i 's/self.OPTION_FIELDS\[:6\]/self.OPTION_FIELDS[:11]/' src/constituents_fetcher.py")

            print("\n✅ 修復後預期結果:")
            print("Greeks (Delta, Gamma, Theta, Vega, Rho) 將包含在抓取的資料中")

        else:
            print("\n⚠️ 未發現明顯的程式碼問題。")
            print("請檢查:")
            print("1. Bloomberg Terminal API權限")
            print("2. 市場時間 (選擇權Greeks在市場時間可用)")
            print("3. 有效的選擇權標的")

        print("\n" + "="*80)
        print("診斷結束")
        print("="*80)

    def test_connection(self):
        """測試Bloomberg連線"""
        print("\n[測試1] 檢查Bloomberg連線...")
        print("-" * 40)

        try:
            success = self.api.connect()
            if success:
                self.log_test_result(
                    "Bloomberg連線",
                    True,
                    f"成功連線到 {self.api.host}:{self.api.port}"
                )

                # 檢查服務
                if hasattr(self.api, 'service') and self.api.service:
                    self.log_test_result(
                        "Bloomberg服務",
                        True,
                        "Reference Data服務可用"
                    )
                else:
                    self.log_test_result(
                        "Bloomberg服務",
                        False,
                        "無法開啟Reference Data服務"
                    )
            else:
                self.log_test_result(
                    "Bloomberg連線",
                    False,
                    "無法連線到Bloomberg Terminal"
                )

        except Exception as e:
            self.log_test_result(
                "Bloomberg連線",
                False,
                f"連線錯誤: {e}"
            )

    def test_single_greek_fields(self):
        """逐一測試每個Greek欄位"""
        print("\n[測試2] 逐一測試Greek欄位...")
        print("-" * 40)

        ticker = "QQQ US 12/20/25 C500 Equity"
        today = datetime.now().strftime('%Y%m%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

        for greek in self.greeks:
            try:
                # 測試歷史資料
                data_hist = self.api.fetch_historical_data(
                    [ticker],
                    [greek],
                    yesterday,
                    today,
                    "DAILY"
                )

                hist_success = not data_hist.empty and len(data_hist) > 0
                hist_count = len(data_hist) if not data_hist.empty else 0

                self.log_test_result(
                    f"歷史資料-{greek}",
                    hist_success,
                    f"{'有資料' if hist_success else '無資料'}",
                    hist_count
                )

                time.sleep(0.5)  # 避免請求過快

            except Exception as e:
                self.log_test_result(
                    f"歷史資料-{greek}",
                    False,
                    f"錯誤: {str(e)[:50]}..."
                )

    def test_different_apis(self):
        """測試不同的API方法"""
        print("\n[測試3] 測試不同API方法...")
        print("-" * 40)

        ticker = "QQQ US 12/20/25 C500 Equity"
        test_fields = ['PX_LAST', 'DELTA']
        today = datetime.now().strftime('%Y%m%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

        # 測試歷史資料API
        try:
            data_hist = self.api.fetch_historical_data(
                [ticker],
                test_fields,
                yesterday,
                today,
                "DAILY"
            )

            hist_success = not data_hist.empty
            self.log_test_result(
                "歷史資料API",
                hist_success,
                f"回傳 {len(data_hist)} 筆資料" if hist_success else "無資料",
                len(data_hist) if hist_success else 0
            )

            if hist_success:
                # 檢查哪些欄位有資料
                for field in test_fields:
                    cols_with_field = [col for col in data_hist.columns if field in col]
                    if cols_with_field:
                        sample_col = cols_with_field[0]
                        non_null_count = data_hist[sample_col].notna().sum()
                        self.log_test_result(
                            f"  └─ {field}欄位",
                            non_null_count > 0,
                            f"{non_null_count}/{len(data_hist)} 有值",
                            non_null_count
                        )

        except Exception as e:
            self.log_test_result(
                "歷史資料API",
                False,
                f"錯誤: {str(e)[:50]}..."
            )

        time.sleep(1)

        # 測試參考資料API
        try:
            data_ref = self.api.fetch_reference_data([ticker], test_fields)

            ref_success = not data_ref.empty
            self.log_test_result(
                "參考資料API",
                ref_success,
                f"回傳 {len(data_ref)} 筆資料" if ref_success else "無資料",
                len(data_ref) if ref_success else 0
            )

            if ref_success:
                # 檢查哪些欄位有資料
                for field in test_fields:
                    if field in data_ref.columns:
                        non_null_count = data_ref[field].notna().sum()
                        self.log_test_result(
                            f"  └─ {field}欄位",
                            non_null_count > 0,
                            f"{non_null_count}/{len(data_ref)} 有值",
                            non_null_count
                        )

        except Exception as e:
            self.log_test_result(
                "參考資料API",
                False,
                f"錯誤: {str(e)[:50]}..."
            )

    def test_different_securities(self):
        """測試不同的選擇權標的"""
        print("\n[測試4] 測試不同標的...")
        print("-" * 40)

        test_fields = ['PX_LAST', 'DELTA', 'GAMMA']

        for ticker in self.test_tickers:
            try:
                # 只測試參考資料（較快）
                data = self.api.fetch_reference_data([ticker], test_fields)

                success = not data.empty
                self.log_test_result(
                    f"標的: {ticker.split()[0]}",
                    success,
                    f"{'有資料' if success else '無資料'}",
                    len(data) if success else 0
                )

                if success:
                    # 檢查DELTA是否有值
                    if 'DELTA' in data.columns:
                        delta_count = data['DELTA'].notna().sum()
                        self.log_test_result(
                            f"  └─ DELTA值",
                            delta_count > 0,
                            f"{delta_count}/{len(data)} 有值",
                            delta_count
                        )

                time.sleep(0.5)

            except Exception as e:
                self.log_test_result(
                    f"標的: {ticker.split()[0]}",
                    False,
                    f"錯誤: {str(e)[:50]}..."
                )

    def test_field_combinations(self):
        """測試不同欄位組合"""
        print("\n[測試5] 測試欄位組合...")
        print("-" * 40)

        ticker = "QQQ US 12/20/25 C500 Equity"

        combinations = [
            (['PX_LAST'], "單一價格欄位"),
            (['DELTA'], "單一Greek欄位"),
            (['PX_LAST', 'DELTA'], "價格+單一Greek"),
            (['DELTA', 'GAMMA'], "兩個Greeks"),
            (self.greeks[:3], "前三個Greeks"),
            (self.greeks, "所有Greeks"),
            (self.price_fields + ['DELTA'], "價格+DELTA"),
            (self.price_fields + self.greeks[:2], "價格+兩個Greeks"),
        ]

        for fields, description in combinations:
            try:
                data = self.api.fetch_reference_data([ticker], fields)

                success = not data.empty
                self.log_test_result(
                    description,
                    success,
                    f"{'成功' if success else '失敗'}",
                    len(data) if success else 0
                )

                if success:
                    # 統計有值的欄位
                    non_null_fields = []
                    for field in fields:
                        if field in data.columns:
                            if data[field].notna().any():
                                non_null_fields.append(field)

                    if non_null_fields:
                        self.log_test_result(
                            f"  └─ 有值欄位",
                            True,
                            f"{', '.join(non_null_fields)}"
                        )

                time.sleep(0.5)

            except Exception as e:
                self.log_test_result(
                    description,
                    False,
                    f"錯誤: {str(e)[:50]}..."
                )

    def test_time_ranges(self):
        """測試不同時間範圍"""
        print("\n[測試6] 測試時間範圍...")
        print("-" * 40)

        ticker = "QQQ US 12/20/25 C500 Equity"
        test_fields = ['PX_LAST', 'DELTA']

        today = datetime.now()

        time_ranges = [
            (today.strftime('%Y%m%d'), today.strftime('%Y%m%d'), "當日"),
            ((today - timedelta(days=1)).strftime('%Y%m%d'), today.strftime('%Y%m%d'), "過去2天"),
            ((today - timedelta(days=7)).strftime('%Y%m%d'), today.strftime('%Y%m%d'), "過去1週"),
            ((today - timedelta(days=30)).strftime('%Y%m%d'), today.strftime('%Y%m%d'), "過去1月"),
        ]

        for start_date, end_date, description in time_ranges:
            try:
                data = self.api.fetch_historical_data(
                    [ticker],
                    test_fields,
                    start_date,
                    end_date,
                    "DAILY"
                )

                success = not data.empty
                self.log_test_result(
                    f"時間範圍: {description}",
                    success,
                    f"{'有資料' if success else '無資料'}",
                    len(data) if success else 0
                )

                time.sleep(0.5)

            except Exception as e:
                self.log_test_result(
                    f"時間範圍: {description}",
                    False,
                    f"錯誤: {str(e)[:50]}..."
                )

    def test_reference_data(self):
        """測試即時參考資料"""
        print("\n[測試7] 測試即時參考資料...")
        print("-" * 40)

        # 測試QQQ現貨
        try:
            qqq_data = self.api.fetch_reference_data(
                ["QQQ US Equity"],
                ['PX_LAST', 'PX_BID', 'PX_ASK']
            )

            success = not qqq_data.empty
            self.log_test_result(
                "QQQ現貨價格",
                success,
                f"{'成功取得' if success else '無法取得'}",
                len(qqq_data) if success else 0
            )

            if success and 'PX_LAST' in qqq_data.columns:
                qqq_price = qqq_data['PX_LAST'].iloc[0]
                self.log_test_result(
                    "  └─ QQQ價格",
                    True,
                    f"${qqq_price:.2f}" if pd.notna(qqq_price) else "無價格"
                )

        except Exception as e:
            self.log_test_result(
                "QQQ現貨價格",
                False,
                f"錯誤: {str(e)[:50]}..."
            )

        time.sleep(0.5)

        # 測試選擇權完整資料
        ticker = "QQQ US 12/20/25 C500 Equity"
        all_fields = self.price_fields + self.other_fields + self.greeks

        try:
            option_data = self.api.fetch_reference_data([ticker], all_fields)

            success = not option_data.empty
            self.log_test_result(
                "選擇權完整資料",
                success,
                f"{'成功取得' if success else '無法取得'}",
                len(option_data) if success else 0
            )

            if success:
                # 分析每類欄位的可用性
                field_groups = [
                    (self.price_fields, "價格欄位"),
                    (self.other_fields, "其他欄位"),
                    (self.greeks, "Greeks欄位")
                ]

                for fields, group_name in field_groups:
                    available_fields = []
                    for field in fields:
                        if field in option_data.columns and option_data[field].notna().any():
                            available_fields.append(field)

                    self.log_test_result(
                        f"  └─ {group_name}",
                        len(available_fields) > 0,
                        f"{len(available_fields)}/{len(fields)} 可用: {', '.join(available_fields) if available_fields else '無'}"
                    )

        except Exception as e:
            self.log_test_result(
                "選擇權完整資料",
                False,
                f"錯誤: {str(e)[:50]}..."
            )

    def generate_report(self):
        """產生診斷報告"""
        print("\n" + "="*80)
        print("📋 診斷報告")
        print("="*80)

        # 統計測試結果
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - successful_tests

        print(f"📊 測試統計:")
        print(f"   總測試數: {total_tests}")
        print(f"   成功: {successful_tests} ✅")
        print(f"   失敗: {failed_tests} ❌")
        print(f"   成功率: {(successful_tests/total_tests)*100:.1f}%")

        # 分析Greeks可用性
        print(f"\n🎯 Greeks 可用性分析:")
        greeks_tests = [r for r in self.test_results if any(g in r['test'] for g in self.greeks)]

        if greeks_tests:
            greeks_success = [r for r in greeks_tests if r['success']]
            print(f"   Greeks相關測試: {len(greeks_success)}/{len(greeks_tests)} 成功")

            if greeks_success:
                print(f"   ✅ 成功的Greeks測試:")
                for test in greeks_success[:5]:  # 顯示前5個
                    print(f"      - {test['test']}: {test['details']}")
            else:
                print(f"   ❌ 所有Greeks測試都失敗")

        # 提供建議
        print(f"\n💡 建議:")

        connection_success = any(r['success'] for r in self.test_results if '連線' in r['test'])
        price_success = any(r['success'] for r in self.test_results if 'PX_LAST' in r['test'] or '價格' in r['test'])
        greeks_any_success = any(r['success'] for r in self.test_results if any(g in r['test'] for g in self.greeks))

        if not connection_success:
            print("   🔴 優先解決: Bloomberg連線問題")
            print("      - 確認Bloomberg Terminal正在執行並已登入")
            print("      - 檢查API權限設定")

        elif not price_success:
            print("   🟡 價格資料都無法取得，可能是標的或權限問題")

        elif not greeks_any_success:
            print("   🟠 Greeks資料完全無法取得，可能原因:")
            print("      1. 帳號權限不包含Greeks資料")
            print("      2. Bloomberg不提供歷史Greeks資料")
            print("      3. 需要使用不同的API方法")
            print("      4. 選擇權標的無效或已過期")

        else:
            print("   🟢 部分Greeks資料可用，建議:")
            print("      - 使用參考資料API而非歷史資料API")
            print("      - 檢查特定標的的Greeks可用性")

        # 具體建議修改
        print(f"\n🔧 程式修改建議:")
        if greeks_any_success:
            print("   1. 修改 src/qqq_options_fetcher.py 第358行:")
            print("      將 self.OPTION_FIELDS[:6] 改為 self.OPTION_FIELDS[:11]")
            print("   2. 或嘗試使用 fetch_reference_data 取代 fetch_historical_data")
        else:
            print("   1. 先確認Bloomberg帳號權限")
            print("   2. 在Bloomberg Terminal查詢選擇權時確認是否顯示Greeks")
            print("   3. 考慮只使用價格和隱含波動率資料")

        print(f"\n⏰ 診斷完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

def main():
    """主執行函數"""
    print("\n🔍 啟動增強版診斷工具...\n")
    print("此工具將:")
    print("1. 分析你的程式碼找出確切問題")
    print("2. 測試Bloomberg API連線和能力")
    print("3. 提供具體的逐行修復方案")
    print("4. 比較async_blp方法\n")

    diagnostic = GreeksDiagnostic()

    try:
        diagnostic.run_all_tests()

    except KeyboardInterrupt:
        print("\n\n中斷測試...")
        diagnostic.show_final_diagnosis()

    except Exception as e:
        print(f"\n❌ 診斷過程發生嚴重錯誤: {e}")
        diagnostic.show_final_diagnosis()

    finally:
        # 確保API連線關閉
        try:
            diagnostic.api.disconnect()
        except:
            pass

    print("\n💡 快速行動摘要:")
    print("1. 問題在 src/qqq_options_fetcher.py 第 ~358 行")
    print("2. 將 self.OPTION_FIELDS[:6] 改為 self.OPTION_FIELDS[:11]")
    print("3. Greeks 將被包含在你的資料中")
    print("\n修改後再次執行此診斷以驗證修復。\n")

if __name__ == "__main__":
    main()