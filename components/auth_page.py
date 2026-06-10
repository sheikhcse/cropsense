"""
components/auth_page.py
Renders the Login / Register UI when user is not logged in.
"""
import streamlit as st
from database import register_user, login_user, get_user_count
from utils.constants import T
def render_auth_page():
    """Show login/register UI. Returns True if user just logged in."""
    lang = st.session_state.get("lang", "bn")
    L    = T[lang]

    # Language selector top-right
    _, _, col3 = st.columns([3, 1, 1])
    with col3:
        lc = st.selectbox("", ["বাংলা", "English"], key="lang_top",
                          index=0 if lang == "bn" else 1,
                          label_visibility="collapsed")
        st.session_state["lang"] = "bn" if lc == "বাংলা" else "en"
        L = T[st.session_state["lang"]]

    st.markdown(f"""
    <div style="text-align:center;padding:2rem 0 1rem">
      <h1 style="font-size:2.5rem;font-weight:800;color:#e2e8f0;margin:0">
        CropSense <span style="color:#4ade80">AI</span>
      </h1>
      <p style="color:#94a3b8;margin:0.3rem 0 0">{L['subtitle']}</p>
    </div>""", unsafe_allow_html=True)

    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        login_t, reg_t = st.tabs([L["login_tab"], L["register_tab"]])

        #  LOGIN
        with login_t:
            st.markdown(f"#### {L['login_title']}")
            uname = st.text_input(L["username"], key="li_user", placeholder="username")
            pw    = st.text_input(L["password"], type="password", key="li_pass", placeholder="••••••••")
            if st.button(L["login_btn"], use_container_width=True, type="primary", key="do_login"):
                if login_user(uname, pw):
                    st.session_state["logged_in"] = True
                    st.session_state["username"]  = uname
                    st.success(f"{L['login_success']}, {uname}!")
                    st.rerun()
                else:
                    st.error(L["login_error"])

            total = get_user_count()
            if total == 0:
                st.info("No accounts yet. Go to 'Register' tab to create one."
                        if lang == "en" else
                        "কোনো অ্যাকাউন্ট নেই। 'নতুন অ্যাকাউন্ট' ট্যাবে গিয়ে তৈরি করুন।")

        #  REGISTER 
        with reg_t:
            st.markdown(f"#### {L['register_title']}")
            new_user  = st.text_input(L["username"],         key="reg_user", placeholder="username")
            new_pass  = st.text_input(L["password"],         type="password", key="reg_pass", placeholder="••••••••")
            conf_pass = st.text_input(L["confirm_password"], type="password", key="reg_conf", placeholder="••••••••")
            if st.button(L["register_btn"], use_container_width=True, type="primary", key="do_reg"):
                if new_pass != conf_pass:
                    st.error(L["reg_pass_mismatch"])
                else:
                    ok, reason = register_user(new_user, new_pass)
                    if ok:
                        st.success(L["reg_success"])
                    else:
                        msg = {
                            "already_exists":  L["reg_exists"],
                            "username_short":  L["reg_user_short"],
                            "password_short":  L["reg_pass_short"],
                        }.get(reason, "Unknown error")
                        st.error(msg)

            total = get_user_count()
            if total > 0:
                st.caption(f"Total accounts: {total}" if lang == "en"
                           else f"মোট অ্যাকাউন্ট: {total}টি")
