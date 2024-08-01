import streamlit as st
from streamlit_extras.let_it_rain import rain

# Used this code to get base64 for SDG Icon
# import base64
# with open("static/sdg-icon.png", "rb") as image_file:
#     base64_image = base64.b64encode(image_file.read()).decode("utf-8")
# print(base64_image)
base64_image = "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"

def show_home():
    def sdgIconRain():
        rain(
            emoji=f'<img src="data:image/png;base64,{base64_image}" class="custom-emoji" width="50" height="50"/>',
            font_size=25,
            falling_speed=5,
            animation_length="infinite",
        )

    # Home Page Content     
    st.title("Welcome to the SDG Application")
    st.write(
        """
        Welcome to the Chatbot application. Navigate using the navigation bar at the top of the app 
        (colored in blue). Here's a brief overview of what each page offers:
        """
    )

    st.markdown("""
    <style>
    .nav-item {
        font-size: 18px;
        padding: 10px;
        position: relative;
        margin-left: 20px;
    }
    .nav-item::before {
        content: "\\2022";  /* bullet point */
        display: inline-block; 
        width: 1em;
        margin-left: -2em;
    }
    .page-description {
        font-size: 16px;
        position: relative;
        margin-left: 40px;
    }
    .page-description::before {
        content: "\\2022";  /* bullet point */
        display: inline-block; 
        width: 1em;
        margin-left: -3em; 
    }
    .custom-emoji {
        opacity: 0.5;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="nav-item"><strong>Chatbot:</strong>
        <div class="page-description">
            Interact with our AI chatbot for a variety of tasks and assistance.
        </div>
    </div>
    <div class="nav-item"><strong>Get Help:</strong>
        <div class="page-description">
            Access help and support resources to resolve any issues you may encounter.
        </div>
    </div>
    <div class="nav-item"><strong>Report a Bug:</strong>
        <div class="page-description">
            Found a bug? Report it here so we can fix it promptly.
        </div>
    </div>
    <div class="nav-item"><strong>About:</strong>
        <div class="page-description">
            Learn more about our application and the team behind it.
        </div>
    </div>
    <div class="nav-item"><strong>Admin:</strong>
        <div class="page-description">
            Admin settings and management area. For authorized personnel only.
        </div>
    </div>
    <div class="nav-item"><strong>Logout:</strong>
        <div class="page-description">
            Logout from the application securely.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    sdgIconRain()    

# Remove in PRD, only for testing file alone || For some reason when updated, doesnt update local streamlit app entirely
# if __name__ == "__main__":
#     show_home()