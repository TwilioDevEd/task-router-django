<a href="https://www.twilio.com">
  <img src="https://static0.twilio.com/marketing/bundles/marketing/img/logos/wordmark-red.svg" alt="Twilio" width="250" />
</a>

# Task Router - Python/Django

[![Build and test](https://github.com/TwilioDevEd/task-router-django/actions/workflows/build_test.yml/badge.svg)](https://github.com/TwilioDevEd/task-router-django/actions/workflows/build_test.yml)

Use Twilio to provide your user with multiple options through phone calls, so
they can be assisted by an agent specialized in the chosen topic. This is
basically a call center created with the Task Router API of Twilio. This example
uses a PostgreSQL database to log phone calls which were not assisted.


[Read the full tutorial here](https://www.twilio.com/docs/taskrouter/tutorials/dynamic-call-center-python-django)

### Prerequisites

1. [Python [3.6+]](https://www.python.org/downloads/) installed in your operative system.
1. A Twilio account with a verified [phone number][twilio-phone-number]. (Get a
   [free account](https://www.twilio.com/try-twilio?utm_campaign=tutorials&utm_medium=readme)
   here.) If you are using a Twilio Trial Account, you can learn all about it
   [here](https://www.twilio.com/help/faq/twilio-basics/how-does-twilios-free-trial-work).


### Local Development

1. First clone this repository and `cd` into it.

   ```
   $ git clone git@github.com:TwilioDevEd/task-router-django.git
   $ cd task-router-django
   ```

1. Create a new virtual environment.

   - If using vanilla with Python 3 [virtualenv](https://docs.python.org/3/library/venv.html):

       ```bash
       python -m venv venv
       source venv/bin/activate
       ```

   - If using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/):

       ```bash
       mkvirtualenv task-router-django
       ```

1. Copy the `.env_example` file to `.env`, and edit it to include your Twilio API credentials 

1. Install the required dependencies, contained in `requirements.txt`.

   ```bash
   $ pip install -r requirements.txt
   ```

1. Setup your database:
   ```bash
   createdb task_router
   ```

1. Run the migrations.

   ```bash
   python manage.py migrate
   ```

1. Make sure the tests succeed.

   ```bash
   $ python manage.py test --settings=twilio_sample_project.settings.test
   ```


1. Start the server.

   ```bash
   $ python manage.py runserver
   ```

1. Expose your local web server to the internet using ngrok.

   You can click [here](https://www.twilio.com/blog/2015/09/6-awesome-reasons-to-use-ngrok-when-testing-webhooks.html)
   for more details. This step is important because the application won't
   work as expected if you run it using `localhost`.

   ```bash
   $ ngrok http 8000
   ```

   Once ngrok is running open up your browser and go to your ngrok URL. It will look something like this:

   `http://<sub-domain>.ngrok.io/`

1. Configure Twilio to call your webhooks.

   You will also need to configure Twilio to call your application via POST when
   phone calls are received on your _Twilio Number_. The configuration of
   **Voice** should look something like this:

   ```
   http://<sub-domain>.ngrok.io/call/incoming/
   ```

   ![Configure SMS](http://howtodocs.s3.amazonaws.com/twilio-number-config-all-med.gif)

*Note:* To enable debug logs in local environment, set the `DEBUG` variable to `True` in the `local.py` file
### Use Production Environment

Follow previous guide and in step 3 do:

1. Copy the `.env.production.example` file to `.env` and add your `DJANGO_SECRET_KEY`

## How to Demo

1. First make sure you have exported all the required environment variables from
   the `.env.example` file. Bob and Alice's number should be two different numbers
   where you can receive calls and SMSs.

1. When you run the app, a new workspace will be configured. Once that is done,
   you are ready to call your [Twilio Number](https://www.twilio.com/console/phone-numbers/incoming)
   where you'll be asked to select a product using your key pad.

1. Select an option and the phone assigned to the product you selected (Bob or Alice's)
   will start ringing. You can answer the call and have a conversation.

1. Alternatively, if you don't answer the call within 15 seconds, the call should be
   redirected to the next worker. If the call isn't answered by the second worker,
   you should be redirected to voice mail and leave a message. The transcription
   of that message should be sent to the email you specified in your environment variables.

1. Each time a worker misses a call, their activity is changed to offline. Right after they
   should receive a notification, via SMS, saying that they missed the call. In order to go
   back online they can reply with `On`. They can as well reply with `Off` in order
   to go back to offline status.

1. If both workers' activity changes to `Offline` and you call your Twilio Number again,
   you should be redirected to voice mail after a few seconds as the workflow timeouts
   when there are no available workers. Change your workers status with the `On`
   SMS command to be able to receive calls again.

1. Navigate to `https://<ngrok_subdomain>.ngrok.io` to see a list of the missed calls.

[twilio-phone-number]: https://www.twilio.com/console/phone-numbers/incoming

## Meta

* No warranty expressed or implied. Software is as is. Diggity.
* [MIT License](http://www.opensource.org/licenses/mit-license.html)
* Lovingly crafted by Twilio Developer Education.
