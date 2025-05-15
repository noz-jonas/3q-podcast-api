# streamlit_app.py
import streamlit as st
import requests
import toml
import datetime
import pytz

# Streamlit UI
st.title("Podcast Management")

st.caption("v1.9.10")
use_staging = st.toggle("Use staging environment", value=False)

podcast_selection = st.selectbox("Select podcast", ["Fokus Schleswig-Holstein", "Fokus Husum"])

env = "staging" if use_staging else "live"

# Preflight check for required secrets
required_keys = [
    f"{env}_project_id",
    f"{env}_api_key",
    f"{env}_podcast_id_fokussh",
    f"{env}_podcast_id_fokushusum",
    "sdnSessionRemember",
    "imgaccess_token",
    "image_clientId_token"
]

missing_keys = [key for key in required_keys if key not in st.secrets]
if missing_keys:
    st.error(f"Missing required configuration keys: {', '.join(missing_keys)}. Please update your secrets.toml.")
    st.stop()

project_id = st.secrets[f"{env}_project_id"]
if podcast_selection == "Fokus Schleswig-Holstein":
    podcast_id = st.secrets[f"{env}_podcast_id_fokussh"]
    category_id = "7453"
    videotype_id = "709"
else:  # Fokus Husum
    podcast_id = st.secrets[f"{env}_podcast_id_fokushusum"]
    category_id = "7593"
    videotype_id = "805"

api_key = st.secrets[f"{env}_api_key"]
season_id = st.secrets[f"{env}_season_id"]

st.divider()
file_id = st.text_input("Enter File ID").strip()
article_id = st.text_input("Enter the article ID of the focus topic").strip()

