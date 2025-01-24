import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
from datetime import datetime
import pytz

# Configuration
st.set_page_config(page_title="Binance Trading Dashboard", layout="wide")

# Server Configuration
API_SERVER = "http://34.47.211.154:5001"

# Utility Functions
def format_timestamp(timestamp):
    """Convert timestamp to Indian Standard Time"""
    try:
        dt = datetime.fromtimestamp(timestamp / 1000, tz=pytz.UTC)
        indian_tz = pytz.timezone('Asia/Kolkata')
        indian_time = dt.astimezone(indian_tz)
        return indian_time.strftime('%d %b %Y %I:%M:%S %p')
    except:
        return "Invalid Time"

def format_pnl(pnl):
    """Format PNL with color coding"""
    try:
        pnl = float(pnl)
        if pnl > 0:
            return f'<span style="color:green">+{pnl:.2f} USDT</span>'
        elif pnl < 0:
            return f'<span style="color:red">{pnl:.2f} USDT</span>'
        else:
            return f'{pnl:.2f} USDT'
    except:
        return "N/A"

def fetch_data(endpoint):
    """Fetch data from API with error handling"""
    try:
        response = requests.get(f"{API_SERVER}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

# Dashboard Sections
def account_summary():
    """Comprehensive Account Summary"""
    st.subheader("Account Summary")
    account_summary = fetch_data("account_summary")
    
    if account_summary:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Total Balance", value=f"{account_summary['Balance']:.2f} USDT")
        
        with col2:
            st.metric(label="Unrealized PNL", value=account_summary['Unrealized PNL'])
        
        with col3:
            st.metric(label="Margin Balance", value=f"{account_summary['Margin Balance']:.2f} USDT")
        
        with col4:
            st.metric(label="Available Balance", value=f"{account_summary['Available Balance']:.2f} USDT")

def positions():
    """Advanced Positions Analysis"""
    st.subheader("Active Positions")
    positions_data = fetch_data("positions")
    
    if positions_data:
        df = pd.DataFrame(positions_data)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            # Position Distribution Chart
            fig = px.pie(df, names='Symbol', values='Size', title='Position Size Distribution')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No active positions found.")

def open_orders():
    """Open Orders Analysis"""
    st.subheader("Open Orders")
    open_orders_data = fetch_data("open_orders")
    
    if open_orders_data:
        df = pd.DataFrame(open_orders_data)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No open orders found.")

def trade_history():
    """Comprehensive Trade History"""
    st.subheader("Trade History")
    trade_history_data = fetch_data("trade_history")

    if trade_history_data:
        df = pd.DataFrame(trade_history_data)
        if not df.empty:
            # Convert timestamp to human-readable format
            if 'Time' in df.columns:
                df['Time'] = df['Time'].apply(format_timestamp)

            # Sort by time, latest first
            df.sort_values(by='Time', ascending=False, inplace=True)

            # Format PNL with color coding
            if 'PNL' in df.columns:
                df['PNL'] = df['PNL'].apply(format_pnl)

            # Display DataFrame
            st.dataframe(df, use_container_width=True, height=500)

            # PNL Distribution Visualization
            if 'PNL' in df.columns:
                fig = px.histogram(
                    df, 
                    x='PNL', 
                    title='PNL Distribution', 
                    labels={'PNL': 'Profit/Loss (USDT)'},
                    color_discrete_sequence=['#636EFA']
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No trade history available.")
    else:
        st.warning("Failed to fetch trade history.")

def closed_positions():
    """Display Closed Positions"""
    st.subheader("Closed Positions")
    closed_positions_data = fetch_data("closed_positions")
    
    if closed_positions_data:
        df = pd.DataFrame(closed_positions_data)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            # PNL Distribution Chart
            fig = px.histogram(df, x='PNL', title='Closed Positions PNL Distribution')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No closed positions available.")

def order_history():
    """Display Order History"""
    st.subheader("Order History")
    order_history_data = fetch_data("order_history")
    
    if order_history_data:
        df = pd.DataFrame(order_history_data)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No order history found.")

def analytics():
    """Trading Analytics"""
    st.subheader("Trading Analytics")
    pnl_data = fetch_data("pnl_analytics")
    
    if pnl_data:
        pnl_df = pd.DataFrame(pnl_data)
        if not pnl_df.empty:
            # Daily PNL Chart
            daily_fig = px.bar(pnl_df, x='Date', y='PNL', title='Daily PNL', color='PNL')
            st.plotly_chart(daily_fig, use_container_width=True)
            # Cumulative PNL Chart
            pnl_df['Cumulative PNL'] = pnl_df['PNL'].cumsum()
            cumulative_fig = px.line(pnl_df, x='Date', y='Cumulative PNL', title='Cumulative PNL')
            st.plotly_chart(cumulative_fig, use_container_width=True)
        else:
            st.warning("No analytics data available.")

# Main Dashboard
def main():
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/4b/Binance_logo.png", width=200)
    st.sidebar.title("Binance Trading Dashboard")
    menu = ["Account Summary", "Positions", "Open Orders", "Trade History", "Closed Positions", "Order History", "Analytics"]
    choice = st.sidebar.radio("Navigation", menu)
    if choice == "Account Summary":
        account_summary()
    elif choice == "Positions":
        positions()
    elif choice == "Open Orders":
        open_orders()
    elif choice == "Trade History":
        trade_history()
    elif choice == "Closed Positions":
        closed_positions()
    elif choice == "Order History":
        order_history()
    elif choice == "Analytics":
        analytics()
    st.markdown("---")
    st.text("© 2025 Binance Trading Dashboard")

if __name__ == "__main__":
    main()
