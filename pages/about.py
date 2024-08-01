import streamlit as st

def show_about():
    st.header("About")
    st.write(
        """
        This app is designed to read Confluence pages that were extracted and imported into Snowflake. It utilizes a chatbot to access the data from Snowflake so users can query questions about the Confluence pages. This integration allows for seamless data retrieval and interactive querying, making it easier to access and analyze Confluence content.
        """
    )

    # horizontal line
    st.markdown("---")
    
    # CSS for "coming soon section"
    st.markdown("""
    <style>
    .coming-soon-section {
        text-align: center;
        margin-top: 10px;
    }
    .coming-soon-image {
        margin-bottom: 20px;
    }
    .coming-soon-text {
        font-size: 1.5em;
        font-weight: bold;
    }
    .stay-tuned {
        font-size: 1.2em;
    }
    </style>
    """, unsafe_allow_html=True)

    # html for "coming soon section"
    st.markdown("""
    <div class="coming-soon-section">
        <img src="https://images.squarespace-cdn.com/content/v1/502c5b17e4b0023d7ed017ec/1542854099598-39NFPWUNG2IXKN4FG1UF/coming-soon.png" class="coming-soon-image" width="150">
        <div class="coming-soon-text">More features coming soon!</div>
        <div class="stay-tuned">
            Stay tuned for more updates and enhancements that will make your experience even better.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Remove in PRD, only for testing file alone || For some reason when updated, doesnt update local streamlit app entirely
# if __name__ == "__main__":
#     show_about()