if st.button("Start Processing"):
    if not file_id or not article_id:
        st.error("Either the File ID or Article ID is missing. Please check.")
    else:
        with st.spinner("Processing..."):
            # TODO: Securely handle authentication cookie
            podcast_url = f"https://sdn.3qsdn.com/de/podcast/{podcast_id}/episode/addnew"
            payload = {'fileIds[]': file_id}
            headers_podcast = {
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://sdn.3qsdn.com',
                'Referer': f'https://sdn.3qsdn.com/de/podcast/{podcast_id}/episode',
                'X-Requested-With': 'XMLHttpRequest'
            }
            cookies_podcast = {'sdnSessionRemember': st.secrets["sdnSessionRemember"]}

            podcast_response = requests.post(podcast_url, headers=headers_podcast, cookies=cookies_podcast, data=payload)

            if podcast_response.status_code == 401:
                st.error("Authorization failed. Please ask the product manager and tell them to 'log in to the Podcast Provider'.")
            elif podcast_response.ok:
                st.success("Episode added to Podcast ✅")

                headers = {
                    "X-AUTH-APIKEY": api_key,
                    "Accept": "application/json"
                }

                errors = 0

                # API calls sequence

                # 3.1 Set Videotype
                # Set generic podcast Videotype (ID 200)
                videotype_url_base = f"https://sdn.3qsdn.com/api/v2/projects/{project_id}/files/{file_id}/metadata/videotype"
                try:
                    response_videotype_generic = requests.patch(f"{videotype_url_base}/200", headers={**headers, "Content-Type": "application/json"})
                    if response_videotype_generic.status_code == 409 and "Link already exists" in response_videotype_generic.text:
                        st.success("Generic Podcast Videotype already set ✅")
                    else:
                        response_videotype_generic.raise_for_status()
                        st.success("Generic Podcast Videotype ✅")
                except requests.exceptions.RequestException as e:
                    st.error(f"Generic Podcast Videotype ❌ - {e}")
                    errors += 1

                videotype_url = f"https://sdn.3qsdn.com/api/v2/projects/{project_id}/files/{file_id}/metadata/videotype/{videotype_id}"
                try:
                    response_videotype = requests.patch(videotype_url, headers={**headers, "Content-Type": "application/json"})
                    if response_videotype.status_code == 409 and "Link already exists" in response_videotype.text:
                        st.success("Videotype already set ✅")
                    else:
                        response_videotype.raise_for_status()
                        st.success("Videotype ✅")
                except requests.exceptions.RequestException as e:
                    st.error(f"Videotype ❌ - {e}")
                    errors += 1

                # 3.2 Set Category
                category_url = f"https://sdn.3qsdn.com/api/v2/projects/{project_id}/files/{file_id}/metadata/category/{category_id}"
                try:
                    response_category = requests.patch(category_url, headers={**headers, "Content-Type": "application/json"})
                    if response_category.status_code == 409 and "Link already exists" in response_category.text:
                        st.success("Category already set ✅")
                    else:
                        response_category.raise_for_status()
                        st.success("Category ✅")
                except requests.exceptions.RequestException as e:
                    st.error(f"Category ❌ - {e}")
                    errors += 1

                if errors >= 2:
                    st.error("Something went wrong. Please check the fileId or ask the product manager.")
                else:
                    # 3.3 Set Vertical Image
                    if podcast_selection == "Fokus Schleswig-Holstein":
                        image_url_vertical = f"https://sdn-global-prog-cache.3qsdn.com/12394/files/25/04/23/11438305/759401e4-e413-4f74-8fa6-d59c8dd37234.jpg"
                    else:
                        image_url_vertical = "https://sdn-global-prog-cache.3qsdn.com/12394/files/25/05/15/11506125/81053dd2-1564-4fdb-953d-9913c49f512c.jpg"
                    try:
                        img_data_vertical = requests.get(image_url_vertical).content

                        response_image_vertical = requests.post(
                            f"https://sdn.3qsdn.com/api/v2/projects/{project_id}/files/{file_id}/pictures",
                            headers={"X-AUTH-APIKEY": api_key, "Content-type": "image/jpeg"},
                            data=img_data_vertical
                        )
                        response_image_vertical.raise_for_status()
                        st.success("Vertical Image ✅")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Vertical Image ❌ - {e}")
                        errors += 1

                    # 3.4 Set Podcast Cover
                    if podcast_selection == "Fokus Schleswig-Holstein":
                        image_url_cover = f"https://sdn-global-prog-cache.3qsdn.com/uploads/252/podcast/3d941bd8-6020-4234-9469-d2245fa5ae0c.jpg"
                    else:
                        image_url_cover = "https://sdn-global-prog-cache.3qsdn.com/uploads/252/podcast/e52765d5-68b8-4777-be48-dbc654f9d3c6.jpg"
                    try:
                        img_data_cover = requests.get(image_url_cover).content

                        response_image_cover = requests.post(
                            f"https://sdn.3qsdn.com/api/v2/projects/{project_id}/files/{file_id}/pictures",
                            headers={"X-AUTH-APIKEY": api_key, "Content-type": "image/jpeg"},
                            data=img_data_cover
                        )
                        response_image_cover.raise_for_status()
                        st.success("Podcast Cover Image ✅")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Podcast Cover Image ❌ - {e}")
                        errors += 1

                    # 3.5 Set Body Text
                    from datetime import datetime, time
                    import pytz

                    berlin = pytz.timezone("Europe/Berlin")
                    if podcast_selection == "Fokus Schleswig-Holstein":
                        release_time = time(7, 0)
                    else:
                        release_time = time(16, 0)
                    release_dt_local = berlin.localize(datetime.combine(datetime.today(), release_time))
                    release_dt_utc = release_dt_local.astimezone(pytz.utc)
                    formatted_release_time = release_dt_utc.strftime("%Y-%m-%d %H:%M:%S")

                    body_payload = {
                        "DisplayTitleSecondLine": "Fokus Schleswig-Holstein" if podcast_selection == "Fokus Schleswig-Holstein" else "Fokus Husum",
                        "cf_Body": """
                            <h1>Du hast Feedback zum neuen Format?</h1>
                            <p>Dann&nbsp;<strong>schreib uns gerne eine E-Mail</strong>&nbsp;an&nbsp;
                            <a href=\"mailto:audio@noz-digital.de\">audio@noz-digital.de</a>&nbsp;
                            oder nimm an unserer&nbsp;<strong>Umfrage zum Podcast</strong>&nbsp;teil:&nbsp;
                            <a href=\"https://de.research.net/r/fokus-sh\">https://de.research.net/r/fokus-sh</a>.</p>
                            """ if podcast_selection == "Fokus Schleswig-Holstein" else "",
                        "IsPublicAt": formatted_release_time
                    }
                    try:
                        body_url = f"https://sdn.3qsdn.com/api/v2/projects/{project_id}/files/{file_id}/metadata"
                        response_body = requests.put(body_url, headers={**headers, "Content-Type": "application/json"}, json=body_payload)
                        response_body.raise_for_status()
                        st.success("Body Text, Subtitle & Release Date ✅")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Body Text, Subtitle & Release Date ❌ - {e}")
                        errors += 1

                    if errors >= 2:
                        st.error("Something went wrong. Please check the fileId or ask the product manager.")
                    # 3.6 Set Season for Episode
                    # try:
                    #     season_payload = {
                    #         "_method": "PATCH",
                    #         "podcast_episode[Permalink]": "",
                    #         "podcast_episode[Author]": "",
                    #         "podcast_episode[Keywords]": "",
                    #         "podcast_episode[EpisodeType]": "full",
                    #         "podcast_episode[FeedGuid]": "",
                    #         "podcast_episode[PodcastSeasons]": season_id
                    #     }
                    #     headers_season = {
                    #         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    #         "Origin": "https://sdn.3qsdn.com",  
                    #         "Referer": f"https://sdn.3qsdn.com/de/podcast/{podcast_id}/episode",
                    #         "X-Requested-With": "XMLHttpRequest"
                    #     }
                    #     if use_staging:
                    #         st.caption(f"POST to: https://sdn.3qsdn.com/de/podcast/{podcast_id}/episode/{file_id}/edit with season ID {season_id}")
                    #     response_season = requests.post(
                    #         f"https://sdn.3qsdn.com/de/podcast/{podcast_id}/episode/{file_id}/edit",
                    #         headers=headers_season,
                    #         cookies={"sdnSessionRemember": st.secrets["sdnSessionRemember"]},
                    #         data=season_payload
                    #     )
                    #     response_season.raise_for_status()
                    #     st.success("Season ✅")
                    # except requests.exceptions.RequestException as e:
                    #     st.error(f"Season ❌ - {e}")
                    #     if use_staging:
                    #         st.text(f"Raw response: {response_season.text if 'response_season' in locals() else 'No response'}")
                    #     errors += 1

                    if article_id:
                        # This may overwrite the podcast cover set in step 3.4 if successful
                        image_api_url = f"https://www.shz.de/imageurl/{article_id}/crop/cvirtual.center-w1080-h1080?dsimgaccess={st.secrets['imgaccess_token']}&imageGeneratorClientIdToken={st.secrets['image_clientId_token']}"
                        try:
                            image_response = requests.get(image_api_url)
                            image_response.raise_for_status()
                            image_url_cover = image_response.json().get("url")
                            
                            if image_url_cover:
                                img_data_cover = requests.get(image_url_cover).content
                                response_image_cover = requests.post(
                                    f"https://sdn.3qsdn.com/api/v2/projects/{project_id}/files/{file_id}/pictures",
                                    headers={"X-AUTH-APIKEY": api_key, "Content-type": "image/jpeg"},
                                    data=img_data_cover
                                )
                                response_image_cover.raise_for_status()
                                st.success("Podcast Cover from article ✅")
                            else:
                                st.error("No URL found in image API response.")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Podcast Cover from article ❌ - {e}")

                        # Set release status to published
                        try:
                            release_url = f"https://sdn.3qsdn.com/api/v2/project/{project_id}/files/{file_id}"
                            release_payload = {"ReleaseStatus": "published"}
                            response_release = requests.post(release_url, headers={**headers, "Content-Type": "application/json"}, json=release_payload)
                            response_release.raise_for_status()
                            st.success("Release status set to published ✅")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Failed to set release status ❌ - {e}")

                        st.success("DONE! ✅")
            else:
                st.error("Something went wrong and I don't know what... Could you please check the File ID?")
