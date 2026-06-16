import streamlit as st
import requests

API_KEY = "YOUR_GOOGLE_API_KEY"

def get_distance(origin, destination):
    url = (
        "https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={origin}&destinations={destination}"
        f"&mode=driving&language=ja&key={API_KEY}"
    )
    res = requests.get(url).json()
    elem = res["rows"][0]["elements"][0]

    if elem["status"] != "OK":
        return None

    return elem["distance"]["value"] / 1000  # km

st.title("🐶 ペットタクシー 概算料金シミュレーター")

home = st.text_input("お客様のご自宅住所")
dest = st.text_input("目的地住所")
roundtrip = st.radio("利用方法", ["往復", "片道"])
wait = st.number_input("待機時間（分）", 0, 300, 0)

if st.button("概算料金を計算する"):
    d_home = get_distance("千葉県柏市若柴174", home)
    d_dest = get_distance(home, dest)

    if d_home is None or d_dest is None:
        st.error("住所が正しくありません。")
    else:
        total = calc_total(
            d_home,
            d_dest,
            is_roundtrip=(roundtrip == "往復"),
            wait_min=wait
        )

        st.success("概算料金はこちらです")
        st.metric("駅 → 自宅 距離", f"{d_home:.1f} km")
        st.metric("自宅 → 目的地 距離", f"{d_dest:.1f} km")
        st.metric("概算料金", f"{total:,} 円")
