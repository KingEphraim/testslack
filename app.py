import os
# Use the package we installed
from slack_bolt import App

# Initializes your app with your bot token and signing secret
app = App(token=os.environ.get("SLACK_BOT_TOKEN"),
          signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))


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

@app.shortcut("linkwebhook")
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


# Handle a view_submission request
@app.view("test2")
def handle_submission(ack, body, client, view, logger):
    # Assume there's an input block with `input_c` as the block_id and `dreamy_input`    
    hopes_and_dreams = view["state"]["values"]["refmid"]["number_input-action"]["value"]
    print(hopes_and_dreams)
    user = body["user"]["id"]
    # Validate the inputs
    errors = {}
    if hopes_and_dreams is not None and len(hopes_and_dreams) <= 0:
        errors["input_c"] = "The value must be longer than 5 characters"
    if len(errors) > 0:
        ack(response_action="errors", errors=errors)
        return
    # Acknowledge the view_submission request and close the modal
    ack()
    # Do whatever you want with the input data - here we're saving it to a DB
    # then sending the user a verification of their submission

    # Message to send user
    msg = ""
    try:
        # Save to DB
        msg = f"Your submission of {hopes_and_dreams} was successful"
    except Exception as e:
        # Handle error
        msg = "There was an error with your submission"

    # Message the user
    try:
        client.chat_postMessage(channel=user, text=msg)
    except e:
        logger.exception(f"Failed to post a message {e}")

@app.action("sGF")
def handle_some_action(ack, body, logger):
    ack()
    logger.info(body)

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 8080)))
