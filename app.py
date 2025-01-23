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
    except Exception:
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
    except Exception:
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
    account_summary_data = fetch_data("account_summary")
    
    if account_summary_data:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Balance", 
                value=f"{account_summary_data['Balance']:.2f} USDT",
                help="Total account balance"
            )
        
        with col2:
            st.metric(
                label="Unrealized PNL", 
                value=format_pnl(account_summary_data['Unrealized PNL']),
                help="Profit/Loss from open positions"
            )
        
        with col3:
            st.metric(
                label="Margin Balance", 
                value=f"{account_summary_data['Margin Balance']:.2f} USDT",
                help="Available margin for trading"
            )
        
        with col4:
            st.metric(
                label="Available Balance", 
                value=f"{account_summary_data['Available Balance']:.2f} USDT",
                help="Free balance for new trades"
            )

def positions():
    """Active Positions Analysis"""
    st.subheader("Active Positions")
    positions_data = fetch_data("positions")
    
    if positions_data:
        df = pd.DataFrame(positions_data)
        
        # Enhanced DataFrame with formatted columns
        styled_df = df.style.format({
            'Entry Time': format_timestamp,
            'Current PNL': format_pnl
        })
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Position Distribution Chart
        if not df.empty:
            fig = px.pie(
                df, 
                names='Symbol', 
                values='Amount', 
                title='Position Size Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No positions found.")

def open_orders():
    """Open Orders Analysis"""
    st.subheader("Open Orders")
    open_orders_data = fetch_data("open_orders")
    
    if open_orders_data:
        df = pd.DataFrame(open_orders_data)
        
        # Format timestamps
        df['Order Time'] = df['Order Time'].apply(format_timestamp)
        
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No open orders found.")

def trade_history():
    """Comprehensive Trade History"""
    st.subheader("Trade History")
    trade_history_data = fetch_data("trade_history")
    
    if trade_history_data:
        df = pd.DataFrame(trade_history_data)
        
        # Dynamically handle column names
        time_column = [col for col in df.columns if 'time' in col.lower()]
        pnl_column = [col for col in df.columns if 'pnl' in col.lower()]
        
        # Format timestamps if time column exists
        if time_column:
            df[time_column[0]] = df[time_column[0]].apply(format_timestamp)
        
        # Format PNL if PNL column exists
        if pnl_column:
            df[pnl_column[0]] = df[pnl_column[0]].apply(format_pnl)
        
        # Interactive Data Table
        st.dataframe(df, use_container_width=True)
        
        # PNL Distribution if PNL column exists
        if pnl_column:
            fig = px.histogram(
                df, 
                x=pnl_column[0], 
                title='PNL Distribution',
                labels={pnl_column[0]: 'Trade Profit/Loss'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No trade history available.")

def analytics():
    """Advanced Trading Analytics with Enhanced Visualizations"""
    st.subheader("Trading Analytics")
    
    # Fetch PNL and Trade Data
    pnl_data = fetch_data("pnl_analytics")
    trade_history_data = fetch_data("trade_history")
    
    if pnl_data and trade_history_data:
        pnl_df = pd.DataFrame(pnl_data)
        trades_df = pd.DataFrame(trade_history_data)
        
        if not pnl_df.empty:
            # Daily PNL Bar Chart
            daily_fig = px.bar(
                pnl_df, 
                x="Date", 
                y="PNL", 
                title="Daily Performance Analysis",
                labels={"Date": "Trading Date", "PNL": "Daily Profit/Loss (USDT)"},
                color="PNL",
                color_continuous_scale=px.colors.sequential.YlGnBu,
                color_continuous_midpoint=0
            )
            daily_fig.update_layout(
                xaxis_title="Trading Date",
                yaxis_title="Daily Profit/Loss (USDT)",
                coloraxis_colorbar_title="PNL"
            )
            st.plotly_chart(daily_fig, use_container_width=True)
            
            # Cumulative PNL Line Chart with Percentage
            pnl_df['Cumulative PNL'] = pnl_df['PNL'].cumsum()
            pnl_df['Cumulative PNL %'] = (pnl_df['Cumulative PNL'] / pnl_df['PNL'].abs().max()) * 100
            
            cumulative_fig = go.Figure()
            
            cumulative_fig.add_trace(go.Scatter(
                x=pnl_df['Date'], 
                y=pnl_df['Cumulative PNL'],
                mode='lines+markers',
                name='Total Profit/Loss (USDT)',
                line=dict(color='blue', width=3),
                marker=dict(size=8)
            ))
            
            cumulative_fig.add_trace(go.Scatter(
                x=pnl_df['Date'], 
                y=pnl_df['Cumulative PNL %'],
                mode='lines',
                name='Cumulative PNL (%)',
                line=dict(color='green', width=2, dash='dot'),
                yaxis='y2'
            ))
            
            cumulative_fig.update_layout(
                title='Cumulative Trading Performance',
                xaxis_title='Date',
                yaxis_title='Total Profit/Loss (USDT)',
                yaxis2=dict(
                    title='Cumulative PNL (%)',
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                legend_title_text='Performance Metrics'
            )
            st.plotly_chart(cumulative_fig, use_container_width=True)

# Main Dashboard Functionality
def main():
    # Sidebar Configuration
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/4b/Binance_logo.png", width=200)
    st.sidebar.title("Binance Trading Dashboard")
    
    # Navigation Menu
    menu_options = [
        "Account Summary", 
        "Positions", 
        "Open Orders", 
        "Trade History", 
        "Analytics"
    ]
    
    selected_option = st.sidebar.radio("Navigation", menu_options)
    
    # Routing to Selected Option
    if selected_option == "Account Summary":
        account_summary()
    elif selected_option == "Positions":
        positions()
    elif selected_option == "Open Orders":
        open_orders()
    elif selected_option == "Trade History":
        trade_history()
    elif selected_option == "Analytics":
        analytics()
    
    # Footer Section
    st.markdown("---")
    st.text("© 2025 Binance Trading Dashboard")

# Run the Streamlit application
if __name__ == "__main__":
    main()
