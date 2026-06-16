import streamlit as st
import requests
import math

# ---------------------------------------------------------
# Google Maps API Key
# ---------------------------------------------------------
API_KEY = "YOUR_GOOGLE_API_KEY"   # ←ここに自分のキーを入れる


# ---------------------------------------------------------
# Google Distance API（安全版）
# ---------------------------------------------------------
def get_distance(origin, destination):
    if not origin or not destination:
        return None

    url = (
        "https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={origin}&destinations={destination}"
        f"&mode=driving&language=ja&key={API_KEY}"
    )

    res = requests.get(url).json()

    # APIエラー対策（IndexErrorを完全防止）
    if res.get("status") != "OK":
        return None

    rows = res.get("rows")
    if not rows or not rows[0].get("elements"):
        return None

    elem = rows[0]["elements"][0]
    if elem.get("status") != "OK":
        return None

    # 距離（m → km）
    return elem["distance"]["value"] / 1000


# ---------------------------------------------------------
# ① 駅 → 自宅の料金
# ---------------------------------------------------------
def calc_home_price(d):
    if d <= 10:
        return 300
    elif d <= 15:
        return 500
    else:
        return 500 + math.ceil(d - 15) * 100


# ---------------------------------------------------------
# ② 自宅 → 目的地（往復 or 片道）
# ---------------------------------------------------------
def calc_dest_price(d, is_roundtrip):
    if is_roundtrip:
        # 往復
        if d <= 3:
            return 2500
        elif d <= 5:
            return 3000
        else:
            return 3000 + math.ceil(d - 5) * 100
    else:
        # 片道
        if d <= 3:
            return 2000
        elif d <= 5:
            return 2500
        else:
            return 2500 + math.ceil(d - 5) * 100


# ---------------------------------------------------------
# ③ 待機料金
# ---------------------------------------------------------
def calc_wait_price(minutes):
    if minutes <= 30:
        return 0
    elif minutes <= 60:
        return 1000
    elif minutes <= 90:
        return 1500
    elif minutes <= 120:
        return 2000
    else:
        extra = math.ceil((minutes - 120) / 30)
        return 2000 + extra * 1000


# ---------------------------------------------------------
# ④ 総額
# ---------------------------------------------------------
def calc_total(d_home, d_dest, is_roundtrip, wait_min):
    home_price = calc_home_price(d_home)
    dest_price = calc_dest_price(d_dest, is_roundtrip)
    wait_price = calc_wait_price(wait_min)
    return home_price + dest_price + wait_price


# ---------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------
st.title("🐶 ペットタクシー 概算料金シミュレーター")

st.write("出発地（ご自宅）と目的地を入力すると、Googleの最適ルートで距離を計算し、概算料金を表示します。")

home = st.text_input("🏠 ご自宅の住所（例：千葉県柏市○○）")
dest = st.text_input("📍 目的地の住所（例：東京都渋谷区○○）")

roundtrip = st.radio("利用方法", ["往復", "片道"])
wait = st.number_input("待機時間（分）", 0, 300, 0)

if st.button("概算料金を計算する"):

    # 入力チェック
    if not home or not dest:
        st.warning("出発地と目的地を入力してください。")
        st.stop()

    # 距離取得
    d_home = get_distance("柏の葉キャンパス駅", home)
    d_dest = get_distance(home, dest)

    if d_home is None or d_dest is None:
        st.error("距離を取得できませんでした。住所を確認してください。")
        st.stop()

    # 料金計算
    total = calc_total(
        d_home,
        d_dest,
        is_roundtrip=(roundtrip == "往復"),
        wait_min=wait
    )

    # 結果表示
    st.success("概算料金はこちらです")

    st.metric("駅 → 自宅 距離", f"{d_home:.1f} km")
    st.metric("自宅 → 目的地 距離", f"{d_dest:.1f} km")
    st.metric("概算料金", f"{total:,} 円")
