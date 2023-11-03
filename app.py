import streamlit as st
import retrieve_menu_from_url as menu_lib
import generate_image as glib
import json
import uuid
import boto3 

st.set_page_config(layout="wide", page_title="Generate images for your menu!")
st.title("Generate images for your menu!")
col1, col2, col3 = st.columns(3)

# Initialize session_state
if 'menu_array' not in st.session_state:
    st.session_state.menu_array = []
if 'process_button_active' not in st.session_state:
    st.session_state.process_button_active = False
if 'image_urls' not in st.session_state:
    st.session_state.image_urls = []
if 'menu_details' not in st.session_state:
    st.session_state.menu_details = []

def upload_to_s3(data, content_type, bucket_name, s3_filename):
    try:
        s3.put_object(Body=data, Bucket=bucket_name, Key=s3_filename, ContentType=content_type, ACL='public-read')
        return f"https://{bucket_name}.s3.amazonaws.com/{s3_filename}"
    except Exception as e:
        st.error(f"Error uploading to S3: {str(e)}")
        return None

s3 = boto3.client('s3')

with col1:
    st.subheader("Input menu url")
    url = st.text_input("Enter a URL:")
    if st.button("Send"):
        if url:
            with st.spinner("Retrieving..."):
                try:
                    web_data = menu_lib.retrieve_web_data(url)
                    if web_data is None:
                        st.text("Web data retrieval failed.")
                    else:
                        st.text("Extracting menu items from Claude v2...")
                        menu_items = menu_lib.get_menu(web_data)
                        if menu_items:
                            st.text("Menu Items:")
                            st.text(menu_items)
                            start_idx = menu_items.index('[')
                            end_idx = menu_items.rindex(']') + 1
                            cleaned_data = menu_items[start_idx:end_idx]
                            st.session_state.menu_array = json.loads(cleaned_data)
                            st.session_state.process_button_active = True
                        else:
                            st.text("Menu extraction failed.")
                except Exception as e:
                    st.error(f"Error processing the URL: {str(e)}")
    process_button = st.button("Generate images", type="primary", disabled=not st.session_state.process_button_active)

with col2:
    st.subheader("Image Result")
    if process_button:
        try:
            with st.spinner("Drawing..."):
                for prompt_text in st.session_state.menu_array:
                    formatted_prompt = "{} - {}".format(prompt_text['title'], prompt_text['ingredients'])
                    generated_image = glib.get_image_response(prompt_content=formatted_prompt)
                    st.image(generated_image)

                    # Upload the image to S3 and store the URL and menu details
                    image_url = upload_to_s3(generated_image, 'image/png', 'jiwony-publicbucket', f"menu_image_{uuid.uuid4()}.png")
                    if image_url:
                        st.session_state.image_urls.append(image_url)
                        st.session_state.menu_details.append({
                            "title": prompt_text['title'],
                            "ingredients": prompt_text['ingredients'],
                            "price": prompt_text.get('price', 'N/A')  # If the price key doesn't exist, replace with 'N/A'
                        })
                
        except Exception as e:
            st.error(f"Error generating images: {str(e)}")
    menu_gen_button = st.button("Generate menu page", disabled=not st.session_state.process_button_active)

with col3:
    st.subheader("New menu with images!")
    try:
        if menu_gen_button:
            html_content = "<html><body><table>"
            for img_url, detail in zip(st.session_state.image_urls, st.session_state.menu_details):
                html_content += f"""
                <tr>
                    <td><img src="{img_url}" alt="Generated Image" width="300"></td>
                    <td>
                        <strong>{detail['title']}</strong><br>
                        {detail['ingredients']}<br>
                        {detail['price']}
                    </td>
                </tr>
                """
            html_content += "</table></body></html>"

            # Upload the generated HTML to S3
            html_file_name = f"menu_page_{uuid.uuid4()}.html"
            s3_url = upload_to_s3(html_content, 'text/html', 'jiwony-publicbucket', html_file_name)

            if s3_url:
                st.markdown(f"[Click here to view the generated menu page]({s3_url})")
            else:
                st.error("Failed to generate the menu page.")
    except Exception as e:
        st.error(f"Error generating the menu page: {str(e)}")
