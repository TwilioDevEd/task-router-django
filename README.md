<a href="https://www.twilio.com">
  <img src="https://static0.twilio.com/marketing/bundles/marketing/img/logos/wordmark-red.svg" alt="Twilio" width="250" />
</a>

# Task Router - Python/Django
[![Build Status](https://travis-ci.org/TwilioDevEd/task-router-django.svg?branch=master)](https://travis-ci.org/TwilioDevEd/task-router-django)

 Use Twilio to provide your user with multiple options through phone calls, so they can be assisted by an agent specialized in the chosen topic. This is basically a call center created with the Task Router API of Twilio. This example uses a PostgreSQL database to log phone calls which were not assisted.

[Read the full tutorial here](//www.twilio.com/docs/tutorials/walkthrough/task-router/python/django)

### Prerequisites

1. [Python [2.7;3.4]](https://www.python.org/downloads/) installed in your operative system.
1. A Twilio account with a verified [phone number][twilio-phone-number]. (Get a [free account](//www.twilio.com/try-twilio?utm_campaign=tutorials&utm_medium=readme)
here.).  If you are using a Twilio Trial Account, you can learn all about it [here](https://www.twilio.com/help/faq/twilio-basics/how-does-twilios-free-trial-work).

### Local Development

1. First clone this repository and `cd` into it.

   ```
   $ git clone git@github.com:TwilioDevEd/task-router-django.git
   $ cd task-router-django
   ```

1. Create a new virtual environment.

   - If using vanilla [virtualenv](https://virtualenv.pypa.io/en/latest/):

       ```bash
       virtualenv venv
       source venv/bin/activate
       ```

   - If using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/):

       ```bash
       mkvirtualenv task-router-django
       ```

1. Setup your configuration in your local environment.

   You can use the `.env.example` in a Unix based operative system with the `source` command to load the variables into your environment:

   ```bash
   $ source .env.example
   ```

 Otherwise load them manually.

1. Install the required dependencies, contained in `requirements.txt`.

   ```bash
   $ pip install -r requirements.txt
   ```

1. Run the migrations.

   ```bash
   python manage.py migrate
   ```

1. Make sure the tests succeed.

   ```bash
   $ python manage.py test --settings=twilio_sample_project.settings.test
   ```

1. Configure the phone number of the agents which are going to answer the calls.

    ```
   $ python manage.py create_workspace https://<sub-domain>.ngrok.io <agent1-phone> <agent2-phone>
    ```
   You will receive a message telling you to export 2 environment variables.

    ```
   $ export WORKFLOW_SID=<hashvalue-workflow-sid>
   $ export POST_WORK_ACTIVITY_SID=<hashvalue-post-work-activity-sid>
    ```

   When the user calls, he will choose one option which will redirect him to the first agent whose phone number is __agent1-phone__. If the user gets no answer in 30 seconds he will be redirected to the second agent whose phone number is __agent2-phone__.

1. Start the server.

   ```bash
   $ python manage.py runserver
   ```

1. Expose your local web server to the internet using ngrok.

You can click [here](https://www.twilio.com/blog/2015/09/6-awesome-reasons-to-use-ngrok-when-testing-webhooks.html) for more details. This step is important because the application won't work as expected if you run it using `localhost`.

   ```bash
   $ ngrok http 8000
   ```

Once ngrok is running open up your browser and go to your ngrok URL. It will look something like this:

  `http://<sub-domain>.ngrok.io/`

1. Configure Twilio to call your webhooks.

 You will also need to configure Twilio to call your application via POST when phone calls are received on your _Twilio Number_. The configuration of **Voice** should look something like this:

  ```
  http://<sub-domain>.ngrok.io/call/incoming
  ```

  ![Configure SMS](http://howtodocs.s3.amazonaws.com/twilio-number-config-all-med.gif)

That's it!

### How To Demo?

1. Call your Twilio Phone Number. You will get a voice response:

   ```txt
  For Programmable SMS, press one.
  For Voice, press any other key.
  ```

1. Reply with 1.
1. The specified phone for agent 1 will be called:  __agent1-phone__.
1. If __agent1-phone__ is not attended in 30 seconds then __agent2-phone__ will be called.
1. In case the second agent doesn't attend the call, it will be logged as a missed call. You can see all missed calls in the main page of the running server at [http://<sub-domain>.ngrok.io](//localhost:8000).
1. Repeat the process but enter any key different to __1__ to choose Voice.

[twilio-phone-number]: https://www.twilio.com/console/phone-numbers/incoming

## Meta

* No warranty expressed or implied. Software is as is. Diggity.
* [MIT License](http://www.opensource.org/licenses/mit-license.html)
* Lovingly crafted by Twilio Developer Education.
