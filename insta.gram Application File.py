import hashlib
import sqlite3
import streamlit as st

# Instagram का ऑफिशियल आइकॉन यूआरएल
insta_logo_url = (
    "https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png"
)

# पेज का टाइटल और ब्राउज़र टैब में आइकॉन सेट करें
st.set_page_config(
    page_title="insta.gram",
    page_icon=insta_logo_url,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# मोबाइल फ्रेंडली लुक देने के लिए CSS
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 600px;
    }
    stButton>button {
        width: 100%;
        border-radius: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# पासवर्ड हैश करने के लिए फंक्शन
def make_hash(password):
  return hashlib.sha256(str.encode(password)).hexdigest()


def check_password(password, hashed_text):
  return make_hash(password) == hashed_text


# डेटाबेस कनेक्शन सेट अप करें
conn = sqlite3.connect("instagarm_app.db", check_same_thread=False)
c = conn.cursor()

# टेबल्स बनाएं
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        insta_handle TEXT
    )
""")
c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        caption TEXT,
        image_url TEXT,
        likes INTEGER
    )
""")
c.execute("""
    CREATE TABLE IF NOT EXISTS post_likes (
        post_id INTEGER,
        username TEXT,
        UNIQUE(post_id, username)
    )
""")
c.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        username TEXT,
        comment_text TEXT
    )
