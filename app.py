import os
import boto3
# Use the package we installed
from slack_bolt import App

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)



# Add functionality here
# @app.event("app_home_opened") etc
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view={
                "type":
                "home",
                "callback_id":
                "home_view",

                # body of the view
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Welcome to your _App's Home_* :tada:"
                    }
                }, {
                    "type": "divider"
                }, {
                    "type": "section",
                    "text": {
                        "type":
                        "mrkdwn",
                        "text":
                        "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
                    }
                }, {
                    "type":
                    "actions",
                    "elements": [{
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Click me!"
                        }
                    }]
                }]
            })

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

@app.shortcut("linktokensezrirx")
def open_modal(ack, shortcut, client):
    # Acknowledge the shortcut request    
    ack()
    # Call the views_open method using the built-in WebClient
    client.views_open(
        trigger_id=shortcut["trigger_id"],
        # A simple view payload for a modal
        view={
            "type":
            "modal",
            "callback_id":
            "test2",
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            },
            "title": {
                "type": "plain_text",
                "text": "Link Webhooks",
                "emoji": True
            },
            "blocks": [{
                "type": "section",                
                "text": {
                    "type": "plain_text",
                    "text":
                    "Please provide the Cardknox Mid or a reference number for the account you'd like to enable cross tokenization for. ",
                    "emoji": True
                }
            }, {
                "type": "input",
                "block_id": "refmid",
                "element": {
                    "type": "number_input",
                    "is_decimal_allowed": False,
                    "action_id": "number_input-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "MID or RefNum",
                    "emoji": True
                }
            }]
        })



@app.view("test2")
def handle_submission(ack, body, client, view, logger):
    user = body["user"]["id"]
    username = body["user"]["username"]
    midref = view["state"]["values"]["refmid"]["number_input-action"]["value"]  
    print(body)
    #logger.error("testcreds:",os.environ.get("SLACK_BOT_TOKEN"),os.environ.get("SLACK_SIGNING_SECRET"),os.environ.get("aws_access_key_id"),os.environ.get("aws_secret_access_key"))
    if midref is not None:    
        try:
            send_plain_email(midref,username)   
        except :
            client.chat_postMessage(channel="U8TL3HS3W", text="Failed to send email")
            logger.exception(f"Failed to send email")

        
    


        
    

    # Acknowledge the view_submission request and close the modal
    ack()
    # Do whatever you want with the input data - here we're saving it to a DB
    # then sending the user a verification of their submission

    # Message to send user
    msg = ""
    try:
        # Save to DB
        msg = f"A ticket was created with the information you provided {midref}"
    except Exception as e:
        # Handle error
        msg = "There was an error with your submission"
        client.chat_postMessage(channel=user, text=msg)

    # Message the user
    try:
        client.chat_postMessage(channel=user, text=msg)
    except e:
        logger.exception(f"Failed to post a message {e}")

def send_plain_email(midref,username):
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    midrefid=midref
    username=username
    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                "gatewaysupport@cardknox.com",
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": f"Please enable cross tokenization: input 4755 in the Cardknox Settings of Cardknox MID/Refnum: {midrefid} and let #ck-partner-ezrirx know when done. This request originated from slack user {username}.",
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "Link tokens request",
            },
        },
        Source="ckintegrations@gmail.com",
    )    



# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 8080)))
