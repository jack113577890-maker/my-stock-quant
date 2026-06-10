import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import mplfinance as mpf
import logging
import os
import sys

# ─── 網頁基本設定 (必須放在程式第一行) ───
st.set_page_config(
    page_title="STOCK_QUANT // 量化終端",
    page_icon="⚡",
    layout="wide"  
)

# ─── 🎮 核心極客外掛：透過 CSS 注入，將 Streamlit 背景與字體強行魔改成「最高亮度電競風」 ───
st.markdown("""
    <style>
        /* 整體背景與字體顏色魔改，強制所有人都是純黑 */
        .stApp, div[data-testid="stMarkdownContainer"] {
            background-color: #050505 !important;
            color: #ffffff !important;
        }
        
        /* 大標題：電光青發光 */
        h1 {
            color: #00ffff !important;
            text-shadow: 0 0 10px #00ffff !important;
            font-family: 'Courier New', Courier, monospace !important;
            font-weight: bold !important;
            margin-top: -10px !important; 
            padding-top: 0px !important;
        }
        
        /* 副標題型態微調 */
        h3 {
            font-family: 'Courier New', Courier, monospace !important;
            background-color: transparent !important;
            background: transparent !important;
            margin-top: 5px !important;
            margin-bottom: 5px !important;
        }
        
        /* 單行代碼 `code` 標籤的純黑透明化 */
        code {
            background-color: transparent !important; 
            background: transparent !important;
            color: #00ff66 !important;               
            text-shadow: 0 0 8px #00ff66 !important;  
            border: none !important;                  
            font-size: 1em !important;
        }
        
        /* 強制把網頁的分隔線 (hr) 變成暗轉換漸層 */
        hr {
            border: 0 !important;
            height: 1px !important;
            background-image: linear-gradient(to right, rgba(189, 0, 255, 0), rgba(189, 0, 255, 0.4), rgba(189, 0, 255, 0)) !important;
            margin-top: 5px !important;
            margin-bottom: 15px !important;
        }
        
        /* ─── 大字卡 (st.metric) 能見度校正 ─── */
        [data-testid="stMetric"] {
            background-color: #111111 !important;
            border: 2px solid #bd00ff !important;
            padding: 15px !important;
            border-radius: 5px !important;
            box-shadow: 0 0 10px rgba(189, 0, 255, 0.3) !important;
        }
        [data-testid="stMetricLabel"] p {
            color: #ffffff !important;
            font-weight: bold !important;
            font-size: 1.1em !important;
        }
        [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-weight: 800 !important;
            font-size: 2.2em !important;
        }
        [data-testid="stMetricDelta"] div, [data-testid="stMetricDelta"] svg {
            font-weight: bold !important;
            font-size: 1.1em !important;
        }
        div[data-testid="stMetricDelta"] {
            color: #ff0055 !important; 
            background-color: rgba(255, 0, 85, 0.1) !important; 
            padding: 2px 6px !important;
            border-radius: 4px !important;
        }
        [data-testid="stMetricDelta"] div[data-percentage-change="positive"] {
            color: #00ff66 !important; 
            background-color: rgba(0, 255, 102, 0.1) !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
        }
        
        /* ─── 表格文字能見度校正 ─── */
        .stTable {
            background-color: #111111 !important;
            border: 2px solid #00ffff !important;
            border-collapse: collapse !important;
        }
        .stTable th {
            background-color: #1a1a1a !important;
            color: #00ffff !important;
            font-weight: bold !important;
            font-size: 1.1em !important;
            border: 1px solid #222222 !important;
            padding: 8px !important;
        }
        .stTable td {
            color: #ffffff !important;
            font-weight: 500 !important;
            font-size: 1.05em !important;
            border: 1px solid #222222 !important;
            padding: 8px !important;
        }
        
        /* ⭐⭐ 終極暴力解決手機格子被吃掉：強制輸入框容器與外殼 100% 滿版擴展 ⭐⭐ */
        div[data-testid="stTextInput"], 
        div[data-testid="stTextInput"] > div,
        div[data-testid="stTextInput"] input {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 100% !important;
            display: block !important;
        }
        
        input {
            color: #ffffff !important;
            background-color: #111111 !important;
            border: 2px solid #bd00ff !important; /* 邊框加粗成 2px 霓虹紫 */
            border-radius: 6px !important;
            padding: 12px !important; /* 內部墊高，更好用手指戳 */
            font-size: 1.1em !important;
        }
    </style>
""", unsafe_allow_html=True)

