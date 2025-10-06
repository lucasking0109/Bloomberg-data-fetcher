#!/usr/bin/env python3
"""
Enhanced Greeks Testing Tool - 找出為什麼Greeks抓不到
測試Reference Data API和各種欄位名稱
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import pandas as pd

def test_greeks():
    """測試Greeks抓取的各種方法"""

    print("="*60)
    print("🔍 Greeks API 深度診斷工具")
    print("="*60)

    try:
        import blpapi
        print("✅ Bloomberg API 已載入")
    except ImportError:
        print("❌ 無法載入 blpapi")
        return

    # 建立連線
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost("localhost")
    sessionOptions.setServerPort(8194)
    session = blpapi.Session(sessionOptions)

    if not session.start():
        print("❌ 無法連接Bloomberg")
        return

    print("✅ Bloomberg 連線成功")

    if not session.openService("//blp/refdata"):
        print("❌ 無法開啟Reference Data服務")
        return

    print("✅ Reference Data 服務已開啟")

    refDataService = session.getService("//blp/refdata")

    # 測試不同的Greeks欄位名稱
    print("\n" + "="*60)
    print("📊 測試 QQQ 選擇權 Greeks")
    print("="*60)

    # 使用實際的QQQ選擇權代碼
    # 格式: QQQ MM/DD/YY CXXX 或 PXXX
    today = datetime.now()
    friday = today + timedelta(days=(4-today.weekday()) % 7)  # 下個週五
    expiry_str = friday.strftime("%m/%d/%y")

    # 建立測試ticker
    test_ticker = f"QQQ US {expiry_str} C500 Equity"
    print(f"\n測試Ticker: {test_ticker}")

    # 測試各種可能的Greeks欄位名稱
    greek_fields_variants = [
        # 標準名稱
        ['DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO'],
        # 加上OPT前綴
        ['OPT_DELTA', 'OPT_GAMMA', 'OPT_THETA', 'OPT_VEGA', 'OPT_RHO'],
        # MID後綴
        ['DELTA_MID', 'GAMMA_MID', 'THETA_MID', 'VEGA_MID', 'RHO_MID'],
        # 使用IVOL相關
        ['OPT_DELTA_MID', 'OPT_GAMMA_MID', 'OPT_THETA_MID', 'OPT_VEGA_MID', 'OPT_RHO_MID'],
        # 其他可能的變體
        ['DELTA_LAST', 'GAMMA_LAST', 'THETA_LAST', 'VEGA_LAST', 'RHO_LAST'],
        # Bloomberg特殊欄位
        ['RT_DELTA', 'RT_GAMMA', 'RT_THETA', 'RT_VEGA', 'RT_RHO']
    ]

    working_fields = []

    for variant_idx, fields in enumerate(greek_fields_variants, 1):
        print(f"\n測試變體 {variant_idx}: {fields}")

        request = refDataService.createRequest("ReferenceDataRequest")
        request.append("securities", test_ticker)

        for field in fields:
            request.append("fields", field)

        # 加入一些確定能工作的欄位做對照
        request.append("fields", "PX_LAST")
        request.append("fields", "VOLUME")

        print(f"發送請求...")
        session.sendRequest(request)

        # 處理回應
        while True:
            ev = session.nextEvent(500)

            for msg in ev:
                if msg.hasElement("securityData"):
                    securityData = msg.getElement("securityData")

                    for i in range(securityData.numValues()):
                        security = securityData.getValue(i)

                        if security.hasElement("fieldData"):
                            fieldData = security.getElement("fieldData")

                            # 檢查每個欄位
                            for field in fields:
                                if fieldData.hasElement(field):
                                    value = fieldData.getElement(field).getValue()
                                    print(f"  ✅ {field}: {value}")
                                    working_fields.append(field)
                                else:
                                    print(f"  ❌ {field}: 不存在")

                            # 顯示對照欄位
                            if fieldData.hasElement("PX_LAST"):
                                px = fieldData.getElement("PX_LAST").getValue()
                                print(f"  📈 PX_LAST: {px} (對照)")

            if ev.eventType() == blpapi.Event.RESPONSE:
                break

    # 測試即時資料
    print("\n" + "="*60)
    print("📡 測試即時資料訂閱（可能有Greeks）")
    print("="*60)

    if session.openService("//blp/mktdata"):
        mktDataService = session.getService("//blp/mktdata")

        subscriptions = blpapi.SubscriptionList()
        subscriptions.add(test_ticker, "LAST_PRICE,BID,ASK,VOLUME", "", blpapi.CorrelationId(1))

        session.subscribe(subscriptions)

        print("等待即時資料（5秒）...")
        end_time = datetime.now() + timedelta(seconds=5)

        while datetime.now() < end_time:
            ev = session.nextEvent(100)
            for msg in ev:
                print(f"  收到: {msg.messageType()}")

        session.unsubscribe(subscriptions)

    # 總結
    print("\n" + "="*60)
    print("📋 診斷結果總結")
    print("="*60)

    if working_fields:
        print(f"✅ 找到可用的Greeks欄位:")
        for field in set(working_fields):
            print(f"   - {field}")
    else:
        print("❌ 無法找到任何Greeks欄位")
        print("\n可能原因：")
        print("1. Bloomberg Terminal 帳號沒有選擇權Greeks權限")
        print("2. 需要額外的數據訂閱（Options Analytics）")
        print("3. Greeks只能從其他欄位計算得出")

    # 測試其他相關欄位
    print("\n" + "="*60)
    print("🔧 測試替代方案欄位")
    print("="*60)

    alternative_fields = [
        "IVOL_MID",           # 隱含波動率
        "IVOL_BID",
        "IVOL_ASK",
        "OPT_UNDL_PX",        # 標的價格
        "DAYS_TO_EXPIRY",     # 到期天數
        "STRIKE_PX",          # 履約價
        "OPT_PUT_CALL",       # 選擇權類型
        "TIME_TO_EXPIRY",     # 到期時間
        "MONEYNESS"           # 價內外程度
    ]

    request = refDataService.createRequest("ReferenceDataRequest")
    request.append("securities", test_ticker)

    for field in alternative_fields:
        request.append("fields", field)

    session.sendRequest(request)

    available_fields = []
    while True:
        ev = session.nextEvent(500)

        for msg in ev:
            if msg.hasElement("securityData"):
                securityData = msg.getElement("securityData")

                for i in range(securityData.numValues()):
                    security = securityData.getValue(i)

                    if security.hasElement("fieldData"):
                        fieldData = security.getElement("fieldData")

                        for field in alternative_fields:
                            if fieldData.hasElement(field):
                                value = fieldData.getElement(field).getValue()
                                print(f"  ✅ {field}: {value}")
                                available_fields.append(field)
                            else:
                                print(f"  ❌ {field}: 不存在")

        if ev.eventType() == blpapi.Event.RESPONSE:
            break

    # 如果沒有Greeks，建議計算方式
    if not working_fields:
        print("\n" + "="*60)
        print("💡 建議：自行計算Greeks")
        print("="*60)

        if "IVOL_MID" in available_fields:
            print("✅ 有隱含波動率，可以使用Black-Scholes模型計算Greeks")
            print("\n需要的資料：")
            print("- 標的價格 (OPT_UNDL_PX 或 QQQ股價)")
            print("- 履約價 (從ticker解析)")
            print("- 到期時間 (DAYS_TO_EXPIRY)")
            print("- 隱含波動率 (IVOL_MID)")
            print("- 無風險利率 (可用固定值或抓取國債利率)")

            print("\n實作方式：")
            print("1. 安裝 scipy: pip install scipy")
            print("2. 使用 Black-Scholes 公式計算")
            print("3. 將計算結果加入DataFrame")

    session.stop()
    print("\n✅ 診斷完成")

if __name__ == "__main__":
    test_greeks()