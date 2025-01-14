import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import time

# Centering the title with Markdown and HTML
st.markdown("<h1 style='text-align: center;'>Interactive Stock Visualization</h1>", unsafe_allow_html=True)

# Input for the user to enter the tickers
tickers = st.text_input("Enter tickers separated by commas:", value="")

# Date range filter
start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2025-01-01"))

# Automatically updating data every 30 seconds
st.cache_data(ttl=30)  # Cache data for 30 seconds

# Process the tickers
tickers = [t.strip() for t in tickers.split(",") if t.strip()]
if not tickers:
    st.error("Please enter at least one valid ticker.")
else:
    try:
        # Get historical data
        data = yf.download(tickers=tickers, start=start_date, end=end_date, group_by="ticker")

        # Transform the data to long format
        df_list = []
        for ticker in tickers:
            temp_df = data[ticker].reset_index()
            temp_df["Ticker"] = ticker
            df_list.append(temp_df)

        final_df = pd.concat(df_list, ignore_index=True)

        # Display the current stock price in a card
        for ticker in tickers:
            try:
                current_price = data[ticker]["Close"].dropna().iloc[-1]  # Most recent closing price
                st.metric(f"Current Price {ticker}", f"R$ {current_price:.2f}")
            except IndexError:
                st.error(f"Could not retrieve the most recent closing price for {ticker}.")

        # Allow the user to choose which stock to observe (dynamic variable)
        selected_ticker = st.selectbox("Choose the Stock to View", tickers)

        # Create an interactive graph with the selected stock
        fig = px.line(
            final_df[final_df["Ticker"] == selected_ticker],  # Filter data for the selected stock
            x="Date",
            y="Close",
            color="Ticker",
            title=f"Stock Price History for {selected_ticker}",
            labels={"Date": "Date", "Close": "Closing Price (BRL)", "Ticker": "Stock"},
            template="plotly_dark"  # Dark theme for the graph
        )

        # Adjust the graph size
        st.plotly_chart(fig, use_container_width=True, height=700)

        # CSV download function
        csv = final_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="stock_history.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error processing the tickers: {e}")

    