# 靜音外掛
logger = logging.getLogger('yfinance')
logger.setLevel(logging.CRITICAL)

@st.cache_data(ttl=3600)  
def download_stock_data(ticker):
    try:
        old_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        df = yf.download(ticker, period="1y", progress=False, auto_adjust=False)
        sys.stderr.close()
        sys.stderr = old_stderr
        return df
    except Exception:
        return pd.DataFrame()

# ─── ⭐ 核心置頂控制台：獨立於所有佈局之外，100% 橫向滿版 ───
user_input = st.text_input("⌨️ 請輸入台股代碼（例如 3231 或 6182）：", "3231").strip()

if user_input:
    if user_input.isdigit():
        tickers_to_try = [f"{user_input}.TW", f"{user_input}.TWO"]
    else:
        tickers_to_try = [user_input.upper()]

    full_df = pd.DataFrame()
    final_ticker = ""

    for t in tickers_to_try:
        full_df = download_stock_data(t)
        if not full_df.empty:
            final_ticker = t
            break

    if full_df.empty:
        st.error(f"❌ [ERROR] 無法識別代碼【{user_input}】，請重新輸入。")
    else:
        # ─── ⭐ 標題與分隔線 ───
        st.title(f"⌨️ {final_ticker} // QUANT_TERMINAL")
        st.write("---")
        
        # ─── 數據清洗與轉換 ───
        clean_data = {}
        for col_name in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col_name in full_df.columns:
                clean_data[col_name] = full_df[col_name].to_numpy().flatten()
            elif isinstance(full_df.columns, pd.MultiIndex) and col_name in full_df.columns.get_level_values(0):
                clean_data[col_name] = full_df.xs(col_name, axis=1, level=0).to_numpy().flatten()
        
        df = pd.DataFrame(clean_data, index=full_df.index)
        df['Volume'] = df['Volume'] / 1000.0  
        
        # 計算移動平均線與指標
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        df['Vol_MA5'] = df['Volume'].rolling(window=5).mean()
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        
        df['STD20'] = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['MA20'] + (df['STD20'] * 2)
        df['BB_Lower'] = df['MA20'] - (df['STD20'] * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['MA20']
        
        # 處置股演算法
        disposal_indices = []
        for idx in range(20, len(df)):
            past_price_20d = df['Close'].iloc[idx-20]
            current_price = df['Close'].iloc[idx]
            current_vol = df['Volume'].iloc[idx]
            vma20 = df['Vol_MA20'].iloc[idx]
            if ((current_price - past_price_20d) / past_price_20d > 0.35) and (current_vol < (vma20 * 0.65)):
                disposal_indices.append(df.index[idx])
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        prev_2 = df.iloc[-3]
        
        close_p = float(latest['Close'].item())
        open_p = float(latest['Open'].item())
        high_p = float(latest['High'].item())
        low_p = float(latest['Low'].item())
        vol = float(latest['Volume'].item())
        ma20 = float(latest['MA20'].item())
        ma60 = float(latest['MA60'].item())
        vol_ma5 = float(latest['Vol_MA5'].item())
        vol_ma20 = float(latest['Vol_MA20'].item())
        bb_upper = float(latest['BB_Upper'].item())
        bb_lower = float(latest['BB_Lower'].item())
        bb_width = float(latest['BB_Width'].item())
        upper_shadow = high_p - max(open_p, close_p)
        body_size = abs(close_p - open_p)
        
        # ─── 網頁佈局：直覺雙區分流 ───
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("<h3 style='color:#00ffff; text-shadow: 0 0 5px #00ffff;'>📊 REALTIME_METRICS</h3>", unsafe_allow_html=True)
            
            price_delta = round(close_p - prev['Close'].item(), 2)
            st.metric(
                label="CURRENT_PRICE (TWD)", 
                value=f"{close_p} TWD", 
                delta=f"{price_delta} TWD"
            )
            
            status_data = {
                "戰略參數": ["O / H / L (開高低)", "月線 (20MA)", "季線 (60MA)", "布林帶 (上/下)", "當日交易量", "量能潮放大比"],
                "即時數據": [
                    f"{open_p} / {high_p} / {low_p}",
                    f"{round(ma20, 2)} TWD",
                    f"{round(ma60, 2)} TWD",
                    f"{round(bb_upper, 2)} / {round(bb_lower, 2)}",
                    f"{int(vol)} 張 (5MA: {int(vol_ma5)}張)",
                    f"{round(vol / vol_ma5, 2)} x"
                ]
            }
            st.table(pd.DataFrame(status_data))
            
            st.markdown(f"""
                <div style='background-color:#111111; border: 2px dashed #ff0055; padding:15px; border-radius:5px;'>
                    <h4 style='color:#ff0055; margin-top:0; text-shadow: 0 0 5px #ff0055;'>🎯 MISSION_OBJECTIVE // 紀律防線</h4>
                    <p style='color:#ffffff; margin-bottom:5px;'>📈 買進突破點：<span style='color:#ff0055; font-weight:bold; font-size:1.2em;'>{round(high_p, 2)} 元</span></p>
                    <p style='color:#ffffff; margin-bottom:0;'>🛑 止損撤退點：<span style='color:#00ff66; font-weight:bold; font-size:1.2em;'>{round(low_p, 2)} 元</span></p>
                </div>
            """, unsafe_allow_html=True)
            st.write("")
            
        with col2:
            st.markdown("<h3 style='color:#bd00ff; text-shadow: 0 0 5px #bd00ff;'>🧠 AI_TACTICAL_REPORT</h3>", unsafe_allow_html=True)
            
            is_currently_disposed = df.index[-1] in disposal_indices
            if is_currently_disposed:
                st.markdown(f"""
                    <div style='background-color:#ff0055; color:#ffffff; padding:12px; font-weight:bold; border-radius:4px; margin-bottom:15px; box-shadow: 0 0 10px #ff0055;'>
                        🚨 DISPOSAL_MODE // 處置分盤交易警告 (5分/20分盤)
                        <br><span style='font-size:0.9em; font-weight:normal;'>當前量能已急凍至常態均量的 {round(vol/vol_ma20*100, 1)}%。</span>
                    </div>
                """, unsafe_allow_html=True)
                if close_p >= prev['Close'].item():
                    st.info("🟢 **[籌碼鎖定]** 縮量抗跌！大戶籌碼死鎖，出關大機率發動二次進攻。續抱！")
                else:
                    st.error("🔴 **[主力棄守]** 處置期股價連續陰跌。小心大戶小單撤退，強制執行防守停利！")
            
            if close_p > prev['Close'].item() and close_p > prev_2['Close'].item() and vol < prev['Volume'].item() and vol < prev_2['Volume'].item() and close_p > ma20 and not is_currently_disposed:
                st.warning("⚠️ **[VOLUME_DIVERGENCE / 量價背離]** 股價創高開出但量能大退潮！小心遭遇誘多大反轉！")
            elif close_p >= bb_upper and (vol / vol_ma5) >= 1.5:
                st.markdown("<div style='background-color:#ff0055; color:#ffffff; padding:10px; font-weight:bold; margin-bottom:10px; box-shadow: 0 0 8px #ff0055;'>🔥 [BREAKOUT_ATTACK / 強勢攻擊] 帶量頂開布林上軌！油門踩死，瘋狂飆股模式啟動！</div>", unsafe_allow_html=True)
            elif high_p >= bb_upper and (vol / vol_ma5) >= 2.0 and upper_shadow > body_size:
                st.markdown("<div style='background-color:#bd00ff; color:#ffffff; padding:10px; font-weight:bold; margin-bottom:10px; box-shadow: 0 0 8px #bd00ff;'>⚠️ [WHALE_DUMP / 巨量出貨] 高檔觸軌爆出世紀天量卻留長上影線！巨鯨主力疑似瘋狂倒貨！</div>", unsafe_allow_html=True)
            elif close_p < ma20 and prev['Close'].item() >= prev['MA20'].item() and (vol / vol_ma5) >= 1.2:
                st.markdown("<div style='background-color:#00ff66; color:#000000; padding:10px; font-weight:bold; margin-bottom:10px; box-shadow: 0 0 8px #00ff66;'>🔴 [CRITICAL_BREAK / 帶量破線] 帶量殺破月線中軌！防守潰敗，現股火速撤退！</div>", unsafe_allow_html=True)
            elif (low_p <= bb_lower or abs(low_p - ma60)/ma60 < 0.01) and (vol / vol_ma5) <= 0.6:
                st.markdown("<div style='background-color:#00ffff; color:#000000; padding:10px; font-weight:bold; margin-bottom:10px; box-shadow: 0 0 8px #00ffff;'>🛡️ [BOTTOM_SUPPORT / 窒息量打底] 強支撐伴隨窒息死量！賣壓完全竭盡，高勝率超底點成形！</div>", unsafe_allow_html=True)
            elif bb_width < 0.10:
                st.warning("💤 **[COMPRESSION_MODE / 壓縮變盤]** 通道極度壓縮！即將發生暴風雨式的大方向變盤！")
            else:
                if close_p > ma20:
                    st.info("🟢 **[BULLISH_TREND]** 偏多格局：股價在月線之上常態震盪，多頭控盤中。")
                else:
                    st.warning("🔵 **[BEARISH_TREND]** 偏空格局：股價在月線之下常態修正，上方賣壓沉重。")
            
            # K 線繪圖
            plot_df = df.tail(60).copy()
            plot_df['Big_Up_Arrow'] = np.nan
            plot_df['Big_Down_Arrow'] = np.nan
            
            for i in range(15, len(plot_df)):
                past_10_days = plot_df.iloc[i-10:i]
                is_above_ma20_10d = all(past_10_days['Close'] > past_10_days['MA20'])
                was_not_above_before = (plot_df['Close'].iloc[i-11] < plot_df['MA20'].iloc[i-11]) or (plot_df['MA20'].iloc[i-11] < plot_df['MA60'].iloc[i-11] and plot_df['MA20'].iloc[i] > plot_df['MA60'].iloc[i])
                is_below_ma20_10d = all(past_10_days['Close'] < past_10_days['MA20'])
                was_not_below_before = (plot_df['Close'].iloc[i-11] > plot_df['MA20'].iloc[i-11]) or (plot_df['MA20'].iloc[i-11] > plot_df['MA60'].iloc[i-11] and plot_df['MA20'].iloc[i] < plot_df['MA60'].iloc[i])
                
                if is_above_ma20_10d and was_not_above_before and plot_df['MA20'].iloc[i] > plot_df['MA60'].iloc[i]:
                    plot_df.iloc[i, plot_df.columns.get_loc('Big_Up_Arrow')] = plot_df['Low'].iloc[i] * 0.96
                elif is_below_ma20_10d and was_not_below_before and plot_df['MA20'].iloc[i] < plot_df['MA60'].iloc[i]:
                    plot_df.iloc[i, plot_df.columns.get_loc('Big_Down_Arrow')] = plot_df['High'].iloc[i] * 1.04

            my_color = mpf.make_marketcolors(
                up='#ff0055', down='#00ff66', edge='inherit', wick='inherit', volume='inherit'
            )
            my_style = mpf.make_mpf_style(
                marketcolors=my_color, gridstyle=':', gridcolor='#222222', facecolor='#000000', figcolor='#050505', y_on_right=True
            )
            
            add_plots = [
                mpf.make_addplot(plot_df['BB_Upper'], color='#00ffff', linestyle='--', width=0.8), 
                mpf.make_addplot(plot_df['BB_Lower'], color='#00ffff', linestyle='--', width=0.8), 
                mpf.make_addplot(plot_df['MA20'], color='#bd00ff', width=1.8),                    
                mpf.make_addplot(plot_df['MA60'], color='#ffff00', width=2.2)                     
            ]
            
            if not plot_df['Big_Up_Arrow'].isna().all():
                add_plots.append(mpf.make_addplot(plot_df['Big_Up_Arrow'], type='scatter', markersize=400, marker='^', color='#ff0055'))
            if not plot_df['Big_Down_Arrow'].isna().all():
                add_plots.append(mpf.make_addplot(plot_df['Big_Down_Arrow'], type='scatter', markersize=400, marker='v', color='#00ff66'))
            
            vlines_spec = dict(vlines=[], colors=[], alpha=[])
            for idx, date in enumerate(plot_df.index):
                if date in disposal_indices:
                    vlines_spec['vlines'].append(date)
                    vlines_spec['colors'].append('#ff0055') 
                    vlines_spec['alpha'].append(0.2)
            
            if vlines_spec['vlines']:
                fig, axlist = mpf.plot(
                    plot_df, type='candle', volume=True, addplot=add_plots, style=my_style,
                    ylabel='PRICE (TWD)', ylabel_lower='VOLUME (K)', show_nontrading=False,
                    vlines=vlines_spec, returnfig=True
                )
            else:
                fig, axlist = mpf.plot(
                    plot_df, type='candle', volume=True, addplot=add_plots, style=my_style,
                    ylabel='PRICE (TWD)', ylabel_lower='VOLUME (K)', show_nontrading=False,
                    returnfig=True
                )
                
            st.pyplot(fig)