""")
conn.commit()

# सेशन स्टेट मैनेज करें
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.username = ""

# --- यदि यूजर लॉगिन नहीं है ---
if not st.session_state.logged_in:
  col1, col2 = st.columns([1, 6])
  with col1:
    st.image(insta_logo_url, width=50)
  with col2:
    st.title("insta.gram")

  st.write("अपने अकाउंट से लॉगिन करें या नया अकाउंट बनाएं।")

  auth_choice = st.selectbox(
      "विकल्प चुनें", ["लॉगिन (Login)", "नया अकाउंट बनाएं (Sign Up)"]
  )

  if auth_choice == "नया अकाउंट बनाएं (Sign Up)":
    st.subheader("नया यूजर रजिस्टर करें")
    new_user = st.text_input("insta.gram यूजरनेम चुनें")
    new_password = st.text_input("पासवर्ड चुनें", type="password")
    new_insta = st.text_input(
        "अपना असली Instagram हैंडल (जैसे: @your_handle) - वैकल्पिक"
    )

    if st.button("साइन अप करें"):
      if new_user and new_password:
        try:
          c.execute(
              "INSERT INTO users (username, password, insta_handle) VALUES"
              " (?, ?, ?)",
              (new_user, make_hash(new_password), new_insta),
          )
          conn.commit()
          st.success("अकाउंट सफल! अब 'लॉगिन' विकल्प चुनें।")
        except sqlite3.IntegrityError:
          st.error("यह यूजरनेम पहले से मौजूद है।")
      else:
        st.warning("कृपया यूजरनेम और पासवर्ड भरें।")

  else:
    st.subheader("लॉगिन करें")
    username = st.text_input("यूजरनेम")
    password = st.text_input("पासवर्ड", type="password")
    remember_me = st.checkbox("मुझे याद रखें (Remember Me)")

    if st.button("लॉगिन"):
      c.execute("SELECT password FROM users WHERE username = ?", (username,))
      result = c.fetchone()
      if result and check_password(password, result[0]):
        st.session_state.logged_in = True
        st.session_state.username = username
        if remember_me:
          st.info("आपका सेशन याद रखा गया है!")
        st.success(f"स्वागत है, {username}!")
        st.rerun()
      else:
        st.error("गलत यूजरनेम या पासवर्ड।")

else:
  # --- मुख्य ऐप (जब यूजर लॉगिन हो) ---
  st.sidebar.image(insta_logo_url, width=35)
  st.sidebar.title(f"👤 @{st.session_state.username}")

  nav_page = st.sidebar.radio(
      "नेविगेशन", ["🏠 होम फीड (Feed)", "👤 माई प्रोफाइल (My Profile)"]
  )

  st.sidebar.markdown("---")
  st.sidebar.subheader("📱 मोबाइल ऐप शॉर्टकट")
  st.sidebar.write(
      "एंड्रॉइड फोन पर क्रोम (Chrome) में ऊपर **(⋮)** पर क्लिक करके **'Add to"
      " Home screen'** चुनें।"
  )

  st.sidebar.markdown("---")
  if st.sidebar.button("लॉग आउट (Logout)"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

  # यूजर का इंस्टाग्राम हैंडल फेच करें
  c.execute(
      "SELECT insta_handle FROM users WHERE username = ?",
      (st.session_state.username,),
  )
  user_data = c.fetchone()
  current_insta = user_data[0] if user_data and user_data[0] else "लिंक नहीं है"

  # ==========================================
  # 1. होम फीड पेज
  # ==========================================
  if nav_page == "🏠 होम फीड (Feed)":
    col1, col2 = st.columns([1, 10])
    with col1:
      st.image(insta_logo_url, width=40)
    with col2:
      st.title("insta.gram")

    # नया पोस्ट फॉर्म
    with st.form("post_form", clear_on_submit=True):
      st.subheader("नई पोस्ट शेयर करें")
      caption = st.text_area("कैप्शन लिखें (Caption)...")
      image_url = st.text_input("इमेज का लिंक (Image URL, जैसे Unsplash फोटो लिंक)")

      submitted = st.form_submit_button("पोस्ट करें")

      if submitted:
        if caption and image_url:
          c.execute(
              "INSERT INTO posts (username, caption, image_url, likes) VALUES"
              " (?, ?, ?, ?)",
              (st.session_state.username, caption, image_url, 0),
          )
          conn.commit()
          st.success("आपकी पोस्ट शेयर हो गई है!")
          st.rerun()
        else:
          st.warning("कृपया कैप्शन और इमेज लिंक दोनों भरें।")

    st.markdown("---")
    st.subheader("🌐 सभी पोस्ट्स")

    c.execute("""
            SELECT posts.id, posts.username, posts.caption, posts.image_url, posts.likes, users.insta_handle 
            FROM posts 
            LEFT JOIN users ON posts.username = users.username 
            ORDER BY posts.id DESC
        """)
    posts = c.fetchall()

    if not posts:
      st.info("अभी कोई पोस्ट नहीं है।")

    # स्पॉन्सर्ड विज्ञापनों (Ads) की लिस्ट
    ads_list = [
        {
            "brand": "Python Pro Coding",
            "caption": (
                "🚀 सीखिए एडवांस्ड पाइथन और Streamlit सिर्फ 30 दिनों में! आज ही"
                " रजिस्टर करें।"
            ),
            "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5",
            "cta": "अभी एनरोल करें",
        },
        {
            "brand": "Vibe Gadgets",
            "caption": (
                "🎧 बेस्ट वायरलेस ईयरबड्स पर चल रहा है 50% डिस्काउंट! स्टॉक सीमित"
                " है।"
            ),
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
            "cta": "शॉप नाउ",
        },
    ]

    post_counter = 0
    for post in posts:
      post_counter += 1
      post_id, post_user, post_caption, post_image, post_likes, post_insta = (
          post
      )

      with st.container():
        insta_display = (
            f" (IG: `{post_insta}`)" if post_insta else " (IG: N/A)"
        )
        st.markdown(f"**@{post_user}** {insta_display}")

        try:
          st.image(post_image, use_container_width=True)
        except:
          st.error("इमेज लोड करने में समस्या आई।")

        st.write(post_caption)

        # वन-लाइक-पर-यूजर चेक
        col1, col2 = st.columns([1, 5])
        with col1:
          c.execute(
              "SELECT 1 FROM post_likes WHERE post_id = ? AND username = ?",
              (post_id, st.session_state.username),
          )
          already_liked = c.fetchone()

          if already_liked:
            st.button("❤️ लाइक किया", key=f"liked_{post_id}", disabled=True)
          else:
            if st.button("🤍 लाइक करें", key=f"like_{post_id}"):
              try:
                c.execute(
                    "INSERT INTO post_likes (post_id, username) VALUES (?, ?)",
                    (post_id, st.session_state.username),
                )
                c.execute(
                    "UPDATE posts SET likes = likes + 1 WHERE id = ?",
                    (post_id,),
                )
                conn.commit()
                st.rerun()
              except sqlite3.IntegrityError:
                pass

        st.write(f"❤️ {post_likes} Likes")

        # --- कमेंट सेक्शन ---
        st.markdown("💬 **कमेंट्स:**")
        c.execute(
            "SELECT username, comment_text FROM comments WHERE post_id = ?"
            " ORDER BY id ASC",
            (post_id,),
        )
        post_comments = c.fetchall()

        if post_comments:
          for c_user, c_text in post_comments:
            st.markdown(
                f"<div style='margin-left: 10px; font-size:"
                f" 14px;'><b>@{c_user}:</b> {c_text}</div>",
                unsafe_allow_html=True,
            )
        else:
          st.markdown(
              "<small style='color: gray;'>कोई कमेंट नहीं है।</small>",
              unsafe_allow_html=True,
          )

        with st.form(key=f"comment_form_{post_id}", clear_on_submit=True):
          comment_input = st.text_input(
              "कमेंट लिखें...", key=f"input_{post_id}"
          )
          submit_comment = st.form_submit_button("कमेंट भेजें")

          if submit_comment:
            if comment_input.strip():
              c.execute(
                  "INSERT INTO comments (post_id, username, comment_text)"
                  " VALUES (?, ?, ?)",
                  (post_id, st.session_state.username, comment_input),
              )
              conn.commit()
              st.rerun()

        st.markdown("---")

      # --- स्पॉन्सर्ड विज्ञापन (हर 2 पोस्ट के बाद) ---
      if post_counter % 2 == 0:
        ad = ads_list[(post_counter // 2 - 1) % len(ads_list)]
        with st.container():
          st.info("📢 **Sponsored • Paid Advertisement**")
          st.markdown(f"**🏢 {ad['brand']}**")
          try:
            st.image(ad["image"], use_container_width=True)
          except:
            pass
          st.write(ad["caption"])
          if st.button(ad["cta"], key=f"ad_btn_{post_counter}"):
            st.success(
                f"धन्यवाद! आप {ad['brand']} के स्पॉन्सर्ड पेज पर रीडायरेक्ट हो"
                " रहे हैं।"
            )
          st.markdown("---")

  # ==========================================
  # 2. माई प्रोफाइल पेज
  # ==========================================
  elif nav_page == "👤 माई प्रोफाइल (My Profile)":
    st.title(f"👤 @{st.session_state.username} की प्रोफाइल")
    st.write(f"**आपका जुड़ा हुआ Instagram:** {current_insta}")

    with st.form("update_insta"):
      new_insta_input = st.text_input(
          "अपना Instagram हैंडल अपडेट करें", value=current_insta
      )
      update_btn = st.form_submit_button("अपडेट करें")
      if update_btn:
        c.execute(
            "UPDATE users SET insta_handle = ? WHERE username = ?",
            (new_insta_input, st.session_state.username),
        )
        conn.commit()
        st.success("इंस्टाग्राम हैंडल अपडेट हो गया!")
        st.rerun()

    st.markdown("---")
    st.subheader("आपके द्वारा शेयर किए गए पोस्ट्स")

    c.execute(
        "SELECT id, caption, image_url, likes FROM posts WHERE username = ?"
        " ORDER BY id DESC",
        (st.session_state.username,),
    )
    my_posts = c.fetchall()

    if not my_posts:
      st.info("आपने अभी तक कोई पोस्ट शेयर नहीं की है।")

    for post in my_posts:
      post_id, post_caption, post_image, post_likes = post

      with st.container():
        try:
          st.image(post_image, use_container_width=True)
        except:
          st.error("इमेज लोड करने में समस्या आई।")

        st.write(post_caption)
        st.write(f"❤️ {post_likes} Likes")

        if st.button("🗑️ इस पोस्ट को डिलीट करें", key=f"del_{post_id}"):
          c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
          c.execute("DELETE FROM post_likes WHERE post_id = ?", (post_id,))
          c.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
          conn.commit()
          st.success("पोस्ट डिलीट कर दी गई!")
          st.rerun()

        st.markdown("---")