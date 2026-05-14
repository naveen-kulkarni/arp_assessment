"""Streamlit dashboard for the ARP Assessment platform."""
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import requests
import json
from datetime import datetime
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.backend.config import get_settings

settings = get_settings()
API_BASE_URL = f"http://localhost:{settings.API_PORT}"


# ============= PAGE CONFIG =============

st.set_page_config(
    page_title="ARP Assessment Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============= SESSION STATE =============

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None


# ============= HELPER FUNCTIONS =============

def get_headers():
    """Get request headers with auth token."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_user(username: str):
    """Login user."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"username": username},
            timeout=5,
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.user = data["user"]["username"]
            st.session_state.role = data["user"]["role"]
            return True
        else:
            st.error(f"Login failed: {response.json().get('error', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Connection error: {e}")
        return False


def logout_user():
    """Logout user."""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.role = None


# ============= LOGIN PAGE =============

def show_login():
    """Show login page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔐 ARP Assessment Platform")
        st.markdown("---")
        st.write("Select a user to login:")
        
        users = ["analyst@local", "risk@local", "manager@local", "intern@local"]
        selected_user = st.selectbox(
            "User",
            users,
            format_func=lambda x: f"{x.split('@')[0].capitalize()} - {x}",
            key="user_select",
        )
        
        st.markdown("---")
        st.write("**Available Roles:**")
        roles_info = {
            "analyst@local": "Portfolio & market data access",
            "risk@local": "Full portfolio, trades, and risk access",
            "manager@local": "Summary and audit log access only",
            "intern@local": "Limited portfolio summary access",
        }
        st.info(roles_info[selected_user])
        
        if st.button("Login", key="login_btn", use_container_width=True):
            if login_user(selected_user):
                st.success(f"Logged in as {selected_user}")
                st.rerun()


def get_available_pages(role: str):
    """Return dashboard pages available for a role."""
    role = (role or "").lower()
    pages = ["📈 Portfolio", "🤖 AI Agent"]

    if role == "risk":
        pages.extend(["💱 Trades", "🚨 Alerts"])
    if role == "manager":
        pages.append("📋 Audit Logs")

    return pages


# ============= DASHBOARD PAGES =============

def page_portfolio():
    """Portfolio analysis page."""
    st.header("📈 Portfolio Analysis")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/data/portfolio",
            headers=get_headers(),
            timeout=5,
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "error" in data:
                st.error(data["error"])
                return
            
            # Portfolio summary
            col1, col2, col3 = st.columns(3)
            
            exposures = data.get("exposures", [])
            
            if exposures:
                total_value = sum(e["position_value"] for e in exposures)
                top_asset = max(exposures, key=lambda x: x["position_value"])
                
                with col1:
                    st.metric("Total Portfolio Value", f"${total_value:,.2f}")
                with col2:
                    st.metric("Number of Holdings", len(exposures))
                with col3:
                    st.metric("Top Position", f"{top_asset['symbol']} ({top_asset['exposure_percentage']:.1f}%)")
            else:
                total_value = data.get("total_portfolio_value", 0)
                allocation = data.get("allocation_percentage", {})
                
                with col1:
                    st.metric("Total Portfolio Value", f"${total_value:,.2f}")
                with col2:
                    st.metric("Number of Holdings", "Summary only")
                with col3:
                    st.metric("Access Level", "Summary")
                
                if allocation:
                    st.write("**Asset allocation:**")
                    allocation_text = ", ".join([f"{k}: {v}%" for k, v in allocation.items()])
                    st.write(allocation_text)
            
            st.markdown("---")
            
            if exposures:
                df = pd.DataFrame(exposures)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['symbol'],
                        y=df['exposure_percentage'],
                        text=df['exposure_percentage'].round(1),
                        textposition='auto',
                        marker_color=['red' if x > 30 else 'blue' for x in df['exposure_percentage']],
                    )
                ])
                fig.update_layout(
                    title="Asset Exposure by Position",
                    xaxis_title="Symbol",
                    yaxis_title="Exposure %",
                    hovermode="x unified",
                    height=400,
                )
                st.plotly_chart(fig, use_container_width=True)
            
            if exposures:
                # Pie chart of asset allocation
                col1, col2 = st.columns(2)
                
                with col1:
                    asset_classes = {}
                    for e in exposures:
                        asset_class = e['asset_class']
                        if asset_class not in asset_classes:
                            asset_classes[asset_class] = 0
                        asset_classes[asset_class] += e['position_value']
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=list(asset_classes.keys()),
                        values=list(asset_classes.values()),
                    )])
                    fig.update_layout(title="Asset Class Distribution", height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Holdings Details")
                    df_display = df[['symbol', 'quantity', 'current_price', 'position_value', 'exposure_percentage']].copy()
                    df_display.columns = ['Symbol', 'Quantity', 'Price', 'Value', 'Exposure %']
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Overexposed assets
                overexposed = data.get("overexposed_assets", [])
                if overexposed:
                    st.warning(f"⚠️ {len(overexposed)} overexposed assets (>30%)")
                    for asset in overexposed:
                        st.write(f"- **{asset['symbol']}**: {asset['exposure_percentage']:.1f}%")
            else:
                st.info("Summary access only. Detailed holdings are not available for this role.")
        
        else:
            st.error(f"Failed to fetch portfolio data: {response.status_code}")
    
    except Exception as e:
        st.error(f"Error: {e}")


def page_trades():
    """Recent trades page."""
    st.header("💱 Recent Trades")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/data/trades",
            headers=get_headers(),
            timeout=5,
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "error" in data:
                st.error(data["error"])
                return
            
            trades = data.get("trades", [])
            
            st.metric("Total Trades (Last 7 days)", len(trades))
            st.markdown("---")
            
            if trades:
                df = pd.DataFrame(trades)
                df = df[[col for col in df.columns if col != 'id']]
                
                # Color code by risk score
                def highlight_risk(val):
                    if val >= 70:
                        return 'background-color: #ffcccc'
                    elif val >= 40:
                        return 'background-color: #ffffcc'
                    return ''
                
                st.dataframe(
                    df.style.applymap(highlight_risk, subset=['risk_score']) if 'risk_score' in df.columns else df,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No trades in the last 7 days")
        
        elif response.status_code == 403:
            st.error("You do not have permission to view trades")
        else:
            st.error(f"Failed to fetch trades: {response.status_code}")
    
    except Exception as e:
        st.error(f"Error: {e}")


def page_risk_alerts():
    """Risk alerts page."""
    st.header("🚨 Risk Alerts")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/data/risk-alerts",
            headers=get_headers(),
            timeout=5,
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "error" in data:
                st.error(data["error"])
                return
            
            alerts = data.get("alerts", [])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Alerts", data.get("total_alerts", 0))
            with col2:
                st.metric("High Severity", data.get("high_severity", 0), delta="alerts")
            with col3:
                st.metric("Alert Types", len(set(a['type'] for a in alerts)) if alerts else 0)
            
            st.markdown("---")
            
            if alerts:
                # Group by type
                for alert_type in set(a['type'] for a in alerts):
                    type_alerts = [a for a in alerts if a['type'] == alert_type]
                    
                    with st.expander(f"**{alert_type.replace('_', ' ').title()}** ({len(type_alerts)})"):
                        for alert in type_alerts:
                            severity_color = "🔴" if alert['severity'] == 'high' else "🟡"
                            st.write(f"{severity_color} **{alert['symbol']}**: {alert.get('reason', alert.get('exposure_percent', 'N/A'))}")
            else:
                st.success("✅ No risk alerts")
        
        elif response.status_code == 403:
            st.error("You do not have permission to view risk alerts")
        else:
            st.error(f"Failed to fetch alerts: {response.status_code}")
    
    except Exception as e:
        st.error(f"Error: {e}")


def page_ai_agent():
    """AI agent chat page."""
    st.header("🤖 AI Investment Agent")
    
    st.write("Ask questions about your portfolio and investments.")
    st.markdown("**Example questions:**")
    st.markdown("""
    - What are our top holdings?
    - What is our asset allocation?
    - Are we overexposed to any assets?
    - Which trades are high risk?
    - What are the recent market movements?
    """)
    
    st.markdown("---")
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me a question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/agent/query",
                json={"question": prompt},
                headers=get_headers(),
                timeout=30,
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "error" in data:
                    answer = f"❌ {data['error']}"
                else:
                    answer = data.get("answer", "No response")
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
                with st.chat_message("assistant"):
                    st.write(answer)
            else:
                error_msg = f"Error: {response.status_code}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.error(error_msg)
        
        except Exception as e:
            error_msg = f"Connection error: {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.error(error_msg)


def page_audit_logs():
    """Audit logs page."""
    st.header("📋 Audit Logs")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/audit/logs",
            headers=get_headers(),
            timeout=5,
        )
        
        if response.status_code == 200:
            data = response.json()
            logs = data.get("logs", [])
            
            st.metric("Total Audit Records", len(logs))
            st.markdown("---")
            
            if logs:
                df = pd.DataFrame(logs)
                
                # Status colors
                def status_color(row):
                    if row['allowed']:
                        return '✅ Allowed'
                    else:
                        return '❌ Denied'
                
                df['Status'] = df.apply(status_color, axis=1)
                
                # Format for display
                display_cols = ['timestamp', 'user', 'role', 'question', 'Status', 'denial_reason']
                df_display = df[[col for col in display_cols if col in df.columns]].copy()
                df_display['timestamp'] = pd.to_datetime(df_display['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info("No audit logs")
        
        elif response.status_code == 403:
            st.error("You do not have permission to view audit logs")
        else:
            st.error(f"Failed to fetch audit logs: {response.status_code}")
    
    except Exception as e:
        st.error(f"Error: {e}")


# ============= MAIN APP =============

def main():
    """Main app."""
    
    # Sidebar
    with st.sidebar:
        st.title("ARP Platform")
        
        if st.session_state.user:
            st.write(f"**Logged in as:** {st.session_state.user}")
            st.write(f"**Role:** {st.session_state.role}")
            st.markdown("---")
            
            # Navigation
            page = st.radio(
                "Navigate",
                ["📈 Portfolio", "💱 Trades", "🚨 Alerts", "🤖 AI Agent", "📋 Audit Logs"],
                label_visibility="collapsed",
            )
            
            st.markdown("---")
            
            if st.button("🚪 Logout"):
                logout_user()
                st.rerun()
        
        else:
            st.info("👈 Please login to continue")
    
    # Main content
    if not st.session_state.user:
        show_login()
    else:
        available_pages = get_available_pages(st.session_state.role)
        page = st.radio(
            "Navigate",
            available_pages,
            label_visibility="collapsed",
        )

        if page == "📈 Portfolio":
            page_portfolio()
        elif page == "💱 Trades":
            page_trades()
        elif page == "🚨 Alerts":
            page_risk_alerts()
        elif page == "🤖 AI Agent":
            page_ai_agent()
        elif page == "📋 Audit Logs":
            page_audit_logs()


if __name__ == "__main__":
    main()
