from playwright.sync_api import sync_playwright

def login_to_instagram(username, password, state_file="auth_state.json"):
    with sync_playwright() as p:
        # Launch a new browser instance
        browser = p.chromium.launch(headless=False)  # Set headless=True to run in the background
        context = browser.new_context()

        # Open a new page
        page = context.new_page()

        # Navigate to Instagram login page
        page.goto("https://www.instagram.com/accounts/login/")

        # Wait for the login form to load
        page.wait_for_selector("input[name='username']")

        # Fill in the username and password
        page.fill("input[name='username']", username)
        page.fill("input[name='password']", password)

        # Click the login button
        with page.expect_navigation():  # Waits for navigation triggered by the login
            page.click("button[type='submit']")

        # Wait for a specific element on the homepage to confirm login
        try:
            page.wait_for_selector("svg[aria-label='Home']", timeout=10000)  # Adjust timeout as needed
            print("Login successful!")
            # Save the session state to a file
            context.storage_state(path=state_file)
        except:
            print("Login failed. Please check your credentials.")

        # Keep the browser open
        input("Press Enter to close the browser...")



def influencer_similar_accounts(influencer_link, page, state_file="auth_state.json"):

    # Navigate to Instagram
    page.goto("https://www.instagram.com/")

    # Verify if the user is logged in
    if page.url == "https://www.instagram.com/":
        print("Logged in using saved state!")
    else:
        print("Session expired. Please log in again.")

    # Navigate to the first influencer's profile
    page.goto(influencer_link)

    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")

    # Click on the "Similar accounts" button
    page.get_by_role("button", name="Similar accounts").click()

    page.get_by_role("link", name="See all").click()
        
    # Wait for dialog to appear
    page.wait_for_selector("[role='dialog']")

    # Scroll 400px down and try to get more links
    page.evaluate("window.scrollBy(0, 400);")
    page.wait_for_timeout(1000)
        
    # Get all links within the dialog
    links = page.locator("[role='dialog'] a[href^='/']").all()
        
    # Extract and print the URLs
    similar_accounts = []
    for link in links:
        href = link.get_attribute('href')
        if href:
            full_url = f"https://www.instagram.com{href}"
            similar_accounts.append(full_url)
                
    # Remove duplicates by converting to a set and back to a list
    similar_accounts = list(set(similar_accounts))

    print("Found similar accounts:", similar_accounts)
    print(f"Total similar accounts found: {len(similar_accounts)}")
        
    return similar_accounts, page

def initial_influencer_filtering(influencer_links, page, state_file="auth_state.json"):
    minFollowers = int(8000)
    maxFollowers = int(350000)
    allowedLocation = "United States"

    filtered_list = []

    for influencer in influencer_links:
        # Navigate to the first influencer's profile
        page.goto(influencer)

        # Wait for the page to load completely
        page.wait_for_load_state("networkidle")

        try:
            # Example of using .get_by_role()
            followers_text = page.get_by_role('link', name='followers').inner_text()      
            followers_str = followers_text.split()[0] 
            followers = int(calculate_followers_num(followers_str))
            print("Followers: ", followers)

            if followers > maxFollowers or followers < minFollowers:
                continue

            username = influencer.split("instagram.com/")[1].split('/')[0] 
            page.get_by_role("heading", name=username).click()

            # Wait for the page to load completely
            page.wait_for_load_state("networkidle")
            accountLocationText = page.get_by_role("button", name="Account based in").text_content()
            location = accountLocationText.split("Account based in")[1]
            print(location)

            if location == allowedLocation:
                filtered_list.append(influencer)
        except:
            continue

    return filtered_list

def calculate_followers_num(followers):
    followers = followers.replace(',', '')
    if followers[-1] == "K":
        return float(followers[:-1])*1000
    elif followers[-1] == "M":
        return float(followers[:-1])*1000000
    return followers

def scraper(influencer_link, page, state_file="auth_state.json"):
    # Navigate to the first influencer's profile
    page.goto(influencer_link)

    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")
    more_button = page.get_by_role("button", name="more")
    if more_button:
        more_button.click()
    header_text = page.locator("header").inner_text()
    print(header_text)

    username = influencer_link.split("instagram.com")[1]
    print(username)
    # Locate all posts
    all_posts = page.locator(f'a[href^="{username}p/"], a[href^="{username}reel/"]')

    post_links = []
    likes = []
    commentNums = []
    MAX_POSTS = 6
    # Loop through the posts and print their href attributes
    for i in range(min(all_posts.count(), MAX_POSTS)):
        post = all_posts.nth(i)  # Access the post at index `i`
        href = post.get_attribute("href")  # Get the href attribute
        post_links.append(href)

        # Navigate to the closest parent div containing the <ul>
        parent_div = post.locator('xpath=ancestor::div[1]')
        parent_div.hover()
        likes_comments_ul = parent_div.locator("ul")  # Locate the <ul> inside the parent
        likes_comments = likes_comments_ul.inner_text()
        
        # Split the text by newline or whitespace
        split_text = likes_comments.split("\n")
        likes.append(split_text[0])
        commentNums.append(split_text[1])

    captions = []
    all_comments = []
    for post_link in post_links:
        link = "https://www.instagram.com"+post_link
        post_caption, comments = post_scraper(link, page)
        captions.append(post_caption)
        all_comments.append(comments)


    print("Likes: ", likes)
    print("Comments: ", commentNums)
    print("Post Links: ", post_links)
    print("Captions: ", captions)
    print("All Comments: ", all_comments)
    

def post_scraper(post_link, page, state_file="auth_state.json"):
    # Navigate to the post link
    page.goto(post_link)
    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")

    post_caption = page.locator("h1").inner_text()

    # Initialize a list to store first comments
    all_comments = []

    comment_containers = page.locator("ul._a9ym")
    # Iterate through each container
    for container_index in range(comment_containers.count()):
        # Get the current container
        container = comment_containers.nth(container_index)

        # Locate all `li` elements in the container
        comments = container.locator('li').all_inner_texts()
        # Check if there are comments and skip sub-comments (like "View replies")
        if comments:
            first_comment = comments[0]
            if "View replies" not in first_comment:
                split_comment = first_comment.split("\n")
                comment = split_comment[0]+": "+split_comment[1]
                all_comments.append(comment)

    return post_caption, all_comments



def scraper_driver():
    #Take in primary influencer username from terminal input
    primary_influencer_link = input("Enter the primary influencer's link: ")

    print("Launching browser...")
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)  # Do NOT use headless=True
    context = browser.new_context(storage_state="auth_state.json")  # Use persistent session if needed
    page = context.new_page()

    # similar_accounts, page = influencer_similar_accounts(primary_influencer_link, page)

    # #Take in list of similar accounts
    # final_list = initial_influencer_filtering(similar_accounts, page)
    # print(final_list)

    scraper("https://www.instagram.com/bradstulberg/", page)

    # Keep the browser open
    input("Press Enter to close the browser...")
    browser.close()
    p.stop()
