# import streamlit as st
# import pandas as pd
# from io import BytesIO

# st.set_page_config(page_title="VDA Profit/Loss Calculator", page_icon="📊")

# st.title("📊 VDA Profit/Loss Calculator (FIFO Method)")
# st.write("Upload your Excel file to calculate profit/loss on Virtual Digital Assets (VDAs) for ITR filing.")

# uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# def compute_vda_fifo(df):
#     # Clean numeric fields
#     def clean_numeric(val):
#         if isinstance(val, str):
#             return float(val.split()[0])
#         return float(val)

#     df["Amount"] = df["Amount"].apply(clean_numeric)
#     df["Total"] = df["Total"].apply(clean_numeric)

#     buys = df[df["Type"].str.lower() == "buy"].copy()
#     sells = df[df["Type"].str.lower() == "sell"].copy()

#     buys = buys.sort_values("Date").reset_index(drop=True)
#     sells = sells.sort_values("Date").reset_index(drop=True)

#     results = []
#     buy_pointer = 0
#     remaining_buy_amount = 0
#     remaining_buy_cost = 0

#     for _, sell in sells.iterrows():
#         sell_qty = sell["Amount"]
#         sell_date = sell["Date"]
#         sell_price = float(sell["Price"].split()[0])

#         while sell_qty > 0 and buy_pointer < len(buys):
#             if remaining_buy_amount == 0:
#                 buy = buys.iloc[buy_pointer]
#                 buy_pointer += 1
#                 remaining_buy_amount = buy["Amount"]
#                 remaining_buy_cost = buy["Total"]
#                 buy_date = buy["Date"]

#             matched_qty = min(sell_qty, remaining_buy_amount)
#             cost = remaining_buy_cost * (matched_qty / remaining_buy_amount)
#             consideration = sell_price * matched_qty
#             profit_loss = consideration - cost

#             results.append({
#                 "Date of acquisition": buy_date,
#                 "Date of transfer": sell_date,
#                 "Cost of acquisition": round(cost, 2),
#                 "Consideration received": round(consideration, 2),
#                 "Net Profit/Loss": round(profit_loss, 2)
#             })

#             remaining_buy_amount -= matched_qty
#             remaining_buy_cost -= cost
#             sell_qty -= matched_qty

#     return pd.DataFrame(results)

# if uploaded_file is not None:
#     df = pd.read_excel(uploaded_file)

#     if st.button("Calculate"):
#         results_df = compute_vda_fifo(df)

#         # Add summary
#         summary = pd.DataFrame([{
#             "Date of acquisition": "Summary",
#             "Date of transfer": "",
#             "Cost of acquisition": results_df["Cost of acquisition"].sum(),
#             "Consideration received": results_df["Consideration received"].sum(),
#             "Net Profit/Loss": results_df["Net Profit/Loss"].sum()
#         }])
#         results_df = pd.concat([results_df, summary], ignore_index=True)

#         st.subheader("Results")
#         st.dataframe(results_df)

#         # Prepare Excel for download
#         output = BytesIO()
#         with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#             results_df.to_excel(writer, index=False, sheet_name="VDA PnL")
#         excel_data = output.getvalue()

#         st.download_button(
#             label="📥 Download Result Excel",
#             data=excel_data,
#             file_name="VDA_PnL_Output.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )


import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="VDA Profit/Loss Calculator", page_icon="📊")

st.title("📊 VDA Profit/Loss Calculator (FIFO Method)")
st.write("Upload your Excel file to calculate profit/loss on Virtual Digital Assets (VDAs) for ITR filing.")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

def compute_vda_fifo(df):
    # Clean numeric fields
    def clean_numeric(val):
        if isinstance(val, str):
            return float(val.split()[0])
        return float(val)

    df["Amount"] = df["Amount"].apply(clean_numeric)
    df["Total"] = df["Total"].apply(clean_numeric)

    buys = df[df["Type"].str.lower() == "buy"].copy()
    sells = df[df["Type"].str.lower() == "sell"].copy()

    buys = buys.sort_values("Date").reset_index(drop=True)
    sells = sells.sort_values("Date").reset_index(drop=True)

    results = []
    buy_pointer = 0
    remaining_buy_amount = 0
    remaining_buy_cost = 0

    for _, sell in sells.iterrows():
        sell_qty = sell["Amount"]
        sell_date = sell["Date"]
        sell_price = float(sell["Price"].split()[0])

        while sell_qty > 0 and buy_pointer < len(buys):
            if remaining_buy_amount == 0:
                buy = buys.iloc[buy_pointer]
                buy_pointer += 1
                remaining_buy_amount = buy["Amount"]
                remaining_buy_cost = buy["Total"]
                buy_date = buy["Date"]

            matched_qty = min(sell_qty, remaining_buy_amount)
            cost = remaining_buy_cost * (matched_qty / remaining_buy_amount)
            consideration = sell_price * matched_qty
            profit_loss = consideration - cost

            results.append({
                "Date of acquisition": buy_date,
                "Date of transfer": sell_date,
                "Cost of acquisition": cost,
                "Consideration received": consideration,
                "Net Profit/Loss": profit_loss
            })

            remaining_buy_amount -= matched_qty
            remaining_buy_cost -= cost
            sell_qty -= matched_qty

    results_df = pd.DataFrame(results)

    # Group by acquisition and transfer date
    grouped = results_df.groupby(["Date of acquisition", "Date of transfer"])

    final_rows = []
    for (acq_date, trf_date), group in grouped:
        net_profit = group[group["Net Profit/Loss"] > 0].sum(numeric_only=True)
        net_loss = group[group["Net Profit/Loss"] < 0].sum(numeric_only=True)

        if net_loss["Net Profit/Loss"] != 0:
            final_rows.append({
                "Date of acquisition": acq_date,
                "Date of transfer": trf_date,
                "Cost of acquisition": round(net_loss["Cost of acquisition"], 2),
                "Consideration received": round(net_loss["Consideration received"], 2),
                "Net Profit/Loss": round(net_loss["Net Profit/Loss"], 2)
            })
        if net_profit["Net Profit/Loss"] != 0:
            final_rows.append({
                "Date of acquisition": acq_date,
                "Date of transfer": trf_date,
                "Cost of acquisition": round(net_profit["Cost of acquisition"], 2),
                "Consideration received": round(net_profit["Consideration received"], 2),
                "Net Profit/Loss": round(net_profit["Net Profit/Loss"], 2)
            })

    return pd.DataFrame(final_rows)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    if st.button("Calculate"):
        results_df = compute_vda_fifo(df)

        st.subheader("Results")
        st.dataframe(results_df)

        # Prepare Excel for download
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            results_df.to_excel(writer, index=False, sheet_name="VDA PnL")
        excel_data = output.getvalue()

        st.download_button(
            label="📥 Download Result Excel",
            data=excel_data,
            file_name="VDA_PnL_Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

