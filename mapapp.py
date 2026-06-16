import streamlit as st
import requests
import math

# ---------------------------------------------------------
# Google Maps API Key
# ---------------------------------------------------------
API_KEY = "AIzaSyBvOicljOkU4UPgLTD7I_x73YLIpLZO74o"   # ←ここに自分のキーを入れる


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

    col1, col2, col3 = st.columns(3)

    # ① 駅 → 自宅
    with col1:
        st.subheader("🏠 駅 → 自宅")
        st.metric("距離", f"{d_home:.1f} km")
        st.metric("料金", f"{calc_home_price(d_home):,} 円")

        # 内訳
        if d_home <= 10:
            st.caption("内訳：10km以内 → 300円")
        elif d_home <= 15:
            st.caption("内訳：10〜15km → 500円")
        else:
            extra = math.ceil(d_home - 15)
            st.caption(f"内訳：15km超 → 500円 + {extra}km × 100円")

    # ② 自宅 → 目的地
    with col2:
        st.subheader("📍 自宅 → 目的地")
        st.metric("距離", f"{d_dest:.1f} km")

        dest_price = calc_dest_price(d_dest, roundtrip == "往復")
        st.metric("料金", f"{dest_price:,} 円")

        # 内訳
        if roundtrip == "往復":
            if d_dest <= 3:
                st.caption("内訳：往復 3km以内 → 2500円")
            elif d_dest <= 5:
                st.caption("内訳：往復 5km以内 → 3000円")
            else:
                extra = math.ceil(d_dest - 5)
                st.caption(f"内訳：5km超 → 3000円 + {extra}km × 100円")
        else:
            if d_dest <= 3:
                st.caption("内訳：片道 3km以内 → 2000円")
            elif d_dest <= 5:
                st.caption("内訳：片道 5km以内 → 2500円")
                st.caption("内訳：片道 5km以内 → 2500円")
            else:
                extra = math.ceil(d_dest - 5)
                st.caption(f"内訳：5km超 → 2500円 + {extra}km × 100円")

    # ③ 待機料金
    with col3:
        st.subheader("⏱ 待機時間")
        st.metric("時間", f"{wait} 分")
    
        wait_price = calc_wait_price(wait)
        st.metric("料金", f"{wait_price:,} 円")

        # 内訳
        if wait <= 30:
            st.caption("内訳：30分以内 → 0円")
        elif wait <= 60:
            st.caption("内訳：30〜60分 → 1000円")
        elif wait <= 90:
            st.caption("内訳：60〜90分 → 1500円")
        elif wait <= 120:
            st.caption("内訳：90〜120分 → 2000円")
        else:
            extra = math.ceil((wait - 120) / 30)
            st.caption(f"内訳：120分超 → 2000円 + {extra} × 1000円")

