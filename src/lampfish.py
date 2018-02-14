#!/usr/bin/python
# Author: Brian Hardenstein

from flask import Flask, render_template, request
import pika
app = Flask(__name__)


def send_to_lights(data):
    ''' data is a string that will be parsed by the receiving end and turned
        into light string commands.  String should be in the format of:
        mode_brightness
        ex: 'on_255' OR 'on_128' OR 'off_0'
    '''
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

    channel = connection.channel()

    channel.queue_declare(queue="lampfish")

    channel.basic_publish(exchange="",
                          routing_key="lampfish",
                          body=data)
    print("send_to_rabbitmq -> sent:", data)
    connection.close()


@app.route("/")
def main():
    # mode_data = {"lamp_on": False,
    #              "lamp_brightness": 255}

    # For each pin, read the pin state and store it in the pins dictionary:
    # for pin in pins:
    #     pins[pin]['state'] = GPIO.input(pin)
    #
    # # Put the pin dictionary into the template data dictionary:
    # templateData = {'pins': pins}

    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', action="off", lamp_brightness=255)


# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<action>")
def action(action):

    # run_strip(mode=action)
    # If the action part of the URL is "on," execute the code indented below:
    if action == "on":
        # Set the pin high:
        send_to_lights("on_255")
        # Save the status message to be passed into the template:
        print("action -> Sent 'lamp on' to queue")

    if action == "off":
        send_to_lights("on_255")
        print("action -> Sent 'lamp off' to queue")

    # print("message: ", message)

    return render_template('main.html', action=action)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
